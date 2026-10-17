#!/usr/bin/env python3
"""아케이드 · Roblox 포맷 규칙 시뮬레이션 (표준 라이브러리만, 결정론적).

실행: --test (규칙 검사, 마지막 줄 passed k/n, 종료코드 = 실패 수) · --demo (시드 고정 한 판 요약)
수치 출처: README §4 (OgarII 공식). 그 밖의 값은 전부 예시값이며 logic.md §2 JSON과 같다.
"""
import math
import random
import sys
from collections import deque

CONFIG = {
    "round": {"min_players": 2, "intermission_s": 15, "round_s": 90, "results_s": 5,
              "win_reward": 50, "participation_reward": 10, "maps": ["A", "B", "C"]},
    "obby": {"stage_count": 50},
    "tycoon": {
        "offline_cap_s": 28800,
        "buttons": [
            {"id": "dropper1", "cost": 0, "requires": [], "income_per_s": 1},
            {"id": "conveyor", "cost": 50, "requires": ["dropper1"], "income_per_s": 0},
            {"id": "dropper2", "cost": 200, "requires": ["conveyor"], "income_per_s": 3},
            {"id": "upgrader", "cost": 500, "requires": ["dropper2"], "income_per_s": 5},
            {"id": "dropper3", "cost": 1500, "requires": ["conveyor", "upgrader"], "income_per_s": 12},
        ],
    },
    "runner": {"base_speed": 16, "accel_per_s": 0.4, "max_speed": 40, "chunk_len": 60, "tier_every_m": 300,
               "chunks": [{"id": "flat", "tier": 1}, {"id": "gap", "tier": 1}, {"id": "double_gap", "tier": 2},
                          {"id": "swing", "tier": 2}, {"id": "laser_grid", "tier": 3}, {"id": "collapse", "tier": 3}]},
    "io": {"speed_base": 88, "speed_exp": -0.4396754, "mass_div": 100,
           "zoom_ref": 64, "zoom_exp": 0.4, "view_w": 1920,
           "eat_margin": 1.15, "start_size": 32, "pellet_size": 10},
    "maze": {"width": 15, "height": 15, "ratio_min": 0.55, "ratio_max": 0.72, "max_attempts": 50},
    "climb": {"fall_min": 10},
}

# ---------------------------------------------------------------- 3.1 Obby
class CheckpointService:
    """스테이지 체크포인트 검증: 다음 스테이지만 받는다 (stage == current + 1)."""

    def __init__(self, cfg):
        self.cfg, self.stage = cfg, {}  # stage: player -> 현재 스테이지 (0 = 시작)

    def touch(self, player, stage):
        """클라이언트가 보고한 체크포인트 접촉. 반환: accepted | ignored | rejected."""
        if not isinstance(stage, int) or stage < 1 or stage > self.cfg["stage_count"]:
            return "rejected"
        cur = self.stage.get(player, 0)
        if stage == cur + 1:
            self.stage[player] = stage
            return "accepted"
        if stage <= cur:
            return "ignored"  # 리스폰 후 같은 체크포인트 재접촉: 치트 아님
        return "rejected"  # 스킵 (cur+2 이상)

    def buy_skip(self, player):
        """유료 스킵: 서버가 한 칸만 올린다. 클라이언트가 목표 스테이지를 정하지 않는다."""
        cur = self.stage.get(player, 0)
        self.stage[player] = min(cur + 1, self.cfg["stage_count"])
        return self.stage[player]

