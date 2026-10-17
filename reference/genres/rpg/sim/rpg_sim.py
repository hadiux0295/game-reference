#!/usr/bin/env python3
"""RPG · 방치형 기본 베이스 로직 시뮬레이션 (표준 라이브러리만, 결정론적).

실행:
  python3 -I rpg_sim.py --test   # 규칙 검사, 마지막 줄 'passed k/n', 종료 코드 = 실패 수
  python3 -I rpg_sim.py --demo   # 시드 고정으로 방치형 환생 3회 + 가차 90뽑 + 서바이버 1런 요약
수치 출처: ../README.md §4 (원신 0.6%/90/10/180, 레진 8분당 1·상한 200, VS 30분,
AdCap 레모네이드 r=1.07·기본비용 4·기본산출 1.67·25/50개 x2). 그 외는 '예시값'.
"""
import math
import random
import sys

# ---------------------------------------------------------------- CONFIG
# logic.md §2 의 JSON 과 같은 값. 코드에는 숫자를 직접 쓰지 않는다.
CONFIG = {
    "version": 1,
    "growth": {"base_cost": 4.0, "rate": 1.07, "base_output": 1.67,
               "milestones": [25, 50], "milestone_mult": 2.0},
    "hero": {"base_atk": 10, "atk_per_level": 2, "attack_interval_s": 1.0,
             "crit_chance": 0.05, "crit_mult": 2.0},
    "damage": {"def_k": 100, "rand_min": 0.95, "rand_max": 1.05, "min_damage": 1},
    "stage": {"enemy_hp_base": 20, "enemy_hp_rate": 1.12, "enemy_def_per_stage": 3,
              "enemy_count": 5, "reward_base": 3, "clear_timeout_s": 60},
    "prestige": {"divisor": 100.0, "per_point": 0.1},
    "offline": {"max_hours": 8.0, "efficiency": 1.0},
    "gacha": {"rates": {"5": 0.006, "4": 0.051, "3": 0.943},
              "hard_pity_5": 90, "hard_pity_4": 10, "featured_rate": 0.5},
    "stamina": {"cap": 200, "sec_per_point": 480},
    "survivor": {"run_seconds": 1800, "spawn_per_min_base": 10, "spawn_per_min_step": 6,
                 "spawn_per_min_cap": 120, "enemy_hp_base": 5, "enemy_hp_per_min": 1,
                 "enemy_dps": 0.003, "player_hp": 100, "player_dps": 15,
                 "dps_per_weapon_lv": 0.25, "dps_per_spinach_lv": 0.1, "armor_cut": 0.1,
                 "xp_base": 3, "xp_exp": 1.5, "choices": 3, "max_level": 8,
                 "weapons": ["whip", "wand", "garlic", "axe"],
                 "upgrade_pool": ["whip", "wand", "garlic", "axe", "spinach", "armor"]},
}


# ---------------------------------------------------------------- 3.1 성장 곡선
def upgrade_cost(n, g=None):
    """n개 보유 시 다음 1개 비용 = base × r^n (Math of Idle Games I)."""
    g = g or CONFIG["growth"]
    return g["base_cost"] * g["rate"] ** n

def bulk_cost(n, k, g=None):
    """n개 보유 상태에서 k개 일괄 구매 비용 = b·r^n·(r^k−1)/(r−1)."""
    g = g or CONFIG["growth"]
    r = g["rate"]
    return g["base_cost"] * r ** n * (r ** k - 1) / (r - 1)

def output_per_sec(n, g=None):
    """산출은 선형(기본산출 × 보유수) × 마일스톤 배율."""
    g = g or CONFIG["growth"]
    mult = g["milestone_mult"] ** sum(1 for m in g["milestones"] if n >= m)
    return g["base_output"] * n * mult

def time_to_level(n_from, n_to, income_per_sec, g=None):
    """현재 수입이 유지된다고 가정할 때 n_from → n_to 까지 걸리는 초."""
    if income_per_sec <= 0:
        return math.inf
    return bulk_cost(n_from, n_to - n_from, g) / income_per_sec


# ---------------------------------------------------------------- 3.2 데미지
def damage(atk, defense, rng, skill_mul=1.0, crit=False, d=None, h=None):
    """비율형 방어: atk × skill × k/(k+def) × crit × rand. 항상 ≥ min_damage."""
    d = d or CONFIG["damage"]
    h = h or CONFIG["hero"]
    mitig = d["def_k"] / (d["def_k"] + max(0, defense))
    raw = atk * skill_mul * mitig * (h["crit_mult"] if crit else 1.0)
    raw *= rng.uniform(d["rand_min"], d["rand_max"])
    return max(d["min_damage"], int(round(raw)))


