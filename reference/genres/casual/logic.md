# 캐주얼 기본 베이스 로직

> 엔진 무관. 구현 전에 읽는 설계 뼈대. 숫자는 README §4에서만. 시뮬레이션으로 검증한 규칙에는 ✅ 표시.
> 확인일 2026-10-17. 대표작·루프·수치·원전은 [`README.md`](README.md), 정렬 퍼즐 생성·솔버 상세는 [`puzzle_levels.md`](puzzle_levels.md), 매치3·2048 한 장 요약은 [`../../systems/genres.md`](../../systems/genres.md).

> 수치 출처 표기: README §4 표에는 시장 수치(매출·DL·리텐션)만 있고 게임플레이 수치는 없다. 따라서 이 문서의 게임플레이 값(보드 크기·무브·목숨·가격 등)은 **전부 "예시값"**이며, README §3에 언급된 값(4색·평균 25무브 [47], 목숨 5개 [46], "무브 +5" 컨티뉴)은 "예시값(README §3 언급)"으로 구분한다.

## 0. 최소 플레이 가능 단위 (MVP 루프)

도형 그래픽으로 1~2일 안에 만드는 범위. 하위 장르는 **레벨형 매치3**를 뼈대로 하고, **정렬(sort) 퍼즐**을 변형 1로 둔다.

**넣는 것**
- 엔티티: `Board`(8×8 int 그리드, 예시값), `Tile`(색 int), `Level`(JSON: seed·무브·목표), `LevelRun`(한 판 상태), `Profile`(목숨·코인·별)
- 규칙: 인접 스왑 → 3줄 매치 → 제거 → 낙하 → 리필 → 연쇄 → 데드락이면 셔플. 무브 0에 목표 미달이면 실패, 목표 달성이면 승리.
- 경제: 목숨 5개(예시값, README §3 언급) 실패 시 1 차감, 타임스탬프 재생. 실패 시 "무브 +5" 컨티뉴 오퍼(코인) → 보상형 광고 → 목숨 차감.
- 화면: 레벨 맵(번호만) · 플레이 보드 · 승리/실패 팝업(컨티뉴 버튼 포함). 셋이면 한 판이 성립한다.
- 변형 1(정렬 퍼즐): 통 N개·용량 4(예시값), 같은 색 위로만 붓기. 레벨은 **완성 상태에서 역순 섞기 → BFS 솔버 검증 → 불합격 폐기**로 만든다.

**넣지 않는 것**
- 스페셜 피스(로켓·TNT·라이트볼), 블로커(얼음·상자), 사전 부스터, 별 3개 채점 UI, 레벨 맵 장식, 결제·광고 SDK 연동, 이벤트·시즌, 소셜(목숨 선물), 2048·머지 보드(에너지 규칙만 §3.7에 둔다).

## 1. 게임 흐름 상태 머신

공통 뼈대(레벨형 퍼즐 전체에 적용):

```
Lobby ──(레벨 선택, lives>0)──▶ Playing ──(목표 달성)──▶ Won ──(보상 수령)──▶ Lobby
  ▲                              │  ▲                       
  │                              │  └──(컨티뉴 수락: 코인 또는 보상형 광고)── Failed
  │                              └──(무브 0 & 목표 미달)──▶ Failed ──(거절: lives−1)──▶ Lobby
  └──(lives==0)── LivesEmpty ──(재생 타이머 또는 리필 구매)──▶ Lobby
```

| 상태 | 허용 입력 | 전이 조건 |
|---|---|---|
| Lobby | 레벨 선택, 상점, 장식 메타 | `lives > 0` 이면 Playing, 아니면 LivesEmpty |
| Playing | 인접 스왑 1회 (처리 중에는 잠금), 부스터 사용, 일시정지 | `remaining == 0` → Won, `moves_left == 0` → Failed |
| Resolving (Playing의 하위) | **입력 없음** | 연쇄 종료 + 데드락 검사 후 Playing 복귀 |
| Failed | 컨티뉴 구매, 보상형 광고 시청, 포기 | 수락 → Playing(+5 무브), 포기 → Lobby(lives−1) |
| Won | 보상 수령 | 별·코인 지급 후 Lobby |
| LivesEmpty | 리필 구매, 대기 | `lives > 0` 되면 Lobby |

변형 1 — 정렬 퍼즐: Playing의 입력이 "통 A 탭 → 통 B 탭"(붓기)으로 바뀌고 무브 제한 대신 **"합법 수 없음 = 실패"**(빈 통 추가 부스터가 컨티뉴 역할). Resolving 상태는 없다(연쇄가 없음).
변형 2 — 머지/타이머형: Playing 진입 조건이 `lives > 0` 대신 `energy >= tap_cost`. 실패 상태가 없고 에너지 고갈이 LivesEmpty를 대신한다.

## 2. 엔티티와 데이터 모델

