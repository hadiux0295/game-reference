#!/usr/bin/env python3
"""MOBA(1레인·소규모) 규칙 시뮬레이션. 표준 라이브러리만. `--test` / `--demo`."""
import copy
import functools
import math
import random
import sys

# 출처는 logic.md §2 참조. README §4 출처값(웨이브 주기·미니언 골드·플레이트·현상금) 외는 전부 예시값.
CONFIG = {
    "version": 1, "match": {"target_minutes": 15, "sim_tick_sec": 1.0, "max_minutes": 25},
    "lane": {"length": 100, "minion_speed": 1.5, "hero_speed": 3.0},
    "wave": {"first_spawn_sec": 30, "period_sec": [[0, 30], [840, 25], [1800, 20]],
             "melee": 3, "ranged": 3, "siege_every": 3, "growth_per_min": 0.03},
    "minion": {"melee": {"hp": 100, "atk": 10, "range": 2, "gold": 20, "xp": 30},
               "ranged": {"hp": 70, "atk": 12, "range": 8, "gold": 14, "xp": 30},
               "siege": {"hp": 220, "atk": 25, "range": 10, "gold": [50, 69, 1800], "xp": 60}},
    "hero": {"base_hp": 500, "hp_per_level": 90, "base_atk": 55, "atk_per_level": 4, "range": 8, "max_level": 15,
             "xp_base": 180, "xp_per_level": 100, "xp_share_range": 15, "regen_per_sec": 2, "max_items": 6},
    "income": {"passive_gold_per_sec": 2.0, "passive_start_sec": 110, "start_gold": 500,
               "kill_gold": 300, "kill_xp": 150, "shutdown_per_streak": 150, "shutdown_cap": 700},
    "tower": {"outer": {"pos": 30, "hp": 2200, "atk": 90, "range": 9, "plates": 5, "plate_gold": 120},
              "inner": {"pos": 12, "hp": 2000, "atk": 100, "range": 9, "plates": 0, "plate_gold": 0},
              "first_tower_bonus": 300, "team_gold_on_destroy": 150, "aggro_window_sec": 2},
    "nexus": {"pos": 3, "hp": 2500}, "dragon": {"first_spawn_sec": 150, "respawn_sec": 120, "take_sec": 5, "team_gold": 100, "xp": 150},
    "bounty": {"activate_sec": 840, "min_deficit": 1000, "sustain_sec": 60, "gap_ratio": 0.10, "cap": 1000,
               "base": {"outer": 250, "inner": 400, "dragon": 500, "baron": 300}},
    "death": {"base_sec": 10, "per_level_sec": 2.0, "late_start_sec": 600, "per_minute_sec": 1.0, "cap_sec": 60},
    "items": {"sword": {"cost": 350, "atk": 10}, "vest": {"cost": 400, "hp": 150}, "blade": {"cost": 1100, "atk": 30},
              "plate": {"cost": 1300, "hp": 450}}, "build": ["sword", "vest", "blade", "plate", "blade", "plate"]
}

def period_at(cfg, t):
    """시각 t(초)의 웨이브 간격: [[시작초, 간격], ...]에서 마지막으로 넘은 행."""
    return [sec for start, sec in cfg["wave"]["period_sec"] if t >= start][-1]

def siege_gold(cfg, t):
    """공성 미니언 골드: [시작값, 끝값, 끝에 도달하는 초]를 선형 보간."""
    lo, hi, end = cfg["minion"]["siege"]["gold"]
    return int(round(lo + (hi - lo) * min(1.0, t / end)))

def xp_needed(cfg, level):
    """level → level+1 에 필요한 경험치(선형 곡선)."""
    return cfg["hero"]["xp_base"] + cfg["hero"]["xp_per_level"] * (level - 1)

def death_timer(cfg, level, t):
    """사망 대기: 기본 + 레벨 비례 + 후반 분당 가산, 상한."""
    d = cfg["death"]
    return min(d["cap_sec"], d["base_sec"] + d["per_level_sec"] * level + max(0.0, (t - d["late_start_sec"]) / 60.0) * d["per_minute_sec"])

