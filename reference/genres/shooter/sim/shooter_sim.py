#!/usr/bin/env python3
"""슈팅 장르 기본 베이스 로직 시뮬레이션 (표준 라이브러리만, 결정론).

실행:
  python3 -I shooter_sim.py --test   # 규칙 검증, 마지막 줄 `passed k/n`, 종료 코드 = 실패 수
  python3 -I shooter_sim.py --demo   # 시드 고정 데스매치 한 판 요약
수치 출처: ../logic.md §2 와 동일. (출처) = README §4, (예시값) = 출처 없음.
"""
import math
import random
import sys

CONFIG = {
    "version": 1,
    "tick_hz": 128,                 # (출처) VALORANT 128틱 [26]
    "max_rewind_ms": 200,           # (예시값) 랙 보상 최대 되감기
    "player_hp": 100,               # (예시값) Vandal 몸 40×3발 = 사망과 맞춤
    "weapons": {
        "vandal": {                 # (출처) 헤드 160/몸 40/다리 34, 거리 감쇠 없음 [19]
            "kind": "hitscan", "damage": {"head": 160, "body": 40, "leg": 34},
            "fire_rate_rpm": 600, "falloff": None, "price": 2900},   # rpm·가격 (예시값)
        "smg": {                    # (예시값) 전부
            "kind": "hitscan", "damage": {"head": 50, "body": 25, "leg": 20},
            "fire_rate_rpm": 800,
            "falloff": {"start_m": 15, "end_m": 40, "min_mult": 0.6}, "price": 1000},
        "rocket": {                 # (예시값) 투사체 예시
            "kind": "projectile", "damage": {"head": 100, "body": 100, "leg": 100},
            "fire_rate_rpm": 60, "speed_mps": 40, "max_range_m": 120, "falloff": None,
            "price": 2000},
    },
    "spawn": {
        "protection_ms": 2000,      # (예시값)
        "enemy_dist_cap_m": 40,     # (예시값) 이보다 멀면 점수 더 안 오름
        "recent_use_penalty": 30,   # (예시값)
        "ally_weight": 0.2,         # (예시값)
    },
    "deathmatch": {
        "max_players": 16,          # (출처) Arsenal 서버 16명 [16]
        "kill_target": 32,          # (출처) Arsenal 32킬 선취 (README §2, 2차)
        "time_limit_s": 600,        # (예시값)
        "respawn_delay_s": 3,       # (예시값)
    },
    "tactical": {
        "rounds_regulation": 24,    # (출처) CS2 MR12 [32]
        "rounds_to_win": 13,        # (출처) 13선취 [32]
        "overtime_block": 6,        # (출처) 동점 시 6라운드 OT [32]
        "overtime_to_win": 4,       # (예시값) OT 블록 내 4승
    },
    "economy": {                    # (예시값) CS식 라운드 경제
        "start_money": 800, "kill_reward": 300, "win_reward": 3250,
        "loss_rewards": [1400, 1900, 2400, 2900, 3400], "max_money": 16000,
    },
    "battle_royale": {
        "players": 50,              # (출처) Free Fire 50명 (README §2)
        "start_radius_m": 1000,     # (예시값)
        "circle_phases": [          # (예시값) [대기 s, 축소 s, 축소 후 반지름 배율, 틱당 데미지]
            [60, 60, 0.6, 1], [45, 45, 0.5, 2], [30, 30, 0.4, 4], [20, 20, 0.0, 8]],
    },
}

# ───────────────────────── 3.1 무기·데미지·TTK ─────────────────────────
def damage_at(weapon, zone, dist_m):
    """부위·거리를 반영한 1발 데미지. falloff 구간에서 선형 감쇠."""
    base, f = weapon["damage"][zone], weapon["falloff"]
    if not f or dist_m <= f["start_m"]:
        return base
    t = min(1.0, (dist_m - f["start_m"]) / (f["end_m"] - f["start_m"]))
    return base * (1 - t * (1 - f["min_mult"]))

def shots_to_kill(weapon, zone, hp, dist_m=0.0):
    """처치에 필요한 발수 = ceil(hp / 1발 데미지)."""
    return math.ceil(hp / damage_at(weapon, zone, dist_m))