| 엔티티 | 핵심 필드(타입) | 소유 | 저장 |
|---|---|---|---|
| Level | `id:int, seed:int, rows:int, cols:int, colors:int, moves:int, goal:{type,color,count}`, 선택 `board:int[][]` | 서버/빌드 자산 (읽기 전용) | 자산(JSON) |
| Match3Board | `grid:int[rows][cols]` (−1 = 빈 칸), `rng:Random(seed)` | 권위 측 시뮬 코어 | 저장 안 함 (seed로 재현) |
| LevelRun | `state:enum, moves_left:int, collected:int, continues_used:int, history:[(a,b,cascades)]` | 권위 측 | 진행 중인 판만 임시 저장(앱 종료 복구용) |
| Profile | `version:int, lives:{value,last:int}, coins:int, stars:int, energy:{value,last:int}, level_progress:int, decorations:[id]` | 권위 측 | 저장 (version 필드 필수) |
| BoosterInventory | `{booster_id: count}` | 권위 측 | 저장 |
| SortLevel | `capacity:int, tubes:int[][]`, 생성 시 `solution_len:int` | 빌드 자산 | 자산(JSON, 솔버 통과분만) |
| AdState | `rewarded_this_level:int, last_interstitial:int` | 클라이언트(노출) + 서버(보상 지급 판정) | 세션 한정 |
| Collection(메타) | `decorations:[id], next_cost_stars:int` | 권위 측 | 저장(Profile에 포함) |

밸런스 Config (실제 파싱 가능, `sim/casual_sim.py`의 `CONFIG`와 같은 값. README §4에 없으므로 전부 **예시값**):

```json
{
  "version": 1,
  "match3": {
    "rows": 8, "cols": 8, "colors": 4, "moves": 25,
    "goal": {"type": "collect", "color": 0, "count": 40},
    "continue_moves": 5, "continue_cost": 900, "continue_max_per_level": 1,
    "star_moves_left": [0, 3, 8]
  },
  "sort": {"capacity": 4, "colors": 6, "empty_tubes": 2, "scramble_steps": 40, "solver_node_budget": 200000},
  "lives": {"max": 5, "regen_sec": 1800},
  "energy": {"cap": 100, "regen_sec": 120, "tap_cost": 1},
  "ads": {"rewarded_contexts": ["loss_recovery"], "rewarded_per_level": 1},
  "difficulty": {"target_fail_rate": 0.5, "near_miss_remaining": 5, "bot_levels": 30},
  "meta": {"decoration_cost_stars": 3}
}
```

`colors: 4`, `moves: 25`, `lives.max: 5`, `continue_moves: 5`는 README §3 언급값. `difficulty.target_fail_rate: 0.5`는 [`puzzle_levels.md`](puzzle_levels.md) ★등불 항구 6항(SayGames: 실패율 50% ≈ 평균 2회 시도)에서 가져온 목표치.

## 3. 핵심 시스템

### 3.1 보드 모델과 매치3 처리 순서
- 규칙: 보드는 렌더와 분리된 2차원 int 배열이다. 한 수는 **스왑 → 매치 탐색 → 제거 → 낙하 → 리필 → (매치가 남아 있으면) 반복**의 고정 순서로 처리되며, 처리 중에는 입력을 받지 않는다. 매치가 생기지 않는 스왑은 되돌리고 무브를 소모하지 않는다. 리필은 **새 타일이 즉시 매치를 만들지 않는 색**만 고른다([`../../systems/genres.md`](../../systems/genres.md) 퍼즐 절).
- 공식: 리필 후보 `cands(r,c) = {k | run_h(r,c,k) < 3 ∧ run_v(r,c,k) < 3}`. 낙하 후 빈 칸은 열의 위쪽에만 있고 아래 행부터 채우므로 금지색은 최대 3개(왼쪽 줄·오른쪽 줄·아래 줄) → `colors ≥ 4`이면 후보가 항상 존재한다.
- 의사코드:
```
function play_swap(board, a, b) -> (removed: map<color,int>, cascades: int, shuffled: bool) | null
    if preview_swap(board, a, b) is empty: return null       // 매치 없는 스왑 = 무효
    swap(board, a, b)
    removed, cascades = {}, 0
    loop:
        cells = find_matches(board)                            // 가로·세로 3줄 이상
        if cells is empty: break
        removed += clear(board, cells)
        apply_gravity(board)                                   // 열마다 아래로 압축
        refill(board, rng)                                     // 아래 행부터, 즉시 매치 금지색 제외
        cascades += 1
    shuffled = not has_valid_move(board)
    if shuffled: shuffle(board, rng)                           // §3.2
    return removed, cascades, shuffled
```
- 함정: (1) 리필을 위에서 아래로 채우면 아래 칸이 비어 있어 세로 금지색을 계산하지 못한다. (2) `colors == 3`이면 금지색 3개로 후보가 비어 fallback이 매치를 만든다 — 연쇄로 처리되긴 하지만 "리필은 매치를 만들지 않는다"는 보장이 깨진다. (3) 되돌린 스왑에 무브를 차감하면 데드락 직전 플레이어가 억울하게 진다.
- 검증 ✅ `test_match3_processing_order`, `test_refill_no_immediate_match`

