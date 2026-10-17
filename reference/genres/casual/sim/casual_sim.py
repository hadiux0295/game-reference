#!/usr/bin/env python3
"""캐주얼(레벨형 매치3 + 정렬 퍼즐) 기본 베이스 로직 시뮬레이션. 표준 라이브러리만, 결정론적.
실행: python3 -I casual_sim.py --test (마지막 줄 `passed k/n`, 종료 코드 = 실패 수) / --demo (시드 고정 한 판)
"""
import copy
import json
import random
import sys
from collections import Counter, deque

# logic.md §2의 JSON과 같은 값. README §4에 없는 값은 전부 "예시값".
CONFIG = {
    "version": 1, "match3": {"rows": 8, "cols": 8, "colors": 4, "moves": 25,
               "goal": {"type": "collect", "color": 0, "count": 40},
               "continue_moves": 5, "continue_cost": 900, "continue_max_per_level": 1,
               "star_moves_left": [0, 3, 8]},
    "sort": {"capacity": 4, "colors": 6, "empty_tubes": 2, "scramble_steps": 40, "solver_node_budget": 200000},
    "lives": {"max": 5, "regen_sec": 1800},
    "energy": {"cap": 100, "regen_sec": 120, "tap_cost": 1},
    "ads": {"rewarded_contexts": ["loss_recovery"], "rewarded_per_level": 1},
    "difficulty": {"target_fail_rate": 0.5, "near_miss_remaining": 5, "bot_levels": 30},
    "meta": {"decoration_cost_stars": 3},
}
EMPTY = -1

class Match3Board:
    """2차원 int 그리드. 렌더와 분리된 순수 상태 + 처리 순서(스왑→매치→제거→낙하→리필→연쇄→셔플)."""
    def __init__(self, rows, cols, colors, rng, grid=None):
        self.rows, self.cols, self.colors, self.rng = rows, cols, colors, rng
        self.grid = grid if grid is not None else [[EMPTY] * cols for _ in range(rows)]
        if grid is None:
            self.refill()
    def _run(self, r, c, k, dr, dc):
        """(r,c)에서 (dr,dc) 방향으로 색 k가 몇 칸 이어지나."""
        n, r, c = 0, r + dr, c + dc
        while 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == k:
            n, r, c = n + 1, r + dr, c + dc
        return n
    def creates_match(self, r, c, k):
        """(r,c)에 색 k를 두면 3개 이상 줄이 생기나 (리필 규칙용)."""
        return 1 + self._run(r, c, k, 0, -1) + self._run(r, c, k, 0, 1) >= 3 or \
            1 + self._run(r, c, k, -1, 0) + self._run(r, c, k, 1, 0) >= 3
    def refill(self):
        """빈 칸을 아래 행부터 채우되 즉시 매치가 생기는 색은 피한다 (colors>=4면 항상 가능)."""
        for r in range(self.rows - 1, -1, -1):
            for c in range(self.cols):
                if self.grid[r][c] == EMPTY:
                    cands = [k for k in range(self.colors) if not self.creates_match(r, c, k)]
                    self.grid[r][c] = self.rng.choice(cands or list(range(self.colors)))
    def find_matches(self):
        """가로·세로 3개 이상 줄에 속한 칸 집합."""
        cells, g = set(), self.grid
        for r in range(self.rows):
            for c in range(self.cols):
                k = g[r][c]
                if k != EMPTY and c + 2 < self.cols and g[r][c + 1] == k == g[r][c + 2]:
                    cells |= {(r, c), (r, c + 1), (r, c + 2)}
                if k != EMPTY and r + 2 < self.rows and g[r + 1][c] == k == g[r + 2][c]:
                    cells |= {(r, c), (r + 1, c), (r + 2, c)}
        return cells
    def clear(self, cells):
        """칸을 비우고 색별 제거 수(Counter)를 돌려준다."""
        removed = Counter(self.grid[r][c] for r, c in cells)
        for r, c in cells:
            self.grid[r][c] = EMPTY
        return removed
    def apply_gravity(self):
        """열마다 타일을 아래로 떨어뜨린다. 빈 칸은 위쪽으로 모인다."""
        for c in range(self.cols):
            col = [self.grid[r][c] for r in range(self.rows) if self.grid[r][c] != EMPTY]
            for r, k in enumerate([EMPTY] * (self.rows - len(col)) + col):
                self.grid[r][c] = k
    def resolve(self):
        """매치→제거→낙하→리필을 매치가 없을 때까지 반복. (색별 제거 수, 연쇄 횟수)."""
        total, cascades = Counter(), 0
        while cells := self.find_matches():
            total += self.clear(cells)
            self.apply_gravity()
            self.refill()
            cascades += 1
        return total, cascades
    def swap(self, a, b):
        """두 칸 교환."""
        (r1, c1), (r2, c2) = a, b
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
    def preview_swap(self, a, b):
        """스왑했을 때 생기는 매치 칸의 (칸, 색) 목록. 보드는 되돌린다."""
        self.swap(a, b)
        out = [(rc, self.grid[rc[0]][rc[1]]) for rc in self.find_matches()]
        self.swap(a, b)
        return out
    def valid_swaps(self):
        """매치를 만드는 인접 스왑 목록 (스캔 순서 고정 = 결정론). 비어 있으면 데드락."""
        return [((r, c), (r + dr, c + dc)) for r in range(self.rows) for c in range(self.cols)
                for dr, dc in ((0, 1), (1, 0)) if r + dr < self.rows and c + dc < self.cols
                and self.preview_swap((r, c), (r + dr, c + dc))]
    def shuffle(self, max_tries=200):
        """타일 다중집합을 보존한 채 섞는다. 매치 없음 + 유효 수 있음이 될 때까지. 시도 횟수 반환."""
        tiles = [k for row in self.grid for k in row]
        for i in range(1, max_tries + 1):
            self.rng.shuffle(tiles)
            self.grid = [tiles[r * self.cols:(r + 1) * self.cols] for r in range(self.rows)]
            if not self.find_matches() and self.valid_swaps():
                return i
        raise RuntimeError("shuffle 실패: 타일 구성으로는 유효 수를 만들 수 없음 (레벨 데이터 오류)")
    def play_swap(self, a, b):
        """한 수. 매치가 없는 스왑은 되돌리고 None. 성공하면 (제거 Counter, 연쇄 수, 셔플 여부)."""
        if not self.preview_swap(a, b):
            return None
        self.swap(a, b)
        removed, cascades = self.resolve()
        if shuffled := not self.valid_swaps():
            self.shuffle()
        return removed, cascades, shuffled

