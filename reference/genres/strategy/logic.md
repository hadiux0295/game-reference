# 전략 기본 베이스 로직

> 엔진 무관. 구현 전에 읽는 설계 뼈대. 숫자는 README §4(와 [`../../data/td_progression.md`](../../data/td_progression.md))에서만. 시뮬레이션으로 검증한 규칙에는 ✅ 표시.
> 확인일 2026-10-17. 대표작·루프·출처는 [`README.md`](README.md), 공통 시스템은 [`../../systems/core_systems.md`](../../systems/core_systems.md)·[`../../systems/genres.md`](../../systems/genres.md) 타워 디펜스 절. 여기서는 중복 서술하지 않고 링크한다.

전략 장르(RTS · 4X · 모바일 SLG · 실시간 카드 전략 · 오토배틀러 · 타워 디펜스)의 **공통 뼈대로 "타워 디펜스 + 자원 경제 루프"**를 고른다. 웨이브 → 처치 → 골드 → 건설·업그레이드 → 다음 웨이브. 엔진 부담이 가장 적고(좌표만 시뮬레이션, 물리 불필요), SLG의 타이머·가속과 오토배틀러의 공유 풀·이자는 같은 뼈대 위의 변형으로 붙는다(§1 변형, §3.6, §3.7). RTS의 락스텝은 §3.8에서 "명령만 교환 + 체크섬"으로 다룬다.

## 0. 최소 플레이 가능 단위 (MVP 루프)

도형 그래픽으로 1~2일 프로토타입. Thronefall도 도형으로 약 2개월 프로토타이핑했다([`defense_management_survivors.md`](defense_management_survivors.md)).

**엔티티 (5개)**
- 경로 `Path`: 웨이포인트 배열 1개 (꺾인 선 하나).
- 적 `Enemy`: 종류 2개 (빠르고 약한 것 · 느리고 강한 것). 필드는 hp·speed·reward·leak·progress뿐.
- 타워 `Tower`: 종류 1개, 단계 4개(기본 + 업그레이드 3). 사거리·데미지·쿨다운·타겟팅 규칙.
- 웨이브 테이블 `WaveTable`: 5행. 행마다 (적 종류, 수, 간격) 그룹 1~2개.
- 판 상태 `Match`: gold · lives · wave · state.

**규칙 (7개)**
1. 웨이브 시작 버튼 → 테이블대로 적 스폰.
2. 적은 경로를 따라 일정 속도로 전진. 끝에 닿으면 `lives -= leak`, 사라짐.
3. 타워는 쿨다운마다 사거리 안 적 하나를 규칙(First)으로 골라 데미지.
4. 적 hp ≤ 0 → `gold += reward`.
5. 웨이브의 적이 모두 사라지면 `gold += 100 + 웨이브 번호`(BTD6), 건설 단계로.
6. 건설 단계에서만 슬롯에 타워 건설·업그레이드(비용은 사다리 표).
7. `lives == 0` → 패배, 마지막 웨이브 클리어 → 승리. 남은 목숨으로 별 1~3개(KR).

**화면 (2개)**: 플레이 화면 1개(경로·슬롯·적·타워·gold/lives/wave 텍스트 + "웨이브 시작" 버튼) · 결과 화면 1개(승/패, 별, 다시 하기).

**넣지 않는 것**: 메타 진행(XP·해금·상점), 여러 경로·분기, 영웅·액티브 스킬, 상태이상(둔화·독), 스플래시·관통, 타워 판매·환불, 멀티플레이, 저장(한 판은 메모리), 튜토리얼, 아트·사운드.

## 1. 게임 흐름 상태 머신

공통 뼈대(TD). 상태 머신 구현은 [`../../systems/core_systems.md`](../../systems/core_systems.md) §2, Godot [`StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd), Roblox [`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau).

```
Lobby ──start──▶ Build ──start_wave──▶ Wave ──all_enemies_gone──▶ Build
                   ▲                     │                          │
                   │                     ├──lives==0──▶ Lost ──▶ Result
                   │                     └──last_wave_cleared──▶ Won ──▶ Result
                   └────────────────────── retry ◀──────────────────┘
```

| 상태 | 들어갈 때 | 허용 입력 | 나갈 조건 |
|---|---|---|---|
| Lobby | 맵·난이도 선택 표시 | start | start → Build |
| Build | 웨이브 보너스 지급 완료 후 | build, upgrade, start_wave | start_wave → Wave (마지막 웨이브 다음이면 Won) |
| Wave | 스폰 큐 생성 | build, upgrade (허용 여부는 다이얼 §6) | 스폰 큐·적 모두 소진 → Build/Won; lives ≤ 0 → Lost |
| Won / Lost | 보상 계산(완주 보너스는 Won만, §3.1 패배 보상) | — | 자동 → Result |
| Result | 별·보상 표시 | retry, home | retry → Build(초기화), home → Lobby |

허용되지 않은 입력은 **무시**한다(예외를 내지 않는다). Wave 중 `start_wave`는 무시, Lost 뒤 `build`는 무시.

**변형 1 — 모바일 SLG (타이머)**: `Build` 안에 건물별 하위 상태 `Idle → Building(timer) → Done`. "웨이브" 대신 타이머 만료가 전이 조건이고, `accelerate(item)`·`help(ally)`가 `Building`에서만 허용되는 입력이다(§3.6). 전투는 서버가 즉시 판정하는 `Rally → Resolve` 두 상태.