### 3.2 데드락 검사와 셔플
- 규칙: 연쇄가 끝날 때마다 "매치를 만드는 인접 스왑"이 하나라도 있는지 검사한다. 없으면 타일 다중집합을 보존한 채 섞고, **매치 없음 + 유효 수 있음**이 될 때까지 반복한다. 시도 상한을 두고, 상한을 넘기면 레벨 데이터 오류로 본다(타일 구성상 유효 수가 불가능한 경우).
- 공식: `has_valid_move = ∃(a,b) 인접 : |find_matches(swap(a,b))| > 0`. 8×8 보드는 인접 쌍 112개 × 매치 탐색 1회 — 턴마다 돌려도 충분히 싸다.
- 의사코드:
```
function shuffle(board, rng, max_tries = 200) -> int
    tiles = flatten(board.grid)
    for i in 1..max_tries:
        rng.shuffle(tiles)
        board.grid = reshape(tiles)
        if find_matches(board) is empty and has_valid_move(board): return i
    raise LevelDataError("유효 수를 만들 수 없는 타일 구성")
```
- 함정: (1) 셔플로 생긴 매치를 그대로 두면 플레이어 입력 없이 연쇄가 터져 무브 없이 목표가 줄어든다. (2) 셔플에 새 RNG를 쓰면 리플레이(§3.3)가 깨진다 — 반드시 레벨 RNG를 쓴다. (3) 셔플 애니메이션 중 입력을 열어두면 보드가 꼬인다(FSM Resolving 상태로 잠근다).
- 검증 ✅ `test_deadlock_shuffle`

### 3.3 결정론적 레벨 데이터와 리플레이
- 규칙: 레벨은 JSON 하나(`seed, rows, cols, colors, moves, goal`, 선택 `board`)로 완전히 정의된다. 보드 생성·리필·셔플은 모두 `Random(seed)` 하나에서 뽑으므로 **같은 레벨 + 같은 입력 열 = 같은 결과**다. 재시작해도 같은 판이 나오고(puzzle_levels ★6), 서버는 입력 열만 받아 재시뮬레이션으로 결과를 검증할 수 있다.
- 공식: `outcome = simulate(level_json, inputs)` — 순수 함수. `history = [(a, b, cascades)]`가 리플레이 로그이자 검증 입력이다.
- 의사코드:
```
function play_level(level, policy) -> LevelRun
    run = LevelRun(level)                     // rng = Random(level.seed), board = fill(rng)
    while run.state == Playing:
        a, b = policy(run.board, level.goal)
        run.step(a, b)                        // play_swap → moves_left−1 → collected += removed[goal.color]
                                              // remaining==0 → Won, moves_left==0 → Failed
    return run
```
- 함정: (1) 봇·UI·서버가 각각 다른 RNG 인스턴스를 만들면 같은 seed라도 결과가 다르다 — RNG는 `LevelRun`이 하나만 소유한다. (2) `valid_swaps()` 스캔 순서가 바뀌면 봇의 동률 선택이 바뀌어 난이도 측정값이 달라진다. (3) JSON 키 순서에 의존하지 않는다(`sort_keys`로 직렬화해 diff 가능하게).
- 검증 ✅ `test_level_replay_deterministic`