# ---------------------------------------------------------------- 3.3 스테이지·벽·환생
def enemy_stats(stage, s=None):
    """스테이지별 적 체력(지수)·방어(선형)."""
    s = s or CONFIG["stage"]
    return int(s["enemy_hp_base"] * s["enemy_hp_rate"] ** stage), s["enemy_def_per_stage"] * stage

def stage_clear_time(hero_atk, stage, rng):
    """적 enemy_count 마리를 잡는 데 걸리는 초."""
    s, h = CONFIG["stage"], CONFIG["hero"]
    hp, df = enemy_stats(stage, s)
    total = 0.0
    for _ in range(s["enemy_count"]):
        remaining = hp
        while remaining > 0:
            remaining -= damage(hero_atk, df, rng, crit=rng.random() < h["crit_chance"])
            total += h["attack_interval_s"]
    return total

def is_wall(hero_atk, stage, rng):
    """클리어 시간이 제한을 넘으면 벽."""
    return stage_clear_time(hero_atk, stage, rng) > CONFIG["stage"]["clear_timeout_s"]

def prestige_points(lifetime_coins, p=None):
    """환생 포인트 = floor(sqrt(누적 코인 / divisor)). 예시값."""
    p = p or CONFIG["prestige"]
    return int(math.sqrt(max(0.0, lifetime_coins) / p["divisor"]))

def prestige_multiplier(total_points, p=None):
    """영구 배율 = 1 + per_point × 누적 포인트 (환생해도 리셋되지 않음)."""
    p = p or CONFIG["prestige"]
    return 1.0 + p["per_point"] * total_points

class IdleRun:
    """방치형 한 사이클: 코인 → 공격력 업그레이드 → 스테이지 → 벽."""

    def __init__(self, seed, prestige_mult=1.0):
        self.rng = random.Random(seed)
        self.mult = prestige_mult
        self.coins = self.lifetime = self.elapsed = 0.0
        self.level, self.stage = 0, 1

    def hero_atk(self):
        h = CONFIG["hero"]
        return (h["base_atk"] + h["atk_per_level"] * self.level) * self.mult

    def step_stage(self):
        """한 스테이지 시도. 벽이면 False."""
        t = stage_clear_time(self.hero_atk(), self.stage, self.rng)
        if t > CONFIG["stage"]["clear_timeout_s"]:
            return False
        self.elapsed += t
        reward = CONFIG["stage"]["reward_base"] * self.stage * self.mult
        self.coins += reward
        self.lifetime += reward
        self.stage += 1
        while self.coins >= upgrade_cost(self.level):
            self.coins -= upgrade_cost(self.level)
            self.level += 1
        return True

    def run_until_wall(self, max_stage=10_000):
        while self.stage < max_stage and self.step_stage():
            pass
        return self.stage


# ---------------------------------------------------------------- 3.4 오프라인 수익
def calc_offline(last_seen_unix, now_unix, per_sec, o=None):
    """오프라인 보상: 시간 역행·첫 실행은 0, 상한 max_hours (Economy.gd 와 같은 규칙)."""
    o = o or CONFIG["offline"]
    if last_seen_unix <= 0 or now_unix <= last_seen_unix:
        return 0
    elapsed = min(now_unix - last_seen_unix, int(o["max_hours"] * 3600))
    return int(elapsed * per_sec * o["efficiency"])


# ---------------------------------------------------------------- 3.5 가차
class Gacha:
    """확률 + 하드 천장(5★ 90 / 4★ 10) + 픽업 50/50. 천장 상태는 세이브 소유."""

    def __init__(self, seed, g=None):
        self.g = g or CONFIG["gacha"]
        self.rng = random.Random(seed)
        self.pity5 = self.pity4 = 0
        self.guaranteed = False

    def table(self):
        """공개용 확률표(%): 실제 뽑기와 같은 데이터에서 생성."""
        return {k: round(v * 100, 2) for k, v in self.g["rates"].items()}

    def pull(self):
        """반환 (등급, 픽업 여부, 천장 강제 여부)."""
        self.pity5 += 1
        self.pity4 += 1
        forced, rarity = False, "3"
        if self.pity5 >= self.g["hard_pity_5"]:
            rarity, forced = "5", True
        elif self.pity4 >= self.g["hard_pity_4"]:
            rarity, forced = "4", True
        else:
            r, acc = self.rng.random(), 0.0
            for k in ("5", "4", "3"):
                acc += self.g["rates"][k]
                if r < acc:
                    rarity = k
                    break
        featured = False
        if rarity == "5":
            self.pity5 = self.pity4 = 0
            featured = self.guaranteed or self.rng.random() < self.g["featured_rate"]
            self.guaranteed = not featured
        elif rarity == "4":
            self.pity4 = 0
        return rarity, featured, forced