def make_level(level_id, seed, cfg=None):
    """결정론적 레벨 JSON(dict). 보드는 seed로 생성하므로 저장하지 않아도 재현된다."""
    m = cfg or CONFIG["match3"]
    return {"id": level_id, "seed": seed, "rows": m["rows"], "cols": m["cols"],
            "colors": m["colors"], "moves": m["moves"], "goal": dict(m["goal"])}

def greedy_bot(board, goal):
    """탐욕 봇: 목표 색 제거 수 ×10 + 총 제거 수가 최대인 스왑. 동률은 스캔 순서 (결정론)."""
    def score(mv):
        cells = board.preview_swap(*mv)
        return 10 * sum(1 for _, k in cells if k == goal["color"]) + len(cells)
    return max(board.valid_swaps(), key=score, default=None)

class LevelRun:
    """레벨 한 판의 상태 (Playing / Won / Failed). 입력은 Playing일 때만 받는다."""
    def __init__(self, level):
        self.level, self.rng = level, random.Random(level["seed"])
        self.board = Match3Board(level["rows"], level["cols"], level["colors"], self.rng,
                                 grid=copy.deepcopy(level["board"]) if "board" in level else None)
        self.moves_left, self.collected, self.state = level["moves"], 0, "Playing"
        self.continues_used, self.history = 0, []
    def remaining(self):
        """목표까지 남은 수집 수."""
        return max(0, self.level["goal"]["count"] - self.collected)
    def step(self, a, b):
        """한 수 적용 후 판정. 유효하지 않은 스왑은 무브를 소모하지 않는다."""
        if self.state != "Playing" or (res := self.board.play_swap(a, b)) is None:
            return False
        self.moves_left -= 1
        self.collected += res[0].get(self.level["goal"]["color"], 0)
        self.history.append((a, b, res[1]))
        if self.remaining() == 0:
            self.state = "Won"
        elif self.moves_left == 0:
            self.state = "Failed"
        return True
    def grant_continue(self, extra_moves):
        """컨티뉴: Failed → Playing, 무브 +N."""
        if self.state != "Failed":
            return False
        self.moves_left, self.continues_used, self.state = self.moves_left + extra_moves, self.continues_used + 1, "Playing"
        return True
    def stars(self, thresholds):
        """남은 무브로 별 1~3 (예시값 임계)."""
        return sum(1 for t in thresholds if self.moves_left >= t) if self.state == "Won" else 0