### 3.4 정렬 퍼즐 레벨 생성(역순 섞기)과 BFS 솔버 검증
- 규칙: Water/Ball Sort의 해결 가능성 판정은 NP-완전이므로(README §5 Ito et al. [38]) 공식으로 판정하지 않고 **생성 → 솔버 검증 → 불합격 폐기**한다. 생성은 완성 상태(색별 단색 통 + 빈 통)에서 **정방향 합법 수의 정확한 역수**만 적용해 섞는다. 정방향 수 `a→b, n개`의 역은 "b 위의 색 k n개를 a 위로 되돌리기"인데, 되돌린 뒤 정방향이 정확히 n개만 붓도록 (i) a의 top이 k가 아니고 (ii) 되돌린 뒤 b가 비었거나 b.top == k여야 한다. 그래도 최종 검증은 BFS 솔버(노드 예산)로 한다.
- 공식: 정방향 합법 수 `(s, d, n)`: `top(s)=k, run(s)=r, d≠s, |d|<cap, (d 빈 통 ∨ top(d)=k), n = min(r, cap−|d|)`. 단색 통→빈 통, 완성된 통에서 붓기는 제외(상태 공간만 늘린다). 상태 키는 통 순서를 정렬한 튜플(통은 교환 가능).
- 의사코드:
```
function generate_verified(rng, cfg) -> SortLevel | null
    for try in 1..max_tries:
        tubes = [[k]*cap for k in colors] + [[] for _ in empty_tubes]
        repeat cfg.scramble_steps:
            cands = all reverse moves (b -> a, n) satisfying (i),(ii)
            if cands empty: break
            apply rng.choice(cands)
        n = bfs_solve(tubes, cap, cfg.solver_node_budget)   // 최단 해 길이 또는 null
        if n is not null and n > 0: return {tubes, cap, solution_len: n}
    return null                                              // 폐기

function bfs_solve(tubes, cap, budget) -> int | null
    seen = {canonical(tubes)}; q = [(tubes, 0)]
    while q: state, d = q.pop_front()
        for mv in legal_moves(state): nxt = apply(state, mv)
            if canonical(nxt) in seen: continue
            if solved(nxt): return d + 1
            seen.add(canonical(nxt)); if |seen| > budget: return null
            q.push((nxt, d + 1))
    return null
```
- 함정: (1) 역수를 "아무 통에서 아무 통으로 옮기기"로 느슨하게 두면 정방향으로 되돌릴 수 없는 상태가 섞인다 — 그래서 솔버 검증을 생략하면 안 된다. (2) 상극 잠금·숨은 색 같은 추가 제약은 **역 섞기 뒤에** 얹고 다시 검증한다(puzzle_levels ★오행 정리 2). (3) 통 순서를 정규화하지 않으면 BFS 상태 수가 `N!`배 부푼다.
- 검증 ✅ `test_sort_pour_rule`, `test_sort_reverse_generation_solvable`

### 3.5 난이도 추정: 봇 승률과 아슬아슬(near-miss) 비율
- 규칙: 레벨 난이도의 1차 지표는 **봇 플레이테스트 승률**이다(King은 CNN 모방학습 봇, README §3 [34]; MVP는 탐욕 봇). 레벨 N판(seed만 바꿔)을 돌려 실패율을 목표(50%, puzzle_levels ★6)와 비교하고, 실패 중 "남은 목표 ≤ k"인 비율을 near-miss 비율로 따로 본다 — near-miss는 패배보다 재도전·과금 동기가 높다(README §3 [36]).
- 공식: `fail_rate = fails / N`, `near_miss_rate = |{fail : remaining ≤ near_miss_remaining}| / fails`, 판정 `too_hard` if `fail_rate > target + 0.2`, `too_easy` if `< target − 0.2`. 탐욕 봇 점수 `score(swap) = 10·(목표색 제거 수) + (총 제거 수)`.
- 의사코드:
```
function estimate_difficulty(template, N, base_seed) -> {win_rate, fail_rate, near_miss_rate, verdict}
    wins = near = 0
    for i in 0..N-1:
        run = play_level(template with seed = base_seed + i, greedy_bot)
        if run.state == Won: wins += 1
        else if run.remaining() <= cfg.near_miss_remaining: near += 1
    ...
```
- 측정 예(시뮬, 8×8·4색·25무브·탐욕 봇·30판): 목표 40개 → 실패율 0.00(too_easy), **60개 → 0.57(ok, near-miss 0.18)**, 80개 → 0.97(too_hard). 즉 이 봇·보드에서는 `goal.count`가 가장 민감한 다이얼이다. 봇 승률은 사람 승률이 아니므로 출시 후 실제 실패율로 회귀 보정한다(puzzle_levels §3 van Kreveld).
- 함정: (1) 봇이 사람보다 강하면 "ok"가 사람에게는 too_hard다 — 봇 승률은 레벨 간 **상대 순서**로만 쓴다. (2) N이 작으면 ±0.2 밴드가 노이즈에 묻힌다. (3) 무브를 늘리면 승률이 떨어지지 않아야 한다(같은 seed에서 앞 무브의 플레이가 같으므로) — 이 단조성이 깨지면 RNG 공유 버그다.
- 검증 ✅ `test_bot_winrate_and_near_miss`

