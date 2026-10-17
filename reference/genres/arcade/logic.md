# 아케이드 · Roblox 포맷 기본 베이스 로직

> 엔진 무관. 구현 전에 읽는 설계 뼈대. 숫자는 README §4에서만. 시뮬레이션으로 검증한 규칙에는 ✅ 표시.
> 확인일 2026-10-17. 대표작·원전은 [`README.md`](README.md), 포맷별 자료는 [`roblox_formats.md`](roblox_formats.md).

이 폴더는 한 장르가 아니라 **작은 포맷의 묶음**이다(Obby · 타이쿤 · 러너 · .io · 미로 탈출 · 라운드제 · 무체크포인트 등반). 그래서 §1은 공통 뼈대 하나와 변형 둘, §3는 포맷마다 시스템 하나씩이다. 공통 시스템(FSM, RNG, 경제, 저장, 신뢰 경계)은 [`../../systems/core_systems.md`](../../systems/core_systems.md)에 있고 여기서는 링크만 한다.

## 0. 최소 플레이 가능 단위 (MVP 루프)

포맷마다 "한 판"이 다르므로, **라운드제 + 포맷 하나**를 MVP로 잡는다. 도형 그래픽으로 1~2일.

**넣는 것**
- 엔티티: 플레이어(위치·상태), 맵 1장(또는 생성기 1개), 결과판.
- 규칙: 라운드 상태 머신(§1), 포맷 하나의 핵심 판정(§3 중 하나), 서버 보상 1종(승리/참가).
- 화면: 상태·남은 시간 표시, 포맷 고유 수치 1개(스테이지 번호 · 코인 · 거리 · 크기 · 최고 높이 중 하나), 결과 목록.
- 포맷별 최소 판정 — Obby: 체크포인트 3개 · 타이쿤: 버튼 3개(드로퍼 → 컨베이어 → 드로퍼2) · 러너: 청크 3종 · .io: 펠릿과 플레이어 1:1 · 미로: 15×15 생성 + 출구 · 등반: 발판 10개와 추락 거리 표시.

**넣지 않는 것**
- 저장(타이쿤 제외: 구매 ID 목록은 MVP에도 넣는다, 아니면 설계가 틀어진다), 상점·게임패스, 리더보드, 팀, 관전, 맵 2장 이상, 애니메이션·파티클, 오브젝트 풀링(러너는 "나중에 풀링으로 바꾼다"는 주석만).

## 1. 게임 흐름 상태 머신