# ---------------------------------------------------------------- 3.6 스태미나
def regen_stamina(current, last_unix, now_unix, s=None):
    """sec_per_point 마다 1 회복, cap 초과 금지, 시간 역행이면 그대로. 잔여초 보존."""
    s = s or CONFIG["stamina"]
    if now_unix <= last_unix or current >= s["cap"]:
        return current, last_unix
    gained, rem = divmod(now_unix - last_unix, s["sec_per_point"])
    return min(s["cap"], current + gained), now_unix - rem


# ---------------------------------------------------------------- 3.7 서바이버 런
def spawn_per_min(minute, v=None):
    """웨이브 밀도: 선형 증가 후 상한."""
    v = v or CONFIG["survivor"]
    return min(v["spawn_per_min_cap"], v["spawn_per_min_base"] + v["spawn_per_min_step"] * minute)

def xp_to_next(level, v=None):
    """다음 레벨 필요 XP = base × level^exp (다항 곡선)."""
    v = v or CONFIG["survivor"]
    return int(v["xp_base"] * level ** v["xp_exp"])

def draw_choices(levels, rng, v=None):
    """레벨업 3택: 만렙 제외 · 중복 없음 · 후보가 부족하면 있는 만큼."""
    v = v or CONFIG["survivor"]
    pool = [u for u in v["upgrade_pool"] if levels.get(u, 0) < v["max_level"]]
    return rng.sample(pool, min(v["choices"], len(pool)))

class SurvivorRun:
    """30분 런: 스폰 → 자동 공격 → XP 젬 → 레벨업 3택 → 리퍼."""

    def __init__(self, seed, v=None):
        self.v = v or CONFIG["survivor"]
        self.rng = random.Random(seed)
        self.t, self.level, self.xp = 0, 1, 0
        self.hp = self.v["player_hp"]
        self.levels, self.alive, self.kills, self.spawned, self.ended = {}, 0, 0, 0, None

    def tick(self):
        """1초 진행: 리퍼 → 스폰 → 처치·XP → 레벨업 3택 → 접촉 피해."""
        v, minute = self.v, self.t // 60
        if self.t >= v["run_seconds"]:
            self.ended = "reaper"
            return
        if self.t % 60 == 0:
            self.alive += spawn_per_min(minute, v)
            self.spawned += spawn_per_min(minute, v)
        weapon_lv = sum(l for u, l in self.levels.items() if u in v["weapons"])
        dps = v["player_dps"] * (1 + v["dps_per_weapon_lv"] * weapon_lv)
        dps *= 1 + v["dps_per_spinach_lv"] * self.levels.get("spinach", 0)
        rate = dps / (v["enemy_hp_base"] + v["enemy_hp_per_min"] * minute)
        killed = min(self.alive, int(rate) + (1 if self.rng.random() < rate % 1 else 0))
        self.alive -= killed
        self.kills += killed
        self.xp += killed
        while self.xp >= xp_to_next(self.level, v):
            self.xp -= xp_to_next(self.level, v)
            self.level += 1
            choices = draw_choices(self.levels, self.rng, v)
            if choices:
                pick = self.rng.choice(choices)
                self.levels[pick] = self.levels.get(pick, 0) + 1
        armor = max(0.2, 1 - v["armor_cut"] * self.levels.get("armor", 0))
        self.hp -= self.alive * v["enemy_dps"] * armor
        if self.hp <= 0:
            self.ended = "dead"
            return
        self.t += 1

    def run(self):
        while self.ended is None:
            self.tick()
        return self.ended


# ---------------------------------------------------------------- 테스트
def test_cost_exponential():
    """비용이 base × r^n 이고 일괄 구매식이 개별 합과 일치."""
    assert abs(upgrade_cost(0) - 4.0) < 1e-9 and abs(upgrade_cost(10) - 4.0 * 1.07 ** 10) < 1e-9
    assert abs(bulk_cost(5, 20) - sum(upgrade_cost(5 + i) for i in range(20))) < 1e-6