**변형 2 — 오토배틀러**: `Shop(roll/buy/sell/level) → Combat(자동, 입력 없음) → Shop …`. `Combat` 진입 시 이자·승리 골드 지급(§3.7). 8인 공유 풀이 `Shop`의 `roll` 결과를 정한다. Super Auto Pets는 `Combat`을 비동기(저장된 상대 덱)로 치환한 것.

## 2. 엔티티와 데이터 모델

| 엔티티 | 핵심 필드 (타입) | 소유 | 저장 |
|---|---|---|---|
| Match | tick(int) · state(enum) · wave(int) · gold(int) · lives(int) · seed(int) | 서버 | 판 끝 결과만 (시드·웨이브·목숨·별) |
| Path | points([[x,y]…] 정수 밀리타일) · seg_len([int]) · total(int) | 데이터 | 맵 파일 |
| Enemy | id · kind · hp · max_hp · speed · reward · leak · progress(int) · alive | 서버 | 없음 |
| Tower | id · kind · tier · x · y · cooldown(ms) · targeting(enum) · kills | 서버 | 없음 (리플레이는 명령 로그로 복원) |
| WaveRow | groups[{enemy, count, interval_ms}] | 데이터 | 맵 파일 |
| Command | tick · player · seq · op(build/upgrade/start_wave) · 인자 | 클라→서버 | 리플레이·검증용 로그 |
| Ledger | gold · log[(reason, amount)] | 서버 | 분석 로그 |
| BuildTimer (SLG) | remaining_s · helps · max_helps | 서버 | 서버 시각 기준 종료 시각(절대값) |
| SharedPool (오토배틀러) | remaining{(cost, unit): copies} | 서버(방) | 없음 |

좌표·속도·진행도는 **정수(밀리타일, 밀리타일/초)**, 시간은 **정수 ms**. 부동소수를 판 안 상태에 넣지 않는 것이 §3.8 결정론의 전제다.

밸런스 Config (sim의 `CONFIG`와 같은 값). 출처 표시가 없는 항목은 **예시값**.

```json
{
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
```

| 키 | 출처 |
|---|---|
| `tick_ms` 100 | SupCom 시뮬 10fps 고정 (README §4) |
| `lives` 20 | KR 별 표 "남은 목숨 18~20 → 3개"의 상한에서 추정 (td_progression §3, inferred) |
| `economy.start_gold` 650, 보너스 100 + r | BTD6 시작 자금·라운드 종료 보너스 (td_progression §2) |
| `economy.loss_reward_p` 1.3 | TDS 패배 보상 지수 Easy~Intermediate (td_progression §3) |
| `cost_curve.ratio_pct` 200 | BTD6 T1~T3 지수 r ≈ 2.0 (td_progression §4, inferred) |
| `cost_ladders` · `towers.dart.costs` | BTD6 Dart Medium 200/140/200/320, KR1 궁수 70/110/160, Thronefall 탑 3/5/15 (td_progression §1) |
| `slg.th17_build_s` 1,296,000 | CoC TH17 15일 (README §4) |
| `autobattler.pool_copies` | TFT Set 18 공유 풀 30/25/18/10/9 (README §4) |
| `autobattler.interest_*`, `win_gold` | TFT 이자 10골드당 1, 최대 5, 승리 +1 (README §4) |
| `lockstep` 200ms · 2턴 | AoE "1500 Archers" (README §4) |
| `towers.dart.damage/range/cooldown_ms`, `enemies`, `path`, `build_slots`, `waves`, `hp_growth_pct_per_wave`, `slg.help_reduce_s/max_helps`, `autobattler.units_per_cost` | **예시값** |

## 3. 핵심 시스템

### 3.1 자원 경제 (수입과 소비)
- **규칙**: 판 안 재화는 gold 하나. 수입원은 (a) 처치 보상 `enemy.reward`, (b) 웨이브 종료 보너스 `100 + wave`, (c) 시작 자금. 소비처는 건설·업그레이드뿐. 모든 증감은 `Ledger.add(amount, reason)` 한 함수를 지나며([`../../systems/core_systems.md`](../../systems/core_systems.md) §4), 잔액이 음수가 되는 소비와 비정수는 거부한다. 판 밖(메타) 보상은 TDS식 패배 보상과 KR식 별로 계산한다.
- **공식**:
  - `wave_bonus(w) = wave_bonus_base + wave_bonus_per_wave × w` (BTD6: 100 + 라운드).
  - 패배 보상 `reward(w) = base ÷ (1 + (W/w − 1)^p)`, w = 도달 웨이브, W = 전체 웨이브, p = 1.3. w = W면 base + 완주 보너스.
  - 별: 남은 목숨 18~20 → 3, 6~17 → 2, 1~5 → 1, 0 → 0 (KR).
  - 참고 규모: BTD6 r10 누적 자금 2,443, KR Pagras 시작 300 + 처치 수입 합 1,624(11웨이브) (td_progression §2).
- **의사코드**:
  ```
  function Ledger.add(amount: int, reason: string) -> bool:
      if not isInt(amount) or gold + amount < 0: return false
      gold += amount; log.push((reason, amount)); return true

  function onEnemyKilled(e):        ledger.add(e.reward, "kill:" + e.kind)
  function onWaveCleared(w):        ledger.add(wave_bonus(w), "wave_bonus")
  function tryBuild(kind, slot) -> bool:
      if not ledger.add(-towers[kind].costs[0], "build:" + kind): return false
      placeTower(kind, slot); return true
  function lossReward(base, w, W, p) -> float:
      return base if w >= W else base / (1 + (W / w - 1) ^ p)
  ```