def ttk_ms(weapon, zone, hp, dist_m=0.0):
    """TTK = (발수 − 1) × 발사 간격. 첫 발은 즉시 맞는다고 본다."""
    return (shots_to_kill(weapon, zone, hp, dist_m) - 1) * 60000.0 / weapon["fire_rate_rpm"]

# ───────────────────────── 3.2 hitscan vs 투사체 ─────────────────────────
def _ray_circle(origin, direction, center, radius):
    """2D 레이-원 교차. 맞으면 거리 t(≥0), 아니면 None."""
    ox, oy = origin[0] - center[0], origin[1] - center[1]
    b, c = 2 * (ox * direction[0] + oy * direction[1]), ox * ox + oy * oy - radius * radius
    disc = b * b - 4 * c
    t = (-b - math.sqrt(disc)) / 2 if disc >= 0 else -1
    return t if t >= 0 else None

def hitscan(origin, direction, targets):
    """레이에 처음 맞는 표적 (id, 거리) 반환. targets = [(id, (x,y), radius)]."""
    n = math.hypot(*direction) or 1.0
    d = (direction[0] / n, direction[1] / n)
    best = None
    for tid, pos, r in targets:
        t = _ray_circle(origin, d, pos, r)
        if t is not None and (best is None or t < best[1]):
            best = (tid, t)
    return best

def lead_point(shooter, target_pos, target_vel, speed):
    """등속 이동 표적을 탄속 speed 로 맞추는 조준점. 해 없으면 None."""
    rx, ry = target_pos[0] - shooter[0], target_pos[1] - shooter[1]
    vx, vy = target_vel
    a, b, c = vx * vx + vy * vy - speed * speed, 2 * (rx * vx + ry * vy), rx * rx + ry * ry
    if abs(a) < 1e-9:                      # 탄속 == 표적 속도: 1차식
        ts = [-c / b] if b else []
    else:
        disc = b * b - 4 * a * c
        s = math.sqrt(disc) if disc >= 0 else None
        ts = [] if s is None else [(-b - s) / (2 * a), (-b + s) / (2 * a)]
    ts = [t for t in ts if t > 0]
    return (target_pos[0] + vx * min(ts), target_pos[1] + vy * min(ts)) if ts else None

def fly_projectile(origin, aim, speed, max_range, target_pos, target_vel, radius, dt):
    """투사체를 dt 단위로 전진시키며 이동 표적과의 충돌을 검사. 맞으면 비행 시간(s)."""
    n = math.hypot(aim[0] - origin[0], aim[1] - origin[1]) or 1.0
    vx, vy = (aim[0] - origin[0]) / n * speed, (aim[1] - origin[1]) / n * speed
    px, py, tx, ty, t = origin[0], origin[1], target_pos[0], target_pos[1], 0.0
    while t * speed <= max_range:
        if math.hypot(px - tx, py - ty) <= radius:
            return t
        px, py, tx, ty = px + vx * dt, py + vy * dt, tx + target_vel[0] * dt, ty + target_vel[1] * dt
        t += dt
    return None

# ───────────────────────── 3.3 랙 보상 (되감기 버퍼) ─────────────────────────
class PositionHistory:
    """플레이어별 틱 → 위치 링버퍼. 서버가 과거 위치로 되감을 때 쓴다."""
    def __init__(self, max_ticks):
        self.max_ticks = max_ticks
        self.buf = {}  # tick -> {pid: (x, y)}
    def record(self, tick, positions):
        self.buf[tick] = dict(positions)
        for old in [t for t in self.buf if t < tick - self.max_ticks]:
            del self.buf[old]
    def at(self, tick):
        """정확한 틱이 없으면 가장 가까운 과거 틱을 쓴다 (보간 생략, 단순화)."""
        if tick in self.buf:
            return self.buf[tick]
        past = [t for t in self.buf if t <= tick]
        return self.buf[max(past)] if past else None