def test_output_linear_vs_cost():
    """n ≥ 1/ln(r)≈15 부터 마일스톤 사이에서 비용/산출 비가 단조 증가(벽이 반드시 생김)."""
    assert 14 < 1 / math.log(1.07) < 16
    for lo, hi in ((15, 25), (25, 50), (50, 120)):
        ratios = [upgrade_cost(n) / output_per_sec(n) for n in range(lo, hi)]
        assert all(a < b for a, b in zip(ratios, ratios[1:])), (lo, hi)
    assert output_per_sec(25) == 1.67 * 25 * 2.0 and output_per_sec(24) == 1.67 * 24

def test_time_to_wall():
    """같은 수입이면 10레벨 올리는 시간 비가 r^10 에 수렴(지수 벽)."""
    t1, t2 = time_to_level(50, 60, 100.0), time_to_level(60, 70, 100.0)
    assert abs(t2 / t1 - 1.07 ** 10) < 1e-6
    assert time_to_level(0, 10, 0) == math.inf

def test_damage_never_zero():
    """방어가 아무리 커도 0·음수 데미지가 나오지 않음."""
    rng = random.Random(1)
    for df in (0, 100, 10_000, 10 ** 9):
        assert all(damage(1, df, rng) >= 1 for _ in range(200))

def test_damage_ratio_defense():
    """def_k 와 같은 방어는 정확히 절반 경감."""
    rng = random.Random(2)
    vals = [damage(1000, 100, rng) for _ in range(2000)]
    assert 475 <= min(vals) and max(vals) <= 525, (min(vals), max(vals))
    assert abs(sum(vals) / len(vals) - 500) < 5

def test_stage_wall_detection():
    """공격력이 고정이면 어느 스테이지부터 반드시 벽이 되고 그 뒤로 유지."""
    rng = random.Random(3)
    wall = next(s for s in range(1, 300) if is_wall(50, s, rng))
    assert 1 < wall < 300
    assert all(is_wall(50, s, rng) for s in range(wall + 5, wall + 15))

def test_prestige_compound():
    """환생을 거듭할수록 배율이 누적되고 벽 스테이지가 더 멀어짐."""
    points, walls = 0, []
    for i in range(3):
        run = IdleRun(seed=100 + i, prestige_mult=prestige_multiplier(points))
        walls.append(run.run_until_wall())
        points += prestige_points(run.lifetime)
    assert walls[0] < walls[1] < walls[2], walls
    assert prestige_multiplier(points) > 1.0 and prestige_points(-5) == 0

def test_offline_cap():
    """오프라인 수익은 max_hours 에서 잘림."""
    assert calc_offline(1000, 1000 + 3 * 86400, 1.0) == int(8 * 3600)
    assert calc_offline(1000, 1000 + 600, 2.0) == 1200

def test_offline_negative_rejected():
    """시간 역행·동일 시각·첫 실행은 0."""
    assert calc_offline(5000, 4000, 10.0) == 0
    assert calc_offline(5000, 5000, 10.0) == 0
    assert calc_offline(0, 999_999, 10.0) == 0

def test_gacha_hard_pity():
    """10만 뽑기에서 5★ 간격이 90 을, 4★ 간격이 10 을 넘지 않음."""
    g, gap5, gap4 = Gacha(seed=7), 0, 0
    for _ in range(100_000):
        rarity, _, _ = g.pull()
        gap5, gap4 = gap5 + 1, gap4 + 1
        assert gap5 <= 90 and gap4 <= 10
        if rarity == "5":
            gap5 = gap4 = 0
        elif rarity == "4":
            gap4 = 0

def test_gacha_empirical_rate():
    """천장 미강제 뽑기의 5★ 비율 ≈ 0.6%, 전체 비율 ≈ 1/E[간격] (해석식)."""
    g, n = Gacha(seed=11), 100_000
    free_n = free_hit = total5 = 0
    for _ in range(n):
        rarity, _, forced = g.pull()
        total5 += rarity == "5"
        if not forced:
            free_n += 1
            free_hit += rarity == "5"
    p = CONFIG["gacha"]["rates"]["5"]
    assert abs(free_hit / free_n - p) < 0.001, free_hit / free_n
    expected_gap = (1 - (1 - p) ** 90) / p
    assert abs(total5 / n - 1 / expected_gap) < 0.002, (total5 / n, 1 / expected_gap)