- **함정**: ① `gold -= cost` 를 여기저기 직접 쓰면 로그·UI·치트 탐지가 흩어진다. ② 보너스를 "웨이브 시작"에 주면 마지막 웨이브를 안 끝내도 받는다 — 반드시 **종료** 시점. ③ 패배 보상을 완주 보상과 같은 식으로 주면 "일부러 지기"가 생긴다 — 완주 보너스는 클리어에만.
- **검증 ✅**: `test_economy_single_entry`, `test_economy_wave_bonus`, `test_loss_reward_formula`, `test_kr_stars`.

### 3.2 건설·업그레이드 비용 곡선
- **규칙**: 타워마다 비용 사다리 `costs = [기본, T1, T2, T3…]`를 데이터로 둔다. 사다리를 생성할 때는 지수 곡선을 쓰되 **정수 연산**으로 만든다. 출처 있는 세 게임 모두 "3단계까지 누적 ÷ 기본가 ≈ 4~8배"에 들어온다(BTD6 Dart 4.3×, KR 궁수 4.9×, Thronefall 탑 7.7×; td_progression §4). 상위 단계(BTD6 T4 10×, T5 84×)는 60라운드 이상 장기전용 벽이므로 짧은 판에는 넣지 않는다. 난이도 보정은 Easy −15% / Hard +8% (BTD6).
- **공식**: `cost(n) = base × ratio_pct^n ÷ 100^n` (정수 나눗셈, n = 0부터). k개 연속 구매 합 `Σ_{i=n}^{n+k−1} cost(i)` = 등비 합 `base·r^n·(r^k−1)/(r−1)` ([`../../systems/core_systems.md`](../../systems/core_systems.md) §5). 수입 환산: Lv2 ≈ 1~1.5웨이브, Lv3 ≈ 2~3웨이브 수입(td_progression §4).
- **의사코드**:
  ```
  function expCost(base: int, ratioPct: int, n: int) -> int:
      return base * ratioPct^n // 100^n          # 정수만, pow는 정수 거듭제곱
  function tryUpgrade(tower) -> bool:
      next = tower.tier + 1
      if next >= len(tower.spec.costs): return false     # 최고 단계
      if not ledger.add(-tower.spec.costs[next], "upgrade:" + tower.kind): return false
      tower.tier = next; return true
  function ladderOk(costs) -> bool:                       # 데이터 검증(로드 시)
      return 4.0 <= sum(costs[0..3]) / costs[0] <= 8.0
  ```
- **함정**: ① `base * r ** n`을 float로 계산하면 플랫폼마다 반올림이 달라 락스텝이 깨진다. ② 업그레이드 비용을 "다음 단계 비용 − 현재 비용"으로 착각 — 사다리의 각 칸은 **그 단계로 올리는 추가 비용**이다. ③ 환불(판매)을 100%로 두면 "건설 → 환불"로 공짜 정찰·공짜 재배치가 된다 — 환불 비율은 README §4에 없음(미조사). 넣는다면 100% 미만으로 하고 데이터로 둔다.
- **검증 ✅**: `test_cost_curve_exponential`, `test_cost_ladder_total_ratio`, `test_build_rejects_invalid`.

### 3.3 웨이브 생성 (데이터 테이블)
- **규칙**: 웨이브는 코드가 아니라 테이블 한 행이다. 행 = 그룹 목록, 그룹 = (적 종류, 수, 간격 ms). 웨이브 시작 틱에 행을 **스폰 큐**(스폰 틱, 그룹 번호, 번호, 종류, hp)로 펼쳐 정렬해 두고, 틱마다 큐 앞만 본다. 그룹은 동시에 시작한다(순차 시작이 필요하면 `delay_ms` 열을 추가). HP는 웨이브 인덱스마다 `+hp_growth_pct`(예시값 10%)로 정수 스케일.
- **공식**: `spawn_tick(i) = start_tick + interval_ms × i ÷ tick_ms` (정수 나눗셈), `hp = base_hp × (100 + growth × wave_idx) ÷ 100`.
- **의사코드**:
  ```
  function buildSpawnQueue(cfg, waveIdx: int, startTick: int) -> list:
      growth = 100 + cfg.hp_growth_pct_per_wave * waveIdx
      q = []
      for gi, g in enumerate(cfg.waves[waveIdx].groups):
          spec = cfg.enemies[g.enemy]
          for i in 0..g.count-1:
              q.push((startTick + g.interval_ms * i // cfg.tick_ms, gi, i, g.enemy, spec.hp * growth // 100))
      return sorted(q)
  function spawnStep(match):                     # 틱마다
      while q and q[0].tick <= match.tick:
          row = q.pop(0); match.enemies.push(Enemy(nextId++, row.kind, row.hp))
  ```
- **함정**: ① `interval_ms`가 `tick_ms`의 배수가 아니면 정수 나눗셈으로 두 마리가 같은 틱에 나온다 — 테이블 로드 시 경고. ② 큐를 정렬하지 않으면 그룹 2가 그룹 1보다 먼저 나와 "표와 다르다"는 버그 리포트가 온다. ③ 웨이브 종료 판정에 "스폰 큐 비었음"을 빠뜨리면 첫 적이 죽는 순간 다음 웨이브로 넘어간다.
- **검증 ✅**: `test_wave_table_spawn`.

