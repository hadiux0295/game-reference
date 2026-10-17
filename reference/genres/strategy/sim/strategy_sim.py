#!/usr/bin/env python3
"""전략 장르 기본 베이스 로직 시뮬레이션: 타워 디펜스 + 경제 루프 뼈대, SLG 타이머·오토배틀러 공유 풀 변형 포함.
순수 표준 라이브러리, 판 안은 정수 연산만(결정론). 실행: python3 -I strategy_sim.py --test | --demo
숫자 출처: README §4, ../../data/td_progression.md. 출처 없는 값은 logic.md §2에 "예시값"으로 표시.
"""
import math
import random
import sys
import zlib

CONFIG = {
    "version": 1,
    "tick_ms": 100,
    "lives": 20,
    "economy": {"start_gold": 650, "wave_bonus_base": 100, "wave_bonus_per_wave": 1, "loss_reward_p": 1.3},
    "cost_curve": {"ratio_pct": 200},
    "cost_ladders": {"btd6_dart": [200, 140, 200, 320], "kr1_archer": [70, 110, 160], "thronefall_tower": [3, 5, 15]},
    "towers": {"dart": {"costs": [200, 140, 200, 320], "damage": [3, 5, 8, 12], "range": 2500, "cooldown_ms": 500, "targeting": "first"}},
    "enemies": {"grunt": {"hp": 10, "speed": 1000, "reward": 1, "leak": 1}, "brute": {"hp": 40, "speed": 600, "reward": 5, "leak": 3}},
    "path": [[0, 0], [6000, 0], [6000, 4000], [0, 4000]],
    "build_slots": [[3000, 1200], [6000, 2000], [3000, 2800], [1000, 1200], [5000, 2800]],
    "waves": [
        {"groups": [{"enemy": "grunt", "count": 6, "interval_ms": 1000}]},
        {"groups": [{"enemy": "grunt", "count": 10, "interval_ms": 800}]},
        {"groups": [{"enemy": "grunt", "count": 8, "interval_ms": 800}, {"enemy": "brute", "count": 2, "interval_ms": 2000}]},
        {"groups": [{"enemy": "grunt", "count": 12, "interval_ms": 600}, {"enemy": "brute", "count": 4, "interval_ms": 1500}]},
        {"groups": [{"enemy": "brute", "count": 8, "interval_ms": 1000}]}
    ],
    "hp_growth_pct_per_wave": 10,
    "slg": {"th17_build_s": 1296000, "help_reduce_s": 60, "max_helps": 30},
    "autobattler": {"pool_copies": {"1": 30, "2": 25, "3": 18, "4": 10, "5": 9},
                    "units_per_cost": {"1": 13, "2": 13, "3": 13, "4": 12, "5": 8},
                    "interest_per": 10, "interest_cap": 5, "win_gold": 1, "players": 8},
    "lockstep": {"turn_ms": 200, "command_delay_turns": 2}
}
# ------------------------------------------------------------ 3.1 경제
class Ledger:
    """재화 증감의 단일 진입점. add() 외의 경로로 gold를 바꾸지 않는다."""
    def __init__(self, start):
        self.gold, self.log = start, []
    def add(self, amount, reason):
        """정수만 허용(부동소수 거부). 잔액이 음수가 되는 소비도 거부(False)."""
        if not isinstance(amount, int) or self.gold + amount < 0:
            return False
        self.gold, _ = self.gold + amount, self.log.append((reason, amount))
        return True

def wave_bonus(cfg, wave):
    """BTD6 라운드 종료 보너스: 100 + 라운드 번호."""
    return cfg["economy"]["wave_bonus_base"] + cfg["economy"]["wave_bonus_per_wave"] * wave

def loss_reward(base, reached, total, p):
    """TDS 패배 보상: base ÷ (1 + (W/w − 1)^p). 완주(w ≥ W)면 base."""
    return float(base) if reached >= total else base / (1 + (total / reached - 1) ** p)

