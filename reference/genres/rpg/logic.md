# RPG · 방치형 기본 베이스 로직

> 엔진 무관. 구현 전에 읽는 설계 뼈대. 숫자는 README §4에서만. 시뮬레이션으로 검증한 규칙에는 ✅ 표시.
> 확인일 2026-10-17. 대표작·수치·원전은 [`README.md`](README.md), 공통 시스템은 [`../../systems/core_systems.md`](../../systems/core_systems.md)·[`../../systems/genres.md`](../../systems/genres.md). 이 문서는 그것을 "구현 뼈대"로 옮긴 것이다.

## 0. 최소 플레이 가능 단위 (MVP 루프)

**MVP = 자동 전투 방치형 RPG.** 도형 그래픽으로 1~2일 안에 만드는 범위.

| 요소 | 최소 내용 |
|---|---|
| 엔티티 | 영웅 1명(공격력·레벨), 적 1종(체력·방어, 스테이지마다 지수 증가), 코인 1종 |
| 규칙 | 영웅이 1초마다 자동 공격 → 적 5마리 처치 = 스테이지 클리어 → 코인 → 공격력 업그레이드(지수 비용) → 제한 시간 안에 못 잡으면 "벽" → 환생(리셋 + 영구 배율) |
| 화면 | 전투 화면 1개(영웅 원 · 적 사각형 · 체력 바), 업그레이드 버튼 1개, 환생 버튼 1개, 오프라인 보상 팝업 1개 |
| 저장 | `version, coins, upgrade_level, stage, prestige_points, last_seen_unix, pity5, pity4, guaranteed` |

**변형 (서바이버류)** 한 판 30분: 플레이어 1명 자동 공격, 적이 매분 더 많이 스폰, 처치 시 XP 젬, 레벨업마다 3택1, 30분 도달 시 리퍼(사망) = "성공". 메타 진행 없이 런 1개만으로 MVP가 성립한다.

**넣지 않는 것:** 장비·돌파·합성 3단 깊이, 스킬 쿨다운, 길드·PvP, 스토리, 배틀패스·광고, 큰 수 표기(1e30), 진화(최대 레벨 무기+패시브), 웨이브 사이 상점, 메타 언락. 전부 루프가 돌아간 뒤에 추가한다.

## 1. 게임 흐름 상태 머신