def play_level(level, bot=greedy_bot):
    """봇으로 한 판 끝까지. LevelRun 반환."""
    run = LevelRun(level)
    while run.state == "Playing":
        run.step(*bot(run.board, level["goal"]))  # shuffle이 유효 수를 보장하므로 None 없음
    return run

def estimate_difficulty(template, n_levels, base_seed, cfg=None):
    """봇 승률·실패율·아슬아슬 비율(실패 중 남은 목표 ≤ near_miss_remaining)을 N판에서 추정."""
    d, wins, near = cfg or CONFIG["difficulty"], 0, 0
    for i in range(n_levels):
        run = play_level(dict(template, seed=base_seed + i, id=i + 1))
        wins += run.state == "Won"
        near += run.state == "Failed" and run.remaining() <= d["near_miss_remaining"]
    fails, fr = n_levels - wins, (n_levels - wins) / n_levels
    verdict = "too_hard" if fr > d["target_fail_rate"] + 0.2 else "too_easy" if fr < d["target_fail_rate"] - 0.2 else "ok"
    return {"win_rate": wins / n_levels, "fail_rate": fr, "near_miss_rate": near / fails if fails else 0.0, "verdict": verdict}

# ───────── 정렬 퍼즐 (water/ball sort) ─────────
def sort_top_run(tube):
    """맨 위 색과 그 연속 개수. 빈 통이면 (None, 0)."""
    if not tube:
        return None, 0
    return tube[-1], next((i for i, x in enumerate(reversed(tube)) if x != tube[-1]), len(tube))

def sort_legal_moves(tubes, cap):
    """정방향 합법 수 (src, dst, 개수): 같은 색 위로 또는 빈 통으로, 들어가는 만큼 붓는다."""
    out = []
    for s, src in enumerate(tubes):
        k, n = sort_top_run(src)
        if k is None or n == len(src) == cap:
            continue  # 빈 통, 또는 이미 완성된 통은 옮기지 않는다
        for d, dst in enumerate(tubes):
            if d == s or len(dst) == cap or (dst and dst[-1] != k) or (not dst and n == len(src)):
                continue  # 가득 참 / 다른 색 / 단색 통→빈 통(무의미)
            out.append((s, d, min(n, cap - len(dst))))
    return out

def sort_apply(tubes, move):
    """수를 적용한 새 상태 (튜플의 튜플)."""
    s, d, n = move
    t = [list(x) for x in tubes]
    t[d].extend(t[s][-n:])
    del t[s][-n:]
    return tuple(tuple(x) for x in t)

def sort_is_solved(tubes, cap):
    """모든 통이 비었거나 단색으로 가득 찼다."""
    return all(not t or (len(t) == cap and len(set(t)) == 1) for t in tubes)

def sort_solve_bfs(tubes, cap, node_budget):
    """BFS 최단 해. (해 길이, 방문 수) 또는 (None, 방문 수). 통 순서를 정렬해 중복 상태를 합친다."""
    start = tuple(tuple(t) for t in tubes)
    if sort_is_solved(start, cap):
        return 0, 1
    seen, q = {tuple(sorted(start))}, deque([(start, 0)])
    while q:
        state, depth = q.popleft()
        for mv in sort_legal_moves(state, cap):
            nxt = sort_apply(state, mv)
            if (key := tuple(sorted(nxt))) in seen:
                continue
            if sort_is_solved(nxt, cap):
                return depth + 1, len(seen)
            seen.add(key)
            if len(seen) > node_budget:
                return None, len(seen)
            q.append((nxt, depth + 1))
    return None, len(seen)