# -------------------------------------------------------------- 3.2 Tycoon
class Plot:
    """타이쿤 플롯: 구매 버튼 ID 집합이 곧 상태. 수입은 집합에서 매번 다시 계산."""

    def __init__(self, cfg, purchased=None, coins=0):
        self.cfg, self.by_id = cfg, {b["id"]: b for b in cfg["buttons"]}
        self.purchased, self.coins = set(purchased or []), coins

    def income_per_s(self):
        return sum(self.by_id[i]["income_per_s"] for i in self.purchased)

    def can_buy(self, button_id):
        """구매 가능 여부와 사유."""
        b = self.by_id.get(button_id)
        if b is None:
            return False, "unknown"
        if button_id in self.purchased:
            return False, "owned"
        if any(r not in self.purchased for r in b["requires"]):
            return False, "prereq"
        if self.coins < b["cost"]:
            return False, "coins"
        return True, "ok"

    def buy(self, button_id):
        ok, why = self.can_buy(button_id)
        if ok:
            self.coins -= self.by_id[button_id]["cost"]
            self.purchased.add(button_id)
        return ok, why

    def collect(self, elapsed_s):
        """온라인 수입. 음수 시간(시계 역행)은 0."""
        gained = max(0, elapsed_s) * self.income_per_s()
        self.coins += gained
        return gained

    def offline_income(self, elapsed_s):
        """오프라인 수입: 경과 시간을 상한으로 자르고 음수는 0."""
        t = min(max(0, elapsed_s), self.cfg["offline_cap_s"])
        return t * self.income_per_s()

    def save(self):
        """저장은 구매 ID 목록과 재화만. 플롯의 파트·위치는 저장하지 않는다."""
        return {"version": 1, "purchased": sorted(self.purchased), "coins": self.coins}

    @classmethod
    def rebuild(cls, cfg, data):
        """접속 시 저장 데이터에서 플롯 재구성. Config에 없는 ID는 버린다."""
        known = {b["id"] for b in cfg["buttons"]}
        return cls(cfg, [i for i in data["purchased"] if i in known], data["coins"])