### 3.6 목숨·무브·부스터 경제와 "무브 +5" 컨티뉴 오퍼
- 규칙: 과금 지점은 (1) 레벨 시작 전 부스터, (2) 레벨 중 부스터, (3) 실패 직후 "무브 +5" 컨티뉴(README §3). MVP는 (3)만 구현한다. 실패 시 분기: **코인 컨티뉴(레벨당 상한) → 보상형 광고 컨티뉴(§3.8) → 목숨 차감**. 모든 재화 증감은 단일 함수 `wallet.add(kind, amount, reason)`를 거치고 잔액 부족이면 거부한다([`../../systems/core_systems.md`](../../systems/core_systems.md) §4). 목숨은 `TimedResource`(상한·재생 간격·타임스탬프)로 관리한다.
- 공식: `lives(now) = min(cap, value + ⌊(now − last) / regen_sec⌋)`, 가득 차 있으면 `last = now`(타이머 정지). `now < last`(시계 역행)이면 재생 0.
- 의사코드:
```
function fail_flow(run, wallet, lives, ads, now, choice) -> "continued" | "continued_ad" | "life_lost"
    assert run.state == Failed
    if choice == "buy" and run.continues_used < cfg.continue_max_per_level
       and wallet.add("coins", -cfg.continue_cost, "continue_moves"):
        run.grant_continue(cfg.continue_moves); return "continued"     // Failed → Playing, moves += 5
    if choice == "ad" and ads.show_rewarded("loss_recovery"):
        run.grant_continue(cfg.continue_moves); return "continued_ad"
    lives.spend(now); return "life_lost"
```
- 함정: (1) 컨티뉴를 무제한으로 두면 "어려운 레벨 = 무한 과금"이 되어 리뷰가 무너진다 — 레벨당 상한 또는 가격 상승. (2) 목숨 재생을 매 프레임 `value += dt/regen`으로 누적하면 부동소수 오차와 시계 조작에 취약하다 — 타임스탬프 차이로만 계산. (3) 컨티뉴 뒤 `continues_used`를 리셋하면 상한이 의미 없다.
- 검증 ✅ `test_continue_offer_plus5`, `test_lives_energy_regen_cap`

### 3.7 에너지/타이머 (머지 변형)
- 규칙: 머지류는 목숨 대신 **에너지**가 세션을 제한한다(README §3 Gossip Harbor: 제너레이터 탭당 소모, 리필 가격은 사용할수록 상승). 에너지는 목숨과 같은 `TimedResource`다: 상한, 재생 간격, 타임스탬프 기반, 시계 역행 무시. 구매·광고로 상한을 넘겨 줄 수는 있으나 넘긴 동안 재생은 멈춘다.
- 공식: §3.6과 동일. `tap_cost`만큼 소모하고 `energy(now) < tap_cost`면 입력 거부.
- 의사코드:
```
class TimedResource(cap, regen_sec, now):
    current(now): if now < last or value >= cap: last = now
                  else: g = (now − last) // regen_sec; value = min(cap, value + g); last += g·regen_sec
                  return value
    spend(now, n): ok = current(now) >= n; if ok: value −= n; return ok
```
- 함정: (1) 가득 찬 상태에서 `last`를 갱신하지 않으면 첫 소모 직후 수 시간치가 한꺼번에 재생된다. (2) 상한 위 잔량(구매분)을 `min(cap, …)`로 깎아 버리면 결제 분쟁이 난다 — 재생만 멈추고 값은 보존.
- 검증 ✅ `test_lives_energy_regen_cap`

### 3.8 광고 배치 규칙과 하이브리드 메타 훅
- 규칙: 보상형 광고는 **손실 회복 자리**(실패 직후 컨티뉴, 목숨 0)에만 붙이고 레벨당 횟수를 제한한다 — 유저가 원할 때만 보게 해야 리텐션을 해치지 않는다(README §6 "광고 로드 과다", genres.md 수익화 체크리스트). 전면 광고는 레벨 N 이후·쿨다운(README §6 하이퍼캐주얼 함정)이며 MVP 범위 밖. 메타 훅은 승리 → 별(남은 무브 임계) → 별로 장식/수집 해금 한 가지만 둔다(README §3 하이브리드 캐주얼: 코어 리텐션 먼저, 메타는 뒤).
- 공식: `can_rewarded(ctx) = ctx ∈ rewarded_contexts ∧ shown_this_level < rewarded_per_level`. `stars = |{t ∈ star_moves_left : moves_left ≥ t}|` (승리 시만).
- 의사코드:
```
function show_rewarded(ads, context) -> bool
    ok = context in cfg.ads.rewarded_contexts and ads.rewarded_this_level < cfg.ads.rewarded_per_level
    if ok: ads.rewarded_this_level += 1       // 보상 지급은 광고 SDK 콜백(서버 검증) 뒤에
    return ok
function on_win(run, wallet): s = run.stars(cfg.star_moves_left); if s: wallet.add("stars", s, "level_win")
function unlock_decoration(wallet): return wallet.add("stars", -cfg.meta.decoration_cost_stars, "decoration")
```
- 함정: (1) 광고 "시작" 콜백에서 보상을 주면 중간 이탈로도 보상이 나간다 — 완료 콜백(가능하면 서버 측 검증, SSV)에서만. (2) 별을 레벨 재플레이마다 다시 주면 메타 재화가 인플레이션한다 — 레벨별 최고 별만 반영. (3) 메타가 코어보다 먼저 복잡해지면 D7이 아니라 D1만 오른다.
- 검증 ✅ `test_rewarded_ad_placement`, `test_meta_collection_hook`

## 4. 틱 / 업데이트 순서