def sort_generate(rng, cfg=None):
    """완성 상태에서 역방향 합법 수만으로 섞는다. 역수 = 정방향 수(a→b, n개)를 정확히 되돌리는 것."""
    s = cfg or CONFIG["sort"]
    cap = s["capacity"]
    tubes = [[k] * cap for k in range(s["colors"])] + [[] for _ in range(s["empty_tubes"])]
    for _ in range(s["scramble_steps"]):
        cands = []
        for b, src in enumerate(tubes):  # b 위의 k색 n개를 a 위로 되돌린다
            k, run = sort_top_run(src)
            for a, dst in enumerate(tubes):
                if k is None or a == b or len(dst) == cap or (dst and dst[-1] == k):
                    continue  # a.top이 같은 색이면 정방향이 더 많이 쏟으므로 정확한 역이 아님
                cands += [(b, a, n) for n in range(1, min(run, cap - len(dst)) + 1)
                          if not src[:-n] or src[-n - 1] == k]  # 정방향 조건: b 비었거나 b.top==k
        if not cands:
            break
        b, a, n = rng.choice(cands)
        tubes[a].extend(tubes[b][-n:])
        del tubes[b][-n:]
    return {"capacity": cap, "tubes": tubes}

def sort_generate_verified(rng, cfg=None, max_tries=20):
    """생성 → BFS 검증 → 불합격 폐기. 풀 수 있는 레벨만 돌려준다 (solution_len 포함)."""
    s = cfg or CONFIG["sort"]
    for _ in range(max_tries):
        lv = sort_generate(rng, s)
        if n := sort_solve_bfs(lv["tubes"], lv["capacity"], s["solver_node_budget"])[0]:
            return dict(lv, solution_len=n)
    return None

# ───────── 경제 · 목숨 · 에너지 · 광고 · 메타 ─────────
class Wallet:
    """재화 증감의 단일 진입점. 잔액 부족이면 거부, 모든 변동은 reason과 함께 로그."""
    def __init__(self, **balances):
        self.bal, self.log = dict(balances), []
    def add(self, kind, amount, reason):
        """증감 요청. 음수 잔액이 되면 False."""
        if self.bal.get(kind, 0) + amount < 0:
            return False
        self.bal[kind] = self.bal.get(kind, 0) + amount
        self.log.append((kind, amount, reason))
        return True

class TimedResource:
    """목숨·에너지 공통: 타임스탬프 기반 재생, 상한, 시간 역행 무시."""
    def __init__(self, cap, regen_sec, now):
        self.cap, self.regen_sec, self.value, self.last = cap, regen_sec, cap, now
    def current(self, now):
        """now 시점의 값. 가득 차 있거나 시계가 역행하면 타이머를 흘리지 않는다."""
        if now < self.last or self.value >= self.cap:
            self.last = now
        else:
            gained = (now - self.last) // self.regen_sec
            self.value = min(self.cap, self.value + gained)
            self.last += gained * self.regen_sec
        return self.value
    def spend(self, now, n=1):
        """n만큼 소모. 부족하면 False."""
        ok = self.current(now) >= n
        self.value -= n * ok
        return ok

class AdPolicy:
    """보상형은 손실 회복 자리에만, 레벨당 N회 (전면 광고 규칙은 범위 밖)."""
    def __init__(self, cfg):
        self.cfg, self.rewarded_this_level = cfg, 0
    def show_rewarded(self, context):
        """허용 문맥·횟수 안이면 노출하고 True."""
        ok = context in self.cfg["rewarded_contexts"] and self.rewarded_this_level < self.cfg["rewarded_per_level"]
        self.rewarded_this_level += ok
        return ok

def fail_flow(run, wallet, lives, ads, now, choice, cfg=None):
    """실패 시 분기: 'buy' 컨티뉴(코인) → 'ad' 보상형 → 그 외 목숨 차감. 결과 문자열 반환."""
    m = cfg or CONFIG["match3"]
    if run.state != "Failed":
        return "not_failed"
    if choice == "buy" and run.continues_used < m["continue_max_per_level"] \
            and wallet.add("coins", -m["continue_cost"], "continue_moves"):
        run.grant_continue(m["continue_moves"])
        return "continued"
    if choice == "ad" and ads.show_rewarded("loss_recovery"):
        run.grant_continue(m["continue_moves"])
        return "continued_ad"
    lives.spend(now)
    return "life_lost"

def collect_stars(run, wallet, cfg=None):
    """승리 → 별을 지갑에 적립 (하이브리드 메타 훅: 별로 장식 해금)."""
    s = run.stars((cfg or CONFIG["match3"])["star_moves_left"])
    return s if s and wallet.add("stars", s, "level_win") else 0