def test_gacha_fifty_fifty():
    """50/50 실패 다음 5★는 픽업 확정, 픽업 비율 ≈ 2/3, 최악 180 뽑."""
    g, prev_lost, since_feat, worst, feat, total = Gacha(seed=13), False, 0, 0, 0, 0
    for _ in range(200_000):
        rarity, featured, _ = g.pull()
        since_feat += 1
        if rarity == "5":
            total, feat = total + 1, feat + featured
            assert featured or not prev_lost
            prev_lost = not featured
            if featured:
                worst, since_feat = max(worst, since_feat), 0
    assert abs(feat / total - 2 / 3) < 0.02, feat / total
    assert worst <= 180

def test_probability_table_sums():
    """공개 확률표가 실제 뽑기 데이터에서 나오고 합이 100%."""
    t = Gacha(seed=0).table()
    assert abs(sum(t.values()) - 100.0) < 1e-6 and t["5"] == 0.6

def test_stamina_regen():
    """8분당 1 회복, 상한 200, 시간 역행 무시, 잔여초 보존."""
    assert regen_stamina(0, 0, 480 * 3 + 100) == (3, 480 * 3)
    assert regen_stamina(199, 0, 480 * 50)[0] == 200
    assert regen_stamina(50, 1000, 900) == (50, 1000)

def test_survivor_three_choice():
    """3택은 서로 다르고 만렙 항목은 제외, 후보 부족 시 그만큼만."""
    rng = random.Random(5)
    for _ in range(500):
        c = draw_choices({"whip": 8, "wand": 3}, rng)
        assert len(c) == 3 and len(set(c)) == 3 and "whip" not in c
    assert draw_choices({u: 8 for u in CONFIG["survivor"]["upgrade_pool"]}, rng) == []
    assert len(draw_choices({u: 8 for u in ["whip", "wand", "garlic", "axe"]}, rng)) == 2

def test_survivor_run_ends_30min():
    """런은 1800초를 넘기지 못함(리퍼) 또는 그 전에 사망으로 끝남."""
    ends = set()
    for seed in range(8):
        r = SurvivorRun(seed)
        ends.add(r.run())
        assert r.ended in ("reaper", "dead") and r.t <= 1800
        assert r.ended != "reaper" or r.t == 1800
    assert ends == {"reaper", "dead"}, ends

def test_survivor_wave_density():
    """분당 스폰 수는 단조 증가하고 상한에서 멈춤."""
    seq = [spawn_per_min(m) for m in range(31)]
    assert all(a <= b for a, b in zip(seq, seq[1:])) and seq[-1] == 120 and seq[0] == 10

def test_survivor_xp_curve():
    """필요 XP 는 다항 증가(선형보다 가파르고 지수보다 완만)."""
    xs = [xp_to_next(l) for l in range(1, 40)]
    assert all(a < b for a, b in zip(xs, xs[1:]))
    assert xs[-1] / xs[0] < 1.07 ** 100 and xs[-1] > 39 * xs[0]

TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

def run_tests():
    """모든 test_* 실행, 'passed k/n' 출력, 실패 수 반환."""
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"ok   {t.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL {t.__name__}: {e!r}")
    print(f"passed {len(TESTS) - failed}/{len(TESTS)}")
    return failed

def demo(seed=42):
    """시드 고정 데모: 방치형 환생 3회 + 가차 90뽑 + 서바이버 2런."""
    points = 0
    print("== 방치형: 환생 3회 ==")
    for i in range(3):
        run = IdleRun(seed + i, prestige_multiplier(points))
        wall = run.run_until_wall()
        gained = prestige_points(run.lifetime)
        print(f"환생 {i}: 배율 x{prestige_multiplier(points):.2f} → 벽 스테이지 {wall}, 업그레이드 "
              f"{run.level}레벨, 누적 코인 {run.lifetime:,.0f}, {run.elapsed / 60:.1f}분, 포인트 +{gained}")
        points += gained
    print(f"오프라인 24h 보상(초당 1.67): {calc_offline(1, 1 + 86400, 1.67):,} (8h 상한)\n== 가차 90뽑 ==")
    g, got = Gacha(seed), []
    for i in range(90):
        r, f, forced = g.pull()
        if r == "5":
            got.append(f"{i + 1}번째{'(천장)' if forced else ''}{'·픽업' if f else '·일반'}")
    print("5★:", ", ".join(got) or "없음", "| 확률표", g.table())
    print("== 서바이버 런 (시드 2: 생존 / 시드 0: 근접 실패) ==")
    for s in (SurvivorRun(2), SurvivorRun(0)):
        end = s.run()
        print(f"종료 {end} @ {s.t}s, 레벨 {s.level}, 처치 {s.kills}/{s.spawned}, 빌드 {s.levels}")


if __name__ == "__main__":
    sys.exit(demo() if "--demo" in sys.argv else run_tests())