구현은 [`../../systems/core_systems.md`](../../systems/core_systems.md) §2 FSM, Godot은 [`../../platforms/godot/patterns/StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd).

**공통 뼈대 (방치형)**

```
Boot ──load save──▶ OfflineReward ──claim/skip──▶ Lobby ◀──────────────┐
                                                   │ start               │
                                                   ▼                     │
                                                Battling ──wall──▶ Walled ──rebirth──▶ Lobby
                                                   │ ▲                   │
                                      stage clear  │ │ upgrade           │ keep grinding
                                                   ▼ │                   ▼
                                                 Reward ──────────────▶ Battling
Lobby ──summon──▶ Gacha ──result──▶ Lobby
Any ──background──▶ Saving ──done──▶ (이전 상태)
```

| 상태 | 전이 조건 | 허용 입력 |
|---|---|---|
| Boot | 세이브 로드·마이그레이션 완료 | 없음 |
| OfflineReward | `calc_offline() > 0`이면 팝업, 아니면 즉시 Lobby | 받기(광고 2배는 MVP 제외) |
| Lobby | — | 전투 시작, 업그레이드, 소환, 환생 |
| Battling | 적 처치 누적 = `enemy_count` → Reward; 제한 시간 초과 → Walled | 업그레이드(전투 중 허용), 일시정지 |
| Reward | 코인 지급·저장 → Battling(다음 스테이지) | 없음(자동) |
| Walled | 같은 스테이지 재시도 반복(수입은 계속 들어옴) | 업그레이드, 환생 |
| Gacha | 재화 차감 → 서버 판정 → 결과 연출 | 1회/10회, 결과 스킵 |
| Saving | 백그라운드 진입·주기 저장 | 없음 |

**변형 1 (서바이버류)**: `Lobby → Running → (LevelUp ⇄ Running) → Ended(사망 | 30분 리퍼) → Lobby`. `LevelUp`은 시간이 멈추고 3택 외 입력을 받지 않는다. 변형 2 (가차 RPG 허브): `Lobby`가 허브이고 `Battling`이 스태미나를 소비하는 스테이지 선택으로 바뀐다 (§3.6).

## 2. 엔티티와 데이터 모델

| 엔티티 | 핵심 필드 (타입) | 소유 | 저장 |
|---|---|---|---|
| PlayerSave | `version:int, coins:int, lifetime_coins:int, upgrade_level:int, stage:int, prestige_points:int, last_seen_unix:int, stamina:int, stamina_ts:int, pity5:int, pity4:int, guaranteed:bool, processed_receipts:[str]` | 서버(온라인) / 클라이언트(오프라인 싱글) | O |
| Hero | `atk:float` (파생: `base_atk + atk_per_level×level`)×환생 배율, `attack_interval_s:float` | 권위 측에서 파생 계산 | X (파생) |
| Enemy | `stage:int, hp:int, def:int` (스테이지에서 파생) | 권위 측 | X |
| StageState | `stage:int, kills:int, elapsed_s:float` | 권위 측 | 부분(stage만) |
| GachaBanner | `rates:{rarity:float}, hard_pity_5:int, hard_pity_4:int, featured_rate:float, pool:[id]` | 서버 Config | Config |
| SurvivorRun | `t:int, hp:float, level:int, xp:int, levels:{upgrade:int}, alive:int, ended:enum` | 클라이언트(싱글) | X (런 종료 시 결과만) |
| Config | 아래 JSON | 서버 (Remote Config 가능) | Config |

**밸런스 Config 예시** (`sim/rpg_sim.py`의 `CONFIG`와 같은 값. `growth`는 AdCap 레모네이드 [4], `gacha`는 원신 [1][2], `stamina`는 원신 레진 [45], `survivor.run_seconds`는 VS [8]. 나머지는 **예시값**):

```json
{
  "version": 1,
  "growth": {"base_cost": 4.0, "rate": 1.07, "base_output": 1.67, "milestones": [25, 50], "milestone_mult": 2.0},
  "hero": {"base_atk": 10, "atk_per_level": 2, "attack_interval_s": 1.0, "crit_chance": 0.05, "crit_mult": 2.0},
  "damage": {"def_k": 100, "rand_min": 0.95, "rand_max": 1.05, "min_damage": 1},
  "stage": {"enemy_hp_base": 20, "enemy_hp_rate": 1.12, "enemy_def_per_stage": 3, "enemy_count": 5, "reward_base": 3, "clear_timeout_s": 60},
  "prestige": {"divisor": 100.0, "per_point": 0.1},
  "offline": {"max_hours": 8.0, "efficiency": 1.0},
  "gacha": {"rates": {"5": 0.006, "4": 0.051, "3": 0.943}, "hard_pity_5": 90, "hard_pity_4": 10, "featured_rate": 0.5},
  "stamina": {"cap": 200, "sec_per_point": 480},
  "survivor": {
    "run_seconds": 1800, "spawn_per_min_base": 10, "spawn_per_min_step": 6, "spawn_per_min_cap": 120,
    "enemy_hp_base": 5, "enemy_hp_per_min": 1, "enemy_dps": 0.003, "player_hp": 100, "player_dps": 15,
    "dps_per_weapon_lv": 0.25, "dps_per_spinach_lv": 0.1, "armor_cut": 0.1,
    "xp_base": 3, "xp_exp": 1.5, "choices": 3, "max_level": 8,
    "weapons": ["whip", "wand", "garlic", "axe"],
    "upgrade_pool": ["whip", "wand", "garlic", "axe", "spinach", "armor"]
  }
}
```

## 3. 핵심 시스템

### 3.1 성장 곡선 — 지수 비용 vs 선형 산출
- **규칙**: 업그레이드 비용은 보유 수에 지수로, 산출(공격력·초당 코인)은 보유 수에 선형으로 늘린다. 비용/산출 비가 계속 커지므로 반드시 "벽"이 생기고, 벽은 마일스톤 배율·환생·가차로만 넘는다 (The Math of Idle Games I [4]).
- **공식**: `cost(n) = b · r^n` (b 기본비용, r 성장률, n 보유 수). k개 일괄 구매 `bulk(n,k) = b · r^n · (r^k − 1)/(r − 1)`. 산출 `out(n) = o · n · m^(통과한 마일스톤 수)`. 다음 n레벨까지 걸리는 시간 `t = bulk(n, k) / income`. 비용/산출 비 `r^n / n`은 `n ≥ 1/ln r` (r=1.07이면 ≈15)부터 단조 증가한다.
- **의사코드**:
```pseudo
function upgradeCost(n, cfg): return cfg.base_cost * cfg.rate ^ n
function bulkCost(n, k, cfg): return cfg.base_cost * cfg.rate^n * (cfg.rate^k - 1) / (cfg.rate - 1)
function outputPerSec(n, cfg):
    mult = cfg.milestone_mult ^ count(m in cfg.milestones where n >= m)
    return cfg.base_output * n * mult
function timeToLevel(nFrom, nTo, incomePerSec, cfg):
    if incomePerSec <= 0: return INF
    return bulkCost(nFrom, nTo - nFrom, cfg) / incomePerSec
function tryBuy(save, k):                       // 서버
    cost = bulkCost(save.upgrade_level, k)
    if not Economy.spend(save, "coins", ceil(cost), "upgrade"): return false
    save.upgrade_level += k; return true
```
- **함정**: (1) 산출도 지수로 두면 벽이 사라진다 (README §6 첫 항목). (2) 비용을 `float`로 누적하면 오차가 쌓인다. 정수로 올림해서 차감하고 큰 수는 `mantissa×10^exp`로 ([`core_systems.md`](../../systems/core_systems.md) §4). (3) "최대 구매" 버튼은 역산(`k = floor(log_r(coins·(r−1)/(b·r^n) + 1))`)으로 하고 루프를 돌리지 않는다.
- **검증** ✅ `test_cost_exponential`, `test_output_linear_vs_cost`, `test_time_to_wall`

### 3.2 데미지 공식 — 비율형 방어
- **규칙**: `방어`는 데미지를 빼는 감산형이 아니라 비율로 줄이는 형태로 둔다. 어떤 방어에서도 데미지가 0이나 음수가 되지 않고, 최소 데미지 1을 보장한다 ([`genres.md`](../../systems/genres.md) 전투/RPG).
- **공식**: `dmg = max(min_dmg, round(atk × skillMul × k/(k + def) × critMul × rand(0.95, 1.05)))`. `def = k`일 때 정확히 절반.
- **의사코드**:
```pseudo
function damage(atk, def, skillMul, isCrit, rng, cfg):
    mitig = cfg.def_k / (cfg.def_k + max(0, def))
    raw = atk * skillMul * mitig * (isCrit ? cfg.crit_mult : 1.0)
    raw *= rng.uniform(cfg.rand_min, cfg.rand_max)
    return max(cfg.min_damage, round(raw))
```
- **함정**: (1) `def`에 음수 디버프를 넣으면 `k/(k+def)`가 1을 넘거나 분모가 0이 된다. `max(0, def)`로 막는다. (2) 반올림 전에 최소 데미지를 적용하면 0.4 → 0이 된다. 반올림 후 `max`. (3) 치명타 판정을 클라이언트에서 하면 치명 100% 조작이 가능하다. 판정 RNG는 권위 측.
- **검증** ✅ `test_damage_never_zero`, `test_damage_ratio_defense`

### 3.3 스테이지 · 벽 감지 · 환생(프레스티지)
- **규칙**: 적 체력은 스테이지에 지수(`enemy_hp_rate`), 방어는 선형으로 오른다. 공격력은 선형이므로 어느 스테이지에서 `clear_timeout_s` 안에 못 잡는 "벽"이 반드시 온다. 환생은 코인·업그레이드·스테이지를 리셋하고 누적 코인에 비례한 포인트를 **영구**로 쌓는다. 배율은 포인트에 선형이라 환생마다 조금씩 더 멀리 간다 [4].
- **공식**: `enemyHp(s) = hp0 · r_e^s`, `enemyDef(s) = d · s`. 벽: `clearTime(s) > timeout`. `points = floor(sqrt(lifetime_coins / divisor))` (예시값, AdCap 엔젤식과 같은 제곱근 형태 [4]), `mult = 1 + per_point × Σpoints`.
- **의사코드**:
```pseudo
function stageClearTime(heroAtk, stage, rng, cfg):     // 기대값 근사
    hp = floor(cfg.enemy_hp_base * cfg.enemy_hp_rate ^ stage)
    def = cfg.enemy_def_per_stage * stage
    t = 0
    repeat cfg.enemy_count times:
        remaining = hp
        while remaining > 0:
            remaining -= damage(heroAtk, def, 1.0, rng.random() < crit_chance, rng)
            t += cfg.attack_interval_s
    return t
function isWall(heroAtk, stage): return stageClearTime(...) > cfg.clear_timeout_s
function rebirth(save):                                 // 서버
    gained = floor(sqrt(save.lifetime_coins / cfg.divisor))
    if gained <= 0: return REJECT("too_early")
    save.prestige_points += gained                      // 영구, 리셋 대상 아님
    save.coins = 0; save.upgrade_level = 0; save.stage = 1; save.lifetime_coins = 0
    log("rebirth", gained)
function heroAtk(save): return (base_atk + atk_per_level * save.upgrade_level) * (1 + per_point * save.prestige_points)
```
- **함정**: (1) `lifetime_coins`를 환생 때 안 지우면 다음 환생 포인트가 이중 계산된다. (2) 배율이 너무 크면 1회 환생 후 이전 스테이지가 무의미, 너무 작으면 리셋 손실만 느껴진다 (README §6). 시뮬로 "환생마다 벽이 몇 스테이지 멀어지나"를 본 뒤 `per_point`를 정한다. (3) 벽을 "사망"으로 처리하면 방치 중 수입이 끊긴다. 벽에서는 같은 스테이지를 반복하며 수입이 계속 들어와야 한다.
- **검증** ✅ `test_stage_wall_detection`, `test_prestige_compound`

### 3.4 오프라인 수익
- **규칙**: 접속하면 `(now − last_seen) × 초당 수입 × 효율`을 주되 `max_hours`로 자른다. 상한은 "돌아올 이유"지 벌이 아니다 (README §6). 기기 시간은 믿지 않는다: 온라인이면 서버 시간, 오프라인 싱글이면 `now ≤ last_seen`(시간 역행)을 0으로 처리한다 ([`genres.md`](../../systems/genres.md) 방치형, [`Economy.gd`](../../platforms/godot/patterns/Economy.gd) `calc_offline_reward`).
- **공식**: `reward = min(now − last, max_hours×3600) × perSec × efficiency` (단, `last ≤ 0 or now ≤ last`이면 0).
- **의사코드**:
```pseudo
function calcOffline(lastSeenUnix, nowUnix, perSec, cfg):
    if lastSeenUnix <= 0 or nowUnix <= lastSeenUnix: return 0   // 첫 실행·시간 역행
    elapsed = min(nowUnix - lastSeenUnix, cfg.max_hours * 3600)
    return floor(elapsed * perSec * cfg.efficiency)
function onLogin(save, serverNow):
    reward = calcOffline(save.last_seen_unix, serverNow, outputPerSec(save) * mult(save))
    save.last_seen_unix = serverNow        // 지급 여부와 무관하게 갱신 (중복 지급 방지)
    if reward > 0: Economy.add(save, "coins", reward, "offline")
```
- **함정**: (1) `last_seen`을 지급 **전**에 갱신하면 앱 재시작마다 다시 받는다 — 계산 후 갱신하되 같은 트랜잭션에서. (2) 오프라인 수입의 `perSec`을 클라이언트가 보내게 두면 조작된다. 서버가 세이브에서 파생 계산. (3) 상한 8시간은 **예시값** — 게임별로 다르다 (예: AFK Arena 12시간 [https://afk-arena.fandom.com/wiki/AFK_Arena_-_A_beginner's_guide_to_managing_resources, https://www.afk.global/tips — 위키/팬 가이드, 2차 출처]; Egg, Inc.는 사일로 업그레이드로 방치 시간 상한이 늘어남 [https://egg-inc.fandom.com/wiki/Grain_Silos — 위키, 2차 출처]; 공식 출처 확인 및 확인일 기재 미검증).
- **검증** ✅ `test_offline_cap`, `test_offline_negative_rejected`

### 3.5 가차 — 확률 + 하드 천장 + 50/50
- **규칙**: 등급별 기본 확률로 뽑되, 5★ 카운터가 `hard_pity_5`(90)에 닿으면 5★ 강제, 4★ 카운터가 10에 닿으면 4★ 강제. 5★가 나오면 픽업 여부를 `featured_rate`(50%)로 정하고, 실패했으면 다음 5★는 픽업 확정 → 최악 180뽑 (원신 [1][2]). 천장 카운터와 확정 플래그는 세이브에 저장하고 배너 간 공유 여부를 명시한다. **공개 확률표는 실제 뽑기와 같은 데이터에서 생성**한다 — 한국은 2024-03-22부터 확률 표시가 법적 의무이고 거짓 표시는 형사처벌 대상 [43][44]. 유료 뽑기는 서버에서 판정한다 ([`Gacha.gd`](../../platforms/godot/patterns/Gacha.gd), [`core_systems.md`](../../systems/core_systems.md) §3).
- **공식**: 하드 천장만 있을 때 5★ 평균 간격 `E[gap] = (1 − (1−p)^N) / p` (p=0.006, N=90 → ≈69.7뽑), 전체 5★ 비율 `1/E[gap] ≈ 1.43%`. 픽업 비율은 50/50 규칙으로 `2/3`.
- **의사코드**:
```pseudo
function pull(save, banner, rng):                       // 서버
    save.pity5 += 1; save.pity4 += 1; forced = false
    if save.pity5 >= banner.hard_pity_5: rarity = "5"; forced = true
    elif save.pity4 >= banner.hard_pity_4: rarity = "4"; forced = true
    else: rarity = weightedPick(banner.rates, rng)
    featured = false
    if rarity == "5":
        save.pity5 = 0; save.pity4 = 0
        featured = save.guaranteed or rng.random() < banner.featured_rate
        save.guaranteed = not featured
    elif rarity == "4": save.pity4 = 0
    item = pickFromPool(banner.pool[rarity], featured, rng)
    return {rarity, item, featured, forced}
function probabilityTable(banner): return {r: rate*100 for r, rate in banner.rates}   // 공개용, 같은 데이터
```
- **함정**: (1) 천장 카운터를 메모리에만 두면 앱 재시작으로 초기화된다 — 세이브 필드. (2) 10연차를 10번의 `pull`로 돌리지 않고 "10연 중 4★ 1개 보장"을 따로 구현하면 4★ 천장 카운터와 어긋난다. 10연차 = `pull`×10. (3) 공개 확률표를 손으로 적으면 코드와 불일치 → 규제 리스크. 함수로 생성.
- **검증** ✅ `test_gacha_hard_pity`, `test_gacha_empirical_rate`, `test_gacha_fifty_fifty`, `test_probability_table_sums`

### 3.6 스태미나 · 세션 게이팅
- **규칙**: 스테이지 입장마다 스태미나를 소비하고 `sec_per_point`(원신 레진 8분당 1 [45])마다 1 회복, 상한 `cap`(200 [45]). 일일 세션을 15~30분으로 자르고 "내일 또"를 만든다. 방치형은 스태미나 대신 오프라인 상한(§3.4)으로 같은 역할을 한다 (README §3). 회복 시각은 마지막 회복 시각 + 잔여초를 보존해 틱 간격과 무관하게 정확히 회복한다.
- **공식**: `gained = floor((now − last) / sec_per_point)`, `stamina = min(cap, stamina + gained)`, `last = now − ((now − last) mod sec_per_point)`.
- **의사코드**:
```pseudo
function regenStamina(save, nowUnix, cfg):              // 서버, 입장 요청 직전에 호출
    if nowUnix <= save.stamina_ts or save.stamina >= cfg.cap: return
    gained, rem = divmod(nowUnix - save.stamina_ts, cfg.sec_per_point)
    save.stamina = min(cfg.cap, save.stamina + gained)
    save.stamina_ts = nowUnix - rem
function enterStage(save, cost, nowUnix):
    regenStamina(save, nowUnix)
    if save.stamina < cost: return REJECT("no_stamina")
    save.stamina -= cost
```
- **함정**: (1) 상한에 있는 동안 `stamina_ts`를 갱신하지 않으면 상한에서 1 쓰는 순간 몇 시간치가 한 번에 회복된다. 상한 도달 시 `stamina_ts = now`로 맞춘다. (2) 회복을 "매 틱 −1초"로 세면 백그라운드에서 멈춘다. 타임스탬프 방식.
- **검증** ✅ `test_stamina_regen`

### 3.7 서바이버류 런 — 밀도 곡선 · XP 곡선 · 3택1 · 30분 종료
- **규칙**: 매분 스폰 수가 단조 증가(상한 있음)하고 적 체력도 분마다 오른다. 처치마다 XP 젬, 필요 XP는 다항 곡선. 레벨업마다 풀에서 **서로 다른** 후보 3개를 뽑되 최대 레벨(8) 항목은 제외하고, 후보가 부족하면 있는 만큼만 보여 준다. 1800초 도달 시 리퍼가 등장해 런을 끝낸다 = "성공" (VS 30분 [8][10]). 그 전 사망은 "거의 다 왔다"가 되게 밀도·체력 곡선을 맞춘다 ([`../strategy/defense_management_survivors.md`](../strategy/defense_management_survivors.md) snake_survivor 절).
- **공식**: `spawn(m) = min(cap, base + step·m)`, `xpToNext(L) = xp_base · L^xp_exp` (다항, [`core_systems.md`](../../systems/core_systems.md) §5), `dps = player_dps · (1 + 0.25·무기레벨합) · (1 + 0.1·spinach)`, 접촉 피해 `alive · enemy_dps · max(0.2, 1 − 0.1·armor)`.
- **의사코드**:
```pseudo
function drawChoices(levels, pool, rng, cfg):
    candidates = [u for u in pool if levels[u] < cfg.max_level]
    return rng.sampleWithoutReplacement(candidates, min(cfg.choices, len(candidates)))
function tick(run, cfg):                                 // 1초
    if run.t >= cfg.run_seconds: run.ended = REAPER; return
    if run.t % 60 == 0: run.alive += spawnPerMin(run.t / 60)
    killed = min(run.alive, stochasticRound(dps(run) / enemyHp(run.t / 60), rng))
    run.alive -= killed; run.xp += killed
    while run.xp >= xpToNext(run.level):
        run.xp -= xpToNext(run.level); run.level += 1
        choices = drawChoices(run.levels, cfg.upgrade_pool, rng, cfg)
        if choices: apply(run, playerPick(choices))      // 시간 정지 상태에서 선택
    run.hp -= run.alive * cfg.enemy_dps * armorFactor(run)
    if run.hp <= 0: run.ended = DEAD; return
    run.t += 1
```
- **함정**: (1) 3택을 `random.choice` 3번으로 뽑으면 중복이 난다. 비복원 추출. (2) 만렙 항목을 후보에서 안 빼면 "선택이 선택이 아닌" 빈 칸이 된다 (README §6). (3) 레벨업 중 시간을 멈추지 않으면 적이 겹쳐 즉사. FSM `LevelUp` 상태에서 틱 정지. (4) 리퍼를 "매우 강한 적"으로 두면 빌드에 따라 잡히는 버그 — 리퍼는 무적 플래그.
- **검증** ✅ `test_survivor_three_choice`, `test_survivor_run_ends_30min`, `test_survivor_wave_density`, `test_survivor_xp_curve`

## 4. 틱 / 업데이트 순서

권위 측 한 틱 (방치형, 틱 주기 **1초 = `attack_interval_s`**, 예시값. 서바이버류는 클라이언트 싱글이므로 고정 스텝 1/60초에 로직, 1초 단위 집계 — [`core_systems.md`](../../systems/core_systems.md) §1):

1. **입력 수집**: 큐에서 클라이언트 요청(업그레이드 k개, 소환, 환생, 스테이지 입장)을 꺼내 §5 규칙으로 검증. 거부는 즉시 응답.
2. **시간 보정**: `serverNow` 확정. 오프라인 보상·스태미나 회복은 로그인 틱에서만 (§3.4, §3.6).
3. **시뮬**: 영웅 공격 1회 → `damage()` → 적 체력 차감 → 처치 시 `kills += 1`, 다음 적 생성.
4. **판정**: `kills == enemy_count` → 스테이지 클리어; `elapsed > clear_timeout_s` → 벽(스테이지 유지, `elapsed = 0`).
5. **보상**: 클리어면 `Economy.add(coins, reward_base × stage × mult, "stage_clear")`, `lifetime_coins` 갱신, `stage += 1`.
6. **요청 적용**: 검증된 업그레이드·환생·소환을 재화 차감과 **같은 트랜잭션**으로 적용.
7. **이벤트 발행**: `StageCleared`, `Walled`, `ItemAcquired` — 퀘스트·업적·분석이 구독 ([`EventBus.gd`](../../platforms/godot/patterns/EventBus.gd)).
8. **저장/스냅샷**: 더티 플래그가 서 있으면 저장 (주기 30~60초, 백그라운드 진입 시 즉시). 클라이언트에는 파생값(공격력·확률표·남은 스태미나)을 포함한 스냅샷 전송.

## 5. 신뢰 경계

재화·점수·확률·보상은 반드시 서버 ([`core_systems.md`](../../systems/core_systems.md) §7, Roblox [`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau)). 오프라인 싱글 앱은 클라이언트가 권위이되, 랭킹·결제와 엮이는 값은 같은 규칙으로 서버 재검증.