def unlock_decoration(wallet, cfg=None):
    """별로 장식 1개 해금. 단일 진입점을 거치므로 부족하면 거부."""
    return wallet.add("stars", -(cfg or CONFIG["meta"])["decoration_cost_stars"], "decoration")

DEADLOCK_5x5 = [[0, 1, 3, 3, 0], [3, 1, 3, 1, 2], [0, 0, 2, 1, 3], [3, 0, 2, 2, 0], [2, 1, 1, 3, 3]]

def test_refill_no_immediate_match():
    for seed in range(20):
        b = Match3Board(8, 8, 4, random.Random(seed))
        assert not b.find_matches(), "초기 채움에 매치"
        for _ in range(5):
            b.clear(b.find_matches() or {(0, c) for c in range(8)} | {(3, 2), (4, 2), (5, 2)})
            b.apply_gravity()
            new = {(r, c) for r in range(8) for c in range(8) if b.grid[r][c] == EMPTY}
            b.refill()
            assert not (new & b.find_matches()), "새 타일이 즉시 매치를 만듦"

def test_match3_processing_order():
    b = Match3Board(8, 8, 4, random.Random(3))
    removed, cascades, _ = b.play_swap(*greedy_bot(b, {"color": 0}))
    assert sum(removed.values()) >= 3 and cascades >= 1
    assert not b.find_matches() and all(k != EMPTY for row in b.grid for k in row)
    b.clear({(7, 0), (6, 0), (2, 3), (0, 1)})
    b.apply_gravity()  # 낙하 후: 각 열은 위쪽 빈 칸 + 아래쪽 타일, 공중에 뜬 타일 없음
    for c in range(8):
        col = [b.grid[r][c] for r in range(8)]
        assert col == sorted(col, key=lambda k: k != EMPTY), "빈 칸은 위, 타일은 아래"
    b.refill()
    snap, run = copy.deepcopy(b.grid), LevelRun(make_level(1, 5))
    bad = next(((r, c), (r, c + 1)) for r in range(8) for c in range(7) if not b.preview_swap((r, c), (r, c + 1)))
    assert b.play_swap(*bad) is None and b.grid == snap, "매치 없는 스왑은 되돌린다"
    assert run.step(*bad) is False and run.moves_left == CONFIG["match3"]["moves"], "무브 미소모"

def test_deadlock_shuffle():
    b = Match3Board(5, 5, 4, random.Random(1), grid=copy.deepcopy(DEADLOCK_5x5))
    assert not b.find_matches() and not b.valid_swaps(), "데드락 보드가 아님"
    before = sorted(k for row in b.grid for k in row)
    b.shuffle()
    assert b.valid_swaps() and not b.find_matches() and sorted(k for row in b.grid for k in row) == before, "유효 수 + 타일 다중집합 보존"

def test_level_replay_deterministic():
    lv = make_level(7, 1234)
    a, b = play_level(lv), play_level(json.loads(json.dumps(lv, sort_keys=True)))
    assert a.history == b.history and a.state == b.state and a.board.grid == b.board.grid and len(a.history) >= 1

def test_bot_winrate_and_near_miss():
    base = make_level(1, 100)
    lo, hi = estimate_difficulty(dict(base, moves=10), 15, 500), estimate_difficulty(dict(base, moves=40), 15, 500)
    assert 0 <= lo["win_rate"] <= hi["win_rate"] <= 1, "무브가 늘면 승률은 줄지 않는다"
    assert estimate_difficulty(base, 10, 500) == estimate_difficulty(base, 10, 500), "결정론"
    r = estimate_difficulty(dict(base, moves=6), 20, 900)
    assert 0 <= r["near_miss_rate"] <= 1 and r["verdict"] in ("too_hard", "ok", "too_easy")

def test_sort_pour_rule():
    t = ((1, 1, 2, 2), (2,), (), (1, 1))
    moves = sort_legal_moves(t, 4)
    assert (0, 1, 2) in moves and (0, 2, 2) in moves and (3, 0, 2) not in moves
    assert (3, 2, 2) not in moves, "단색 통→빈 통은 무의미"
    assert sort_apply(t, (0, 1, 2)) == ((1, 1), (2, 2, 2), (), (1, 1))
    assert sort_solve_bfs([[0, 1], [1, 0]], 2, 10000)[0] is None and sort_solve_bfs([[0, 0], [1, 1], []], 2, 10000)[0] == 0