def rewind_hit_check(history, server_tick, client_tick, shooter_id, origin, direction, radius, cfg=CONFIG):
    """클라이언트가 본 시각(client_tick)으로 되감아 판정. 결과 ('hit', id) | ('miss',) | ('reject', 이유)."""
    if client_tick > server_tick:
        return ("reject", "future_tick")
    if (server_tick - client_tick) * 1000.0 / cfg["tick_hz"] > cfg["max_rewind_ms"]:
        return ("reject", "rewind_too_far")
    snap = history.at(client_tick)
    if snap is None:
        return ("reject", "no_snapshot")
    targets = [(pid, pos, radius) for pid, pos in snap.items() if pid != shooter_id]
    hit = hitscan(origin, direction, targets)
    return ("hit", hit[0]) if hit else ("miss",)

# ───────────────────────── 3.4 클라이언트 예측·리컨실리에이션 ─────────────────────────
def apply_input(pos, inp, speed, dt):
    """이동 입력 (dx, dy) ∈ [-1,1] 을 위치에 적용. 서버·클라이언트가 같은 함수를 쓴다."""
    return (pos[0] + inp[0] * speed * dt, pos[1] + inp[1] * speed * dt)

def reconcile(server_pos, last_acked_seq, pending, speed, dt):
    """서버 스냅샷 위치에서 아직 확인 안 된 입력(seq > acked)을 다시 재생한 예측 위치."""
    pos = server_pos
    for seq, inp in pending:
        pos = apply_input(pos, inp, speed, dt) if seq > last_acked_seq else pos
    return pos

# ───────────────────────── 3.5 스폰 선택·스폰 보호 ─────────────────────────
def score_spawn(spawn_pos, enemies, allies, recently_used, cfg=CONFIG["spawn"]):
    """스폰 점수 = min(적 거리, cap) + 아군 근접 보너스 − 최근 사용 페널티. 높을수록 좋다."""
    d_enemy = min((math.hypot(spawn_pos[0] - e[0], spawn_pos[1] - e[1]) for e in enemies),
                  default=cfg["enemy_dist_cap_m"])
    score = min(d_enemy, cfg["enemy_dist_cap_m"])
    if allies:
        d_ally = min(math.hypot(spawn_pos[0] - a[0], spawn_pos[1] - a[1]) for a in allies)
        score += cfg["ally_weight"] * max(0.0, cfg["enemy_dist_cap_m"] - d_ally)
    if recently_used:
        score -= cfg["recent_use_penalty"]
    return score

def pick_spawn(spawns, enemies, allies, recent, rng):
    """최고 점수 스폰. 동점이면 시드 RNG로 하나 고른다."""
    scored = [(score_spawn(p, enemies, allies, p in recent), p) for p in spawns]
    return rng.choice([p for sc, p in scored if sc == max(x for x, _ in scored)])

def is_spawn_protected(spawned_ms, now_ms, has_fired, cfg=CONFIG["spawn"]):
    """스폰 후 protection_ms 동안 무적. 사격하면 즉시 해제."""
    return (not has_fired) and (now_ms - spawned_ms) < cfg["protection_ms"]

# ───────────────────────── 3.6 라운드·매치 상태 ─────────────────────────
class DeathmatchState:
    """킬 목표 또는 제한 시간으로 끝나는 아레나 데스매치."""
    def __init__(self, cfg=CONFIG["deathmatch"]):
        self.cfg, self.kills, self.elapsed_s, self.state = cfg, {}, 0.0, "Playing"
    def add_kill(self, pid):
        self.kills[pid] = self.kills.get(pid, 0) + 1
        self._check()
    def tick(self, dt):
        self.elapsed_s += dt
        self._check()
    def _check(self):
        if self.state != "Playing":
            return
        if any(k >= self.cfg["kill_target"] for k in self.kills.values()):
            self.state = "MatchEnd"
        elif self.elapsed_s >= self.cfg["time_limit_s"]:
            self.state = "MatchEnd"
    def winner(self):
        return max(self.kills, key=self.kills.get) if self.kills else None