서버만 상태를 바꾸고 클라이언트는 표시만 한다([`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau)의 Attribute 구독 방식).

**공통 뼈대 (라운드제)**

```
Lobby ──(인원 ≥ min_players)──▶ Intermission ──(타이머 0)──▶ Round ──(타이머 0 또는 생존 ≤ 1)──▶ Results ──(타이머 0)──▶ Lobby
  ▲                                   │
  └────────(인원 < min_players)───────┘
```

| 상태 | 들어갈 때 | 허용 입력 | 나갈 조건 |
|---|---|---|---|
| Lobby | 캐릭터를 로비에 두고 타이머 0 | 이동·상점·설정 | 접속 인원 ≥ `min_players` |
| Intermission | 타이머 = `intermission_s`, 다음 맵 결정 | 이동·상점 | 타이머 0 → Round / 인원 부족 → Lobby |
| Round | 타이머 = `round_s`, 참가자·생존자 집합 확정, 아레나 텔레포트 | 포맷 고유 입력만(점프·이동·구매 요청) | 타이머 0 **또는 생존 ≤ 1** → Results |
| Results | 타이머 = `results_s`, 보상 지급(서버) | 없음(표시만) | 타이머 0 → Lobby |

**변형 A: 영구 월드 (Obby · 타이쿤 · 무체크포인트 등반).** 라운드가 없다. 플레이어마다 `Joining → Playing → Leaving` 셋뿐이고, 진행도(스테이지 번호 · 구매 ID 목록 · 최고 높이)가 상태를 대신한다. `Joining`에서 저장 데이터로 월드를 **재구성**하고(§3.2), `Leaving`에서 저장한다.

**변형 B: 상시 입장 (.io · 러너).** 라운드 대신 **개인 생명 주기**가 루프다. `Spawn → Alive → Dead → (즉시) Spawn`. 서버 월드는 계속 돌고 플레이어만 들락거린다. 죽었을 때 결과(최대 크기·거리)를 서버가 기록한 뒤 리스폰한다.

## 2. 엔티티와 데이터 모델

| 엔티티 | 핵심 필드(타입) | 소유 | 저장 |
|---|---|---|---|
| RoundState | `state(enum)`, `timer(int)`, `map_id(str)`, `participants(set)`, `alive(set)` | 서버(Attribute로 복제) | 아니오 |
| ObbyProgress | `player`, `stage(int, 0=시작)` | 서버 | **예** (stage만) |
| TycoonPlot | `owner`, `purchased(set<str>)`, `coins(int)`, `income_per_s(파생)` | 서버 | **예** (`version`, `purchased`, `coins`) |
| TycoonButtonDef | `id`, `cost(int)`, `requires(list<str>)`, `income_per_s(int)` | Config(공유) | Config |
| RunnerTrack | `seed(int)`, `chunks(list<(dist, id, tier)>)`, `speed(float)` | 서버 생성, 클라가 미리 받아 렌더 | 아니오 (seed만 로그) |
| ChunkDef | `id`, `tier(int)` | Config | Config |
| IoCell | `owner`, `pos`, `size(float, 반지름)`, `mass(파생 size²/100)` | 서버 | 아니오 (최대 크기는 통계로) |
| Maze | `seed`, `w,h`, `passages(adjacency)`, `exit`, `path_ratio(float)` | 서버 | 아니오 (seed·ratio만 로그) |
| ClimbStats | `player`, `best_height(float)`, `falls(list<float>)` | 서버 | 예 (best_height, biggest_fall) |

밸런스 Config (시뮬레이션의 `CONFIG`와 같은 값). OgarII 공식의 88 · −0.4396754 · 100 · 64 · 0.4 · 1920 은 README §4 출처, 경로 비율 창 0.55~0.72는 [`roblox_formats.md`](roblox_formats.md)의 예시 창, **그 밖은 전부 예시값**:

```json
{
  "round": {"min_players": 2, "intermission_s": 15, "round_s": 90, "results_s": 5,
            "win_reward": 50, "participation_reward": 10, "maps": ["A", "B", "C"]},
  "obby": {"stage_count": 50},
  "tycoon": {"offline_cap_s": 28800,
             "buttons": [{"id": "dropper1", "cost": 0, "requires": [], "income_per_s": 1},
                         {"id": "conveyor", "cost": 50, "requires": ["dropper1"], "income_per_s": 0},
                         {"id": "dropper2", "cost": 200, "requires": ["conveyor"], "income_per_s": 3},
                         {"id": "upgrader", "cost": 500, "requires": ["dropper2"], "income_per_s": 5},
                         {"id": "dropper3", "cost": 1500, "requires": ["conveyor", "upgrader"], "income_per_s": 12}]},
  "runner": {"base_speed": 16, "accel_per_s": 0.4, "max_speed": 40, "chunk_len": 60, "tier_every_m": 300,
             "chunks": [{"id": "flat", "tier": 1}, {"id": "gap", "tier": 1}, {"id": "double_gap", "tier": 2},
                        {"id": "swing", "tier": 2}, {"id": "laser_grid", "tier": 3}, {"id": "collapse", "tier": 3}]},
  "io": {"speed_base": 88, "speed_exp": -0.4396754, "mass_div": 100,
         "zoom_ref": 64, "zoom_exp": 0.4, "view_w": 1920,
         "eat_margin": 1.15, "start_size": 32, "pellet_size": 10},
  "maze": {"width": 15, "height": 15, "ratio_min": 0.55, "ratio_max": 0.72, "max_attempts": 50},
  "climb": {"fall_min": 10}
}
```

## 3. 핵심 시스템

### 3.1 Obby 체크포인트 진행 (서버 검증)
- **규칙.** 플레이어의 진행도는 서버가 가진 정수 `stage` 하나다. 클라이언트(또는 Touched 이벤트)가 "체크포인트 N에 닿았다"고 알리면 서버는 **`N == stage + 1`일 때만** 올린다. `N ≤ stage`는 리스폰 후 같은 발판을 다시 밟은 것이니 무시하고(치트 아님), `N ≥ stage + 2`는 스킵이므로 거부한다. 유료 스킵은 클라이언트가 목표 스테이지를 정하지 않고 서버가 `stage + 1`로만 올린다.
- **공식.** 없음. 범위 검사: `1 ≤ N ≤ stage_count`, 정수.
- **의사코드.**
  ```
  function touchCheckpoint(player, n) -> "accepted" | "ignored" | "rejected":
      if not isInt(n) or n < 1 or n > cfg.stage_count: return "rejected"
      cur = progress[player] ?? 0
      if n == cur + 1: progress[player] = n; return "accepted"
      if n <= cur:     return "ignored"
      return "rejected"            // 스킵: 로그 남기고 필요하면 횟수 누적
  function buySkip(player):        // 결제 영수증 검증 뒤에만 호출
      progress[player] = min((progress[player] ?? 0) + 1, cfg.stage_count)
  ```
- **함정.** (1) `n > cur`로 검사하면 스킵이 통과한다. 반드시 `== cur + 1`. (2) 리스폰 위치를 클라이언트가 보내게 하면 스킵과 같다. 서버가 `stage`로 스폰 위치를 찾는다. (3) 같은 체크포인트 재접촉을 거부로 처리하면 치트 로그가 오염된다.
- **검증 ✅** `test_obby_accepts_next_stage`, `test_obby_rejects_skip_and_backward`

### 3.2 타이쿤 드로퍼 경제 (버튼 트리 · 구매 ID만 저장)
- **규칙.** 플롯의 상태는 **구매한 버튼 ID 집합**이 전부다. 버튼마다 가격·선행 버튼·수입 증가량은 Config 테이블에 있고, 수입/초는 집합에서 매번 다시 계산한다. 구매는 서버가 `존재 → 미구매 → 선행 충족 → 재화 충분` 순으로 검사한다. 저장은 `{version, purchased[], coins}`뿐이고 접속 시 이 목록으로 플롯을 다시 세운다. 오프라인 수입은 경과 시간을 `offline_cap_s`로 자른 뒤 곱한다(시계 역행이면 0). 재화 증감은 [`core_systems.md` §4](../../systems/core_systems.md)의 단일 함수를 거친다.
- **공식.** `income_per_s = Σ income(b) for b in purchased`, `offline = min(max(0, Δt), offline_cap_s) × income_per_s`.
- **의사코드.**
  ```
  function canBuy(plot, id) -> (bool, reason):
      def = cfg.buttons[id];            if def == nil: return (false, "unknown")
      if id in plot.purchased:          return (false, "owned")
      if any(r not in plot.purchased for r in def.requires): return (false, "prereq")
      if plot.coins < def.cost:         return (false, "coins")
      return (true, "ok")
  function buy(plot, id):
      (ok, why) = canBuy(plot, id)
      if ok: addCurrency(plot.owner, "coins", -def.cost, "tycoon_buy:"+id); plot.purchased.add(id)
      return (ok, why)
  function save(plot):    return { version: 1, purchased: sorted(plot.purchased), coins: plot.coins }
  function rebuild(data): return Plot(purchased = [id for id in data.purchased if id in cfg.buttons], coins = data.coins)
  ```
- **함정.** (1) 플롯의 파트 위치·수량을 저장하면 맵을 고칠 때마다 마이그레이션이 필요하다. ID만 저장. (2) 저장 목록에 Config에 없는 ID가 있으면(버튼 삭제·조작) 재구성에서 조용히 버린다. (3) 수입을 누적 변수로 들고 있으면 저장·재구성 뒤 값이 어긋난다. 항상 집합에서 파생.
- **검증 ✅** `test_tycoon_prerequisite_tree`, `test_tycoon_save_rebuild_roundtrip`, `test_tycoon_offline_income_cap`

### 3.3 러너 청크 생성과 속도 곡선
- **규칙.** 트랙은 미리 만든 청크(난이도 티어 태그)를 이어 붙인 것이다. 거리로 티어를 정하고(`tier_every_m`마다 +1, 최대 티어에서 멈춤), 그 티어의 청크 중 하나를 시드 RNG로 고른다. 그러면 티어 열은 **내려가지 않는다**. 속도는 시간에 선형으로 오르되 `max_speed`에서 멈춘다. 히트박스는 보이는 것보다 살짝 작게. 청크·장애물·코인은 **오브젝트 풀**로 재사용한다(생성/파괴를 반복하면 GC 끊김; [`ObjectPool.gd`](../../platforms/godot/patterns/ObjectPool.gd)).
- **공식.** `tier(d) = min(max_tier, 1 + ⌊d / tier_every_m⌋)`, `v(t) = min(max_speed, base_speed + accel_per_s × t)`.
- **의사코드.**
  ```
  function generate(seed, n) -> list<(dist, chunkId, tier)>:
      rng = Random(seed); out = []
      for i in 0..n-1:
          d = i * cfg.chunk_len; tier = tierAt(d)
          pool = [c for c in cfg.chunks if c.tier == tier]
          out.append((d, rng.choice(pool).id, tier))
      return out
  function speedAt(t): return min(cfg.max_speed, cfg.base_speed + cfg.accel_per_s * t)
  ```
- **함정.** (1) 티어를 "≤ tier에서 아무거나"로 뽑으면 후반에 쉬운 청크가 섞여 긴장이 풀린다. 섞고 싶으면 가중치를 따로 둔다. (2) 속도에 상한이 없으면 프레임당 이동이 히트박스보다 커져 터널링이 난다. (3) 거리 점수는 서버가 `speed × dt` 누적으로 계산한다. 클라이언트 보고값을 믿지 않는다.
- **검증 ✅** `test_runner_difficulty_monotone`, `test_runner_speed_capped`

### 3.4 .io 먹고 커지기 (OgarII 공식, 서버 크기 비교)
- **규칙.** 셀의 상태는 반지름 `size` 하나다. 질량은 `size²/100`, 속도는 size가 클수록 느리고, 카메라는 size가 64를 넘으면서부터 물러난다(64 이하는 줌 1). 누가 누구를 먹는지는 **서버가 두 size를 비교**해서 정한다: 먹는 쪽이 `eat_margin`배 이상 커야 한다(같거나 조금 큰 것은 못 먹는다). 먹으면 **질량**을 더하고 size로 되돌린다(size를 더하면 안 된다).
- **공식.** (README §4, OgarII) `speed = 88 × size^-0.4396754 × moveMult`, `mass = size² / 100`, `s = min(64/size, 1)^0.4`, `viewWidth = 1920 / s / 2`. 먹은 뒤 `size' = sqrt((mass_a + mass_b) × 100)`. `eat_margin = 1.15`는 예시값.
- **의사코드.**
  ```
  function speed(size, moveMult=1):  return 88 * size^-0.4396754 * moveMult
  function mass(size):               return size*size / 100
  function zoom(size):               s = min(64/size, 1)^0.4; return (s, 1920 / s / 2)
  function tryEat(eater, prey) -> newSize | nil:     // 서버에서만 호출
      if eater.size < prey.size * cfg.eat_margin: return nil
      return sqrt((mass(eater.size) + mass(prey.size)) * 100)
  ```
- **함정.** (1) 클라이언트가 보낸 size로 판정하면 "내가 더 크다"고 거짓말할 수 있다. 서버의 size만. (2) `eater.size > prey.size`(여유 없음)로 하면 동률 근처에서 겹칠 때마다 판정이 뒤집힌다. (3) size를 더하면 질량이 보존되지 않아 작은 펠릿 여러 개가 큰 셀보다 커진다.
- **검증 ✅** `test_io_speed_decreases_zoom_widens`, `test_io_eat_requires_margin`

### 3.5 미로 생성 + BFS 출구 거리 + 경로 비율 창
- **규칙.** Recursive backtracker로 완전 미로(모든 셀이 연결된 신장 트리)를 만든다. 시작점에서 BFS 거리장을 구해 출구 거리와 가장 먼 셀의 거리를 잰다. **경로 비율**이 창(예: 0.55~0.72)을 벗어나면 버리고 `seed+1`로 다시 만든다(또는 브레이딩으로 막다른 길을 없애 거리를 줄인다). 채택한 시드와 비율을 서버 로그에 남기면 문제가 된 미로를 그대로 재현할 수 있다. 추격자 플로우필드도 같은 거리장으로 만든다.
- **공식.** `path_ratio = dist(start → exit) / max(dist(start → any cell))` (분모 정의는 예시. "출구가 가장 먼 셀 대비 얼마나 먼가"). 창 0.55~0.72는 [`roblox_formats.md`](roblox_formats.md) 예시. 15×15 · backtracker에서 원시 비율의 중앙값은 약 0.65, 창 통과율 약 1/4 (시뮬레이션 측정).
- **의사코드.**
  ```
  function generate(w, h, rng) -> adjacency:          // recursive backtracker
      visited = {start}; stack = [start]
      while stack: c = stack.top()
          nb = unvisitedNeighbors(c)
          if nb.empty(): stack.pop(); continue
          n = rng.choice(nb); carve(c, n); visited.add(n); stack.push(n)
  function bfs(adj, start) -> dist map
  function acceptMaze(seed) -> (adj, ratio, usedSeed):
      for i in 0..cfg.max_attempts-1:
          adj = generate(w, h, Random(seed + i)); d = bfs(adj, start)
          ratio = d[exit] / max(d.values())
          if cfg.ratio_min <= ratio <= cfg.ratio_max: return (adj, ratio, seed + i)
      raise "window not reached"                       // 창이 너무 좁거나 크기가 안 맞음
  ```
- **함정.** (1) 생성만 하고 비율을 재지 않으면 "너무 쉽거나 너무 어려운" 미로가 그대로 나간다. (2) 재생성 때 같은 시드를 다시 쓰면 무한 루프다. 시드를 바꿔야 한다. (3) 창을 지나치게 좁히면 `max_attempts`에 걸린다. 크기별로 통과율을 한 번 재 본다.
- **검증 ✅** `test_maze_in_window_only`, `test_maze_seed_reproducible`

### 3.6 라운드 매니저 (최소 인원 · 조기 종료 · 맵 로테이션)
- **규칙.** §1의 공통 뼈대. 서버가 1초 틱마다 전이 조건을 **한 곳에서** 평가한다. Lobby는 인원이 `min_players` 이상이면 Intermission으로, Intermission 중 인원이 빠지면 Lobby로 돌아간다. Round 진입 시 참가자·생존자 집합을 확정하고 맵은 `maps[round_index mod n]`로 돈다. **생존 ≤ 1**이면 타이머를 기다리지 않고 Results로 간다. 보상은 Results 진입 시 서버가 계산하고, 라운드 중 나간 플레이어는 받지 않는다.
- **공식.** `map = maps[round_index mod len(maps)]`, `reward = win_reward if alive else participation_reward`.
- **의사코드.**
  ```
  function tick():                                   // 서버, 1초
      enough = count(players) >= cfg.min_players
      if state == Lobby:        if enough: enter(Intermission); return
      timer -= 1
      if state == Intermission: if not enough: enter(Lobby) elif timer <= 0: enter(Round)
      elif state == Round:      if count(alive) <= 1 or timer <= 0: enter(Results)
      elif state == Results:    if timer <= 0: enter(Lobby)
  function enter(s):
      state = s; timer = durationOf(s)
      if s == Round:   map = cfg.maps[roundIndex % n]; roundIndex += 1; alive = participants = copy(players)
      if s == Results: for p in participants ∩ players: addCurrency(p, cfg[p in alive ? win : participation], reason)
  ```
- **함정.** (1) 사망·이탈을 `Died`/`PlayerRemoving` 콜백에서 바로 상태 전이하면 콜백 순서에 따라 Results가 두 번 들어간다. 집합만 갱신하고 전이는 `tick`에서. (2) 1명만 남았을 때 "승자"로 보상하되, **혼자 시작한 라운드**가 생기지 않도록 Intermission에서 인원을 다시 검사한다. (3) 맵 로테이션을 랜덤으로 하면 같은 맵이 연속으로 나온다. 인덱스 순환.
- **검증 ✅** `test_round_requires_min_players`, `test_round_early_end`, `test_round_map_rotation`

### 3.7 무체크포인트 등반: 추락 거리·최고 높이 기록
- **규칙.** 체크포인트가 없으므로 진행도는 "지금 높이"뿐이고, 설계상 보여 줄 것은 **최고 높이**와 **추락 거리**다. 서버가 위치를 관측하면서 올라갈 때마다 `peak`를 갱신하고, **착지했을 때** `peak − y`가 `fall_min` 이상이면 추락 한 건으로 확정한다(공중에서는 확정하지 않는다: 아직 더 떨어질 수 있다). 확정하면 `peak`를 현재 높이로 내린다. 다른 플레이어의 추락은 모두에게 보이게 한다(구경거리).
- **공식.** `fall = peak − y` (착지 시, `≥ fall_min`), `best_height = max(best_height, y)`.
- **의사코드.**
  ```
  function observe(player, y, grounded):              // 서버 틱마다
      st = stats[player]
      if y > st.peak: st.peak = y; st.best_height = max(st.best_height, y)
      elif grounded and st.peak - y >= cfg.fall_min:
          st.falls.append(st.peak - y); st.peak = y
          broadcast("Fell", player, st.peak - y)      // 구경거리 연출용 이벤트
  ```
- **함정.** (1) 공중에서 매 틱 추락을 기록하면 한 번 떨어지는 동안 수십 건이 쌓인다. 착지 시 한 번. (2) 작은 낙차(발판 사이)를 추락으로 세면 통계가 소음이 된다. `fall_min`. (3) 최고 높이를 클라이언트가 보고하면 리더보드가 깨진다. 서버 관측값만.
- **검증 ✅** `test_climb_fall_and_best_height`

## 4. 틱 / 업데이트 순서

권위 측(서버) 한 틱. 라운드 매니저는 1초 틱(예시값; RoundService.luau의 `task.wait(1)` 카운트다운과 같다), 판정 계열(.io 충돌·러너 거리·등반 관측)은 엔진 하트비트(Roblox `Heartbeat`, Godot `_physics_process`) `dt`로 돈다. 러너와 .io는 고정 스텝이 유리하다([`core_systems.md` §1](../../systems/core_systems.md)).

1. **입력·요청 수집** — 이동 입력, 체크포인트 접촉, 버튼 구매 요청, 스킵 결제 영수증. 전부 큐에 넣고 타입·범위·레이트 리밋 검사(§5).
2. **라운드 상태 전이** — `RoundManager.tick()`: 인원·생존·타이머 조건을 한 곳에서 평가. Round가 아니면 3~5는 건너뛴다(영구 월드 변형은 항상 실행).
3. **시뮬레이션** — 이동 적용, 러너 속도 `v(t)`와 거리 누적, .io 위치 갱신, 등반 위치 관측.
4. **판정** — 체크포인트 `== stage+1`, .io `tryEat`(크기 비교), 러너 충돌(작은 히트박스), 미로 출구 도달, 등반 착지 시 추락 확정.
5. **보상·재화** — 구매 처리(`canBuy` → `addCurrency`), 라운드 결과 보상, 오프라인 수입 지급(접속 시 한 번). 모두 단일 함수 경유.
6. **복제·스냅샷** — RoundState Attribute 갱신, 각 플레이어에게 필요한 값만(stage · coins · size · best_height) 복제. 프로필 객체 자체는 넘기지 않는다.
7. **저장 지점** — 체크포인트 승인, 버튼 구매, 라운드 결과, 이탈 시. 주기 저장은 30~60초(예시값, [`core_systems.md` §6](../../systems/core_systems.md)).

## 5. 신뢰 경계

원칙은 [`../../platforms/roblox/architecture.md` §1](../../platforms/roblox/architecture.md)과 [`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau). 재화·점수·확률·보상은 전부 서버.

| 클라이언트가 보내는 것 | 서버가 검증하는 규칙 | 거부 시 처리 |
|---|---|---|
| 체크포인트 접촉 `(n)` | 정수, `1 ≤ n ≤ stage_count`, `n == stage+1` (≤ stage는 무시) | 무시 + 스킵 시도 카운트, 임계 넘으면 킥 |
| 스킵 구매 | 영수증 ID 멱등, 처리 후 서버가 `stage+1` | 영수증 중복이면 지급 없이 성공 응답 |
| 버튼 구매 `(id)` | 존재 → 미구매 → 선행 충족 → 재화 충분, 플롯 소유자 본인 | 사유 코드 반환, 재화 변동 없음 |
| 수집(타이쿤 수금) 요청 | 플롯 소유자, 수금 쿨다운, 서버 누적치만 지급 | 무시 |
| 이동 입력(방향·점프) | 범위·NaN·속도 상한(러너는 서버가 `v(t)` 결정) | 입력 클램프 |
| .io 먹기/크기 | **받지 않는다.** 충돌·크기 비교는 서버 | 해당 Remote 없음 |
| 러너 거리·점수 | **받지 않는다.** 서버가 `v×dt` 누적 | 해당 Remote 없음 |
| 미로 출구 도달 | 서버 위치 기준 출구 셀 거리 ≤ 허용치, 라운드 중 | 무시 |
| 최고 높이·추락 | **받지 않는다.** 서버 관측값 | 해당 Remote 없음 |
| 물리 잔해 Touched (발파) | 잔해는 `SetNetworkOwner(nil)` 서버 소유, 멈춘 뒤 서버 채점 | 클라 소유 파트의 Touched는 점수에 쓰지 않음 |

## 6. 밸런스 다이얼

| 다이얼 | 무엇을 바꾸나 | 기본값(출처) | 올리면 / 내리면 |
|---|---|---|---|
| `round.min_players` | 라운드 시작 최소 인원 | 2 (예시값, RoundService.luau 기본값) | 올리면 빈 서버에서 대기만 / 내리면 1:1 라운드가 잦음 |
| `round.round_s` | 라운드 길이 | 90 (예시값) | 올리면 생존 전략화 / 내리면 짧고 반복적 |
| `obby.stage_count` | 코스 길이 | 50 (예시값) | 올리면 스킵 판매 늘지만 이탈도 / 내리면 완주 빠름 |
| `tycoon.buttons[].cost` | 성장 벽 간격 | 0·50·200·500·1500 (예시값) | 올리면 방치 대기 길어짐 / 내리면 금방 끝 |
| `tycoon.offline_cap_s` | 오프라인 수입 상한 | 28800 = 8h (예시값, genres.md의 예) | 올리면 복귀 보상 커지나 인플레 / 내리면 자주 접속 유도 |
| `runner.accel_per_s` · `max_speed` | 난이도 상승 속도와 천장 | 0.4 · 40 (예시값) | 올리면 세션 짧아짐 / 내리면 지루 |
| `runner.tier_every_m` | 티어 상승 간격 | 300 (예시값) | 올리면 완만 / 내리면 급격 |
| `io.speed_exp` | 커질수록 느려지는 정도 | −0.4396754 (README §4) | 절댓값 올리면 큰 셀이 둔해져 추격 쉬움 / 내리면 큰 셀이 지배 |
| `io.eat_margin` | 먹기에 필요한 크기 차 | 1.15 (예시값) | 올리면 비슷한 크기끼리 공존 / 내리면 근소 우위로 먹힘 |
| `maze.ratio_min~max` | 출구 경로 길이 창 | 0.55~0.72 (roblox_formats.md 예시) | 올리면 어렵고 재생성 잦음 / 내리면 쉬움 |
| `climb.fall_min` | 추락으로 세는 최소 낙차 | 10 (예시값) | 올리면 큰 추락만 기록 / 내리면 소음 |

## 7. 플랫폼 매핑

| 시스템 | Godot | Roblox |
|---|---|---|
| 라운드 상태 머신 (§3.6) | [`StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd) + [`State.gd`](../../platforms/godot/patterns/State.gd), 타이머는 `Timer` 노드 | [`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau) (Attribute로 상태 복제, 조기 종료 포함) |
| 체크포인트·구매 요청 검증 (§3.1, §3.2) | 싱글이면 로컬 판정([`godot/architecture.md` §6](../../platforms/godot/architecture.md)) | [`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau) 타입·범위·쿨다운 검증, `RemoteEvent` |
| 진행도·구매 ID 저장 (§3.1, §3.2, §3.7) | [`SaveManager.gd`](../../platforms/godot/patterns/SaveManager.gd) (version·마이그레이션·원자적 저장) | [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau) (ProfileStore 세션 잠금·Reconcile) |
| 재화·오프라인 수입 (§3.2) | [`Economy.gd`](../../platforms/godot/patterns/Economy.gd) (단일 진입점, 오프라인 보상 상한) | DataService의 `AddCoins` 한 함수, 스킵·패스는 [`ShopService.luau`](../../platforms/roblox/patterns/ShopService.luau) `ProcessReceipt` 멱등 |
| 버튼·청크 Config (§2) | `Resource` 정의 + `.tres` ([`godot/architecture.md` §4](../../platforms/godot/architecture.md)) | `ReplicatedStorage/Shared/Config` 모듈, `table.freeze` ([`roblox/architecture.md` §4](../../platforms/roblox/architecture.md)) |
| 러너 청크·풀링 (§3.3) | [`ObjectPool.gd`](../../platforms/godot/patterns/ObjectPool.gd), 청크는 `PackedScene` | 청크 Model을 `ServerStorage`에 두고 `Clone()`, 풀은 직접 구현 |
| .io 이동·카메라 (§3.4) | `CharacterBody2D`, `Camera2D.zoom = s` | `Humanoid.WalkSpeed = speed(size)`, 클라 `Camera` 거리 = viewWidth 기반; 판정은 서버 |
| 미로 생성·BFS (§3.5) | `TileMapLayer`에 통로 그리기, 거리장은 Dictionary | 셀을 Part로 조립, 추격자는 [`simplepath`](https://github.com/ahmicy/simplepath) (MIT, [`libraries.md`](../../platforms/roblox/libraries.md)) |
| 이벤트(추락 구경거리, 체크포인트) | [`EventBus.gd`](../../platforms/godot/patterns/EventBus.gd) | `BindableEvent`/`RemoteEvent` 브로드캐스트 |
| 물리 잔해 채점 (발파) | `RigidBody3D.sleeping` 뒤 구역 계산 | `SetNetworkOwner(nil)`, `Explosion.DestroyJointRadiusPercent = 0` ([`roblox_formats.md`](roblox_formats.md)) |

## 8. 검증 (sim/)

[`sim/arcade_sim.py`](sim/arcade_sim.py) (표준 라이브러리만, `random.Random(seed)`로 결정론). 검사 규칙:

1. `test_obby_accepts_next_stage` — 1→2→3 순서만 승인, 같은 체크포인트 재접촉은 무시.
2. `test_obby_rejects_skip_and_backward` — 1에서 5, 0, 999, 문자열은 거부하고 stage 불변. 서버 스킵은 +1만.
3. `test_tycoon_prerequisite_tree` — 선행 미충족·중복·미존재·재화 부족을 사유와 함께 거부, 트리 순서대로만 구매.
4. `test_tycoon_save_rebuild_roundtrip` — `rebuild(save(plot)).save() == save(plot)`, 수입 동일, 조작된 ID는 버려짐.
5. `test_tycoon_offline_income_cap` — 상한 초과 시간은 상한과 같은 수입, 음수 시간은 0.
6. `test_runner_difficulty_monotone` — 40청크 티어 열이 비감소, 1에서 시작해 3까지, 같은 시드면 같은 열.
7. `test_runner_speed_capped` — 속도 비감소, `max_speed`에서 고정.
8. `test_io_speed_decreases_zoom_widens` — size 10→400에서 속도 단조 감소·시야 폭 단조 증가, 64 이하 줌 1, `mass(100)=100`.
9. `test_io_eat_requires_margin` — 동률·소폭 우위·열세는 못 먹음, 1.25배는 먹고 질량 보존, 먹은 뒤 더 느려짐.
10. `test_maze_in_window_only` — 20개 시드 모두 창 안의 비율, 완전 연결, 재생성이 실제로 발생, 원시 미로 중 창 밖이 존재.
11. `test_maze_seed_reproducible` — 같은 시드 → 같은 미로·비율, 기록한 시드만으로 재생성 가능.
12. `test_round_requires_min_players` — 1명이면 Lobby 유지, 2명이면 Intermission, 인터미션 중 이탈하면 Lobby.
13. `test_round_early_end` — 3명 중 1명 사망·1명 이탈 → 타이머 전 Results, 생존자 승리 보상·사망자 참가 보상·이탈자 없음, 이후 Lobby.
14. `test_round_map_rotation` — 라운드 3회의 맵이 A, B, C 순.
15. `test_climb_fall_and_best_height` — 소폭 하강은 무시, 공중에서는 미확정, 착지 시 `peak−y` 기록, 최고 높이 유지.

```bash
cd reference/genres/arcade/sim
python3 -I arcade_sim.py --test     # 종료 코드 = 실패 수
python3 -I arcade_sim.py --demo     # 시드 42 요약
```

결과 (2026-10-17, Python 3 표준 라이브러리): **`passed 15/15`**, 종료 코드 0.

## 9. 흔한 구현 버그

1. **스킵이 통과한다.** 증상: 1스테이지 플레이어가 갑자기 40에 있다. → 원인: `n > stage`로 검사했거나 클라이언트가 리스폰 위치를 보낸다. → 고침: `n == stage + 1`, 스폰 위치는 서버가 `stage`로 찾는다 (§3.1).
2. **재접속하면 플롯이 비거나 수입이 다르다.** 증상: 버튼은 다시 살 수 없는데 드로퍼가 없다. → 원인: 파트 상태를 저장했거나 수입을 누적 변수로 들고 있었다. → 고침: 구매 ID 집합만 저장하고 접속 시 재구성, 수입은 집합에서 파생 (§3.2).
3. **오프라인 수입이 폭발한다.** 증상: 한 달 만에 온 유저가 억 단위 재화. → 원인: 경과 시간에 상한이 없거나 클라이언트 시각을 썼다. → 고침: 서버 시각, `min(Δt, offline_cap_s)`, 음수는 0 (§3.2).
4. **러너 후반에 장애물을 뚫고 지나간다.** 증상: 빠를 때만 충돌이 빠진다. → 원인: 속도 상한이 없어 프레임당 이동이 히트박스보다 크다. → 고침: `max_speed`, 고정 스텝, 필요하면 스윕 판정 (§3.3).
5. **작은 셀이 큰 셀을 먹는다.** 증상: 비슷한 크기가 겹치면 판정이 매 틱 뒤집힌다. → 원인: 클라이언트 size를 믿었거나 여유 없는 `>` 비교. → 고침: 서버 size, `eater ≥ prey × eat_margin`, 질량으로 합산 (§3.4).
6. **미로가 늘 너무 쉽다.** 증상: 출구가 시작점 바로 옆. → 원인: 비율을 재지 않고 생성만 했거나 분모를 셀 수로 잡아 창에 거의 안 걸린다. → 고침: BFS 거리장, 최장 거리 대비 비율, 창 밖이면 `seed+1` 재생성 (§3.5).
7. **빈 라운드가 끝까지 돈다 / 결과가 두 번 뜬다.** 증상: 혼자 남았는데 90초를 기다린다, 또는 보상이 2배. → 원인: 생존 수 검사를 안 했거나 `Died` 콜백에서 직접 전이했다. → 고침: 집합만 갱신하고 `tick`에서 `alive ≤ 1`로 한 번만 전이 (§3.6).
8. **추락 기록이 수십 건씩 쌓인다.** 증상: 한 번 떨어졌는데 "추락 37회". → 원인: 공중에서 매 틱 기록. → 고침: 착지 시 `peak − y ≥ fall_min`일 때 한 번, 그 뒤 `peak` 재설정 (§3.7).