### 3.4 타겟팅 규칙 (First / Last / Strongest / Closest)
- **규칙**: 타워는 쿨다운이 0일 때 사거리 안의 살아 있는 적 중 하나를 고른다. First = 경로 진행도 최대, Last = 최소, Strongest = 현재 hp 최대, Closest = 타워와 거리 최소. **동점은 id가 작은 쪽**으로 고정한다(결정론). 사거리 비교는 제곱 거리로 하고 제곱근을 쓰지 않는다.
- **공식**: 사거리 판정 `(tx − ex)² + (ty − ey)² ≤ range²`. 정렬 키: First `(−progress, id)`, Last `(progress, id)`, Strongest `(−hp, −progress, id)`, Closest `(dist², −progress, id)`.
- **의사코드**:
  ```
  function pickTarget(tower, enemies, path, rule) -> Enemy | null:
      cands = []
      for e in enemies where e.alive:
          p = path.positionAt(e.progress)
          d2 = (tower.x - p.x)^2 + (tower.y - p.y)^2
          if d2 <= tower.range^2: cands.push((e, d2))
      if cands.empty: return null
      key = { first: (e,d) -> (-e.progress, e.id),  last: (e,d) -> (e.progress, e.id),
              strongest: (e,d) -> (-e.hp, -e.progress, e.id),  closest: (e,d) -> (d, -e.progress, e.id) }[rule]
      return min(cands, key)
  ```
- **함정**: ① "Strongest"를 max_hp로 구현하면 빈사 보스를 계속 쏜다 — **현재 hp**. ② 타겟을 캐시해 두고 사거리 밖으로 나가도 계속 쏘는 버그 — 매 사격마다 재판정하거나 사거리 이탈 체크. ③ 수백 마리에서 매 틱 전체 순회는 O(타워 × 적) — 쿨다운이 0인 타워만 순회하고, 필요하면 경로 진행도 정렬 배열을 쓴다.
- **검증 ✅**: `test_targeting_first_last`, `test_targeting_strongest_closest`.

### 3.5 경로(웨이포인트)와 누출·목숨
- **규칙**: 경로는 웨이포인트 배열. 적은 좌표가 아니라 **진행도 `progress`(밀리타일)** 하나만 갱신하고, 좌표는 필요할 때 구간 보간으로 계산한다(렌더·타겟팅). `progress ≥ path.total`이면 누출: `lives = max(0, lives − leak)`, 적 제거. `lives == 0`이면 즉시 Lost. 플로우 필드는 분기·장애물이 있을 때만([`../../systems/core_systems.md`](../../systems/core_systems.md) §10).
- **공식**: 구간 길이 `isqrt(dx² + dy²)`(정수), `total = Σ seg_len`. 틱당 전진 `speed × tick_ms ÷ 1000`. 도착 틱 `= total ÷ (speed × tick_ms ÷ 1000)`. 보간 `x = ax + (bx − ax) × rem ÷ seg_len`.
- **의사코드**:
  ```
  function Path.positionAt(progress: int) -> (int, int):
      rem = max(0, progress)
      for (a, b), len in segments:
          if rem <= len: return (a.x + (b.x - a.x) * rem // len, a.y + (b.y - a.y) * rem // len)
          rem -= len
      return points.last
  function moveStep(match):
      for e in match.enemies:
          e.progress += e.speed * tick_ms // 1000
          if e.progress >= path.total:
              e.alive = false; match.lives = max(0, match.lives - e.leak); stats.leaks++
      if match.lives == 0: match.state = Lost
  ```
- **함정**: ① 좌표를 float로 누적하면 같은 속도의 적이 기기마다 다른 틱에 도착한다 — 정수 진행도. ② 누출과 처치가 같은 틱에 겹치면 둘 다 세어 보상과 목숨이 동시에 깎인다 — 이동(누출) → 사격(처치) 순서를 고정하고 `alive`를 먼저 확인. ③ 목숨을 음수로 두면 UI가 "-3"을 보여 주고 별 계산이 깨진다.
- **검증 ✅**: `test_waypoint_path_progress`, `test_leak_lives_and_lost`.

### 3.6 SLG 타이머 · 가속 · 동맹 도움 (변형)
- **규칙**: 건설·연구는 초 단위 타이머(CoC TH17 15일 = 1,296,000초). 시간 경과·가속 아이템·동맹 도움은 **모두 `remaining`만 줄이는 같은 함수**를 지나고 0 아래로 내려가지 않는다. 도움은 건물당 횟수 상한이 있다(예시값 30회 × 60초). 서버는 종료 **절대 시각**을 저장하고 남은 시간은 서버 시각으로 계산한다(기기 시각을 믿지 않는다 — [`../../platforms/godot/architecture.md`](../../platforms/godot/architecture.md) §6 오프라인 보상과 같은 원칙).
- **공식**: `remaining = max(0, remaining − Δ)`, Δ ∈ {경과 초, 아이템 초, 적용 도움 수 × help_reduce_s}. `applied_helps = min(요청, max_helps − helps)`.
- **의사코드**:
  ```
  class BuildTimer(total_s, help_reduce_s, max_helps):
      remaining = total_s; helps = 0
      function tick(dt_s):          remaining = max(0, remaining - dt_s)
      function accelerate(item_s):  tick(item_s)                       # 같은 경로
      function help(n) -> int:
          applied = min(n, max_helps - helps); helps += applied
          remaining = max(0, remaining - applied * help_reduce_s); return applied
      function done(): return remaining == 0
  function serverRemaining(building): return max(0, building.finish_at - serverNow())
  ```