class TacticalMatch:
    """MR12: 13선취, 12-12 면 6라운드 OT 블록, 블록 내 overtime_to_win 승이면 끝."""
    def __init__(self, cfg=CONFIG["tactical"]):
        self.cfg, self.score, self.block = cfg, {"A": 0, "B": 0}, {"A": 0, "B": 0}
        self.rounds_played, self.winner = 0, None
    def round_won(self, team):
        if self.winner:
            return
        self.score[team] += 1
        self.rounds_played += 1
        c = self.cfg
        if self.rounds_played <= c["rounds_regulation"]:
            if self.score[team] >= c["rounds_to_win"]:
                self.winner = team
            return
        self.block[team] += 1                       # 연장
        if self.block[team] >= c["overtime_to_win"]:
            self.winner = team
        elif sum(self.block.values()) >= c["overtime_block"]:
            self.block = {"A": 0, "B": 0}           # 동점 → 다음 OT 블록

# ───────────────────────── 3.7 무기 경제 (구매 라운드) ─────────────────────────
class Wallet:
    """플레이어 돈. 모든 증감은 add() 한 곳을 지나며 상한을 지킨다."""
    def __init__(self, cfg=CONFIG["economy"]):
        self.cfg, self.money, self.log, self.loss_streak = cfg, cfg["start_money"], [], 0
    def add(self, amount, reason):
        self.money = max(0, min(self.cfg["max_money"], self.money + amount))
        self.log.append((reason, amount))
    def try_buy(self, weapon_id, weapons=CONFIG["weapons"]):
        price = weapons[weapon_id]["price"]
        if price > self.money:
            return False
        self.add(-price, "buy:" + weapon_id)
        return True
    def round_end(self, won):
        if won:
            self.loss_streak = 0
            self.add(self.cfg["win_reward"], "round_win")
        else:
            idx = min(self.loss_streak, len(self.cfg["loss_rewards"]) - 1)
            self.add(self.cfg["loss_rewards"][idx], "round_loss")
            self.loss_streak += 1

# ───────────────────────── 3.8 배틀로얄 서클 축소 ─────────────────────────
def circle_radius_at(t_s, cfg=CONFIG["battle_royale"]):
    """경과 시간 → (반지름, 현재 페이즈 틱당 데미지). 대기 구간은 유지, 축소 구간은 선형."""
    r, dmg = cfg["start_radius_m"], 0
    for wait, shrink, mult, phase_dmg in cfg["circle_phases"]:
        dmg = phase_dmg
        if t_s < wait:
            return r, dmg
        t_s -= wait
        target = r * mult
        if t_s < shrink:
            return r + (target - r) * (t_s / shrink), dmg
        t_s -= shrink
        r = target
    return r, dmg

def outside_circle_damage(pos, center, t_s, cfg=CONFIG["battle_royale"]):
    """서클 밖이면 현재 페이즈의 틱당 데미지, 안이면 0."""
    r, dmg = circle_radius_at(t_s, cfg)
    return dmg if math.hypot(pos[0] - center[0], pos[1] - center[1]) > r else 0

# ───────────────────────── 테스트 ─────────────────────────
def test_ttk_vandal_head_oneshot():
    w = CONFIG["weapons"]["vandal"]
    assert shots_to_kill(w, "head", CONFIG["player_hp"]) == 1 and ttk_ms(w, "head", 100) == 0

def test_ttk_vandal_body_three_shots():
    w = CONFIG["weapons"]["vandal"]
    assert shots_to_kill(w, "body", 100) == 3 and abs(ttk_ms(w, "body", 100) - 200.0) < 1e-9
    assert damage_at(w, "body", 500) == 40                     # 감쇠 없음

def test_falloff_reduces_damage():
    w = CONFIG["weapons"]["smg"]
    assert damage_at(w, "body", 10) == 25 and damage_at(w, "body", 50) == 15
    assert 15 < damage_at(w, "body", 27.5) < 25
    assert ttk_ms(w, "body", 100, 50) > ttk_ms(w, "body", 100, 0)

def test_hitscan_nearest_target():
    targets = [("far", (30, 0), 1.0), ("near", (10, 0), 1.0), ("side", (10, 5), 1.0)]
    hit = hitscan((0, 0), (1, 0), targets)
    assert hit[0] == "near" and abs(hit[1] - 9.0) < 1e-9
    assert hitscan((0, 0), (0, 1), targets) is None