| 클라이언트가 보내는 것 | 서버가 검증하는 규칙 | 거부 시 처리 |
|---|---|---|
| `upgrade(k)` | `k ∈ [1, 100]` 정수, `bulkCost ≤ coins`, 레이트 리밋 | 무시 + 현재 잔액 재전송 |
| `summon(banner, count)` | `count ∈ {1, 10}`, 배너 활성 기간, 재화 충분, 천장 상태는 서버 세이브의 것만 사용 | 거부, 연속 거부 시 로그 |
| `rebirth()` | `prestige_points 획득량 ≥ 1`, 전투 중 아님 | 거부("too_early") |
| `enterStage(stage)` | `stage ≤ save.stage` (스킵 금지), 스태미나 충분(서버 시각으로 회복 후) | 거부 |
| `claimOffline()` | 서버가 `serverNow`와 `last_seen_unix`로 계산. 클라이언트가 보낸 시간·수입은 무시 | 0 지급, `last_seen` 갱신 |
| `stageResult(kills, time)` (클라 시뮬 시) | 이론상 최소 클리어 시간(`stageClearTime`의 치명타 100% 하한) 이상인지, 요청 간격이 그 시간 이상인지 | 결과 폐기 + 재시뮬 |
| `survivorResult(survived_s, level)` | `survived_s ≤ 1800`, `level ≤ 처치 XP로 가능한 상한`, 시드·픽 로그 동봉 시 재실행 | 랭킹 미반영 |
| `purchase(receipt)` | 영수증 ID 멱등, 스토어 검증 | 중복이면 무지급·성공 응답 ([`ShopService.luau`](../../platforms/roblox/patterns/ShopService.luau)) |