캐주얼 퍼즐은 **턴(입력) 단위**로 시뮬레이션하고, 시간 자원은 타임스탬프로 계산하므로 고정 틱이 필요 없다(core_systems §1: 물리가 없으면 가변 dt로 충분). 권위 측(온라인이면 서버, 오프라인 싱글이면 클라이언트의 시뮬 코어)이 한 턴에 하는 일:

1. **입력 수집** — `Playing` 상태에서만 스왑 1건 수락. `Resolving` 중 입력은 버린다(큐잉하지 않는다).
2. **유효성** — 인접 여부, 좌표 범위, `preview_swap`이 매치를 만드는지. 무효면 보드 되돌리고 무브 미소모.
3. **시뮬** — 스왑 → 매치 → 제거 → 낙하 → 리필 → 연쇄 반복 (§3.1). 모든 난수는 레벨 RNG.
4. **데드락 검사·셔플** (§3.2).
5. **판정** — `collected` 갱신 → `remaining == 0` → Won, 아니면 `moves_left == 0` → Failed.
6. **보상/경제** — Won: 별·코인 `wallet.add`. Failed: 컨티뉴 오퍼 상태로(과금·광고는 다음 입력에서).
7. **저장/스냅샷** — 상태 전이(Won/Failed/컨티뉴/목숨 차감) 직후와 앱 백그라운드 진입 시 Profile 저장. 진행 중인 `LevelRun`은 `history`만 저장하면 seed로 복구된다.
8. **렌더** — 권위 측이 돌려준 `(removed, cascades, shuffled)`로 클라이언트가 애니메이션을 재생. 애니메이션 길이는 로직에 영향을 주지 않는다.

틱 주기: 입력 이벤트 구동(턴당 1회). 목숨·에너지 UI 갱신은 1Hz 폴링이면 충분(예시값; 값 자체는 호출 시점에 타임스탬프로 계산하므로 폴링 주기가 로직에 영향을 주지 않는다).

## 5. 신뢰 경계

오프라인 싱글이면 클라이언트가 권위다(core_systems §7). 랭킹·결제·광고 보상·서버 목숨 중 하나라도 있으면 아래를 서버가 검증한다.

| 클라이언트가 보내는 것 | 서버가 검증하는 규칙 | 거부 시 처리 |
|---|---|---|
| 레벨 결과 `{level_id, history:[(a,b)]}` | 같은 seed로 **재시뮬레이션**해 Won/Failed·별이 일치하는지. `len(history) ≤ moves + continues×5` | 결과 폐기, 진행도 미반영, 반복 시 플래그 |
| 컨티뉴 구매 `{level_id}` | 현재 상태가 Failed인지, `continues_used < max`, 코인 잔액(단일 함수 `wallet.add`) | 거부 응답, 상태 불변 |
| 보상형 광고 완료 `{ad_token}` | 광고 네트워크 SSV 콜백과 토큰 일치, 레벨당 횟수, 문맥이 `loss_recovery`인지 | 보상 미지급 |
| 목숨 사용 `{level_id}` | 서버 시간으로 `lives(now) > 0`. 클라이언트 시계는 무시 | 플레이 거부 |
| 에너지 소모 `{n}` | 서버 시간으로 `energy(now) ≥ n`, 상한 위 잔량 보존 | 거부 |
| 별로 장식 해금 `{deco_id}` | 잔액·해금 선행 조건, 중복 해금 | 거부 |
| 결제 영수증 | 영수증 ID 멱등 처리(core_systems §6), 상품 ID ↔ 지급량 테이블 | 중복이면 지급 생략 |
| 레벨 데이터 요청 | 서버/빌드 자산만 신뢰. 클라이언트가 보낸 `board`·`moves`는 무시 | — |

재화·점수·확률(리필 색 포함)·보상은 **항상 서버**가 결정한다. 리필 색까지 서버 RNG로 재현되므로 클라이언트는 보드를 "보여주기"만 한다.

## 6. 밸런스 다이얼

