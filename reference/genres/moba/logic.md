# 롤 계열 / MOBA 기본 베이스 로직

> 엔진 무관. 구현 전에 읽는 설계 뼈대. 숫자는 [README §4](README.md#4-수치-data)에서만. 시뮬레이션으로 검증한 규칙에는 ✅ 표시.
> 확인일 2026-10-17. 대표작·수치·원전은 [README.md](README.md), 공통 시스템은 [`../../systems/core_systems.md`](../../systems/core_systems.md).

## 0. 최소 플레이 가능 단위 (MVP 루프)

**한 판이 성립하는 최소 요소** (도형 그래픽, 1~2일 프로토타입 범위). README §3·§4 기준으로 PC 5v5가 아니라 **모바일 규모(1레인, 1v1 또는 3v3, 10~15분)**를 MVP로 잡는다. HoK가 1레인 3v3·1v1 모드를 실제로 제공하고, MLBB·Wild Rift가 10~18분을 목표로 한다 [README §2·§3].

| 종류 | 요소 |
|---|---|
| 엔티티 | 영웅(팀당 1~3, 이동·평타·레벨·골드) · 미니언 웨이브(근접·원거리·공성) · 타워(팀당 2: 외곽·내부) · 넥서스(팀당 1) · 중립 오브젝트 1개(선택) |
| 규칙 | 웨이브 주기 생성과 레인 행진 · 미니언 교전 · 라스트힛 골드 + 패시브 골드 · 경험치·레벨 · 타워 타겟팅·플레이트 · 킬 골드·셧다운·사망 타이머 · 오브젝트 현상금(컴백) · 상점(기지에서만) · 타워가 모두 죽어야 넥서스 공격 가능 · 넥서스 파괴 = 승리 |
| 화면 | 탑다운 레인 1개, 체력바, 골드·레벨 HUD, 미니맵 없음, 상점 패널 1개, 결과 화면 |

**넣지 않는 것**: 3레인·정글 캠프·와드/시야 · 스킬 4종 체계(평타 1개로 시작) · 영웅 로스터(1종) · 룬/특성 · 매치메이킹·랭크 · 스킨·BM · 리플레이·관전 · 항복 투표 · 채팅/핑. 이것들은 루프가 돌아간 뒤 §6 다이얼로 길이와 스노우볼이 잡힌 다음에 붙인다.

## 1. 게임 흐름 상태 머신

```
Lobby ──(큐 참가)──▶ Matchmaking ──(인원 충족)──▶ Loading(영웅 선택·로드) ──(전원 준비)──▶ Playing ──(넥서스 파괴 | 시간 상한)──▶ Finished ──(결과 확인)──▶ Lobby
  ▲                      │(취소)                       │(로드 실패·이탈)                       │(전원 이탈)
  └──────────────────────┴───────────────────────────┴────────────────────────────────────────┘
```

| 상태 | 전이 조건 | 허용 입력 |
|---|---|---|
| Lobby | 큐 참가 → Matchmaking | 큐 참가, 설정 |
| Matchmaking | 인원 충족 → Loading; 취소 → Lobby | 취소 |
| Loading | 전원 준비 → Playing; 타임아웃 → Lobby | 영웅 선택, 준비 |
| Playing | 넥서스 HP ≤ 0 → Finished(승자 = 상대); `max_minutes` 도달 → Finished(무승부, 예시 규칙) | 이동, 공격 대상 지정, 구매 요청, 귀환, (후반) 항복 |
| Finished | 결과 확인 → Lobby | 결과 확인만 (게임 입력 전부 무시 ✅ `test_nexus_win`) |

`Playing` 내부는 별도 FSM이 아니라 **시간 기반 페이즈**로 다룬다: 웨이브 간격·현상금 활성·사망 타이머가 전부 `t`의 함수라서 상태를 따로 둘 필요가 없다. 영웅 개체는 `Alive ↔ Dead(respawn_at)` 2상태만 가진다.

**변형 1 — 점수제(Pokémon UNITE)**: `Finished` 전이 조건을 "넥서스 파괴"에서 "10분 타이머 만료 → 점수 비교"로 바꾼다. 항복은 후반에만 허용 [README §3]. 넥서스·타워는 골 지점으로 치환.
**변형 2 — 락스텝(HoK)**: 상태 머신은 같지만 `Playing`의 틱이 서버 시뮬이 아니라 "입력 프레임 교환"이 된다. §4 참고.

## 2. 엔티티와 데이터 모델

| 엔티티 | 핵심 필드(타입) | 소유 | 저장 |
|---|---|---|---|
| Match | `t: float`, `state: enum`, `winner: int?`, `wave_no: int`, `next_wave_t: float`, `first_tower_taken: bool`, `rng_seed: int` | 서버 | 결과만(승패·길이·시드) |
| Team | `gold_earned: int`(총 획득, 현상금 기준), `bounty_since: float?`, `heroes[]`, `towers[]`, `nexus` | 서버 | 아니오 |
| Hero | `pos`, `hp/hp_max: int`, `atk: int`, `level: int`, `xp: int`, `gold: int`(잔액), `gold_earned: int`, `streak: int`, `respawn_at: float?`, `items: string[]`, `last_hit_hero_at: float` | 서버(클라는 입력·예측만) | 아니오(전적 집계만) |
| Minion | `team`, `kind: melee/ranged/siege`, `pos`, `hp`, `atk`, `range`, `gold`, `xp` | 서버 | 아니오 |
| Tower | `team`, `kind: outer/inner`, `pos`, `hp`, `atk`, `range`, `plates_left: int`, `plate_hp: float` | 서버 | 아니오 |
| Nexus | `team`, `pos`, `hp` | 서버 | 아니오 |
| Objective(dragon) | `up_at: float`, `hold: (team?, sec)` | 서버 | 아니오 |
| PlayerProfile | `version`, `mmr`, `owned_heroes[]`, `skins[]`, `processedPurchaseIds[]` | 서버 DB | 예 |

**밸런스 Config JSON** — `sim/moba_sim.py`의 `CONFIG`와 같은 값. 출처 표시: **(s)** = README §4 출처값, 그 외는 전부 **예시값**.

```json
{
  "version": 1, "match": {"target_minutes": 15, "sim_tick_sec": 1.0, "max_minutes": 25},
  "lane": {"length": 100, "minion_speed": 1.5, "hero_speed": 3.0},
  "wave": {"first_spawn_sec": 30, "period_sec": [[0, 30], [840, 25], [1800, 20]],
           "melee": 3, "ranged": 3, "siege_every": 3, "growth_per_min": 0.03},
  "minion": {"melee":  {"hp": 100, "atk": 10, "range": 2,  "gold": 20, "xp": 30},
             "ranged": {"hp": 70,  "atk": 12, "range": 8,  "gold": 14, "xp": 30},
             "siege":  {"hp": 220, "atk": 25, "range": 10, "gold": [50, 69, 1800], "xp": 60}},
  "hero": {"base_hp": 500, "hp_per_level": 90, "base_atk": 55, "atk_per_level": 4, "range": 8, "max_level": 15,
           "xp_base": 180, "xp_per_level": 100, "xp_share_range": 15, "regen_per_sec": 2, "max_items": 6},
  "income": {"passive_gold_per_sec": 2.0, "passive_start_sec": 110, "start_gold": 500,
             "kill_gold": 300, "kill_xp": 150, "shutdown_per_streak": 150, "shutdown_cap": 700},
  "tower": {"outer": {"pos": 30, "hp": 2200, "atk": 90,  "range": 9, "plates": 5, "plate_gold": 120},
            "inner": {"pos": 12, "hp": 2000, "atk": 100, "range": 9, "plates": 0, "plate_gold": 0},
            "first_tower_bonus": 300, "team_gold_on_destroy": 150, "aggro_window_sec": 2},
  "nexus": {"pos": 3, "hp": 2500},
  "dragon": {"first_spawn_sec": 150, "respawn_sec": 120, "take_sec": 5, "team_gold": 100, "xp": 150},
  "bounty": {"activate_sec": 840, "min_deficit": 1000, "sustain_sec": 60, "gap_ratio": 0.10, "cap": 1000,
             "base": {"outer": 250, "inner": 400, "dragon": 500, "baron": 300}},
  "death": {"base_sec": 10, "per_level_sec": 2.0, "late_start_sec": 600, "per_minute_sec": 1.0, "cap_sec": 60},
  "items": {"sword": {"cost": 350, "atk": 10}, "vest": {"cost": 400, "hp": 150},
            "blade": {"cost": 1100, "atk": 30}, "plate": {"cost": 1300, "hp": 450}},
  "build": ["sword", "vest", "blade", "plate", "blade", "plate"]
}
```

(s) 출처값: `wave.first_spawn_sec=30`, `wave.period_sec` 30s→14:00부터 25s→30:00부터 20s, `minion.*.gold` 근접 20·원거리 14·공성 ≈50→69, `tower.outer.plates=5`·`plate_gold=120`·`first_tower_bonus=300`, `bounty.activate_sec=840(14:00)`·`gap_ratio=0.10`·`cap=1000`·`base` 외곽 250/내부 400/드래곤 500/바론 300 [README §3·§4, LoL 위키]. 나머지(체력·공격·레벨 곡선·사망 타이머·아이템·드래곤·패시브 골드)는 예시값이며 §6 다이얼로 조정한다.

## 3. 핵심 시스템

### 3.1 웨이브 생성과 레인 행진
- **규칙**: 양 팀 기지에서 같은 구성의 웨이브가 **동시에** 생성되어 상대 기지 방향으로 전진한다. 사거리 안에 적이 들어오면 멈추고 공격한다. 우선순위는 적 미니언 → 타워 → 영웅 → (타워가 모두 죽었을 때만) 넥서스. 간격은 시간 테이블로 줄어든다(출처값 30s → 25s → 20s). 미니언 스탯은 시간에 따라 성장(예시값 +3%/분)해 후반 교착을 깬다.
- **공식**: `period(t) = period_sec 테이블에서 t ≥ start인 마지막 행의 간격`, `growth(t) = 1 + growth_per_min · t/60`, `siege_gold(t) = 50 + (69−50) · min(1, t/1800)` (선형 보간, "≈50→69"는 inferred).
- **의사코드**
```pseudo
function spawnWaveIfDue(match):
    if match.t < match.next_wave_t: return
    match.wave_no += 1
    kinds = [melee]*3 + [ranged]*3 + ([siege] if wave_no % siege_every == 0 else [])
    for team in (A, B):
        for k in kinds: match.minions.add(Minion(team, k, basePos(team), stats[k] * growth(t), gold(k, t)))
    match.next_wave_t += period(match.t)        // 다음 간격은 "지금" 기준 테이블 값

function actMinion(m):
    pool = enemiesInRange(m).minions or towersInRange(m) or enemiesInRange(m).heroes or attackableNexus(m)
    if pool: damage(nearest(pool), m.atk, src=m)
    else:    m.pos = clamp(m.pos + dir(m.team) * minion_speed, 0, lane_length)
```
- **함정**: (1) `next_wave_t += period(t)`를 "이전 간격"으로 누적하면 14:00 경계에서 한 웨이브가 밀린다 — 간격은 생성 시각 기준으로 다시 읽는다. (2) 두 팀 웨이브를 다른 틱에 생성하면 한쪽이 항상 먼저 중앙에 도착해 비대칭이 생긴다. (3) 미니언이 타워를 건너뛰고 넥서스를 치지 않도록 `attackableNexus`는 "그 팀 타워 전멸"을 조건으로 둔다.
- **검증**: ✅ `test_wave_spawn_timing`, ✅ `test_lane_march_and_clash`

### 3.2 라스트힛 골드와 패시브 수입
- **규칙**: 미니언 처치 골드는 **막타(last hit)를 친 영웅에게만** 간다(근접 20·원거리 14·공성 ≈50→69, 출처값). 그 외 영웅은 `passive_start_sec` 이후 초당 패시브 골드(예시값 2/s)만 받는다. 경험치는 막타와 무관하게 `xp_share_range` 안의 아군 영웅 전원에게 간다. 모든 골드 증감은 `addGold(hero, amount, reason)` 하나를 거친다 [core_systems §4].
- **공식**: 10분 기준 능숙한 농부의 CS 골드 > 패시브 골드가 되도록 잡는다(웨이브당 3×20+3×14=102 vs 패시브 30s×2=60). 라스트힛 능력 `cs_skill ∈ [0,1]`은 "막타 기회가 왔을 때 성공할 확률"로 모델링한다.
- **의사코드**
```pseudo
function onMinionKilled(minion, src):
    if src is Hero: addGold(src, minion.gold, "last_hit")          // 골드는 막타만
    for h in heroesOf(enemyOf(minion.team)):                        // 경험치는 근처 전원
        if h.alive and dist(h, minion) <= xp_share_range: gainXp(h, minion.xp)

function tickIncome(match, dt):
    if match.t >= passive_start_sec:
        for h in allHeroes: addGold(h, floor(passive_gold_per_sec * dt), "passive")   // 사망 중에도 지급

function heroFarm(h):                        // 영웅 행동 중 라스트힛 부분
    lh = [m for m in enemyMinionsInRange(h) if m.hp <= h.atk]
    if lh and rng() < h.cs_skill: damage(lowestHp(lh), h.atk, src=h)
    elif enemyMinionsInRange(h): damage(nearest(...), h.atk, src=h)   // 푸시(막타가 아니어도 공격)
```
- **함정**: (1) 패시브를 부동소수점으로 누적하면 팀 간 1골드 차이가 생겨 현상금 활성 판정이 흔들린다 — 정수 골드. (2) 미니언이 미니언을 죽였을 때 "가장 가까운 영웅"에게 골드를 주면 라스트힛 기술이 사라진다. (3) 경험치 공유 범위를 사망한 영웅에게도 적용하면 사망 페널티가 없어진다.
- **검증**: ✅ `test_last_hit_vs_passive_income`

### 3.3 경험치·레벨 곡선과 스탯 성장
- **규칙**: 레벨업마다 체력·공격이 선형 증가하고, 다음 레벨 요구치도 선형 증가한다(예시값). 상한 15. 킬·오브젝트도 경험치를 준다. 레벨업은 한 번의 지급으로 여러 번 일어날 수 있다(루프).
- **공식**: `xp_needed(L) = xp_base + xp_per_level · (L−1)`, `hp_max(L) = base_hp + hp_per_level · (L−1) + Σitems.hp`, `atk(L) = base_atk + atk_per_level · (L−1) + Σitems.atk`. 모바일 MOBA는 "초반 레벨링 생략"으로 `xp_base`를 낮추고 상한을 줄인다 [README §3 MLBB].
- **의사코드**
```pseudo
function gainXp(h, xp):
    h.xp += xp
    while h.level < max_level and h.xp >= xp_needed(h.level):
        h.xp -= xp_needed(h.level); h.level += 1
        h.hp_max += hp_per_level; h.hp += hp_per_level; h.atk += atk_per_level
```
- **함정**: (1) `if` 한 번만 쓰면 큰 경험치(킬+오브젝트)에서 레벨이 하나만 오른다. (2) 레벨업 시 `hp`를 `hp_max`로 채우면 전투 중 레벨업이 사실상 힐이 된다 — 증가분만 더한다. (3) 아이템 스탯을 레벨 공식에 섞어 두면 아이템 판매 시 역산이 틀린다 — 기본+성장과 아이템 합을 분리.
- **검증**: ✅ `test_level_curve_and_item_shop`

### 3.4 타워 타겟팅과 플레이트
- **규칙**: 타워는 사거리 안에서 (1) 최근 `aggro_window_sec` 안에 아군 영웅을 때린 적 영웅 → (2) 가장 가까운 미니언 → (3) 가장 가까운 영웅 순으로 친다. 외곽 타워는 체력을 `plates` 등분한 플레이트를 가지며 구간이 깎일 때마다 공격 팀에 `plate_gold`(5×120=600, 출처값)를 준다. 파괴 시 팀 골드 + 첫 타워 보너스 300(출처값) + 현상금(§3.5). 영웅은 아군 미니언이 타워 사거리 안에 없으면 들어가지 않는다(다이브 금지 휴리스틱).
- **공식**: `plate_hp = hp / plates`, `plates_now = ceil(max(hp,0) / plate_hp)`, 지급 = `(plates_left − plates_now) · plate_gold`.
- **의사코드**
```pseudo
function towerTarget(tower):
    minions, heroes = enemiesInRange(tower)
    aggro = [h for h in heroes if t - h.last_hit_hero_at <= aggro_window_sec]
    pool = aggro or minions or heroes
    return nearest(pool) if pool else null

function onTowerDamaged(tower, amount, src):         // damage() 내부
    tower.hp -= amount
    if tower.plates_left > 0:
        now = ceil(max(tower.hp, 0) / tower.plate_hp)
        if now < tower.plates_left: giveTeamGold(src.team, (tower.plates_left - now) * plate_gold, "plate"); tower.plates_left = now
    if tower.hp <= 0: giveTeamGold(src.team, team_gold_on_destroy + (first_tower_bonus if first) + objectiveBounty(src.team, tower.kind), "tower")
```
- **함정**: (1) 어그로 창을 "마지막 공격 대상"으로만 저장하면 영웅이 미니언을 한 번 치는 순간 풀린다 — 시각(`last_hit_hero_at`)으로 저장. (2) 플레이트를 "피해량 누적 ÷ plate_hp"로 세면 회복·과잉 피해에서 중복 지급. 남은 체력 기준 `ceil`로 센다. (3) 첫 타워 보너스를 팀별로 주면 양쪽이 다 받는다 — 매치 전역 플래그 1개.
- **검증**: ✅ `test_tower_priority`, ✅ `test_tower_plates_and_first_tower_bonus`

### 3.5 스노우볼과 컴백: 오브젝트 현상금·셧다운
- **규칙**: 골드 격차가 `min_deficit` 이상인 상태가 `activate_sec`(출처값 14:00; 모바일은 §6에서 압축) 이후 `sustain_sec`(60초) 동안 유지되면 **뒤진 팀**의 현상금이 활성된다. 활성 중 그 팀이 오브젝트(타워·드래곤)를 가져가면 `기본값 + 격차×10%`를 **상한 1,000**까지 추가로 받는다(출처값). 격차가 해소되면 즉시 비활성. 활성 중에는 뒤진 팀 영웅의 셧다운 골드가 억제된다(README §3, V25.S1.3). 셧다운은 연속킬 2 이상인 영웅을 잡았을 때 가산(예시값 150/킬, 상한 700). 현상금은 앞선 팀이 오브젝트를 먹어도 0이다.
- **공식**: `deficit(team) = gold_earned(other) − gold_earned(team)` (총 획득 기준, 잔액 아님), `bounty = active ? min(base[kind] + gap_ratio · deficit, cap) : 0`, `shutdown = (streak ≥ 2 and not bountyActive(victim.team)) ? min(per_streak · (streak−1), cap) : 0`.
- **의사코드**
```pseudo
function updateBountyState(match):                    // 매 틱
    for team in teams:
        behind = match.t >= activate_sec and deficit(team) >= min_deficit
        team.bounty_since = behind ? (team.bounty_since ?? match.t) : null
function bountyActive(team): return team.bounty_since != null and t - team.bounty_since >= sustain_sec
function objectiveBounty(team, kind):
    if not bountyActive(team): return 0
    return floor(min(base[kind] + gap_ratio * deficit(team), cap))
function shutdownGold(victim):
    if victim.streak < 2 or bountyActive(victim.team): return 0
    return min(shutdown_cap, shutdown_per_streak * (victim.streak - 1))
```
- **함정**: (1) 격차를 "잔액"으로 재면 아이템을 산 팀이 뒤진 것처럼 보인다 — 총 획득(`gold_earned`). (2) 상한 없이 10%만 두면 1만 골드 격차에서 오브젝트 하나가 1,250골드가 되어 역스노우볼이 난다 — `cap` 필수. (3) 현상금을 받는 팀을 "오브젝트를 먹은 팀"이 아니라 "뒤진 팀"으로 고정하지 않으면 앞선 팀이 받아간다.
- **검증**: ✅ `test_objective_bounty_formula_and_cap`, ✅ `test_bounty_limits_snowball`(격차가 있어도 건당 ≤1,000, 뒤진 팀만 수령, 최종 격차가 현상금 없을 때보다 작음), ✅ `test_death_timer_and_shutdown`(셧다운 상한·억제)

### 3.6 아이템 상점과 골드 소비처
- **규칙**: 구매는 **기지에서만**(귀환 또는 부활 직후). 빌드 순서(`build`) 대로 살 수 있는 만큼 산다. 잔액이 모자라면 거부하고 잔액은 절대 음수가 되지 않는다. 아이템 수 상한 6. 아이템은 스탯 합산만(액티브 없음). 골드의 유일한 소비처이므로 라스트힛·킬·오브젝트 수입이 전부 여기로 흘러 "시간당 전투력"이 결정된다.
- **공식**: 귀환 조건(예시 휴리스틱) `gold ≥ cost(next_item) and 사거리 안에 적 영웅 없음`.
- **의사코드**
```pseudo
function shop(hero):                                  // 기지에서 호출
    while next = nextItem(hero):
        if not addGold(hero, -cost(next), "buy:" + next): break      // 단일 진입점이 잔액 검증
        hero.items.add(next); hero.atk += atk(next); hero.hp_max += hp(next); hero.hp += hp(next)
```
- **함정**: (1) 클라이언트가 "아이템 X 샀음"을 통지하는 구조 → 서버가 가격·위치(기지)·잔액을 다시 검증해야 한다(§5). (2) 구매 함수가 `gold -= cost` 를 직접 하면 로그·치트 탐지가 흩어진다 — `addGold` 경유. (3) 부활 시 상점을 호출하지 않으면 사망 중 번 패시브 골드가 쌓이기만 한다.
- **검증**: ✅ `test_level_curve_and_item_shop`

### 3.7 사망 타이머
- **규칙**: 사망 대기는 레벨과 경과 시간에 단조 증가하고 상한이 있다(전부 예시값). 사망 중에도 패시브 골드는 받는다. 부활은 기지에서 풀 체력, 그 직후 상점.
- **공식**: `death_timer(L, t) = min(cap_sec, base_sec + per_level_sec · L + max(0, (t − late_start_sec)/60) · per_minute_sec)`.
- **의사코드**
```pseudo
function onHeroDeath(victim, killer):
    victim.alive = false; victim.respawn_at = t + deathTimer(victim.level, t); victim.deaths += 1
    if killer is Hero: addGold(killer, kill_gold + shutdownGold(victim), "kill"); gainXp(killer, kill_xp); killer.streak += 1
    victim.streak = 0
function tickRespawn(h):
    if not h.alive and t >= h.respawn_at: h.alive = true; h.hp = h.hp_max; h.pos = h.home; shop(h)
```
- **함정**: (1) 타이머를 "남은 초"로 두고 매 틱 빼면 틱 누락 시 어긋난다 — 만료 시각(`respawn_at`) 저장 [genres.md 전투 절]. (2) 후반 가산을 상한 없이 두면 1데스 = 게임 종료가 된다. (3) 타워·미니언에게 죽었을 때 `killer`를 영웅으로 잘못 귀속하면 킬 골드가 공짜로 생긴다.
- **검증**: ✅ `test_death_timer_and_shutdown`

### 3.8 승리 조건: 넥서스
- **규칙**: 넥서스는 그 팀의 타워가 **모두** 파괴된 뒤에만 피해를 받는다. 넥서스 HP ≤ 0 → `Finished`, 승자 = 상대 팀. `Finished` 이후 모든 틱·입력은 무시. 시간 상한 도달 시 무승부(예시 규칙; 점수제 변형은 §1).
- **의사코드**
```pseudo
function nexusAttackable(team): return all(not tw.alive for tw in team.towers)
function damage(target, amount, src):          // 모든 피해의 단일 경로
    if not target.alive: return
    target.hp -= amount; if target.hp > 0: return
    target.alive = false
    switch target.kind: minion → onMinionKilled; hero → onHeroDeath; tower → onTowerDeath; nexus → match.state = Finished; match.winner = other(target.team)
```
- **함정**: (1) 넥서스를 평범한 타워처럼 두면 미니언이 타워를 우회해 끝낸다. (2) 승패 판정 후 같은 틱의 나머지 처리(보상 지급)를 계속하면 결과 집계가 바뀐다 — 판정 즉시 틱 중단. (3) 동시 파괴(같은 틱에 양쪽 넥서스)는 먼저 처리된 쪽이 이긴다 — 틱 내 처리 순서를 결정론적으로 고정(§4).
- **검증**: ✅ `test_nexus_win`(불가침·승자·입력 무시 + 실전 한 판이 넥서스로 종료), ✅ `test_determinism`

## 4. 틱 / 업데이트 순서

권위 측(서버) 한 틱 — `sim/moba_sim.py::Match.step()`과 같은 순서:

1. **입력 수집**: 이번 틱까지 도착한 클라이언트 명령(이동 목표, 공격 대상, 구매, 귀환)을 플레이어별 최신 1개로 정리. 타임스탬프가 틱보다 미래면 버림.
2. **시간 전진** `t += dt`.
3. **부활·수입**: `respawn_at` 만료 영웅 부활 + 상점; `passive_start_sec` 이후 패시브 골드.
4. **웨이브 생성**: `t ≥ next_wave_t`면 양 팀 동시 생성.
5. **현상금 상태 갱신**: 팀별 `bounty_since` (§3.5).
6. **미니언 행동** (생성 순서 고정): 공격 또는 전진.
7. **영웅 행동** (팀 A → B, 슬롯 순): 이동 → 귀환/구매 → 교전 → 라스트힛 → 푸시 → 타워/넥서스.
8. **중립 오브젝트 판정**.
9. **타워 사격** (팀 A → B, 외곽 → 내부).
10. **정리·판정**: 죽은 미니언 제거, 넥서스 파괴면 `Finished`, 시간 상한이면 무승부.
11. **스냅샷 전송**: 엔티티 상태 + 틱 번호. 전적·결과는 `Finished`에서만 DB 저장.

**틱 주기**: 서버 시뮬이면 LoL 서버 33ms(≈30Hz, 출처값 [README §4])가 기준. 시뮬레이션은 계산 편의로 1초 틱(예시값)을 쓰며 규칙 검증 목적이므로 실제 구현은 30Hz로 내리고 `dt`를 곱해야 한다(패시브 골드·이동 거리가 전부 `dt` 비례).

**서버 시뮬 vs 결정론적 락스텝** [README §3]: 위 순서를 서버가 돌리고 스냅샷을 내려보내는 것이 LoL 방식(치트 방어·관전·되감기 유리, 서버비 높음; Riot은 결정론 확보에 다년 전담팀). HoK는 66ms(15fps) 락스텝 — 서버는 입력 프레임만 중계하고 모든 클라이언트가 같은 순서로 위 1~10을 돌린다(직전 3프레임 중복 전송, 부동소수점·로컬 난수 금지, 비동기율 2%→0.03%). 어느 쪽이든 **틱 내 순서와 RNG 시드를 고정**해야 하며(✅ `test_determinism`), 락스텝을 고르면 §5의 "서버가 검증"은 "모든 클라이언트가 같은 결과를 내고 해시를 비교"로 바뀐다. 결정은 프로토타입 전에 한다(README §6 함정).

## 5. 신뢰 경계

| 클라이언트가 보내는 것 | 서버가 검증하는 규칙 | 거부 시 처리 |
|---|---|---|
| 이동 목표 좌표 | 레인 범위 안, 이전 위치에서 `hero_speed·dt` 이내, 살아 있음 | 서버 위치로 되돌림(스냅샷 보정) |
| 공격 대상 id | 대상 존재·적 팀·살아 있음·사거리 안·공격 쿨다운 경과 | 무시 + 횟수 집계 |
| 구매 요청 `buy(item_id)` | 기지 위치, 아이템 존재, 빌드/슬롯 상한, `addGold(-cost)` 성공 | 거부 응답, 잔액 불변 |
| 귀환 요청 | 살아 있음, 채널링 중 피격 시 취소 | 무시 |
| 항복 투표 | 허용 시간 이후, 팀원 1표씩 | 무시 |
| (락스텝) 입력 프레임 | 프레임 번호 연속성, 크기, 레이트 리밋 | 프레임 드롭 + 재전송 요구 |

클라이언트는 골드·경험치·레벨·킬·현상금·사망 타이머·승패를 **절대 보내지 않는다**. 전부 §4의 서버 틱에서 계산되고 `addGold(hero, amount, reason)` 로그로 남는다. 결과 저장은 `Finished` 전이 한 번만(멱등 키 = match id). 공통 원칙은 [`../../systems/core_systems.md` §7](../../systems/core_systems.md), Roblox 구현 예는 [`../../platforms/roblox/patterns/SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau).

## 6. 밸런스 다이얼

| 다이얼 | 무엇을 바꾸나 | 기본값(출처) | 올리면 / 내리면 체감 |
|---|---|---|---|
| `wave.period_sec` | 웨이브 간격 테이블 | 30s → 14:00부터 25s → 30:00부터 20s (README §4 LoL) | 올리면 라인전이 느긋·게임 길어짐 / 내리면 골드 인플레·푸시 빨라짐 |
| `minion.*.gold` | 라스트힛 보상 | 근접 20·원거리 14·공성 50→69 (README §4) | 올리면 CS 숙련도 격차가 더 큰 골드 격차로 / 내리면 킬·오브젝트 비중 상승 |
| `income.passive_gold_per_sec` | 농사 못 해도 받는 수입 | 2.0 (예시값) | 올리면 서포트·초보 보정, CS 가치 하락 / 내리면 라스트힛 필수 |
| `bounty.activate_sec` | 컴백 장치 시작 시각 | 840 = 14:00 (README §4) | 모바일 15분 게임이면 300~420으로 압축해야 한 번이라도 작동(시뮬 데모·테스트는 300) |
| `bounty.gap_ratio` / `bounty.cap` | 현상금 크기·상한 | 10% / 1,000 (README §4) | 상한을 올리면 역스노우볼 위험(§3.5 함정 2) / 비율을 내리면 컴백 체감 없음 |
| `tower.outer.hp`, `tower.*.atk` | 구조물 내구·방어력 | 2200/90, 2000/100 (예시값) | 올리면 교착·25분 무승부 증가 / 내리면 첫 킬이 곧 타워 |
| `wave.growth_per_min` | 후반 미니언 성장 | 0.03 (예시값) | 올리면 후반 가속·교착 해소 / 0이면 대등한 1v1이 시간 상한까지 감 |
| `death.*` | 사망 페널티 | base 10s + 2s/레벨 + 1s/분(10분 후), 상한 60s (예시값) | 올리면 1데스의 무게·스노우볼 / 내리면 난전·무의미한 죽음 |
| `hero.xp_base`, `hero.max_level` | 레벨 곡선 길이 | 180 / 15 (예시값) | 내리면 MLBB식 "초반 레벨링 생략" / 올리면 PC식 성장 체감 |
| `match.target_minutes`, `max_minutes` | 목표·상한 길이 | 15 / 25 (목표 근거: Wild Rift 16~18분, MLBB 10분 [README §4]) | 상한을 내리면 무승부 규칙(점수제 등) 설계가 필요 |

시뮬 관찰(시드 1~15, 1v1): 실력 차가 큰 매치(0.95/0.6 vs 0.3/0.2)는 9~13분에 넥서스로 끝나고, 비슷한 매치(0.9 vs 0.7)는 17~25분에 끝나거나 무승부 — "목표 15분"은 `tower.*.hp`·`growth_per_min`으로 맞춘다.

## 7. 플랫폼 매핑

| 시스템 | Godot | Roblox |
|---|---|---|
| 게임 흐름 FSM (§1) | [`StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd) + [`State.gd`](../../platforms/godot/patterns/State.gd) (Lobby/Loading/Playing/Finished 노드) | [`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau)의 라운드 루프를 Matchmaking→Playing→Finished로 치환 |
| 밸런스 Config (§2) | `MobaConfig` Resource(`.tres`) — [architecture.md §4](../../platforms/godot/architecture.md) Resource 패턴; 런타임 변경은 `duplicate()` | `ReplicatedStorage/Shared/Config/Moba.luau` 테이블 — [architecture.md §4](../../platforms/roblox/architecture.md) |
| 미니언·웨이브 (§3.1) | `Node2D` 대량 생성은 [`ObjectPool.gd`](../../platforms/godot/patterns/ObjectPool.gd)로 재사용; 위치만 시뮬하고 렌더 분리([genres.md 타워 디펜스 절](../../systems/genres.md)) | 서버 `Service`가 좌표 배열로 시뮬, 클라는 `Model` 보간; 수백 마리면 `Part` 대신 좌표만 |
| 골드·상점 (§3.2, §3.6) | [`Economy.gd`](../../platforms/godot/patterns/Economy.gd)의 단일 진입점·1회 지급 상한을 `addGold`로 사용 | [`ShopService.luau`](../../platforms/roblox/patterns/ShopService.luau)(실결제) + 서버 `EconomyService.add(player, amount, reason)` |
| 타워·현상금·사망 (§3.4~3.7) | 순수 GDScript 클래스(노드 아님), 이벤트는 [`EventBus.gd`](../../platforms/godot/patterns/EventBus.gd)(`tower_destroyed`, `hero_died`) | `BindableEvent`로 서버 내부 이벤트, 결과만 `RemoteEvent`로 복제 |
| 신뢰 경계 (§5) | 멀티플레이면 Godot 서버 권위(`multiplayer_authority`)로 §4 틱을 서버에서만; 싱글/봇전은 로컬 권위 | [`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau): 타입→범위→상태 검증·레이트 리밋 |
| 결과·프로필 저장 | [`SaveManager.gd`](../../platforms/godot/patterns/SaveManager.gd)(version·마이그레이션)는 프로필만; 매치 결과는 서버 DB | [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau)(ProfileStore 세션 잠금) |
| 틱 (§4) | `_physics_process` 고정 스텝(기본 60Hz)을 30Hz 누산기로 — [core_systems §1](../../systems/core_systems.md) | `RunService.Heartbeat`의 `dt` 누산, 서버에서만 시뮬 |

Roblox에는 의미 있는 MOBA가 없고(README §2), 10인 매칭 인구 문제(README §6)가 플랫폼과 무관하게 먼저다. 검증된 패턴 목록은 [`../../platforms/godot/patterns/README.md`](../../platforms/godot/patterns/README.md).

## 8. 검증 (sim/)

[`sim/moba_sim.py`](sim/moba_sim.py) (표준 라이브러리만, `random.Random(seed)` 결정론, 1레인 1v1, 1초 틱)가 검사하는 규칙:

| # | 테스트 | 한 줄 |
|---|---|---|
| 1 | `test_wave_spawn_timing` | 첫 웨이브 0:30, 30s 간격, 14:00부터 25s, 30:00부터 20s; 근접3+원거리3, 3웨이브마다 공성 |
| 2 | `test_lane_march_and_clash` | 양 웨이브가 기지에서 출발해 중앙에서 만나 소모, 대칭 결과 |
| 3 | `test_last_hit_vs_passive_income` | 골드 20/14/50→69; 10분 동안 능숙한 농부는 CS 골드 > 패시브, 무능은 패시브만 |
| 4 | `test_level_curve_and_item_shop` | 요구 경험치 증가·상한 15·레벨당 +90/+4; 빌드 순서 구매·잔액 음수 불가·`add_gold` 단일 경로 |
| 5 | `test_tower_priority` | 미니언 우선, 아군 영웅을 때린 적 영웅으로 전환, 2초 뒤 해제 |
| 6 | `test_tower_plates_and_first_tower_bonus` | 플레이트 5×120, 첫 타워 +300, 팀 보상 150 → 합 1050 |
| 7 | `test_objective_bounty_formula_and_cap` | `min(기본+격차×10%, 1000)`, 14:00 전·앞선 팀·60초 미유지면 0, 격차 해소 시 즉시 비활성 |
| 8 | `test_bounty_limits_snowball` | 초반 우위 팀이 있어도 현상금 건당 ≤1000·뒤진 팀만 수령·최종 격차가 현상금 없을 때보다 작음 |
| 9 | `test_death_timer_and_shutdown` | 사망 대기 레벨·시간 단조 증가·상한 60s; 셧다운 연속킬 2부터·상한 700·현상금 활성 중 0 |
| 10 | `test_nexus_win` | 타워 생존 시 넥서스 불가침, 파괴 시 Finished+승자, 이후 틱 무시; 실전 한 판이 넥서스로 종료 |
| 11 | `test_determinism` | 같은 시드 → 같은 승자·시각·골드 로그 |

```bash
cd reference/genres/moba/sim
python3 -I moba_sim.py --test     # 마지막 줄 passed 11/11, 종료 코드 = 실패 수
python3 -I moba_sim.py --demo     # 시드 10, 1v1 한 판 요약 (현상금 활성 5:00으로 압축)
```

실행 결과 (2026-10-17, Python 3.13): **`passed 11/11`**, 종료 코드 0. 데모: 17:32에 A팀 넥서스 승, 드래곤 현상금 688·659골드 2회 지급, 최종 격차 835. 검증하지 않는 것은 [`sim/README.md`](sim/README.md).

## 9. 흔한 구현 버그

1. **14:00 경계에서 웨이브 하나가 밀린다** → `next_wave_t`에 이전 간격을 더함 → 생성 시각 기준으로 `period(t)`를 다시 읽는다(§3.1).
2. **영웅이 라스트힛을 안 해도 골드가 들어온다** → 미니언이 죽인 미니언 골드를 "가장 가까운 영웅"에 귀속 → 골드는 `src is Hero`일 때만, 경험치만 범위 공유(§3.2).
3. **컴백 현상금이 켜졌는데 뒤진 팀이 더 벌어진다** → 현상금을 "오브젝트를 먹은 팀"에 지급 / 격차를 잔액으로 측정 → 뒤진 팀 고정, `gold_earned` 기준, 상한 1,000(§3.5).
4. **현상금 한 번에 승부가 뒤집힌다** → `cap` 누락 또는 비율을 격차 전체에 곱함 → `min(base + 10%·gap, 1000)`; ✅ `test_bounty_limits_snowball`로 회귀 방지.
5. **타워가 미니언을 두고 영웅만 쏜다** → 어그로를 "마지막 대상"으로 저장해 풀리지 않음 → `last_hit_hero_at` 시각 + 2초 창(§3.4).
6. **플레이트 골드가 두 번 지급된다** → 누적 피해량으로 플레이트 계산 → 남은 체력 기준 `ceil`(§3.4).
7. **잔액이 음수가 된다** → 구매 코드가 `gold -= cost`를 직접 수행 → `addGold`가 거부하면 구매 취소(§3.6, core_systems §4).
8. **부활 시각이 클라이언트마다 다르다** → "남은 초"를 매 프레임 감산 → 서버의 `respawn_at` 만료 시각 하나를 복제(§3.7).
9. **같은 시드인데 결과가 다르다** → 엔티티를 `set`/dict 순회로 처리하거나 `Finished` 뒤에도 틱 진행 → 리스트 순서 고정, 판정 즉시 중단(§4, ✅ `test_determinism`).