## 6. 밸런스 다이얼

| 다이얼 | 무엇을 바꾸나 | 기본값 (출처) | 올리면 / 내리면 체감 |
|---|---|---|---|
| `growth.rate` | 업그레이드 비용 지수 | 1.07 (AdCap [4]) | 올리면 벽이 빨리 와 환생 빈도↑ / 내리면 단조롭고 숫자만 커짐 |
| `growth.milestones` | 산출 2배 지점 | 25, 50 (AdCap [4]) | 촘촘하면 "다음 마일스톤까지" 목표가 잦음 / 드물면 벽이 길어짐 |
| `stage.enemy_hp_rate` | 적 체력 지수 | 1.12 (예시값) | 올리면 벽이 가까워지고 환생 압력↑ / 내리면 업그레이드만으로 진행 |
| `stage.clear_timeout_s` | 벽 판정 시간 | 60 (예시값) | 올리면 벽이 늦게 체감 / 내리면 벽이 명확 |
| `prestige.per_point` | 환생 배율 기울기 | 0.1 (예시값) | 올리면 환생 후 이전 구간 무의미 / 내리면 리셋 손실만 느껴짐 (README §6) |
| `offline.max_hours` | 오프라인 수입 상한 | 8 (예시값; 실제 사례: Melvor Idle 24h [https://wiki.melvoridle.com/w/Offline_Progression], AFK 아레나 12h(신규 기준, 팬 가이드) [https://www.afk.global/afk-arena/guides/tips]) | 올리면 접속 동기↓ / 내리면 "벌"로 느껴짐 |
| `gacha.rates.5` · `hard_pity_5` | 5★ 확률·천장 | 0.6% · 90 (원신 [1]) | 확률↑ 천장↓면 매출↓ 만족↑ / 천장 없음은 규제·이탈 리스크 |
| `gacha.featured_rate` | 픽업 당첨률 | 0.5 (원신 [1]) | 올리면 최악 케이스 완화 / 내리면 180뽑 체감 빈번 |
| `stamina.cap` · `sec_per_point` | 세션 길이 | 200 · 480초 (원신 [45]) | 상한↑이면 몰아치기 허용 / 회복 빠르면 세션 분할 효과↓ |
| `survivor.spawn_per_min_step` · `enemy_hp_per_min` | 런 밀도·체력 곡선 | 6 · 1 (예시값) | 올리면 사망 시점이 앞당겨져 근접 실패가 사라짐 / 내리면 30분이 쉬워 긴장↓ |

## 7. 플랫폼 매핑

| 시스템 | Godot | Roblox |
|---|---|---|
| Config (§2) | `Resource` 서브클래스 `.tres` ([`architecture.md`](../../platforms/godot/architecture.md) §4; 런타임 변경 시 `duplicate()`) + 원격 JSON | `ReplicatedStorage.Shared.Config` 모듈 ([`architecture.md`](../../platforms/roblox/architecture.md) §4) |
| 재화·오프라인 (§3.1, §3.4) | [`Economy.gd`](../../platforms/godot/patterns/Economy.gd) `add/spend/calc_offline_reward` | `ServerScriptService` 서비스 + [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau) (ProfileStore 세션 잠금), 서버 시각 `os.time()` |
| 저장 (§2) | [`SaveManager.gd`](../../platforms/godot/patterns/SaveManager.gd) (버전·마이그레이션·원자적 저장, JSON — `.tres` 세이브 금지) | [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau) `Reconcile()` |
| 가차 (§3.5) | [`Gacha.gd`](../../platforms/godot/patterns/Gacha.gd) (가중치·천장·확률표 생성·시드) — 유료면 서버 | 서버 모듈로 같은 로직, 클라이언트는 결과만 수신 ([`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau)) |
| 결제·게임패스 | 스토어 플러그인 + 영수증 멱등 (`processed_receipts`) | [`ShopService.luau`](../../platforms/roblox/patterns/ShopService.luau) (`ProcessReceipt` 한 곳) |
| 흐름 FSM (§1) | [`StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd) + [`State.gd`](../../platforms/godot/patterns/State.gd) | [`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau) 구조 (라운드제 변형 시) |
| 이벤트 (§4-7) | [`EventBus.gd`](../../platforms/godot/patterns/EventBus.gd) 시그널 | `BindableEvent` / 서비스 간 모듈 시그널 |
| 서바이버 스폰·젬 (§3.7) | [`ObjectPool.gd`](../../platforms/godot/patterns/ObjectPool.gd) (적·젬 재사용), CC0/MIT 스타터는 [`survivors`](../strategy/defense_management_survivors.md) 표 | 서버가 좌표만 시뮬, `RunService.Heartbeat`, 수백 마리는 파츠 대신 좌표 배열 |
| 시드 RNG | `RandomNumberGenerator.seed` | `Random.new(seed)` |

## 8. 검증 (sim/)

`sim/rpg_sim.py`가 검사하는 규칙 (테스트 이름 = §3의 ✅ 이름):

1. `test_cost_exponential` — `cost(n) = b·r^n`, 일괄 구매식 = 개별 합
2. `test_output_linear_vs_cost` — n ≥ 15부터 비용/산출 비 단조 증가 (벽 필연), 마일스톤 x2
3. `test_time_to_wall` — 같은 수입에서 10레벨 소요 시간 비 = r^10, 수입 0이면 ∞
4. `test_damage_never_zero` — def 10^9에서도 데미지 ≥ 1
5. `test_damage_ratio_defense` — def = k이면 정확히 절반(±5%)
6. `test_stage_wall_detection` — 고정 공격력이면 벽 스테이지가 존재하고 그 뒤로 유지
7. `test_prestige_compound` — 환생 3회 동안 벽 스테이지 단조 증가 (데모: 31 → 34 → 37)
8. `test_offline_cap` — 3일 부재도 8시간치, 10분은 정확히 10분치
9. `test_offline_negative_rejected` — 시간 역행·동일 시각·첫 실행 = 0
10. `test_gacha_hard_pity` — 10만 뽑기에서 5★ 간격 ≤ 90, 4★ 간격 ≤ 10
11. `test_gacha_empirical_rate` — 비강제 뽑기의 5★ 비율 = 0.6% ± 0.1%p, 전체 비율 ≈ 1/E[gap] (±0.2%p)
12. `test_gacha_fifty_fifty` — 실패 다음 5★는 픽업 확정, 픽업 비율 2/3 ± 0.02, 최악 ≤ 180
13. `test_probability_table_sums` — 공개 확률표 합 100%, 5★ 0.6
14. `test_stamina_regen` — 480초당 1, 상한 200, 역행 무시, 잔여초 보존
15. `test_survivor_three_choice` — 3개 모두 다름, 만렙 제외, 후보 부족 시 그만큼만(0개 포함)
16. `test_survivor_run_ends_30min` — 시드 8개에서 리퍼(정확히 1800초)와 사망이 모두 발생, 1800초 초과 없음
17. `test_survivor_wave_density` — 분당 스폰 단조 증가, 10 → 120 상한
18. `test_survivor_xp_curve` — 필요 XP 단조 증가, 선형보다 가파르고 지수보다 완만

```bash
cd reference/genres/rpg/sim
python3 -I rpg_sim.py --test    # 종료 코드 = 실패 수
python3 -I rpg_sim.py --demo    # 시드 42: 환생 3회·가차 90뽑·서바이버 2런(시드 2 생존, 시드 0 근접 실패 1638초)
```

결과 (2026-10-17, Python 3.13): **`passed 18/18`**, 종료 코드 0.

## 9. 흔한 구현 버그

1. **환생 후에도 숫자가 그대로** → `prestige_points`를 리셋 목록에 같이 넣었거나, 배율을 `coins`에만 곱하고 공격력에는 안 곱함 → 리셋 목록에서 영구 필드를 분리하고 `heroAtk()`·`reward` 둘 다 `mult`를 곱한다 (§3.3).
2. **앱을 껐다 켤 때마다 오프라인 보상이 또 나옴** → `last_seen_unix`를 지급 전에 갱신하지 않았거나 저장 실패 → 계산 → 갱신 → 지급을 한 트랜잭션으로, 저장 성공 후 팝업 (§3.4).
3. **기기 시계를 미래로 돌리면 8시간치가 무한 반복** → 상한만 있고 `last_seen` 갱신이 서버 시각이 아님 → 온라인은 `serverNow`, 오프라인 싱글은 역행 0 + 상한, 그리고 "하루 N회"로 추가 제한 (§3.4).
4. **방어 높은 보스가 무적** → 감산형 `atk − def` → 비율형 `k/(k+def)` + `max(min_damage, …)` (§3.2).
5. **90뽑 안에 5★가 안 나왔다는 민원** → 천장 카운터가 메모리에만 있어 재시작·배너 전환에 초기화 → 세이브 필드로, 배너 간 공유 규칙 명시 (§3.5).
6. **공개 확률과 실제 확률이 다름** → 확률표를 기획서 숫자로 하드코딩 → `probabilityTable()`을 뽑기 데이터에서 생성하고 10만 뽑기 통계 테스트를 CI에 둔다 (§3.5, `test_gacha_empirical_rate`).
7. **스태미나가 상한에서 1 쓰자마자 가득 참** → 상한일 때 `stamina_ts`를 갱신하지 않음 → 상한 도달·유지 중에도 `stamina_ts = now` (§3.6).
8. **레벨업 3택에 같은 무기가 두 번, 또는 만렙 무기가 뜸** → 복원 추출·필터 누락 → 비복원 추출 + `level < max_level` 필터, 후보 0개면 보상(골드)으로 대체 (§3.7).