class Ent:
    """레인 위 모든 것(미니언·영웅·타워·넥서스)의 공통 필드. dist()는 1차원 레인 거리."""
    def __init__(self, team, kind, pos, hp, atk, rng):
        self.team, self.kind, self.pos, self.hp, self.hp_max = team, kind, pos, hp, hp
        self.atk, self.range, self.alive = atk, rng, True
    def dist(self, o):
        return abs(self.pos - o.pos)

class Minion(Ent):
    """웨이브 미니언. growth는 시간 경과 성장 배율, gold/xp는 처치 보상."""
    def __init__(self, team, kind, pos, c, gold, growth=1.0):
        super().__init__(team, kind, pos, int(c["hp"] * growth), int(c["atk"] * growth), c["range"])
        self.gold, self.xp = gold, c["xp"]

class Tower(Ent):
    """타워. 플레이트는 체력을 plates 등분한 구간이며 구간을 깎을 때마다 골드."""
    def __init__(self, team, kind, pos, c):
        super().__init__(team, kind, pos, c["hp"], c["atk"], c["range"])
        self.plates_left, self.plate_gold = c["plates"], c["plate_gold"]
        self.plate_hp = c["hp"] / c["plates"] if c["plates"] else 0

class Hero(Ent):
    """영웅. cs_skill=라스트힛 성공률, aggression=교전 확률 (둘 다 예시값)."""
    def __init__(self, team, name, cfg, cs_skill, aggression, pos):
        h = cfg["hero"]
        super().__init__(team, "hero", pos, h["base_hp"], h["base_atk"], h["range"])
        self.name, self.cs_skill, self.aggression, self.home = name, cs_skill, aggression, pos
        self.level, self.xp, self.gold, self.gold_earned, self.streak = 1, 0, 0, 0, 0
        self.respawn_at, self.items, self.last_hit_hero_at = None, [], -999
        self.stats = {"cs": 0, "kills": 0, "deaths": 0, "cs_gold": 0, "passive_gold": 0}