- **함정**: ① 남은 시간을 클라이언트가 보내면 `remaining = 0` 한 줄로 즉시 완성 — 서버가 `finish_at`로 계산. ② 가속 아이템이 남은 시간보다 크면 초과분을 환불·이월하지 않으면 유저 불만, 이월하면 악용 — 정책을 데이터에 적고 테스트. ③ 동맹 도움을 상한 없이 두면 큰 동맹이 모든 타이머를 0으로 만든다.
- **검증 ✅**: `test_slg_timer_accelerate`.

### 3.7 오토배틀러 공유 풀 · 이자 (변형)
- **규칙**: 상점은 개인 RNG가 아니라 **방 전체가 나눠 쓰는 풀**에서 뽑는다(TFT Set 18: 1코 30장, 2코 25, 3코 18, 4코 10, 5코 9). 누가 사면 풀에서 빠지고, 팔거나 탈락하면 돌아온다. 티어가 정해진 슬롯에서 특정 유닛이 나올 확률 = 그 유닛의 남은 장수 ÷ 그 티어의 남은 장수 합. 이자는 은행 10골드당 +1, 최대 +5(50골드), PvP 승리 +1. 티어별 상점 확률(레벨표)은 README §4에 없어 **예시값/미조사** — 데이터로 둔다.
- **공식**: `P(unit | cost) = remaining[cost][unit] ÷ Σ_u remaining[cost][u]`. `interest = min(gold ÷ 10, 5)`. Super Auto Pets 단순화: 턴당 10골드 고정, 펫 3, 롤 1, 이자 없음(README §4).
- **의사코드**:
  ```
  class SharedPool(cfg):
      remaining[(cost, unit)] = cfg.pool_copies[cost]  for each unit in cfg.units_per_cost[cost]
      function draw(rng, cost) -> unit | null:          # 남은 장수 가중
          items = [(k, v) for k, v in remaining if k.cost == cost and v > 0]
          if items.empty: return null
          r = rng.randrange(sum(v))
          for (k, v) in items: r -= v; if r < 0: remaining[k] -= 1; return k.unit
      function release(cost, unit): remaining[(cost, unit)] += 1
  function roundIncome(player) -> int:
      return base_income + min(player.gold // 10, 5) + (1 if player.won else 0)
  ```
- **함정**: ① 풀을 플레이어별로 복사하면 롤이 슬롯머신이 되고 "상대 조합 읽기"가 사라진다(README §6). ② 유닛 합성(3장 → 1장)으로 풀에서 빠진 장수를 돌려주면 안 된다 — 합성된 유닛을 팔 때 **3장** 반환. ③ 이자를 소수점으로 계산하면 49골드가 4.9 → 5로 반올림되는 버그 — 정수 나눗셈.
- **검증 ✅**: `test_shared_pool_draw`, `test_shared_pool_exhaust`, `test_interest_cap`.

### 3.8 결정론적 락스텝 (명령만 교환 + 체크섬)
- **규칙**: 멀티·리플레이·검증은 유닛 상태가 아니라 **명령(tick, player, seq, op, 인자)만** 교환·저장하고, 모든 참여자가 같은 시드·같은 Config로 같은 시뮬레이션을 돌린다. AoE: 통신 턴 ~200ms, 명령은 2턴 뒤 실행, 250ms까지 체감 양호/500ms 한계; SupCom: 시뮬 10fps 고정, 렌더 분리(README §4). 매 틱 정수 상태만 직렬화해 CRC32 체크섬을 남기고, 참여자 간 체크섬이 갈라진 첫 틱이 디싱크 지점이다. 서버 권위형(SLG·Clash Royale)에서도 같은 구조가 "클라이언트 예측 + 서버 재검증"의 토대가 된다.
- **공식**: `exec_tick = issue_tick + turn_ms × delay_turns ÷ tick_ms` (200 × 2 ÷ 100 = 4틱). 명령 실행 순서 `(exec_tick, player, seq)` 고정. `checksum(t) = crc32(repr([tick, gold, lives, wave, state, (e.id, e.hp, e.progress)…, (t.id, t.tier, t.cooldown, t.kills)…]))`.
- **의사코드**:
  ```
  function runLockstep(cfg, seed, commands) -> Match:
      m = Match(cfg, seed)
      delay = cfg.lockstep.turn_ms * cfg.lockstep.command_delay_turns // cfg.tick_ms
      for c in commands: m.queueCommand(c.tick + delay, c.player, c.seq, c.cmd)   # (tick, player, seq)로 정렬
      while m.state not in (Won, Lost): m.step()                                  # step 끝에 checksums.push(m.checksum())
      return m
  function compareChecksums(a: list, b: list) -> int:        # 첫 디싱크 틱, 없으면 -1
      for t in 0..min(len(a), len(b))-1: if a[t] != b[t]: return t
      return -1
  ```
- **함정**: ① 부동소수(특히 `pow`, 삼각함수)·딕셔너리 순회 순서·초기화 안 된 변수가 디싱크의 대부분(README §6). ② RNG를 렌더·UI(파티클, 사운드 랜덤)와 공유하면 호출 횟수가 달라져 갈라진다 — 시뮬 RNG는 별도 인스턴스. ③ 체크섬에 객체 주소·float·렌더 상태를 넣으면 정상인데도 불일치가 난다.
- **검증 ✅**: `test_lockstep_checksum`, `test_full_match_deterministic`.