def test_projectile_lead_hits_moving_target():
    w = CONFIG["weapons"]["rocket"]
    tpos, tvel = (40, 0), (0, 6)
    aim = lead_point((0, 0), tpos, tvel, w["speed_mps"])
    assert aim is not None and aim[1] > 0
    assert fly_projectile((0, 0), aim, w["speed_mps"], w["max_range_m"], tpos, tvel, 1.0, 1 / 128) is not None

def test_projectile_no_lead_misses():
    w = CONFIG["weapons"]["rocket"]
    assert fly_projectile((0, 0), (40, 0), w["speed_mps"], w["max_range_m"], (40, 0), (0, 6), 1.0, 1 / 128) is None

def _history_with_runner():
    h = PositionHistory(max_ticks=64)
    for t in range(0, 101):                                   # 표적이 x=10 에서 +y 로 달림
        h.record(t, {"runner": (10, t * 0.1), "shooter": (0, 0)})
    return h

def test_rewind_accept_within_window():
    h = _history_with_runner()
    server_tick, client_tick = 100, 90                        # 10틱 = 78ms 되감기 < 200ms
    assert rewind_hit_check(h, server_tick, client_tick, "shooter", (0, 0), (10, 9.0), 0.5) == ("hit", "runner")
    assert rewind_hit_check(h, server_tick, server_tick, "shooter", (0, 0), (10, 9.0), 0.5) == ("miss",)

def test_rewind_reject_beyond_window():
    h = _history_with_runner()
    assert rewind_hit_check(h, 100, 70, "shooter", (0, 0), (10, 7.0), 0.5) == ("reject", "rewind_too_far")
    assert rewind_hit_check(h, 100, 101, "shooter", (0, 0), (10, 7.0), 0.5) == ("reject", "future_tick")

def test_reconcile_replays_unacked_inputs():
    speed, dt = 5.0, 1 / 60
    inputs = [(1, (1, 0)), (2, (1, 0)), (3, (0, 1)), (4, (0, 1))]
    server_pos = (0, 0)
    for seq, inp in inputs[:2]:                               # 서버는 seq 2까지 처리
        server_pos = apply_input(server_pos, inp, speed, dt)
    predicted = reconcile(server_pos, 2, inputs, speed, dt)
    full = (0, 0)
    for _, inp in inputs:
        full = apply_input(full, inp, speed, dt)
    assert all(abs(a - b) < 1e-9 for a, b in zip(predicted, full))

def test_spawn_prefers_far_from_enemy():
    rng = random.Random(1)
    spawns = [(0, 0), (30, 0), (100, 0)]
    assert pick_spawn(spawns, enemies=[(5, 0)], allies=[], recent=[], rng=rng) == (100, 0)
    assert pick_spawn(spawns, enemies=[(5, 0)], allies=[], recent=[(100, 0)], rng=rng) == (30, 0)
    # 적 거리 cap(40m) 때문에 (0,0)과 (100,0)이 동점 → 아군 근접 보너스가 (0,0)을 고른다
    assert pick_spawn(spawns, enemies=[(60, 0)], allies=[(0, 0)], recent=[], rng=rng) == (0, 0)

def test_spawn_protection_expires_or_breaks_on_fire():
    assert is_spawn_protected(0, 1500, False) and not is_spawn_protected(0, 2000, False)
    assert not is_spawn_protected(0, 500, True)

def test_deathmatch_kill_target_win():
    m = DeathmatchState()
    for _ in range(CONFIG["deathmatch"]["kill_target"] - 1):
        m.add_kill("p1")
    assert m.state == "Playing"
    m.add_kill("p1")
    assert m.state == "MatchEnd" and m.winner() == "p1"

def test_deathmatch_timer_win():
    m = DeathmatchState()
    m.add_kill("p2"); m.add_kill("p2"); m.add_kill("p1")
    m.tick(CONFIG["deathmatch"]["time_limit_s"] - 1)
    assert m.state == "Playing"
    m.tick(1)
    assert m.state == "MatchEnd" and m.winner() == "p2"

def test_mr12_first_to_13_and_overtime():
    m = TacticalMatch()
    for _ in range(12):
        m.round_won("A"); m.round_won("B")
    assert m.winner is None and m.rounds_played == 24
    for _ in range(3):                                        # OT 3-3 → 다음 블록
        m.round_won("A"); m.round_won("B")
    assert m.winner is None and m.block == {"A": 0, "B": 0}
    for _ in range(4):
        m.round_won("B")
    assert m.winner == "B"
    m2 = TacticalMatch()
    [m2.round_won("A") for _ in range(13)]
    assert m2.winner == "A" and m2.rounds_played == 13