class Match:
    """한 판. 권위 측(서버) 시뮬레이션: 상태 Playing → Finished."""
    def __init__(self, seed=1, heroes=((0.8, 0.3), (0.8, 0.3)), overrides=None, per_team=1):
        self.cfg = copy.deepcopy(CONFIG)
        for path, v in (overrides or {}).items():          # "bounty.cap": 0 처럼 점 경로로 덮어쓰기
            keys = path.split(".")
            functools.reduce(dict.__getitem__, keys[:-1], self.cfg)[keys[-1]] = v
        self.rng, self.t, self.state, self.winner, self.log = random.Random(seed), 0.0, "Playing", None, []
        self.wave_no, self.next_wave_t, self.minions = 0, self.cfg["wave"]["first_spawn_sec"], []
        self.first_tower_taken, self.bounty_paid, self.dragon_hold = False, [], (None, 0)
        self.dragon_up_at, self.teams, L = self.cfg["dragon"]["first_spawn_sec"], [], self.cfg["lane"]["length"]
        for team in (0, 1):
            mirror = (lambda p: p) if team == 0 else (lambda p: L - p)
            towers = [Tower(team, k, mirror(self.cfg["tower"][k]["pos"]), self.cfg["tower"][k]) for k in ("outer", "inner")]
            nexus = Ent(team, "nexus", mirror(self.cfg["nexus"]["pos"]), self.cfg["nexus"]["hp"], 0, 0)
            hs = [Hero(team, "AB"[team] + str(i), self.cfg, *heroes[team], towers[0].pos) for i in range(per_team)]
            self.teams.append({"heroes": hs, "towers": towers, "nexus": nexus, "gold_earned": 0, "bounty_since": None})
            for h in hs:
                self.add_gold(h, self.cfg["income"]["start_gold"], "start")
                self.shop(h)
    def add_gold(self, hero, amount, reason):
        """영웅 골드 증감의 유일한 함수. 잔액 부족이면 거부(False). 로그에 사유 기록."""
        if hero.gold + amount < 0: return False
        hero.gold += amount
        if amount > 0:
            hero.gold_earned += amount
            self.teams[hero.team]["gold_earned"] += amount
        self.log.append((self.t, hero.name, amount, reason))
        return True
    def give_team_gold(self, team, amount, reason):
        """팀 보상(플레이트·타워·현상금)을 팀 영웅에게 균등 분배(나머지 버림)."""
        for h in self.teams[team]["heroes"]:
            self.add_gold(h, amount // len(self.teams[team]["heroes"]), reason)
    def deficit(self, team):
        """team이 상대보다 뒤처진 골드(양수=뒤처짐)."""
        return self.teams[1 - team]["gold_earned"] - self.teams[team]["gold_earned"]
    def bounty_active(self, team):
        """오브젝트 현상금 활성: 활성 시각 이후, 격차 ≥ 기준을 sustain_sec 동안 유지했을 때."""
        since = self.teams[team]["bounty_since"]
        return since is not None and self.t - since >= self.cfg["bounty"]["sustain_sec"]
    def objective_bounty(self, team, kind, record=False):
        """현상금 = min(기본[kind] + 격차×비율, 상한). 비활성이면 0. record=True면 지급 기록."""
        b = self.cfg["bounty"]
        bounty = int(min(b["base"][kind] + b["gap_ratio"] * self.deficit(team), b["cap"])) if self.bounty_active(team) else 0
        if bounty and record:
            self.bounty_paid.append((self.t, team, kind, bounty))
        return bounty
    def shutdown_gold(self, victim):
        """셧다운: 연속킬 2 이상부터 가산, 상한. 피해자 팀의 현상금이 활성이면 0(억제)."""
        inc = self.cfg["income"]
        return 0 if victim.streak < 2 or self.bounty_active(victim.team) else min(inc["shutdown_cap"], inc["shutdown_per_streak"] * (victim.streak - 1))
    def next_item(self, hero):
        """빌드 순서상 다음 아이템 id (다 샀으면 None)."""
        b = self.cfg["build"]
        return b[len(hero.items)] if len(hero.items) < min(len(b), self.cfg["hero"]["max_items"]) else None
    def shop(self, hero):
        """기지에서 빌드 순서대로 살 수 있는 만큼 구매. 골드 소비처(add_gold 단일 경로)."""
        while self.next_item(hero):
            iid, it = self.next_item(hero), self.cfg["items"][self.next_item(hero)]
            if not self.add_gold(hero, -it["cost"], "buy:" + iid): break
            hero.items.append(iid)
            hero.atk, hero.hp_max, hero.hp = hero.atk + it.get("atk", 0), hero.hp_max + it.get("hp", 0), hero.hp + it.get("hp", 0)
    def gain_xp(self, hero, xp):
        """경험치 지급과 레벨업(상한까지 반복), 레벨당 체력·공격 성장."""
        h = self.cfg["hero"]
        hero.xp += xp
        while hero.level < h["max_level"] and hero.xp >= xp_needed(self.cfg, hero.level):
            hero.xp -= xp_needed(self.cfg, hero.level)
            hero.level += 1
            hero.hp_max, hero.hp, hero.atk = hero.hp_max + h["hp_per_level"], hero.hp + h["hp_per_level"], hero.atk + h["atk_per_level"]
    def spawn_wave(self):
        """양 팀 기지에서 같은 구성의 웨이브를 동시에 생성. 시간 성장 배율 적용."""
        w, mc, growth = self.cfg["wave"], self.cfg["minion"], 1.0 + self.cfg["wave"]["growth_per_min"] * self.t / 60.0
        self.wave_no += 1
        kinds = ["melee"] * w["melee"] + ["ranged"] * w["ranged"] + (["siege"] if self.wave_no % w["siege_every"] == 0 else [])
        for team in (0, 1):
            for k in kinds:
                gold = siege_gold(self.cfg, self.t) if k == "siege" else mc[k]["gold"]
                self.minions.append(Minion(team, k, self.teams[team]["nexus"].pos, mc[k], gold, growth))
        self.next_wave_t += period_at(self.cfg, self.t)
    def damage(self, target, amount, src):
        """피해 적용과 처치 분기. 처치 보상(라스트힛·경험치·킬·타워·넥서스 판정)은 전부 여기서만 발생한다."""
        if not target.alive: return
        target.hp -= amount
        if isinstance(target, Tower) and target.plates_left > 0:
            now_plates = math.ceil(max(target.hp, 0) / target.plate_hp)
            if now_plates < target.plates_left:
                self.give_team_gold(src.team, (target.plates_left - now_plates) * target.plate_gold, "plate")
                target.plates_left = now_plates
        if target.hp > 0: return
        target.alive = False
        if isinstance(target, Minion):
            if isinstance(src, Hero):                          # 라스트힛: 영웅이 막타일 때만 골드
                self.add_gold(src, target.gold, "last_hit")
                src.stats["cs"] += 1
                src.stats["cs_gold"] += target.gold
            for h in self.teams[1 - target.team]["heroes"]:    # 경험치는 근처 아군 영웅 모두
                if h.alive and h.dist(target) <= self.cfg["hero"]["xp_share_range"]:
                    self.gain_xp(h, target.xp)
        elif isinstance(target, Hero):
            self.on_hero_death(target, src)
        elif isinstance(target, Tower):
            gold = self.cfg["tower"]["team_gold_on_destroy"] + (0 if self.first_tower_taken else self.cfg["tower"]["first_tower_bonus"])
            self.first_tower_taken = True
            self.give_team_gold(src.team, gold + self.objective_bounty(src.team, target.kind, True), "tower")
        else:                                                  # 넥서스 → 승패 판정
            self.state, self.winner = "Finished", 1 - target.team
    def on_hero_death(self, victim, killer):
        """킬 골드·셧다운·경험치 지급, 사망 타이머 설정."""
        victim.stats["deaths"], victim.respawn_at = victim.stats["deaths"] + 1, self.t + death_timer(self.cfg, victim.level, self.t)
        if isinstance(killer, Hero):
            self.add_gold(killer, self.cfg["income"]["kill_gold"] + self.shutdown_gold(victim), "kill")
            self.gain_xp(killer, self.cfg["income"]["kill_xp"])
            killer.streak, killer.stats["kills"] = killer.streak + 1, killer.stats["kills"] + 1
        victim.streak = 0
    def nexus_attackable(self, team):
        """그 팀의 타워가 모두 죽어야 넥서스를 칠 수 있다."""
        return all(not t.alive for t in self.teams[team]["towers"])
    def enemies_in_range(self, e):
        """사거리 안의 적 (미니언 목록, 영웅 목록)."""
        foe = 1 - e.team
        ms = [m for m in self.minions if m.alive and m.team == foe and e.dist(m) <= e.range]
        return ms, [h for h in self.teams[foe]["heroes"] if h.alive and e.dist(h) <= e.range]
    def act_minion(self, m):
        """미니언: 사거리 안 적 미니언 → 타워 → 영웅 → 넥서스 순으로 공격, 없으면 전진."""
        foe, (ms, hs) = 1 - m.team, self.enemies_in_range(m)
        nexus = [self.teams[foe]["nexus"]] if self.nexus_attackable(foe) and m.dist(self.teams[foe]["nexus"]) <= max(m.range, 1) else []
        pool = ms or [t for t in self.teams[foe]["towers"] if t.alive and m.dist(t) <= m.range] or hs or nexus
        if pool:
            self.damage(min(pool, key=m.dist), m.atk, m)
        else:
            d = 1 if m.team == 0 else -1
            m.pos = min(max(m.pos + d * self.cfg["lane"]["minion_speed"], 0), self.cfg["lane"]["length"])
    def act_hero(self, h):
        """영웅: 아군 웨이브 바로 뒤에 서서 귀환·구매 > 교전 > 라스트힛 > 푸시 > (아군이 탱킹할 때) 타워·넥서스."""
        foe, cfg = 1 - h.team, self.cfg
        h.hp = min(h.hp_max, h.hp + cfg["hero"]["regen_per_sec"])
        d = 1 if h.team == 0 else -1
        allies = [m.pos for m in self.minions if m.alive and m.team == h.team]
        front = (max(allies) if d == 1 else min(allies)) if allies else h.home
        for t in self.teams[foe]["towers"]:                    # 아군 미니언 없이 타워 사거리에 들어가지 않는다
            if t.alive and not any(abs(p - t.pos) <= t.range for p in allies):
                front = min(front, t.pos - (t.range + 1)) if d == 1 else max(front, t.pos + t.range + 1)
        h.pos += max(-cfg["lane"]["hero_speed"], min(cfg["lane"]["hero_speed"], (front - d) - h.pos))
        ms, hs = self.enemies_in_range(h)
        nxt = self.next_item(h)
        if nxt and h.gold >= cfg["items"][nxt]["cost"] and not hs:   # 귀환 후 구매(골드 소비처)
            h.pos = h.home
            return self.shop(h)
        if hs and self.rng.random() < h.aggression:
            h.last_hit_hero_at = self.t
            return self.damage(min(hs, key=h.dist), h.atk, h)
        lh = [m for m in ms if m.hp <= h.atk]
        if lh and self.rng.random() < h.cs_skill:
            return self.damage(min(lh, key=lambda m: m.hp), h.atk, h)
        if ms and not lh:                                      # 라인 푸시(평타로 웨이브 정리)
            return self.damage(min(ms, key=h.dist), h.atk, h)
        for t in self.teams[foe]["towers"]:
            if t.alive and h.dist(t) <= h.range and any(abs(p - t.pos) <= t.range for p in allies):
                return self.damage(t, h.atk, h)
        if self.nexus_attackable(foe) and h.dist(self.teams[foe]["nexus"]) <= h.range:
            self.damage(self.teams[foe]["nexus"], h.atk, h)
    def act_dragon(self):
        """중립 오브젝트: 한 팀만 '여유 있는'(교전 없음, 체력 50%↑) 영웅을 take_sec 동안 유지하면 가져간다."""
        d = self.cfg["dragon"]
        if self.t < self.dragon_up_at: return
        free = {i for i, team in enumerate(self.teams) for h in team["heroes"]
                if h.alive and h.hp >= 0.5 * h.hp_max and not self.enemies_in_range(h)[1]}
        team = free.pop() if len(free) == 1 else None
        self.dragon_hold = (team, self.dragon_hold[1] + 1 if self.dragon_hold[0] == team else 1) if team is not None else (None, 0)
        if self.dragon_hold[1] >= d["take_sec"]:
            self.give_team_gold(team, d["team_gold"] + self.objective_bounty(team, "dragon", True), "dragon")
            for h in self.teams[team]["heroes"]:
                self.gain_xp(h, d["xp"])
            self.dragon_up_at, self.dragon_hold = self.t + d["respawn_sec"], (None, 0)
    def tower_target(self, t):
        """타워 우선순위: 최근 아군 영웅을 때린 적 영웅 → 가장 가까운 미니언 → 가장 가까운 영웅."""
        ms, hs = self.enemies_in_range(t)
        pool = [h for h in hs if self.t - h.last_hit_hero_at <= self.cfg["tower"]["aggro_window_sec"]] or ms or hs
        return min(pool, key=t.dist) if pool else None
    def step(self):
        """권위 측 한 틱: 시간 → 부활·수입 → 웨이브 → 현상금 상태 → 미니언 → 영웅 → 오브젝트 → 타워 → 정리·판정."""
        if self.state != "Playing": return
        dt, inc, b = self.cfg["match"]["sim_tick_sec"], self.cfg["income"], self.cfg["bounty"]
        self.t += dt
        for h in [h for team in self.teams for h in team["heroes"]]:
            if not h.alive and self.t >= h.respawn_at:
                h.alive, h.hp, h.pos = True, h.hp_max, h.home
                self.shop(h)
            if self.t >= inc["passive_start_sec"] and self.add_gold(h, int(inc["passive_gold_per_sec"] * dt), "passive"):
                h.stats["passive_gold"] += int(inc["passive_gold_per_sec"] * dt)
        if self.t >= self.next_wave_t:
            self.spawn_wave()
        for i, team in enumerate(self.teams):
            behind = self.t >= b["activate_sec"] and self.deficit(i) >= b["min_deficit"]
            team["bounty_since"] = (team["bounty_since"] if team["bounty_since"] is not None else self.t) if behind else None
        for m in list(self.minions):
            if m.alive:
                self.act_minion(m)
        for h in [h for team in self.teams for h in team["heroes"] if h.alive]:
            self.act_hero(h)
        self.act_dragon()
        for t in [t for team in self.teams for t in team["towers"] if t.alive]:
            if self.tower_target(t):
                self.damage(self.tower_target(t), t.atk, t)
        self.minions = [m for m in self.minions if m.alive]
        if self.t >= self.cfg["match"]["max_minutes"] * 60 and self.state == "Playing":
            self.state, self.winner = "Finished", None          # 시간 상한: 무승부(예시 규칙)
    def run(self, seconds=None):
        """Finished 또는 지정 초(기본: 상한)까지 진행."""
        limit = seconds if seconds is not None else self.cfg["match"]["max_minutes"] * 60
        while self.state == "Playing" and self.t < limit:
            self.step()
        return self


def test_wave_spawn_timing():      # 테스트 이름은 logic.md §3 "검증" 항목과 일치
    """첫 웨이브 0:30, 간격 30초 → 14:00부터 25초 → 30:00부터 20초 (README §4); 근접3+원거리3, 3웨이브마다 공성(예시값)."""
    m = Match(seed=1)
    assert m.run(29).wave_no == 0 and m.run(31).wave_no == 1
    a = [x for x in m.minions if x.team == 0]
    assert len(a) == 6 and sum(x.kind == "melee" for x in a) == 3
    assert m.run(91).wave_no == 3 and sum(x.kind == "siege" for x in m.minions) == 2
    assert period_at(m.cfg, 839) == 30 and period_at(m.cfg, 840) == 25 and period_at(m.cfg, 1800) == 20
    assert m.run(840).wave_no == 28 and m.next_wave_t == 865       # 30 + 27×30 = 840 → 28번째, 다음은 +25

def test_lane_march_and_clash():
    """양 웨이브가 기지에서 출발해 레인 중앙에서 만나 서로 소모한다. 대칭이면 결과도 대칭."""
    m = Match(seed=1, heroes=((0.0, 0.0), (0.0, 0.0))).run(31)
    assert all(min(x.dist(m.teams[0]["nexus"]), x.dist(m.teams[1]["nexus"])) <= 3 for x in m.minions)
    m.run(120)
    assert sum(x.team == 0 for x in m.minions) * 2 == len(m.minions) and any(x.hp < x.hp_max for x in m.minions)
    assert all(0 < x.pos < m.cfg["lane"]["length"] for x in m.minions)

def test_last_hit_vs_passive_income():
    """미니언 골드 근접 20/원거리 14/공성 50→69 (README §4). 10분: 능숙(0.95)은 CS 골드 > 패시브, 무능(0.0)은 패시브만."""
    c = CONFIG
    assert c["minion"]["melee"]["gold"] == 20 and c["minion"]["ranged"]["gold"] == 14
    assert siege_gold(c, 0) == 50 and 50 < siege_gold(c, 900) < 69 and siege_gold(c, 9999) == 69
    m = Match(seed=3, heroes=((0.95, 0.0), (0.0, 0.0))).run(600)
    a, b = m.teams[0]["heroes"][0], m.teams[1]["heroes"][0]
    assert a.stats["cs"] > 0 and b.stats["cs"] == 0 and b.stats["cs_gold"] == 0
    assert a.stats["cs_gold"] > a.stats["passive_gold"] > 0, (a.stats, b.stats)
    assert b.stats["passive_gold"] == int(2.0 * (min(m.t, 600) - 110 + 1)) and a.gold_earned > b.gold_earned

def test_tower_priority():
    """미니언·영웅이 함께 있으면 미니언 우선; 적 영웅이 아군 영웅을 때리면 그 영웅으로 전환, 창(2초) 뒤 해제."""
    m = Match(seed=1)
    t, atk, vic = m.teams[1]["towers"][0], m.teams[0]["heroes"][0], m.teams[1]["heroes"][0]
    atk.pos, vic.pos = t.pos - 3, t.pos - 2
    mn = Minion(0, "melee", t.pos - 5, m.cfg["minion"]["melee"], 20)
    m.minions.append(mn)
    assert m.tower_target(t) is mn
    m.t, atk.last_hit_hero_at = 100, 99
    assert m.tower_target(t) is atk
    m.t = 100 + m.cfg["tower"]["aggro_window_sec"] + 1
    assert m.tower_target(t) is mn

def test_tower_plates_and_first_tower_bonus():
    """플레이트 5×120=600, 첫 타워 +300 (README §4), 팀 보상 150(예시값) → 1v1 합계 1050."""
    m = Match(seed=1)
    h, t = m.teams[0]["heroes"][0], m.teams[1]["towers"][0]
    before = h.gold
    m.damage(t, t.plate_hp * 2 + 1, h)
    assert t.plates_left == 3 and h.gold == before + 240
    m.damage(t, 10 ** 6, h)
    assert not t.alive and m.first_tower_taken and h.gold == before + 600 + 300 + 150

def test_objective_bounty_formula_and_cap():
    """현상금 = min(기본 + 격차×10%, 1000). 활성 전·앞선 팀·격차 미달·60초 미유지면 0."""
    m = Match(seed=1, heroes=((0.0, 0.0), (0.0, 0.0)), overrides={"income.passive_gold_per_sec": 0})
    a, b = m.teams[0]["heroes"][0], m.teams[1]["heroes"][0]
    m.add_gold(a, 3000, "test")
    assert m.run(100).objective_bounty(1, "outer") == 0     # 14:00 이전
    m.t = 839
    assert not m.run(840).bounty_active(1)                  # 60초 유지 전
    m.run(m.t + 61)
    assert m.bounty_active(1) and not m.bounty_active(0)
    assert m.objective_bounty(1, "outer") == 250 + 300 and m.objective_bounty(0, "outer") == 0
    m.add_gold(a, 20000, "test")
    assert m.objective_bounty(1, "inner") == 1000           # 상한
    m.add_gold(b, 23000, "test")
    m.step()
    assert not m.bounty_active(1)                           # 격차 해소 → 즉시 비활성

def test_bounty_limits_snowball():
    """초반 골드 우위 팀이 있어도 현상금은 건당 ≤1000, 뒤진 팀만 받고, 최종 격차는 현상금 없을 때보다 작다."""
    ov, skew = {"bounty.activate_sec": 300}, ((0.95, 0.6), (0.3, 0.2))   # 활성 5:00 = 모바일 압축(예시값)
    with_b = Match(seed=6, heroes=skew, overrides=ov).run()
    without = Match(seed=6, heroes=skew, overrides=dict(ov, **{"bounty.cap": 0})).run()
    assert with_b.teams[0]["gold_earned"] > with_b.teams[1]["gold_earned"]
    assert with_b.bounty_paid, "현상금이 한 번도 지급되지 않음"
    assert all(p[3] <= 1000 and p[1] == 1 for p in with_b.bounty_paid)
    assert with_b.deficit(1) < without.deficit(1), (with_b.deficit(1), without.deficit(1))

def test_death_timer_and_shutdown():
    """사망 대기는 레벨·시간에 단조 증가·상한 60초; 셧다운은 연속킬 2부터·상한 700, 피해자 팀 현상금 활성 중엔 0."""
    c = CONFIG
    assert death_timer(c, 1, 0) < death_timer(c, 10, 0) < death_timer(c, 10, 1200)
    assert death_timer(c, 5, 0) == death_timer(c, 5, 600) and death_timer(c, 15, 10 ** 6) == 60
    m = Match(seed=1)
    v = m.teams[1]["heroes"][0]
    for streak, gold in ((1, 0), (3, 300), (30, 700)):
        v.streak = streak
        assert m.shutdown_gold(v) == gold
    m.teams[1]["bounty_since"] = -1000
    assert m.bounty_active(1) and m.shutdown_gold(v) == 0

def test_level_curve_and_item_shop():
    """레벨: 요구 경험치 증가·상한 15·레벨당 체력 +90 공격 +4. 상점: add_gold 단일 경로, 잔액 음수 불가, 빌드 순서대로 스탯 적용."""
    m = Match(seed=1)
    h = m.teams[0]["heroes"][0]
    assert h.items == ["sword"] and h.gold == 150 and h.atk == 65      # 시작 500골드, 빌드 1번
    assert not m.add_gold(h, -151, "test") and h.gold == 150
    m.add_gold(h, 1400, "test")
    m.shop(h)
    assert h.gold == 50 and h.items == ["sword", "vest", "blade"] and h.hp_max == 650 and h.atk == 95
    assert sum(x[2] for x in m.log if x[1] == "A0" and x[3].startswith("buy:")) == -(350 + 400 + 1100)
    assert xp_needed(m.cfg, 1) < xp_needed(m.cfg, 2) < xp_needed(m.cfg, 10)
    m.gain_xp(h, xp_needed(m.cfg, 1))
    assert h.level == 2 and h.hp_max == 740 and h.atk == 99
    m.gain_xp(h, 10 ** 6)
    assert h.level == m.cfg["hero"]["max_level"]

def test_nexus_win():
    """타워가 서 있으면 넥서스 불가침, 둘 다 죽으면 공격 가능, 파괴 시 Finished + 승자, 이후 틱 무시. 실전 한 판도 넥서스로 끝난다."""
    m = Match(seed=1)
    h, nx = m.teams[0]["heroes"][0], m.teams[1]["nexus"]
    assert not m.nexus_attackable(1)
    for t in m.teams[1]["towers"]:
        m.damage(t, 10 ** 6, h)
    assert m.nexus_attackable(1) and m.state == "Playing"
    m.damage(nx, 10 ** 6, h)
    assert m.state == "Finished" and m.winner == 0 and m.run(m.t + 10).t == 0.0   # Finished 후 틱 무시(t=0에서 정지)
    f = Match(seed=11, heroes=((0.9, 0.4), (0.7, 0.4)), overrides={"bounty.activate_sec": 300}).run()
    assert f.winner in (0, 1) and f.t <= 1500 and f.teams[1 - f.winner]["nexus"].hp <= 0, (f.state, f.t)

def test_determinism():
    """같은 시드·설정이면 결과(승자·시각·골드 로그)가 같다."""
    a, b = [Match(seed=42, heroes=((0.9, 0.5), (0.6, 0.3))).run() for _ in range(2)]
    assert (a.winner, a.t, a.log) == (b.winner, b.t, b.log)
TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

def run_tests():
    """모든 테스트 실행, 마지막 줄 `passed k/n`, 종료 코드 = 실패 수."""
    failed = 0
    for fn in TESTS:
        try:
            fn()
            print("ok   ", fn.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL ", fn.__name__, "-", repr(e))
    print("passed %d/%d" % (len(TESTS) - failed, len(TESTS)))
    return failed

def demo(seed=10):
    """시드 고정 1v1 한 판 요약 (현상금 활성 5:00 = 모바일 압축 예시값)."""
    m = Match(seed=seed, heroes=((0.9, 0.4), (0.7, 0.4)), overrides={"bounty.activate_sec": 300}).run()
    print("seed=%d result=%s winner=%s time=%d:%02d waves=%d" % (seed, m.state, m.winner, m.t // 60, m.t % 60, m.wave_no))
    for team in m.teams:
        for h in team["heroes"]:
            print("  %s lv%2d gold_earned=%5d cs=%3d (cs_gold %d / passive %d) K/D=%d/%d items=%s" % (h.name, h.level, h.gold_earned,
                  h.stats["cs"], h.stats["cs_gold"], h.stats["passive_gold"], h.stats["kills"], h.stats["deaths"], ",".join(h.items)))
        print("    towers alive=%s nexus_hp=%d" % ([t.alive for t in team["towers"]], max(0, team["nexus"].hp)))
    print("  bounty paid:", m.bounty_paid or "none", " first tower taken:", m.first_tower_taken, " gold gap(A-B):", m.deficit(1))

if __name__ == "__main__":
    sys.exit(run_tests() if "--test" in sys.argv else demo())