## 4. 틱 / 업데이트 순서

권위 측(서버 또는 락스텝의 각 피어) 한 틱. 틱 주기 **100ms**(SupCom 시뮬 10fps, README §4; 입력 체감은 AoE 기준 250ms까지 양호). 고정 타임스텝은 [`../../systems/core_systems.md`](../../systems/core_systems.md) §1. 렌더는 틱 사이를 보간한다.

1. **명령 수집·적용**: `pending`에서 `exec_tick ≤ tick`인 명령을 `(exec_tick, player, seq)` 순으로 꺼내 검증(§5) 후 적용. 거부는 무시(로그만).
2. **스폰**: 스폰 큐 앞에서 `spawn_tick ≤ tick`인 행을 꺼내 적 생성.
3. **이동·누출**: 모든 적 `progress += speed × tick_ms ÷ 1000`; 끝에 닿으면 `alive = false`, `lives −= leak`.
4. **사격**: 타워마다 쿨다운 감소 → 0이면 타겟 선택(§3.4) → 데미지 → 쿨다운 재설정.
5. **처치 보상**: hp ≤ 0인 적 `alive = false`, `ledger.add(reward)`, 타워 kills++. 죽은 적 목록에서 제거.
6. **판정**: `lives == 0` → Lost. 스폰 큐·적 모두 비면 `ledger.add(wave_bonus)` → Build 또는 Won.
7. **스냅샷**: `tick++`, 체크섬 기록. (서버 권위형이면 여기서 클라이언트에 상태 델타 전송; 저장은 Won/Lost에서만.)

SLG 변형은 1(명령) → 타이머 갱신(서버 시각) → 완료 건물 처리 → 저장(틱이 아니라 명령 처리 직후). 오토배틀러는 Shop 단계가 1에 해당하고 Combat은 2~6을 자동으로 돌린다.

## 5. 신뢰 경계