def test_economy_rejects_unaffordable_buy():
    w = Wallet()
    assert not w.try_buy("vandal") and w.money == 800              # 2900 > 800 → 거부, 잔액 불변
    w.add(300, "kill")
    assert w.try_buy("smg") and w.money == 100
    w2 = Wallet()
    w2.round_end(False); w2.round_end(False)
    assert w2.money == 800 + 1400 + 1900 and w2.loss_streak == 2
    w2.round_end(True)
    assert w2.loss_streak == 0 and w2.money == 800 + 1400 + 1900 + 3250
    w3 = Wallet(); w3.add(10 ** 9, "cheat_test")
    assert w3.money == CONFIG["economy"]["max_money"]

def test_circle_schedule_monotonic():
    prev = CONFIG["battle_royale"]["start_radius_m"]
    total = sum(p[0] + p[1] for p in CONFIG["battle_royale"]["circle_phases"])
    for t in range(0, total + 10):
        r, _ = circle_radius_at(t)
        assert r <= prev + 1e-9
        prev = r
    assert circle_radius_at(0)[0] == 1000 and abs(circle_radius_at(120)[0] - 600) < 1e-9
    assert circle_radius_at(total)[0] == 0

def test_circle_damage_outside():
    assert outside_circle_damage((0, 0), (0, 0), 0) == 0
    assert outside_circle_damage((999, 0), (0, 0), 0) == 0
    assert outside_circle_damage((999, 0), (0, 0), 119) == 1        # 1페이즈 축소 중, 반지름 < 999
    assert outside_circle_damage((999, 0), (0, 0), 120) == 2        # 2페이즈 진입: 데미지 2
    assert outside_circle_damage((599, 0), (0, 0), 120) == 0        # 반지름 600 안

TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

def run_tests():
    """모든 test_* 실행, `passed k/n` 출력, 실패 수 반환."""
    failed = 0
    for fn in TESTS:
        try:
            fn()
            print("ok   ", fn.__name__)
        except Exception as e:
            failed += 1
            print("FAIL ", fn.__name__, repr(e))
    print(f"passed {len(TESTS) - failed}/{len(TESTS)}")
    return failed

def demo(seed=7):
    """시드 고정 8인 데스매치: 매 초 무작위 교전, 킬 목표 또는 시간으로 종료."""
    rng, cfg, w = random.Random(seed), CONFIG["deathmatch"], CONFIG["weapons"]["vandal"]
    players = [f"p{i}" for i in range(8)]
    m, hp = DeathmatchState(), {p: CONFIG["player_hp"] for p in players}
    spawns = [(x, y) for x in (0, 50, 100) for y in (0, 50)]
    pos = {p: pick_spawn(spawns, [], [], [], rng) for p in players}
    print(f"demo seed={seed} players={len(players)} kill_target={cfg['kill_target']} tick={CONFIG['tick_hz']}Hz")
    print(f"vandal TTK: head {ttk_ms(w,'head',100):.0f}ms / body {ttk_ms(w,'body',100):.0f}ms")
    while m.state == "Playing":
        a, b = rng.sample(players, 2)
        hp[b] -= damage_at(w, rng.choices(["head", "body", "leg"], [0.2, 0.6, 0.2])[0], math.dist(pos[a], pos[b]))
        if hp[b] <= 0:
            m.add_kill(a)
            hp[b], pos[b] = CONFIG["player_hp"], 0
            pos[b] = pick_spawn(spawns, [pos[q] for q in players if q != b], [], [pos[b]], rng)
            if m.kills[a] % 8 == 0:
                print(f"  t={m.elapsed_s:4.0f}s  {a} reaches {m.kills[a]} kills")
        m.tick(1)
    print(f"end: {m.state} at {m.elapsed_s:.0f}s, winner={m.winner()} kills={sorted(m.kills.items())}")

if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.exit(run_tests())
    demo() if "--demo" in sys.argv else print(__doc__)