| 다이얼 | 무엇을 바꾸나 | 기본값(출처) | 올리면 / 내리면 체감 |
|---|---|---|---|
| `match3.colors` | 보드 색 수 | 4 (예시값, README §3 [47] 언급) | 올리면 매치·연쇄가 줄어 어려움 / 내리면 연쇄 폭발, 3이면 리필 보장 깨짐 |
| `match3.moves` | 레벨당 무브 | 25 (예시값, README §3 [47] 언급) | 올리면 승률 단조 증가 / 내리면 near-miss 빈도↑ |
| `match3.goal.count` | 목표 수집 수 | 40 (예시값) | 시뮬에서 가장 민감: 40→실패율 0.00, 60→0.57, 80→0.97 (탐욕 봇) |
| `match3.continue_cost` · `continue_max_per_level` | 컨티뉴 가격·상한 | 900 / 1 (예시값) | 올리면 과금 전환↓·이탈↑ / 상한 없으면 무한 과금 리뷰 |
| `lives.max` · `lives.regen_sec` | 세션 길이 | 5 / 1800s (예시값, 목숨 5개는 README §3 [46]) | 올리면 세션 길어지고 리필 과금↓ / 내리면 LivesEmpty 노출↑ |
| `sort.empty_tubes` | 정렬 퍼즐 주 난이도 손잡이 | 2 (예시값; puzzle_levels ★오행 3) | 올리면 쉬워지고 해 길이↓ / 내리면 해 없음 비율↑ (폐기율↑) |
| `sort.scramble_steps` | 역 섞기 깊이 | 40 (예시값) | 올리면 해 길이·상태 공간↑ / 내리면 거의 풀린 판 |
| `energy.cap` · `energy.regen_sec` | 머지 세션 길이 | 100 / 120s (예시값) | 올리면 과금 레버 약화 / 내리면 대기 벽 |
| `difficulty.target_fail_rate` | 레벨 승인 기준 | 0.5 (puzzle_levels ★6, SayGames) | 올리면 단기 전환↑·장기 리텐션↓ (King 레벨 65 A/B, README §3 [35]) |
| `ads.rewarded_per_level` | 광고 컨티뉴 상한 | 1 (예시값) | 올리면 광고 매출↑·IAP 컨티뉴 잠식 |

## 7. 플랫폼 매핑