def test_sort_reverse_generation_solvable():
    rng, s = random.Random(42), CONFIG["sort"]
    for _ in range(30):
        lv = sort_generate(rng)
        n, _ = sort_solve_bfs(lv["tubes"], lv["capacity"], s["solver_node_budget"])
        assert n is not None and n >= 1, "역순 생성 레벨이 풀리지 않음"
        assert sorted(k for t in lv["tubes"] for k in t) == sorted(k for k in range(s["colors"]) for _ in range(s["capacity"]))
    assert all(sort_generate_verified(random.Random(7))["solution_len"] >= 1 for _ in range(5))

def test_lives_energy_regen_cap():
    L = TimedResource(5, 1800, now=0)
    assert L.spend(0) and L.spend(0) and L.current(0) == 3
    assert L.current(1799) == 3 and L.current(1800) == 4 and L.current(100000) == 5
    assert L.current(105000) == 5 and L.spend(105000) and L.current(105000 + 1800) == 5, "상한 초과 금지·상한에서 소모 시 타이머 재시작"
    assert L.current(50) == 5, "시계 역행은 무시"
    assert all(L.spend(50) for _ in range(5)) and not L.spend(50), "목숨 0이면 시작 불가"
    E = TimedResource(100, 120, now=0)  # 에너지(머지 변형)도 같은 클래스
    assert all(E.spend(10, CONFIG["energy"]["tap_cost"]) for _ in range(30))
    assert E.current(10) == 70 and E.current(10 + 120 * 3) == 73 and E.current(10 ** 7) == 100

def test_continue_offer_plus5():
    run = LevelRun(dict(make_level(1, 1), moves=1))
    run.step(*greedy_bot(run.board, run.level["goal"]))
    assert run.state == "Failed"
    w, lives, ads = Wallet(coins=1000), TimedResource(5, 1800, 0), AdPolicy(CONFIG["ads"])
    assert fail_flow(run, w, lives, ads, 0, "buy") == "continued"
    assert run.moves_left == 5 and run.state == "Playing" and w.bal["coins"] == 100
    assert w.log == [("coins", -900, "continue_moves")], "재화는 단일 진입점·reason 로그"
    assert not w.add("coins", -101, "x") and w.bal["coins"] == 100, "잔액 부족 거부"
    run.moves_left, run.state = 0, "Failed"
    assert fail_flow(run, w, lives, ads, 0, "buy") == "life_lost", "레벨당 1회 + 잔액 부족"
    assert lives.current(0) == 4

def test_rewarded_ad_placement():
    ads = AdPolicy(CONFIG["ads"])
    assert not ads.show_rewarded("level_start"), "손실 회복 문맥에서만"
    assert ads.show_rewarded("loss_recovery") and not ads.show_rewarded("loss_recovery"), "레벨당 1회"

def test_meta_collection_hook():
    w, run = Wallet(), play_level(dict(make_level(1, 3), moves=60))
    assert run.state == "Won" and collect_stars(run, w) >= 1
    assert w.add("stars", 3, "test") and unlock_decoration(w) and w.bal["stars"] >= 0 and not unlock_decoration(Wallet())

def run_tests():
    """test_* 전부 실행, `passed k/n` 출력, 실패 수 반환."""
    tests, failed = [v for k, v in sorted(globals().items()) if k.startswith("test_")], 0
    for t in tests:
        try:
            t()
            print(f"ok   {t.__name__}")
        except Exception as e:  # noqa
            failed += 1; print(f"FAIL {t.__name__}: {e!r}")
    print(f"passed {len(tests) - failed}/{len(tests)}")
    return failed
def demo():
    """시드 고정 한 판 요약."""
    lv, d = make_level(1, 2026), CONFIG["difficulty"]
    run = play_level(lv)
    print(f"level {json.dumps(lv, sort_keys=True)}")
    print(f"result={run.state} moves_left={run.moves_left} collected={run.collected} cascades={sum(h[2] for h in run.history)}")
    print(f"bot over {d['bot_levels']} levels: {estimate_difficulty(lv, d['bot_levels'], 10)}")
    print(f"sort level (generated+verified): {sort_generate_verified(random.Random(2026))}")

if __name__ == "__main__":
    sys.exit(demo() if "--demo" in sys.argv else run_tests())