재화·점수·확률·보상은 반드시 서버([`../../systems/core_systems.md`](../../systems/core_systems.md) §7, Roblox [`architecture.md`](../../platforms/roblox/architecture.md) §1·§5, [`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau)).

| 클라이언트가 보내는 것 | 서버가 검증하는 규칙 | 거부 시 처리 |
|---|---|---|
| `build(kind, slot)` | kind가 Config에 있음 · slot이 `build_slots`에 있고 비어 있음 · 상태가 Build(또는 다이얼로 Wave 허용) · `ledger.add(−cost)` 성공 | 무시, gold 불변 (`test_build_rejects_invalid`) |
| `upgrade(tower_id)` | 타워가 존재하고 요청자 소유 · 최고 단계가 아님 · 잔액 충분 | 무시 |
| `start_wave` | 상태가 Build · 남은 웨이브 있음 | 무시 |
| 명령의 `tick` | `now − 허용 지연 ≤ tick ≤ now` · 플레이어당 레이트 리밋(AoE 평균 1명령/1.5~2초, 전투 시 3~4/초) | 초과분 버림, 반복 시 킥 |
| (SLG) `accelerate(item_id)` · `help(building)` | 아이템 보유·소모 멱등 · 도움 상한 · 남은 시간은 서버 `finish_at`로 계산 | 무시, 아이템 불변 |
| (오토배틀러) `roll` · `buy(slot)` | 골드 ≥ 비용 · 슬롯이 서버가 제시한 상점과 일치 · 풀 잔량 | 무시 |
| 점수·결과 제출 | **받지 않는다** — 서버가 명령 로그를 재생해 결과를 만든다. 싱글 오프라인(Godot)은 시드 + 명령 로그를 함께 제출해 리더보드에서 재검증 | 리더보드 미등록 |
| 결제 영수증 | 영수증 ID로 멱등 처리 (AGENTS.md 공통 규칙) | 중복 지급 안 함 |

## 6. 밸런스 다이얼

| 다이얼 | 무엇을 바꾸나 | 기본값 (출처) | 올리면 / 내리면 체감 |
|---|---|---|---|
| `start_gold` | 첫 건설 단계의 선택지 수 | 650 (BTD6, td_progression §2) | 올리면 첫 웨이브가 시시함 / 내리면 1타워 강제, 튜토리얼화 |
| `wave_bonus_base` | 처치와 무관한 보장 수입 (눈덩이 상쇄) | 100 + 웨이브 (BTD6) | 올리면 못해도 회복 가능, 긴장 ↓ / 내리면 초반 실수가 치명적 |
| `enemy.reward` ÷ `tower.costs` | 웨이브당 살 수 있는 단계 수 | Lv2 ≈ 1~1.5웨이브, Lv3 ≈ 2~3웨이브 (td_progression §4) | 올리면 풀업이 빨라 후반 지루 / 내리면 업그레이드가 안 보여 답답 |
| `cost_curve.ratio_pct` | 단계 간 가격 비율 | 200 (BTD6 r ≈ 2.0, inferred) | 올리면 "넓게"(타워 수) 유도 / 내리면 "깊게"(한 타워 집중) 유도 |
| `hp_growth_pct_per_wave` | 웨이브 난이도 기울기 | 10 (예시값) | 올리면 중반 벽 / 내리면 후반까지 평탄 |
| `lives` · `enemy.leak` | 실수 허용 횟수 | 20 (KR 별 표 상한, inferred) · 1/3 (예시값) | 올리면 느슨, 별 구간 넓어짐 / 내리면 한 번 누출이 패배 |
| `targeting` 기본값 | 플레이어 조작 깊이 | first (예시값) | 규칙 선택을 열면 깊이 ↑, UI 복잡 / 고정하면 배치만 남음 |
| Wave 중 건설 허용 | 템포 | 허용 (예시값; 실시간 TD의 일반 관행) | 허용하면 실시간 대응, 긴장 ↑ / 금지하면 퍼즐·계획형 |
| `slg.help_reduce_s × max_helps` | 동맹 압력 크기 | 60초 × 30 (예시값) | 올리면 동맹 필수 / 내리면 솔로 가능하지만 타이머가 순수 대기 (README §6) |
| `pool_copies` | 오토배틀러 경쟁 강도 | 30/25/18/10/9 (TFT) | 올리면 모두가 원하는 조합을 완성, 긴장 ↓ / 내리면 상대 읽기와 경합이 핵심 |

## 7. 플랫폼 매핑

Godot 공통: 엔티티 정의는 Resource(`.tres`)로 데이터 주도([`../../platforms/godot/architecture.md`](../../platforms/godot/architecture.md) §4), 밸런스 JSON은 §2 그대로. Roblox 공통: Config는 `ReplicatedStorage`의 공유 모듈, 판정은 `ServerScriptService`([`../../platforms/roblox/architecture.md`](../../platforms/roblox/architecture.md) §1·§4). TD용 Godot 오픈소스(quiver-dev, youtd2 등)는 [`defense_management_survivors.md`](defense_management_survivors.md)의 표.

| 시스템 | Godot (노드 · Resource · 패턴) | Roblox (Service · API · 패턴) |
|---|---|---|
| 상태 머신 (§1) | `StateMachine` 노드 + `State` 자식 — [`StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd), [`State.gd`](../../platforms/godot/patterns/State.gd) | `RoundService` 상태를 Attribute로 복제 — [`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau) |
| 재화 Ledger (§3.1) | Autoload `Economy.add()/spend()` — [`Economy.gd`](../../platforms/godot/patterns/Economy.gd) | 서버 `EconomyService`(ShopService의 구매 경로 재사용) — [`ShopService.luau`](../../platforms/roblox/patterns/ShopService.luau) |
| 비용 사다리 (§3.2) | `TowerData` Resource(`@export var costs: Array[int]`) | `shared/Config/Towers.luau` `table.freeze` |
| 웨이브 테이블 (§3.3) | `WaveData` Resource 배열 또는 JSON → `JSON.parse_string` | `shared/Config/Waves.luau`; 스폰은 서버 `WaveService` |
| 타겟팅·사격 (§3.4) | 적 좌표 배열을 서버 스크립트가 들고 순회, 투사체·이펙트는 [`ObjectPool.gd`](../../platforms/godot/patterns/ObjectPool.gd) | 서버가 판정, 투사체는 클라이언트 이펙트만(`RemoteEvent`로 "발사" 통지) |
| 경로·이동 (§3.5) | `Path2D` + `PathFollow2D`로 **표시**, 진행도는 정수로 자체 관리; 분기·회피는 `NavigationServer2D` | 웨이포인트는 `Folder` 안 `Part` 배열; 서버가 progress 갱신, 클라이언트가 보간 |
| 이벤트 (처치·누출·웨이브 종료) | [`EventBus.gd`](../../platforms/godot/patterns/EventBus.gd) 시그널 | `BindableEvent`(서버 내부) + `RemoteEvent`(클라이언트 통지) |
| SLG 타이머 (§3.6) | 싱글이면 [`SaveManager.gd`](../../platforms/godot/patterns/SaveManager.gd) 오프라인 보상 규칙(시간 역행 무시·상한); 온라인이면 서버 `finish_at` | 서버 `os.time()` 기준 `finish_at`, [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau)에 저장 |
| 공유 풀·확률 (§3.7) | 가중 뽑기·시드 고정은 [`Gacha.gd`](../../platforms/godot/patterns/Gacha.gd) 구조 재사용 | 서버 `Random.new(seed)`; 상점 결과만 클라이언트에 복제 |
| 락스텝·체크섬 (§3.8) | `MultiplayerAPI`로 명령만 RPC, 시뮬은 `_physics_process` 고정 스텝, 체크섬은 `hash()`/`PackedByteArray` CRC | Roblox는 서버 권위이므로 락스텝 대신 서버 시뮬 + 클라이언트 보간; 명령 검증은 [`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau) |
| 저장·결과 (§4 7단계) | [`SaveManager.gd`](../../platforms/godot/patterns/SaveManager.gd) (`version` 필드·마이그레이션) | [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau) (세션 잠금·버전) |

## 8. 검증 (sim/)

[`sim/strategy_sim.py`](sim/strategy_sim.py) (표준 라이브러리만, 정수 결정론, 설명은 [`sim/README.md`](sim/README.md)).

```bash
cd reference/genres/strategy/sim
python3 -I strategy_sim.py --test    # 마지막 줄 passed k/n, 종료 코드 = 실패 수
python3 -I strategy_sim.py --demo    # 시드 11, 5웨이브 한 판 요약
```

| # | 테스트 | 검사하는 규칙 (한 줄) |
|---|---|---|
| 1 | `test_economy_single_entry` | 모든 증감이 `Ledger.add`를 지나고 로그 합 = 잔액, 잔액 부족·비정수 거부 |
| 2 | `test_economy_wave_bonus` | BTD6 보너스 100 + r: r10 = 110, 10라운드 합 1,055 |
| 3 | `test_loss_reward_formula` | TDS 패배 보상: 완주 = base, 절반 도달(p 1.3) = base/2, 단조 증가 |
| 4 | `test_kr_stars` | KR 별 구간 경계 20/18/17/6/5/1/0 |
| 5 | `test_cost_curve_exponential` | 정수 지수 곡선 r = 2.0, 등비 합 공식 = 루프 합 |
| 6 | `test_cost_ladder_total_ratio` | BTD6·KR·Thronefall 사다리 모두 누적 ÷ 기본 4~8배 |
| 7 | `test_build_rejects_invalid` | 슬롯 밖·중복·잔액 부족 건설 거부, gold 불변 |
| 8 | `test_wave_table_spawn` | 테이블 → 스폰 큐 개수·간격·그룹 동시 시작, HP +10%/웨이브 |
| 9 | `test_targeting_first_last` | First = 진행도 최대, Last = 최소 |
| 10 | `test_targeting_strongest_closest` | Strongest = 현재 hp 최대, Closest = 거리 최소, 사거리 밖 제외 |
| 11 | `test_waypoint_path_progress` | 경로 길이·정수 보간·도착 틱 = 길이 ÷ 속도 |
| 12 | `test_leak_lives_and_lost` | 타워 없이 6기 누출 → 목숨 −6, 목숨 0 → Lost |
| 13 | `test_slg_timer_accelerate` | 15일 타이머 1일 가속 → 14일, 도움 상한 30회, 음수 없음 |
| 14 | `test_shared_pool_draw` | 확률 = 남은 장수 ÷ 티어 합, 남이 가져가면 감소, 몬테카를로(시드 42, 2만 회) ±0.01 |
| 15 | `test_shared_pool_exhaust` | 5코 72장 소진 → None, release 후 복귀 |
| 16 | `test_interest_cap` | 이자 9→0, 10→1, 49→4, 50→5, 100→5 |
| 17 | `test_lockstep_checksum` | 같은 명령 → 같은 체크섬, 명령 1개 차이 → 4틱 뒤 갈라짐 |
| 18 | `test_full_match_deterministic` | 5웨이브 두 번 실행 결과·최종 체크섬 동일 |

실행 결과 (2026-10-17, Python 3.13): **`passed 18/18`**, 종료 코드 0. `--demo`(시드 11): 타워 3기 → 5웨이브 승리, 처치 48 · 누출 2 · 남은 목숨 14 → 별 2개.

검증하지 않은 것: 렌더·입력, 실제 네트워크 지연, 플로우 필드, 수백 유닛 성능, 실제 서버 저장·결제, 티어별 상점 확률표(README §4에 없음).

## 9. 흔한 구현 버그

1. **같은 적이 두 타워에서 동시에 죽어 보상이 두 번** → 증상: gold가 처치 수보다 많다. 원인: 사격 루프 안에서 `alive`를 갱신하지 않고 틱 끝에 일괄 정리. 고침: 데미지 직후 `hp ≤ 0`이면 즉시 `alive = false`로 두고 다음 타워의 후보에서 제외(§4 4~5단계).
2. **마지막 웨이브에서 보너스를 못 받거나 두 번 받음** → 증상: 결과 화면 gold가 로그와 다르다. 원인: 웨이브 종료 판정이 Build 전이와 Won 전이에 따로 있어 한쪽만 보너스를 준다. 고침: 종료 판정 한 곳에서 보너스를 주고, 그다음에 Build/Won을 가른다(§3.1 함정 ②).
3. **기기마다 적 도착 시점이 달라 멀티가 디싱크** → 증상: 체크섬이 수십 틱 뒤에 갈라진다. 원인: 속도 × dt를 float로 누적, `pow`로 비용 계산. 고침: 밀리타일 정수 진행도, 정수 거듭제곱(§3.2 · §3.5 · §3.8).
4. **Strongest 타워가 빈사 보스만 쫓음** → 증상: 큰 적이 거의 죽은 채로 끝까지 걸어감. 원인: `max_hp` 기준 정렬. 고침: 현재 `hp` 기준, 동점은 진행도(§3.4).
5. **웨이브가 첫 적이 죽자마자 넘어감** → 증상: 웨이브 2 적이 웨이브 1 적과 섞여 나온다. 원인: 종료 조건에 "스폰 큐 비었음"이 없다. 고침: `not spawn_queue and not enemies` 둘 다(§3.3 함정 ③).
6. **클라이언트가 보낸 남은 시간으로 SLG 타이머가 즉시 완성** → 증상: 결제 없이 15일 건물이 1초에 끝난다. 원인: `remaining`을 요청 본문에서 읽음. 고침: 서버 `finish_at` 절대 시각만 믿고, 가속·도움은 서버가 `finish_at`을 당긴다(§3.6, §5).
7. **오토배틀러에서 상대가 산 유닛이 내 상점에 같은 확률로 나옴** → 증상: 8명이 같은 조합을 완성한다. 원인: 풀을 플레이어별로 복사했거나 `release` 없이 `draw`만 구현. 고침: 방 단위 `SharedPool` 하나, 구매 시 감소·판매/탈락 시 반환(§3.7).
8. **리플레이가 원판과 다르게 끝남** → 증상: 같은 시드인데 결과가 다르다. 원인: 명령이 발행 틱이 아니라 "도착 순서"로 적용되거나, 파티클 RNG가 시뮬 RNG를 소비. 고침: `(exec_tick, player, seq)` 정렬, 시뮬 RNG 분리(§3.8).