| 시스템 | Godot | Roblox |
|---|---|---|
| 보드 시뮬 코어(§3.1~3.2) | 노드 없는 `RefCounted` 클래스(`Match3Board.gd`), 렌더는 `GridContainer`/`Sprite2D` 풀 — [`ObjectPool.gd`](../../platforms/godot/patterns/ObjectPool.gd) | `ServerScriptService`의 ModuleScript(순수 Luau 테이블), 클라이언트는 `ReplicatedStorage` 이벤트로 결과만 수신 |
| 레벨 데이터(§3.3) | `Resource` 서브클래스(`LevelData.gd`, [`architecture.md §4`](../../platforms/godot/architecture.md)) 또는 JSON. 세이브에는 `.tres` 금지 | `ReplicatedStorage/Config/Levels` ModuleScript 테이블 ([`architecture.md §4`](../../platforms/roblox/architecture.md)) |
| 게임 흐름 FSM(§1) | [`StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd) + [`State.gd`](../../platforms/godot/patterns/State.gd): Lobby/Playing/Resolving/Failed/Won | [`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau)의 상태 전이 구조를 레벨 단위로 축소 |
| 재화·컨티뉴(§3.6) | [`Economy.gd`](../../platforms/godot/patterns/Economy.gd) (단일 진입점, 1회 상한) | [`ShopService.luau`](../../platforms/roblox/patterns/ShopService.luau) + [`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau)(요청 검증·레이트 리밋) |
| 목숨·에너지(§3.6~3.7) | `Economy.gd`의 오프라인 보상 계산(타임스탬프·상한·시간 역행 0)과 같은 방식 | 서버 `os.time()` 기준, `DataStore`에 `{value, last}` 저장 — [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau) |
| 저장(§2 Profile) | [`SaveManager.gd`](../../platforms/godot/patterns/SaveManager.gd) (version·마이그레이션·원자적 저장·백그라운드 자동 저장) | [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau) (세션 잠금, version) |
| 이벤트(승리·실패·별) | [`EventBus.gd`](../../platforms/godot/patterns/EventBus.gd) 시그널 → 메타·분석·사운드 구독 | `BindableEvent`/Signal 모듈, 서버 내부 구독 |
| 정렬 퍼즐 생성·솔버(§3.4) | 오프라인: Godot 헤드리스 `--script` 또는 Python(`sim/casual_sim.py`) → JSON 자산 + CI 검증([`tests/`](../../platforms/godot/tests/) 방식). 런타임 Godot 시작점: Matswm86/water-sort (MIT, puzzle_levels §2) | 오프라인 생성 → ModuleScript 테이블. 런타임 BFS는 서버에서만, 노드 예산 필수 |
| 광고(§3.8) | 플러그인(AdMob 등) 완료 콜백 → `Economy.gd`로 보상. 미검증 영역(patterns README) | Roblox 보상형 동영상 광고 있음: `AdService` + Creator Hub(Monetization ⟩ Ads ⟩ Settings ⟩ Rewarded Video) 설정. 보상은 개발자 상품(Developer Product)만 가능(Robux 지급 불가), `ProcessReceipt`에서 지급. 조건: 공개·비제한 게임, 월평균 순방문자 2,000명 이상, 퍼블리셔 13세 이상·2FA·신분증 인증, 버튼 클릭 후 재생 — [Rewarded video ads](https://create.roblox.com/docs/production/promotion/rewarded-video-ads) (2026-10-19 확인, 문서에 베타 표기 없음). 시청자 측 노출 범위(연령·지역·기기) `미검증` |
| 난이도 봇(§3.5) | 헤드리스 CI에서 `casual_sim.py`와 같은 봇을 GDScript로 포팅하거나 Python 결과를 JSON으로 커밋 | 동일(오프라인) |

## 8. 검증 (sim/)

[`sim/casual_sim.py`](sim/casual_sim.py)가 검사하는 규칙 (테스트 이름 = §3의 ✅ 표기):

1. `test_refill_no_immediate_match` — 초기 채움·리필 직후 새 타일이 매치를 만들지 않는다 (20시드 × 5회).
2. `test_match3_processing_order` — 스왑→매치→제거→낙하→리필→연쇄가 끝나면 매치 없음·빈 칸 없음; 낙하 후 공중 타일 없음; 매치 없는 스왑은 되돌리고 무브 미소모.
3. `test_deadlock_shuffle` — 유효 수 없는 5×5 보드를 셔플하면 유효 수 있음·매치 없음·타일 다중집합 보존.
4. `test_level_replay_deterministic` — 같은 레벨 JSON을 두 번 돌리면 입력 열·결과·최종 보드가 같다.
5. `test_bot_winrate_and_near_miss` — 무브 10 vs 40에서 승률 단조, 같은 입력이면 같은 추정값, near-miss 비율·판정 범위.
6. `test_sort_pour_rule` — 붓기 합법 수(같은 색·빈 통·용량, 단색→빈 통 제외), 적용 결과, 빈 통 없는 교착은 해 없음, 완성 상태는 0수.
7. `test_sort_reverse_generation_solvable` — 역순 생성 30판 전부 BFS로 풀리고 색 다중집합 보존; 생성→검증→폐기 함수가 풀리는 레벨만 반환.
8. `test_lives_energy_regen_cap` — 목숨 차감·30분 재생·상한·상한에서 소모 시 타이머 재시작·시계 역행 무시·0이면 거부; 에너지 상한 재생.
9. `test_continue_offer_plus5` — 실패 → 코인 컨티뉴 +5 무브·Playing 복귀, 단일 진입점 로그, 잔액 부족 거부, 레벨당 1회 뒤엔 목숨 차감.
10. `test_rewarded_ad_placement` — 보상형은 `loss_recovery` 문맥에서만, 레벨당 1회.
11. `test_meta_collection_hook` — 승리 → 별 적립, 별로 장식 해금, 부족하면 거부.

```bash
python3 -I reference/genres/casual/sim/casual_sim.py --test   # 종료 코드 = 실패 수
python3 -I reference/genres/casual/sim/casual_sim.py --demo   # 시드 2026 한 판 + 봇 30판 + 정렬 레벨 1개
```

실행 결과(2026-10-17, Python 3 표준 라이브러리): **`passed 11/11`**, 종료 코드 0. 검증하지 않는 것은 [`sim/README.md`](sim/README.md).

## 9. 흔한 구현 버그

1. **애니메이션 중 스왑이 들어가 보드가 꼬임** → 렌더 완료를 기다리지 않고 입력을 받음 → FSM에 `Resolving` 상태를 두고 그 동안 입력을 버린다(큐잉 금지).
2. **리필 직후 플레이어가 아무것도 안 했는데 연쇄가 터짐** → 리필 색을 무작위로 뽑음, 또는 위에서 아래로 채워 세로 금지색을 못 봄 → 아래 행부터 채우고 가로·세로 금지색을 제외(§3.1).
3. **"움직일 수 있는 게 없어요"에서 멈춤** → 데드락 검사를 연쇄 후가 아니라 스왑 전에만 함 → `play_swap` 끝마다 `has_valid_move`, 없으면 셔플(§3.2).
4. **재시작하면 다른 보드가 나옴 / 서버 재검증 불일치** → 보드 생성·리필·셔플이 서로 다른 RNG를 씀 → `LevelRun`이 `Random(seed)` 하나를 소유하고 모든 난수를 거기서 뽑는다(§3.3).
5. **정렬 퍼즐에 "풀 수 없는 레벨" 리뷰** → 랜덤 생성만 하고 솔버 검증을 생략, 또는 역 섞기 뒤 잠금을 얹고 재검증 안 함 → 생성→BFS 검증→폐기 파이프라인, 추가 제약 뒤 재검증(§3.4).
6. **앱을 껐다 켜면 목숨이 한꺼번에 가득 참** → 가득 찬 동안 `last`를 갱신하지 않음, 또는 재생을 프레임마다 누적 → 가득 차면 `last = now`, 값은 타임스탬프 차이로만 계산(§3.6~3.7).
7. **기기 시계를 미래로 돌려 목숨·에너지 무한** → 클라이언트 시간을 신뢰 → 온라인이면 서버 시간, 오프라인이면 역행 시 재생 0 + 마지막 저장 시각 이전 무시(§5).
8. **같은 레벨을 반복 클리어해 별이 무한 적립** → 승리마다 별을 더함 → 레벨별 최고 별만 저장하고 차액만 지급(§3.8).