def kr_stars(lives):
    """Kingdom Rush 별: 남은 목숨 18~20 → 3, 6~17 → 2, 1~5 → 1, 0 → 0."""
    return 3 if lives >= 18 else 2 if lives >= 6 else 1 if lives >= 1 else 0
# ------------------------------------------------------------ 3.2 비용 곡선
def exp_cost(base, ratio_pct, n):
    """지수 비용 cost(n) = base · r^n, 정수 연산(r = ratio_pct/100)."""
    return base * ratio_pct ** n // 100 ** n

def bulk_cost(base, ratio_pct, n, k):
    """n단계부터 k개 연속 구매 총액(정수 루프 합)."""
    return sum(exp_cost(base, ratio_pct, i) for i in range(n, n + k))

# ------------------------------------------------------------ 3.5 경로 · 엔티티
class Path:
    """웨이포인트 배열. 진행도(progress, 밀리타일)를 좌표로 바꾼다."""
    def __init__(self, points):
        self.points = [tuple(p) for p in points]
        self.seg_len = [math.isqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) for a, b in zip(self.points, self.points[1:])]
        self.total = sum(self.seg_len)
    def position_at(self, progress):
        """progress ≥ total이면 마지막 점. 정수 보간."""
        rem = max(0, progress)
        for (a, b), length in zip(zip(self.points, self.points[1:]), self.seg_len):
            if rem <= length and length > 0:
                return (a[0] + (b[0] - a[0]) * rem // length, a[1] + (b[1] - a[1]) * rem // length)
            rem -= length
        return self.points[-1]

class Enemy:
    """경로 위를 걷는 적. 상태는 정수뿐."""
    def __init__(self, eid, kind, spec, hp):
        self.id, self.kind, self.hp, self.max_hp = eid, kind, hp, hp
        self.speed, self.reward, self.leak = spec["speed"], spec["reward"], spec["leak"]
        self.progress, self.alive = 0, True

class Tower:
    """고정 포탑. tier는 0(기본)~len(costs)-1."""
    def __init__(self, tid, kind, spec, x, y):
        self.id, self.kind, self.spec, self.x, self.y = tid, kind, spec, x, y
        self.tier, self.cooldown, self.kills, self.targeting = 0, 0, 0, spec["targeting"]
# ------------------------------------------------------------ 3.4 타겟팅
def pick_target(tower, enemies, path, rule):
    """사거리 안 적 중 규칙에 맞는 하나. 동점은 id가 작은 쪽(결정론)."""
    r2 = tower.spec["range"] ** 2
    cands = []
    for e in enemies:
        if e.alive:
            p = path.position_at(e.progress)
            d = (tower.x - p[0]) ** 2 + (tower.y - p[1]) ** 2
            if d <= r2:
                cands.append((e, d))
    if not cands:
        return None
    keys = {"first": lambda ed: (-ed[0].progress, ed[0].id),
            "last": lambda ed: (ed[0].progress, ed[0].id),
            "strongest": lambda ed: (-ed[0].hp, -ed[0].progress, ed[0].id),
            "closest": lambda ed: (ed[1], -ed[0].progress, ed[0].id)}
    return min(cands, key=keys[rule])[0]
# ------------------------------------------------------------ 3.3 웨이브 · 판
def build_spawn_queue(cfg, wave_idx, start_tick):
    """웨이브 테이블 한 행 → (spawn_tick, 그룹, 번호, enemy, hp) 목록. 그룹은 동시에 시작."""
    growth = 100 + cfg["hp_growth_pct_per_wave"] * wave_idx
    queue = []
    for gi, g in enumerate(cfg["waves"][wave_idx]["groups"]):
        spec = cfg["enemies"][g["enemy"]]
        for i in range(g["count"]):
            queue.append((start_tick + g["interval_ms"] * i // cfg["tick_ms"], gi, i, g["enemy"], spec["hp"] * growth // 100))
    return sorted(queue)

class Match:
    """권위 측 한 판: 명령 → 스폰 → 이동/누출 → 사격 → 보상 → 웨이브 판정 → 체크섬."""
    def __init__(self, cfg, seed=0):
        self.cfg, self.rng, self.path = cfg, random.Random(seed), Path(cfg["path"])
        self.ledger, self.lives = Ledger(cfg["economy"]["start_gold"]), cfg["lives"]
        self.tick, self.wave, self.state = 0, 0, "build"  # build | wave | won | lost
        self.enemies, self.towers, self.spawn_queue, self.pending = [], [], [], []
        self.next_id, self.checksums, self.stats = 1, [], {"kills": 0, "leaks": 0}
    def queue_command(self, exec_tick, player, seq, cmd):
        """락스텝: 상태가 아니라 명령만 받고 (실행 틱, 플레이어, 순번)으로 정렬."""
        self.pending.append((exec_tick, player, seq, cmd))
        self.pending.sort(key=lambda p: p[:3])
    def apply(self, cmd):
        """명령 1개 검증·실행. 거부되면 False (gold 불변)."""
        if cmd["op"] == "build":
            spec, slot = self.cfg["towers"].get(cmd["kind"]), [cmd["x"], cmd["y"]]
            if spec is None or slot not in self.cfg["build_slots"] or any(t.x == slot[0] and t.y == slot[1] for t in self.towers):
                return False
            if not self.ledger.add(-spec["costs"][0], "build:" + cmd["kind"]):
                return False
            self.towers.append(Tower(self.next_id, cmd["kind"], spec, slot[0], slot[1]))
            self.next_id += 1
            return True
        if cmd["op"] == "upgrade":
            t = next((t for t in self.towers if t.id == cmd["tower"]), None)
            if t is None or t.tier + 1 >= len(t.spec["costs"]) or not self.ledger.add(-t.spec["costs"][t.tier + 1], "upgrade:" + t.kind):
                return False
            t.tier += 1
            return True
        return self.start_wave() if cmd["op"] == "start_wave" else False
    def start_wave(self):
        if self.state != "build" or self.wave >= len(self.cfg["waves"]):
            return False
        self.spawn_queue = build_spawn_queue(self.cfg, self.wave, self.tick)
        self.wave, self.state = self.wave + 1, "wave"
        return True
    def step(self):
        """§4 틱 순서 그대로. 반환: 이 틱에 처리된 명령 수."""
        n = 0
        while self.pending and self.pending[0][0] <= self.tick:          # 1 명령
            self.apply(self.pending.pop(0)[3])
            n += 1
        while self.spawn_queue and self.spawn_queue[0][0] <= self.tick:  # 2 스폰
            _, _, _, kind, hp = self.spawn_queue.pop(0)
            self.enemies.append(Enemy(self.next_id, kind, self.cfg["enemies"][kind], hp))
            self.next_id += 1
        for e in self.enemies:                                            # 3 이동 · 누출
            e.progress += e.speed * self.cfg["tick_ms"] // 1000
            if e.progress >= self.path.total:
                e.alive, self.lives = False, max(0, self.lives - e.leak)
                self.stats["leaks"] += 1
        for t in self.towers:                                             # 4 사격
            t.cooldown = max(0, t.cooldown - self.cfg["tick_ms"])
            target = None if t.cooldown > 0 else pick_target(t, self.enemies, self.path, t.targeting)
            if target is not None:
                target.hp -= t.spec["damage"][t.tier]
                t.cooldown = t.spec["cooldown_ms"]
                if target.hp <= 0:                                        # 5 처치 보상
                    target.alive, t.kills = False, t.kills + 1
                    self.stats["kills"] += 1
                    self.ledger.add(target.reward, "kill:" + target.kind)
        self.enemies = [e for e in self.enemies if e.alive]
        if self.lives <= 0:                                               # 6 판정
            self.state = "lost"
        elif self.state == "wave" and not self.spawn_queue and not self.enemies:
            self.ledger.add(wave_bonus(self.cfg, self.wave), "wave_bonus")
            self.state = "won" if self.wave >= len(self.cfg["waves"]) else "build"
        self.tick += 1
        self.checksums.append(self.checksum())                            # 7 스냅샷
        return n
    def checksum(self):
        """정수 상태만 직렬화해 CRC32. 부동소수·객체 주소·렌더 상태는 넣지 않는다."""
        parts = [self.tick, self.ledger.gold, self.lives, self.wave, self.state]
        parts += [(e.id, e.hp, e.progress) for e in self.enemies] + [(t.id, t.tier, t.cooldown, t.kills) for t in self.towers]
        return zlib.crc32(repr(parts).encode())
    def run_until_build(self, max_ticks=100000):
        """현재 웨이브가 끝나거나 판이 끝날 때까지 진행."""
        for _ in range(max_ticks):
            if self.state != "wave":
                break
            self.step()
        return self.state
# ------------------------------------------------------------ 3.6 SLG 타이머
class BuildTimer:
    """SLG 건설 타이머: 시간 경과·가속 아이템·동맹 도움이 모두 remaining만 줄인다."""
    def __init__(self, total_s, help_reduce_s, max_helps):
        self.remaining, self.help_reduce_s, self.max_helps, self.helps = total_s, help_reduce_s, max_helps, 0
    def tick(self, dt_s):
        """시간 경과. 0 아래로 내려가지 않는다."""
        self.remaining = max(0, self.remaining - dt_s)
    def accelerate(self, item_s):
        """가속 아이템 = 시간 경과와 같은 함수. 남은 시간보다 큰 아이템을 써도 0에서 멈춘다."""
        self.tick(item_s)
    def help(self, n):
        """동맹 도움 n회. 상한(max_helps)까지만 적용하고 실제 적용 횟수를 돌려준다."""
        applied = min(n, self.max_helps - self.helps)
        self.helps += applied
        self.remaining = max(0, self.remaining - applied * self.help_reduce_s)
        return applied
    def done(self):
        return self.remaining == 0
# ------------------------------------------------------------ 3.7 오토배틀러
class SharedPool:
    """8인이 나눠 쓰는 공유 풀. remaining[(cost, unit)]이 줄면 그 유닛을 뽑을 확률도 준다."""
    def __init__(self, ab_cfg):
        self.remaining = {(int(c), u): n for c, n in ab_cfg["pool_copies"].items() for u in range(ab_cfg["units_per_cost"][c])}
    def total_at(self, cost):
        return sum(v for (c, _), v in self.remaining.items() if c == cost)
    def draw_prob(self, cost, unit):
        """상점 슬롯이 cost 티어로 정해졌을 때 unit이 나올 확률 = 남은 장수 ÷ 티어 전체 남은 장수."""
        total = self.total_at(cost)
        return self.remaining[(cost, unit)] / total if total else 0.0
    def draw(self, rng, cost):
        """남은 장수 가중 뽑기. 풀이 비면 None. 뽑힌 장은 풀에서 빠진다."""
        items = [(k, v) for k, v in self.remaining.items() if k[0] == cost and v > 0]
        r = rng.randrange(sum(v for _, v in items)) if items else -1
        for (c, u), v in items:
            r -= v
            if r < 0:
                self.remaining[(c, u)] -= 1
                return u
        return None
    def release(self, cost, unit):
        """판매·탈락 시 풀로 반환."""
        self.remaining[(cost, unit)] += 1

def interest(gold, per=10, cap=5):
    """TFT 이자: 은행 10골드당 +1, 최대 +5."""
    return min(gold // per, cap)
# ------------------------------------------------------------ 3.8 락스텝
def run_lockstep(cfg, seed, commands, max_ticks=100000):
    """명령 목록(발행 틱·플레이어·순번)만으로 한 판을 재생. AoE식 2턴 지연 실행. Match 반환."""
    m = Match(cfg, seed)
    delay = cfg["lockstep"]["turn_ms"] * cfg["lockstep"]["command_delay_turns"] // cfg["tick_ms"]
    for c in commands:
        m.queue_command(c["tick"] + delay, c["player"], c["seq"], c["cmd"])
    for _ in range(max_ticks):
        if m.state in ("won", "lost") or (m.state == "build" and not m.pending and m.tick > delay):
            break
        m.step()
    return m
# ------------------------------------------------------------ 테스트
def test_economy_single_entry():
    """모든 증감이 Ledger.add를 지나고, 로그 합 = 잔액, 잔액 부족 소비·비정수는 거부."""
    l = Ledger(CONFIG["economy"]["start_gold"])
    assert l.add(50, "kill") and l.add(-200, "build") and not l.add(-10000, "build")
    assert l.gold == 500 and 650 + sum(a for _, a in l.log) == l.gold
    assert not l.add(1.5, "bug") and l.gold == 500

def test_economy_wave_bonus():
    """BTD6 라운드 보너스 100 + r: r10 = 110, 10라운드 합 1,055."""
    assert wave_bonus(CONFIG, 10) == 110 and sum(wave_bonus(CONFIG, r) for r in range(1, 11)) == 1055

def test_loss_reward_formula():
    """TDS 패배 보상: 완주면 base, 절반 도달(p=1.3)이면 정확히 base/2, 멀리 갈수록 커진다."""
    p = CONFIG["economy"]["loss_reward_p"]
    assert loss_reward(300, 20, 20, p) == 300.0 and abs(loss_reward(300, 10, 20, p) - 150.0) < 1e-9
    assert loss_reward(300, 5, 20, p) < loss_reward(300, 15, 20, p) < 300

def test_kr_stars():
    """KR 별 구간 경계: 20/18 → 3, 17/6 → 2, 5/1 → 1, 0 → 0."""
    assert [kr_stars(x) for x in (20, 18, 17, 6, 5, 1, 0)] == [3, 3, 2, 2, 1, 1, 0]

def test_cost_curve_exponential():
    """정수 지수 곡선: r=2.0이면 단계마다 정확히 2배, 등비 합 공식과 루프 합 일치."""
    base, r = 200, CONFIG["cost_curve"]["ratio_pct"]
    assert [exp_cost(base, r, n) for n in range(4)] == [200, 400, 800, 1600]
    closed = base * (r / 100) ** 2 * ((r / 100) ** 3 - 1) / (r / 100 - 1)
    assert bulk_cost(base, r, 2, 3) == int(closed)

def test_cost_ladder_total_ratio():
    """출처 있는 세 사다리 모두 3단계 누적 ÷ 기본 ≈ 4~8배 (td_progression §4)."""
    for name, ladder in CONFIG["cost_ladders"].items():
        ratio = sum(ladder) / ladder[0]  # 기본 + 업그레이드 전부
        assert 4.0 <= ratio <= 8.0, (name, ratio)

def test_wave_table_spawn():
    """웨이브 테이블 → 스폰 큐: 개수·간격·그룹 동시 시작이 표대로, HP는 웨이브마다 +10%(정수 내림)."""
    q = build_spawn_queue(CONFIG, 2, start_tick=0)
    assert len(q) == 10 and q[0][0] == 0
    assert [t for t, _, _, k, _ in q if k == "grunt"] == [i * 8 for i in range(8)]
    assert [t for t, _, _, k, _ in q if k == "brute"] == [0, 20]
    assert build_spawn_queue(CONFIG, 0, 0)[0][4] == 10 and build_spawn_queue(CONFIG, 4, 0)[0][4] == 40 * 140 // 100  # HP +10%/웨이브

def _enemies_for_targeting():
    g, b = CONFIG["enemies"]["grunt"], CONFIG["enemies"]["brute"]
    es = [Enemy(1, "grunt", g, 10), Enemy(2, "brute", b, 40), Enemy(3, "grunt", g, 10)]
    es[0].progress, es[1].progress, es[2].progress, es[2].hp = 5000, 3000, 1000, 4
    return es

def test_targeting_first_last():
    """First = 진행도 최대, Last = 진행도 최소."""
    path, es, t = Path(CONFIG["path"]), _enemies_for_targeting(), Tower(9, "dart", CONFIG["towers"]["dart"], 3000, 1200)
    assert pick_target(t, es, path, "first").id == 1 and pick_target(t, es, path, "last").id == 3

def test_targeting_strongest_closest():
    """Strongest = 현재 HP 최대, Closest = 타워와 거리 최소, 사거리 밖은 제외."""
    path, es, t = Path(CONFIG["path"]), _enemies_for_targeting(), Tower(9, "dart", CONFIG["towers"]["dart"], 1000, 1200)
    assert pick_target(t, es, path, "strongest").id == 2 and pick_target(t, es, path, "closest").id == 3
    assert pick_target(Tower(8, "dart", CONFIG["towers"]["dart"], 6000, 20000), es, path, "first") is None

def test_waypoint_path_progress():
    """경로 길이 = 구간 합, 좌표 보간, 도착 틱 = 길이 ÷ 속도 (16000 ÷ 100/틱 = 160틱)."""
    path, e, ticks = Path(CONFIG["path"]), Enemy(1, "grunt", CONFIG["enemies"]["grunt"], 10), 0
    assert path.total == 16000 and path.position_at(7000) == (6000, 1000) and path.position_at(99999) == (0, 4000)
    while e.progress < path.total:
        e.progress += e.speed * CONFIG["tick_ms"] // 1000
        ticks += 1
    assert ticks == 160

def test_leak_lives_and_lost():
    """타워 없이 1웨이브: 적 6기 전부 누출 → 목숨 20 − 6, 처치 0. 목숨이 0이면 lost."""
    m = Match(CONFIG, seed=1)
    m.start_wave()
    assert m.run_until_build() == "build" and m.lives == 14 and m.stats["leaks"] == 6 and m.stats["kills"] == 0
    m.lives = 1
    m.start_wave()
    assert m.run_until_build() == "lost"

def test_build_rejects_invalid():
    """슬롯 밖·중복 슬롯·잔액 부족 건설은 거부되고 gold가 변하지 않는다 (650 − 200×3 = 50)."""
    m, s = Match(CONFIG, seed=1), CONFIG["build_slots"]
    assert m.apply({"op": "build", "kind": "dart", "x": s[0][0], "y": s[0][1]})
    assert not m.apply({"op": "build", "kind": "dart", "x": s[0][0], "y": s[0][1]})
    assert not m.apply({"op": "build", "kind": "dart", "x": 1, "y": 1})
    assert m.apply({"op": "build", "kind": "dart", "x": s[1][0], "y": s[1][1]}) and m.apply({"op": "build", "kind": "dart", "x": s[2][0], "y": s[2][1]})
    assert not m.apply({"op": "build", "kind": "dart", "x": s[3][0], "y": s[3][1]}) and m.ledger.gold == 50

def test_slg_timer_accelerate():
    """CoC TH17 15일 타이머: 1일 가속 → 14일, 도움은 상한(30회)까지만, 음수 없음."""
    s = CONFIG["slg"]
    t = BuildTimer(s["th17_build_s"], s["help_reduce_s"], s["max_helps"])
    t.accelerate(86400)
    assert t.remaining == 14 * 86400
    assert t.help(50) == 30 and t.remaining == 14 * 86400 - 30 * 60 and t.help(1) == 0
    t.tick(10 ** 9)
    assert t.done() and t.remaining == 0

def test_shared_pool_draw():
    """공유 풀: 확률 = 남은 장수 ÷ 티어 합, 남이 가져가면 내 확률이 줄고, 몬테카를로가 공식과 맞는다."""
    pool = SharedPool(CONFIG["autobattler"])
    assert pool.total_at(1) == 30 * 13 and abs(pool.draw_prob(1, 0) - 30 / 390) < 1e-12
    pool.remaining[(1, 0)] -= 27  # 다른 플레이어들이 유닛 0을 27장 보유
    assert abs(pool.draw_prob(1, 0) - 3 / 363) < 1e-12
    rng, hits, n = random.Random(42), 0, 20000
    for _ in range(n):
        snapshot = dict(pool.remaining)
        hits += pool.draw(rng, 1) == 0
        pool.remaining = snapshot
    assert abs(hits / n - 3 / 363) < 0.01

def test_shared_pool_exhaust():
    """5코 9장 × 8종 = 72장을 다 뽑으면 None, 판매(release)하면 다시 나온다."""
    pool, rng = SharedPool(CONFIG["autobattler"]), random.Random(7)
    drawn = [pool.draw(rng, 5) for _ in range(72)]
    assert None not in drawn and all(drawn.count(u) == 9 for u in range(8)) and pool.draw(rng, 5) is None
    pool.release(5, 3)
    assert pool.draw(rng, 5) == 3

def test_interest_cap():
    """이자: 9 → 0, 10 → 1, 49 → 4, 50 → 5, 100 → 5."""
    assert [interest(g) for g in (9, 10, 49, 50, 100)] == [0, 1, 4, 5, 5]

def _demo_commands():
    cmds = [{"tick": 0, "player": 1, "seq": i, "cmd": {"op": "build", "kind": "dart", "x": s[0], "y": s[1]}} for i, s in enumerate(CONFIG["build_slots"][:3])]
    return cmds + [{"tick": 0, "player": 1, "seq": 9, "cmd": {"op": "start_wave"}}]

def test_lockstep_checksum():
    """같은 시드·같은 명령 → 틱별 체크섬 동일; 명령 하나만 달라도 갈라진다; 지연 2턴 = 4틱 뒤 실행."""
    a, b = run_lockstep(CONFIG, 3, _demo_commands()), run_lockstep(CONFIG, 3, _demo_commands())
    assert a.checksums == b.checksums and len(a.checksums) > 10 and a.towers[0].id == 1
    other = _demo_commands()
    other[0]["cmd"]["x"], other[0]["cmd"]["y"] = CONFIG["build_slots"][3]
    c = run_lockstep(CONFIG, 3, other)
    assert c.checksums[:4] == a.checksums[:4] and c.checksums[4] != a.checksums[4]

def test_full_match_deterministic():
    """§4 순서로 5웨이브 전부 돌려 두 번 실행이 같은 결과·같은 최종 체크섬."""
    results = []
    for _ in range(2):
        m = Match(CONFIG, seed=11)
        for s in CONFIG["build_slots"][:3]:
            m.apply({"op": "build", "kind": "dart", "x": s[0], "y": s[1]})
        while m.state == "build":
            for t in m.towers:
                while m.apply({"op": "upgrade", "tower": t.id}):
                    pass
            m.start_wave()
            m.run_until_build()
        results.append((m.state, m.ledger.gold, m.lives, m.stats["kills"], m.checksum()))
    assert results[0] == results[1] and results[0][3] > 0

TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
def run_tests():
    """테스트 전부 실행, 마지막 줄 passed k/n, 반환값 = 실패 수(종료 코드)."""
    failed = 0
    for t in TESTS:
        try:
            t()
            print("ok   ", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL ", t.__name__, "->", repr(e))
    print("passed %d/%d" % (len(TESTS) - failed, len(TESTS)))
    return failed

def run_demo(seed=11):
    """시드 고정 한 판: 웨이브 사이에 (업그레이드 → 남는 돈으로 건설) 단순 정책."""
    m = Match(CONFIG, seed)
    print("demo seed=%d start_gold=%d lives=%d waves=%d" % (seed, m.ledger.gold, m.lives, len(CONFIG["waves"])))
    while m.state == "build":
        for t in m.towers:
            while m.apply({"op": "upgrade", "tower": t.id}):
                pass
        for s in CONFIG["build_slots"]:
            m.apply({"op": "build", "kind": "dart", "x": s[0], "y": s[1]})
        before = m.ledger.gold
        m.start_wave()
        m.run_until_build()
        print("wave %d: gold %d -> %d, lives %d, kills %d, leaks %d, tiers %s, crc %08x" % (
            m.wave, before, m.ledger.gold, m.lives, m.stats["kills"], m.stats["leaks"], [t.tier for t in m.towers], m.checksum()))
    print("result:", m.state, "| tick", m.tick, "| ledger entries", len(m.ledger.log), "| stars", kr_stars(m.lives),
          "| loss reward if stopped at wave 2/5 (base 300):", round(loss_reward(300, 2, 5, 1.3), 1))

if __name__ == "__main__":
    sys.exit(run_tests() if "--test" in sys.argv else run_demo())