# -------------------------------------------------------------- 3.3 Runner
class RunnerTrack:
    """청크 기반 러너 트랙: 거리로 티어를 정하고 티어 안에서 청크를 고른다."""

    def __init__(self, cfg, seed):
        self.cfg, self.rng = cfg, random.Random(seed)
        self.max_tier = max(c["tier"] for c in cfg["chunks"])

    def tier_at(self, distance_m):
        return min(self.max_tier, 1 + int(distance_m // self.cfg["tier_every_m"]))

    def generate(self, n):
        """n개 청크 열. (거리, 청크id, 티어). 오브젝트 풀링은 렌더 쪽 일이라 여기선 다루지 않음."""
        out = []
        for i in range(n):
            d = i * self.cfg["chunk_len"]
            tier = self.tier_at(d)
            pool = [c for c in self.cfg["chunks"] if c["tier"] == tier]
            out.append((d, self.rng.choice(pool)["id"], tier))
        return out

    def speed_at(self, t_s):
        """속도 곡선: 선형 증가, 상한."""
        return min(self.cfg["max_speed"], self.cfg["base_speed"] + self.cfg["accel_per_s"] * t_s)

# ------------------------------------------------------------------ 3.4 .io
def io_speed(cfg, size, move_mult=1.0):
    """OgarII: 88 × size^-0.4396754 × moveMult."""
    return cfg["speed_base"] * (size ** cfg["speed_exp"]) * move_mult

def io_mass(cfg, size):
    """OgarII: mass = size² / 100."""
    return size * size / cfg["mass_div"]

def io_size_from_mass(cfg, mass):
    return math.sqrt(mass * cfg["mass_div"])

def io_zoom(cfg, size):
    """OgarII: s = min(64/size, 1)^0.4, 시야 폭 = 1920 / s / 2. (s, 시야폭) 반환."""
    s = min(cfg["zoom_ref"] / size, 1.0) ** cfg["zoom_exp"]
    return s, cfg["view_w"] / s / 2

def io_try_eat(cfg, eater_size, prey_size):
    """서버 판정: eater가 prey보다 margin 배 이상 커야 먹는다. 성공 시 새 size, 실패 시 None."""
    if eater_size >= prey_size * cfg["eat_margin"]:
        return io_size_from_mass(cfg, io_mass(cfg, eater_size) + io_mass(cfg, prey_size))
    return None

# ----------------------------------------------------------------- 3.5 Maze
def maze_generate(w, h, rng):
    """Recursive backtracker. 반환: 셀 -> 이웃 집합 (통로 그래프)."""
    adj = {(x, y): set() for x in range(w) for y in range(h)}
    seen, stack = {(0, 0)}, [(0, 0)]
    while stack:
        x, y = stack[-1]
        nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= x + dx < w and 0 <= y + dy < h and (x + dx, y + dy) not in seen]
        if not nb:
            stack.pop()
            continue
        n = rng.choice(nb)
        adj[(x, y)].add(n)
        adj[n].add((x, y))
        seen.add(n)
        stack.append(n)
    return adj

def maze_bfs(adj, start):
    """BFS 거리장. 셀 -> 시작점에서의 거리."""
    dist, q = {start: 0}, deque([start])
    while q:
        c = q.popleft()
        for n in adj[c]:
            if n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    return dist

def maze_path_ratio(adj, start, exit_cell):
    """경로 비율 = 출구 BFS 거리 / 시작점에서 가장 먼 셀의 거리 (예시 정의)."""
    dist = maze_bfs(adj, start)
    return dist[exit_cell] / max(dist.values())

def maze_accept(cfg, seed):
    """비율 창 안의 미로가 나올 때까지 (seed, seed+1, ...)로 재생성. 반환: (adj, ratio, used_seed, attempts)."""
    w, h = cfg["width"], cfg["height"]
    for i in range(cfg["max_attempts"]):
        s = seed + i
        adj = maze_generate(w, h, random.Random(s))
        r = maze_path_ratio(adj, (0, 0), (w - 1, h - 1))
        if cfg["ratio_min"] <= r <= cfg["ratio_max"]:
            return adj, r, s, i + 1
    raise RuntimeError("maze: window not reached within max_attempts")

# -------------------------------------------------------- 3.6 Round manager
class RoundManager:
    """로비 → 인터미션 → 라운드 → 결과. 서버만 상태를 바꾸고, 1초 틱으로 진행."""

    def __init__(self, cfg):
        self.cfg, self.state, self.timer = cfg, "Lobby", 0
        self.players, self.alive, self.participants = set(), set(), set()
        self.round_index, self.current_map = 0, None
        self.ledger = []  # (player, amount, reason): addCurrency 단일 진입점 대용

    def _enter(self, state):
        c = self.cfg
        self.state = state
        self.timer = {"Lobby": 0, "Intermission": c["intermission_s"],
                      "Round": c["round_s"], "Results": c["results_s"]}[state]
        if state == "Round":
            self.current_map = c["maps"][self.round_index % len(c["maps"])]
            self.round_index += 1
            self.alive, self.participants = set(self.players), set(self.players)
        if state == "Results":  # 보상은 서버 계산, 이탈자는 미지급
            for p in sorted(self.participants & self.players):
                won = p in self.alive
                self.ledger.append((p, c["win_reward" if won else "participation_reward"], "win" if won else "participation"))

    def join(self, p):
        self.players.add(p)

    def leave(self, p):
        self.players.discard(p)
        self.alive.discard(p)

    def die(self, p):
        if self.state == "Round":
            self.alive.discard(p)

    def tick(self):
        """1초 진행. 전이 조건을 여기서만 평가한다."""
        enough = len(self.players) >= self.cfg["min_players"]
        if self.state == "Lobby":
            if enough:
                self._enter("Intermission")
            return self.state
        self.timer -= 1
        if self.state == "Intermission":
            if not enough:
                self._enter("Lobby")
            elif self.timer <= 0:
                self._enter("Round")
        elif self.state == "Round":
            if len(self.alive) <= 1 or self.timer <= 0:
                self._enter("Results")
        elif self.state == "Results" and self.timer <= 0:
            self._enter("Lobby")
        return self.state

# ------------------------------------------------------- 3.7 No-checkpoint climb
class ClimbTracker:
    """무체크포인트 등반: 최고 높이와 추락 거리를 서버가 기록한다."""

    def __init__(self, cfg, start_y=0.0):
        self.cfg, self.best_height, self.peak = cfg, start_y, start_y
        self.falls = []  # 착지 시 확정된 추락 거리 목록

    def update(self, y, grounded):
        """서버가 관측한 위치. 착지 시 peak-y가 임계 이상이면 추락 1건 확정."""
        if y > self.peak:
            self.peak = y
            self.best_height = max(self.best_height, y)
        elif grounded and self.peak - y >= self.cfg["fall_min"]:
            self.falls.append(self.peak - y)
            self.peak = y

    def biggest_fall(self):
        return max(self.falls) if self.falls else 0.0

# ================================================================== tests
def test_obby_accepts_next_stage():
    s = CheckpointService(CONFIG["obby"])
    assert [s.touch("p", i) for i in (1, 2, 3)] == ["accepted"] * 3 and s.stage["p"] == 3
    assert s.touch("p", 3) == "ignored" and s.stage["p"] == 3

def test_obby_rejects_skip_and_backward():
    s = CheckpointService(CONFIG["obby"])
    assert s.touch("p", 1) == "accepted" and s.touch("p", 5) == "rejected" and s.stage["p"] == 1
    assert s.touch("p", 0) == "rejected" and s.touch("p", 999) == "rejected"
    assert s.touch("p", "2") == "rejected" and s.stage["p"] == 1
    assert s.buy_skip("p") == 2 and s.touch("p", 3) == "accepted"

def test_tycoon_prerequisite_tree():
    p = Plot(CONFIG["tycoon"], coins=10_000)
    assert p.buy("dropper3") == (False, "prereq")
    assert p.buy("dropper1")[0] and p.buy("conveyor")[0] and p.buy("dropper2")[0]
    assert p.buy("dropper3") == (False, "prereq")  # upgrader 미구매
    assert p.buy("upgrader")[0] and p.buy("dropper3")[0]
    assert p.buy("dropper3") == (False, "owned") and p.buy("nope") == (False, "unknown")
    q = Plot(CONFIG["tycoon"], ["dropper1"], coins=10)
    assert q.buy("conveyor") == (False, "coins")

def test_tycoon_save_rebuild_roundtrip():
    p = Plot(CONFIG["tycoon"], coins=1000)
    [p.buy(b) for b in ("dropper1", "conveyor", "dropper2")]
    data, r = p.save(), Plot.rebuild(CONFIG["tycoon"], p.save())
    assert r.save() == data and r.income_per_s() == p.income_per_s() == 4
    bad = dict(data, purchased=data["purchased"] + ["hacked_button"])
    assert Plot.rebuild(CONFIG["tycoon"], bad).save() == data

def test_tycoon_offline_income_cap():
    cfg, p = CONFIG["tycoon"], Plot(CONFIG["tycoon"], ["dropper1", "conveyor", "dropper2"])
    assert p.offline_income(100) == 400
    assert p.offline_income(cfg["offline_cap_s"] * 3) == p.offline_income(cfg["offline_cap_s"])
    assert p.offline_income(-5000) == 0 and p.collect(-10) == 0

def test_runner_difficulty_monotone():
    seq = RunnerTrack(CONFIG["runner"], seed=7).generate(40)
    tiers = [t for _, _, t in seq]
    assert all(a <= b for a, b in zip(tiers, tiers[1:]))  # 티어는 내려가지 않는다
    assert tiers[0] == 1 and tiers[-1] == 3 and len(set(c for _, c, _ in seq)) >= 4
    assert seq == RunnerTrack(CONFIG["runner"], seed=7).generate(40)  # 결정론

def test_runner_speed_capped():
    r, cfg = RunnerTrack(CONFIG["runner"], 1), CONFIG["runner"]
    v = [r.speed_at(t) for t in range(300)]
    assert v[0] == cfg["base_speed"] and all(a <= b for a, b in zip(v, v[1:]))
    assert max(v) == cfg["max_speed"] and r.speed_at(10_000) == cfg["max_speed"]

def test_io_speed_decreases_zoom_widens():
    cfg, sizes = CONFIG["io"], [10, 32, 64, 128, 400]
    sp = [io_speed(cfg, s) for s in sizes]
    assert all(a > b for a, b in zip(sp, sp[1:]))
    view = [io_zoom(cfg, s)[1] for s in sizes]
    assert all(a <= b for a, b in zip(view, view[1:])) and view[-1] > view[0]
    assert io_zoom(cfg, 32)[0] == 1.0 and io_zoom(cfg, 64)[1] == 960  # 64 이하는 줌 없음
    assert abs(io_mass(cfg, 100) - 100) < 1e-9 and abs(io_size_from_mass(cfg, 100) - 100) < 1e-9

def test_io_eat_requires_margin():
    cfg = CONFIG["io"]
    assert io_try_eat(cfg, 32, 32) is None and io_try_eat(cfg, 35, 32) is None and io_try_eat(cfg, 32, 40) is None
    new = io_try_eat(cfg, 40, 32)
    assert new is not None and new > 40
    assert abs(io_mass(cfg, new) - (io_mass(cfg, 40) + io_mass(cfg, 32))) < 1e-9  # 질량 보존
    assert io_speed(cfg, new) < io_speed(cfg, 40)

def test_maze_in_window_only():
    cfg, lo, hi = CONFIG["maze"], CONFIG["maze"]["ratio_min"], CONFIG["maze"]["ratio_max"]
    results = [maze_accept(cfg, seed) for seed in range(0, 2000, 100)]
    assert all(lo <= r <= hi for _, r, _, _ in results)
    assert all(len(maze_bfs(adj, (0, 0))) == cfg["width"] * cfg["height"] for adj, _, _, _ in results)  # 완전 연결
    assert max(n for _, _, _, n in results) > 1  # 재생성이 실제로 일어남
    raw = [maze_path_ratio(maze_generate(15, 15, random.Random(s)), (0, 0), (14, 14)) for s in range(60)]
    assert any(r < lo or r > hi for r in raw)  # 필터가 실제로 거른다

def test_maze_seed_reproducible():
    a, ra, sa, _ = maze_accept(CONFIG["maze"], 123)
    b, rb, sb, _ = maze_accept(CONFIG["maze"], 123)
    assert a == b and ra == rb and sa == sb
    assert maze_generate(15, 15, random.Random(sa)) == a  # 기록한 시드만으로 재현

def _ticks(m, n):
    for _ in range(n):
        m.tick()
    return m.state

def test_round_requires_min_players():
    m = RoundManager(CONFIG["round"])
    m.join("a")
    assert m.tick() == "Lobby"
    m.join("b")
    assert m.tick() == "Intermission"
    m.leave("b")
    assert m.tick() == "Lobby"  # 인터미션 중 이탈 → 로비 복귀

def test_round_early_end():
    cfg, m = CONFIG["round"], RoundManager(CONFIG["round"])
    [m.join(p) for p in "abc"]
    assert _ticks(m, cfg["intermission_s"] + 1) == "Round" and m.alive == {"a", "b", "c"}
    m.die("a")
    assert m.tick() == "Round"
    m.leave("b")
    assert m.tick() == "Results" and m.timer == cfg["results_s"]
    assert {p: a for p, a, _ in m.ledger} == {"a": cfg["participation_reward"], "c": cfg["win_reward"]}  # 이탈자 미지급
    assert _ticks(m, cfg["results_s"]) == "Lobby"

def test_round_map_rotation():
    cfg, m, seen = CONFIG["round"], RoundManager(CONFIG["round"]), []
    m.join("a"), m.join("b")
    for _ in range(3 * (cfg["intermission_s"] + cfg["round_s"] + cfg["results_s"] + 2)):
        before = m.state
        if m.tick() == "Round" and before != "Round":
            seen.append(m.current_map)
    assert seen[:3] == cfg["maps"]

def test_climb_fall_and_best_height():
    c = ClimbTracker(CONFIG["climb"])
    [c.update(y, g) for y, g in ((5, True), (20, False), (30, True), (28, False), (26, True))]
    assert c.best_height == 30 and c.falls == []  # 4 떨어진 건 추락 아님
    c.update(3, False)
    assert c.falls == []  # 공중: 아직 확정 안 함
    c.update(3, True)
    assert c.falls == [27] and c.biggest_fall() == 27 and c.best_height == 30
    c.update(12, True), c.update(0, True)
    assert c.falls == [27, 12] and c.best_height == 30

TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

def run_tests():
    failed = 0
    for t in TESTS:
        try:
            t()
            print("ok   ", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL ", t.__name__, "->", repr(e))
    print(f"passed {len(TESTS) - failed}/{len(TESTS)}")
    return failed

def demo(seed=42):
    """시드 고정 한 판 요약."""
    rng, io = random.Random(seed), CONFIG["io"]
    adj, r, s, n = maze_accept(CONFIG["maze"], seed)
    print(f"[demo] seed={seed}\nmaze   15x15 ratio={r:.3f} seed_used={s} attempts={n}")
    track = RunnerTrack(CONFIG["runner"], seed)
    print("runner", [f"{c}/T{t}" for _, c, t in track.generate(12)], "speed@0/30/60/120:", [track.speed_at(t) for t in (0, 30, 60, 120)])
    size = io["start_size"]
    for _ in range(6):
        size = io_try_eat(io, size, io["pellet_size"]) or size
    print(f"io     after 6 pellets size={size:.1f} speed={io_speed(io, size):.1f} view={io_zoom(io, size)[1]:.0f}")
    p = Plot(CONFIG["tycoon"], coins=300)
    [p.buy(b) for b in ("dropper1", "conveyor", "dropper2")]
    print("tycoon", p.save(), "income/s", p.income_per_s())
    m, log = RoundManager(CONFIG["round"]), []
    [m.join(q) for q in "abcd"]
    for t in range(140):
        if m.state == "Round" and m.alive and rng.random() < 0.05:
            m.die(rng.choice(sorted(m.alive)))
        before = m.state
        if m.tick() != before:
            log.append(f"t={t + 1}:{m.state}")
    print("round ", " ".join(log), "| map", m.current_map, "| ledger", m.ledger)

if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.exit(run_tests())
    demo()
