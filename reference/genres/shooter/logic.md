# 슈팅 기본 베이스 로직

> 엔진 무관. 구현 전에 읽는 설계 뼈대. 숫자는 README §4에서만. 시뮬레이션으로 검증한 규칙에는 ✅ 표시.
> 확인일 2026-10-17. 출처 번호 `[n]`은 [`README.md`](README.md) 맨 아래 목록과 같다. README §4에 없는 값은 **(예시값)**.

MVP 기준: Roblox 아레나 데스매치 규모 (Arsenal 서버 16명 [16], 라운드·리스폰). 택티컬 구매 라운드와 배틀로얄은 §1·§3에서 변형으로만 다룬다.

## 0. 최소 플레이 가능 단위 (MVP 루프)

도형 그래픽(캡슐 + 총구 레이)으로 1~2일에 만드는 범위.

**엔티티**
- 플레이어 캡슐 8~16개 (README §4 Arsenal 16 [16]). 서버가 위치·HP·무기를 소유.
- 무기 1종(hitscan, 부위 배율 있음) + 선택으로 투사체 1종. 무기 정의는 데이터(§2 JSON).
- 스폰 포인트 6개 이상 (적 거리로 점수 매김).

**규칙**
- 서버 권위: 클라이언트는 입력(이동 벡터·조준 방향·발사 시각)만 보낸다. 히트는 서버가 되감기로 판정 (§3.3).
- HP 0 → 사망 → `respawn_delay_s` 뒤 스폰 선택 → 스폰 보호.
- 킬 목표(Arsenal 32킬 [16], README §2) 또는 제한 시간 도달 → 매치 종료 → 결과 → 로비.

**화면**
- 1인칭 또는 숄더뷰 카메라, 크로스헤어, HP·탄약, 킬 피드, 점수판 1장.

**넣지 않는 것**
- 반동·탄퍼짐 패턴, 재장전 애니메이션, 무기 해금·스킨·배틀패스, 랭크 매치메이킹, 팀 밸런싱, 음성, 관전 카메라, 맵 2개 이상, 서브틱(CS2류 [29]) 같은 고급 넷코드.

## 1. 게임 흐름 상태 머신

공통 뼈대 (RoundService 패턴과 같은 구조, [`../../platforms/roblox/patterns/RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau)):

```
Lobby ──(인원 ≥ min)──▶ Warmup ──(타이머 0)──▶ Playing ──(승리 조건)──▶ MatchEnd ──(결과 타이머)──▶ Lobby
  ▲                                               │ (인원 < 2 또는 전원 이탈)
  └───────────────────────────────────────────────┘
Playing 내부 (플레이어별): Alive ──(HP≤0)──▶ Dead ──(respawn_delay)──▶ Spawning ──(스폰 선택)──▶ Alive(보호 중) ──(시간 경과 | 발사)──▶ Alive
```

| 상태 | 전이 조건 | 허용 입력 |
|---|---|---|
| Lobby | 접속 인원 ≥ 최소 인원 → Warmup | 무기 선택·설정만. 이동 불가 |
| Warmup | 카운트다운 0 → Playing | 이동·조준 허용, 데미지 0 |
| Playing | 킬 목표 / 타이머 / 인원 부족 → MatchEnd | 이동·조준·발사·재장전 |
| Playing/Dead | respawn_delay 경과 → Spawning | 관전 전환만 |
| MatchEnd | 결과 표시 후 → Lobby | 없음 (UI만) |

**변형 A — 택티컬 구매 라운드 (CS/VALORANT류)**: `Playing`을 `Buy → Live → RoundEnd` 하위 상태로 쪼갠다. 라운드 승패마다 돈을 지급하고, 매치 승리는 MR12(정규 24라운드 13선취, 12-12면 6라운드 OT [32]).
**변형 B — 배틀로얄**: `Warmup`이 낙하 구간, `Playing`은 서클 페이즈 배열을 순회(§3.8). 리스폰 없음, 생존 1팀이면 MatchEnd.

## 2. 엔티티와 데이터 모델

| 엔티티 | 핵심 필드 (타입) | 소유 | 저장 |
|---|---|---|---|
| WeaponDef | id(str), kind("hitscan"\|"projectile"), damage{head,body,leg}(int), fire_rate_rpm(int), falloff{start_m,end_m,min_mult}\|null, speed_mps(float, 투사체만), price(int) | 데이터(양쪽 읽기) | 아니오 (Config) |
| Player | id, pos(vec), vel(vec), hp(int), weapon_id, ammo(int), money(int), spawned_at_ms(int), has_fired(bool), last_input_seq(int) | 서버 | 매치 중만 |
| InputCmd | seq(int), client_tick(int), move(vec, 각 성분 −1~1), aim_dir(vec), fire(bool) | 클라이언트 생성 → 서버 검증 | 아니오 |
| PositionHistory | tick → {player_id: pos} 링버퍼, max_ticks | 서버 | 아니오 |
| Projectile | id, owner_id, pos, vel, spawned_tick, weapon_id | 서버 (클라이언트는 예측 표시) | 아니오 |
| MatchState | state(enum), elapsed_s, kills{pid:int}, score{team:int}, round_no | 서버 | 결과만 (전적) |
| SpawnPoint | pos, last_used_ms | 서버 | 아니오 (맵 데이터) |
| CirclePhase (BR) | wait_s, shrink_s, radius_mult, dps | 데이터 | 아니오 |
| PlayerProfile | version, kills_total, matches, unlocked[] | 서버 → DataStore | 예 |

밸런스 Config (sim의 `CONFIG`와 같은 값. 출처 표기는 주석 대신 §6 표 참고):

```json
{
  "version": 1,
  "tick_hz": 128,
  "max_rewind_ms": 200,
  "player_hp": 100,
  "weapons": {
    "vandal": {"kind": "hitscan", "damage": {"head": 160, "body": 40, "leg": 34},
               "fire_rate_rpm": 600, "falloff": null, "price": 2900},
    "smg":    {"kind": "hitscan", "damage": {"head": 50, "body": 25, "leg": 20},
               "fire_rate_rpm": 800, "falloff": {"start_m": 15, "end_m": 40, "min_mult": 0.6}, "price": 1000},
    "rocket": {"kind": "projectile", "damage": {"head": 100, "body": 100, "leg": 100},
               "fire_rate_rpm": 60, "speed_mps": 40, "max_range_m": 120, "falloff": null, "price": 2000}
  },
  "spawn": {"protection_ms": 2000, "enemy_dist_cap_m": 40, "recent_use_penalty": 30, "ally_weight": 0.2},
  "deathmatch": {"max_players": 16, "kill_target": 32, "time_limit_s": 600, "respawn_delay_s": 3},
  "tactical": {"rounds_regulation": 24, "rounds_to_win": 13, "overtime_block": 6, "overtime_to_win": 4},
  "economy": {"start_money": 800, "kill_reward": 300, "win_reward": 3250,
              "loss_rewards": [1400, 1900, 2400, 2900, 3400], "max_money": 16000},
  "battle_royale": {"players": 50, "start_radius_m": 1000,
                    "circle_phases": [[60, 60, 0.6, 1], [45, 45, 0.5, 2], [30, 30, 0.4, 4], [20, 20, 0.0, 8]]}
}
```

출처 있는 값: `tick_hz` 128 [26], Vandal 160/40/34 [19], `max_players` 16 [16], `kill_target` 32 (README §2 Arsenal, 2차), MR12 24/13/OT 6 [32], BR 50명 (README §2 Free Fire). 나머지는 전부 **예시값**이다 (`fire_rate_rpm`, 가격, smg·rocket 전체, 스폰·경제·서클 수치).

## 3. 핵심 시스템

### 3.1 무기 데이터 모델과 TTK
- **규칙**: 무기는 코드가 아니라 WeaponDef 데이터다. 데미지는 `부위 × 거리 감쇠`로 결정되고, TTK는 그 결과에서 역산한다. TTK 목표를 먼저 정하고(README §6 둘째 항목) 무기 수치를 거기에 맞춘다. 참고 목표: CoD BO6 AR 평균 약 320ms [20], VALORANT Vandal은 헤드 원샷·몸 3발 [19].
- **공식**: `dmg(zone, d) = base[zone] × m(d)`, `m(d) = 1 (d ≤ start)`, `1 − t·(1 − min_mult)` (start<d<end, `t = (d−start)/(end−start)`), `min_mult (d ≥ end)`. `shots = ceil(hp / dmg)`, `TTK_ms = (shots − 1) × 60000 / rpm` (첫 발은 0ms에 맞는다고 가정).
- **의사코드**:
```pseudo
function damage_at(weapon, zone, dist): number
    base = weapon.damage[zone]
    if weapon.falloff == null or dist <= falloff.start: return base
    t = min(1, (dist - falloff.start) / (falloff.end - falloff.start))
    return base * (1 - t * (1 - falloff.min_mult))

function shots_to_kill(weapon, zone, hp, dist): int
    return ceil(hp / damage_at(weapon, zone, dist))    // 반올림 금지

function ttk_ms(weapon, zone, hp, dist): number
    return (shots_to_kill(weapon, zone, hp, dist) - 1) * 60000 / weapon.fire_rate_rpm  // 첫 발 0ms
```
- **함정**: (1) 감쇠를 거리별 테이블로 만들어 두고 보간을 빼먹으면 특정 거리에서 TTK가 계단식으로 튄다. (2) `ceil` 대신 반올림하면 "39.9 데미지 3발이 안 죽는" 버그. (3) TTK에 첫 발 간격을 더하면 모든 무기가 같은 양만큼 느려 보여 비교가 틀어진다.
- **검증** ✅ `test_ttk_vandal_head_oneshot`, `test_ttk_vandal_body_three_shots`, `test_falloff_reduces_damage`

### 3.2 hitscan vs 투사체 (리드샷)
- **규칙**: hitscan은 발사 틱에 레이캐스트로 즉시 판정하고, 가장 가까운 표적 하나만 맞춘다(관통 없음). 투사체는 서버가 엔티티를 만들어 틱마다 전진시키며 충돌을 검사한다. 사격자는 이동 표적을 맞추려면 리드(미래 위치)를 조준해야 한다. Apex는 전 무기 투사체 [22], Roblox Weapons Kit은 투사체 기반이며 탄속을 높이면 레이캐스트처럼 보인다 [23].
- **공식** (리드 조준점): 표적 상대 위치 `r`, 속도 `v`, 탄속 `s`일 때 `|r + v·t| = s·t`를 풀어 `(v·v − s²)t² + 2(r·v)t + r·r = 0`의 가장 작은 양의 근 `t`; 조준점 `= target_pos + v·t`.
- **의사코드**:
```pseudo
function hitscan(origin, dir, targets): (id, dist) | null
    best = null
    for (id, pos, radius) in targets:
        t = ray_sphere(origin, normalize(dir), pos, radius)   // 가장 가까운 교차 거리
        if t != null and (best == null or t < best.dist): best = (id, t)
    return best

function lead_point(shooter, target_pos, target_vel, speed): vec | null
    r = target_pos - shooter; a = dot(v,v) - speed²; b = 2·dot(r,v); c = dot(r,r)
    t = smallest positive root of a·t² + b·t + c (a≈0이면 -c/b)
    return t == null ? null : target_pos + target_vel * t

function step_projectile(p, dt):            // 서버 틱마다
    p.pos += p.vel * dt
    if traveled(p) > max_range: destroy(p)
    else if overlaps(p.pos, any_player): apply_damage(...); destroy(p)
```
- **함정**: (1) 투사체를 "이전 위치→현재 위치" 선분이 아니라 점으로만 검사하면 빠른 탄이 얇은 표적을 통과한다(터널링). (2) 판별식이 음수(표적이 탄속보다 빨리 도망)인데 `None` 처리를 안 하면 `sqrt` 예외. (3) hitscan 교차 거리 `t < 0`(사격자 뒤쪽)을 걸러내지 않으면 뒤를 보고도 맞는다.
- **검증** ✅ `test_hitscan_nearest_target`, `test_projectile_lead_hits_moving_target`, `test_projectile_no_lead_misses`

### 3.3 서버 권위 히트 판정 + 랙 보상 (되감기 버퍼)
- **규칙**: 클라이언트는 "발사했다 + 내가 본 틱(client_tick) + 조준 방향"만 보낸다. 서버는 매 틱 모든 플레이어 위치를 링버퍼에 기록해 두고, 발사 요청이 오면 `client_tick` 시점의 위치로 되감아 레이캐스트한다 (Bernier [25], Gambetta Part IV [24]). 되감기 허용 폭을 넘는 요청(지연이 너무 크거나 미래 틱)은 거부한다. 틱 주기는 VALORANT 128틱(7.8125ms) [26]이 상한급 사례이고, `max_rewind_ms`는 예시값이다.
- **공식**: `rewind_ms = (server_tick − client_tick) × 1000 / tick_hz`; 수락 조건 `0 ≤ rewind_ms ≤ max_rewind_ms`.
- **의사코드**:
```pseudo
class PositionHistory:                      // tick → {pid: pos}, 길이 max_ticks
    record(tick, positions); at(tick) → 그 틱(없으면 직전 틱)의 스냅샷

function rewind_hit_check(history, server_tick, cmd, shooter): Result
    if cmd.client_tick > server_tick: return Reject("future_tick")
    if (server_tick - cmd.client_tick) * 1000 / TICK_HZ > MAX_REWIND_MS: return Reject("rewind_too_far")
    snap = history.at(cmd.client_tick)
    if snap == null: return Reject("no_snapshot")
    targets = [(pid, pos, HITBOX_R) for (pid, pos) in snap if pid != shooter]
    hit = hitscan(shooter.pos_at(cmd.client_tick), cmd.aim_dir, targets)
    return hit ? Hit(hit.id) : Miss
```
- **함정**: (1) 사격자 본인 위치는 되감지 않고 현재 위치를 쓰면 총구 원점이 틀어진다 — 사격자도 같은 틱으로 되감는다. (2) 링버퍼를 `max_rewind_ms`보다 짧게 잡으면 허용 범위 안인데 `no_snapshot`으로 거부된다. (3) 되감기 폭을 무제한으로 두면 고핑 플레이어가 "이미 엄폐한 사람"을 계속 맞춘다 — 피격자 입장의 불공정은 상한으로만 제어된다.
- **검증** ✅ `test_rewind_accept_within_window`, `test_rewind_reject_beyond_window`

### 3.4 클라이언트 예측 + 리컨실리에이션 (개요)
- **규칙**: 이동은 클라이언트가 입력을 즉시 적용해 보여 주고(예측), 같은 입력에 `seq`를 붙여 서버로 보낸다. 서버 스냅샷에는 `last_acked_seq`가 실린다. 클라이언트는 스냅샷 위치에서 아직 확인되지 않은 입력(`seq > acked`)만 다시 재생해 자기 위치를 고친다 (Gambetta Part II [24], Overwatch는 예측이 틀리면 롤백 후 입력 재생 [27]). 다른 플레이어는 예측하지 않고 스냅샷 두 개 사이를 **보간**해 보여 준다.
- **공식**: `predicted = replay(server_pos, [inp for (seq, inp) in pending if seq > last_acked])`. 이동 함수 `apply_input`은 서버·클라이언트가 **같은 코드**를 쓴다.
- **의사코드**:
```pseudo
function apply_input(pos, inp, speed, dt): vec   // 양쪽 공용, 순수 함수
    return pos + inp.move * speed * dt

function on_local_input(inp):                   // 클라이언트, 매 틱
    seq += 1; pending.append((seq, inp)); send(InputCmd(seq, inp))
    local_player.pos = apply_input(local_player.pos, inp, SPEED, DT)   // 예측

function on_server_snapshot(snap):              // 클라이언트
    pending.remove_while(seq <= snap.last_acked_seq)
    pos = snap.pos
    for (seq, inp) in pending: pos = apply_input(pos, inp, SPEED, DT)
    local_player.pos = pos                      // 오차가 크면 스냅, 작으면 부드럽게 보정
```
- **함정**: (1) 서버 이동 코드와 클라이언트 예측 코드가 조금이라도 다르면(마찰·dt·클램프) 매 스냅샷마다 흔들린다. (2) 확인된 입력을 큐에서 지우지 않으면 큐가 무한히 자라고 재생이 느려진다. (3) 입력에 `dt`를 클라이언트가 실어 보내면 시간 가속 치트 — 서버는 틱 수만 믿는다.
- **검증** ✅ `test_reconcile_replays_unacked_inputs`

### 3.5 스폰 선택과 스폰 보호
- **규칙**: 후보 스폰마다 점수를 매겨 최고점을 고른다. 적과 가까울수록 감점, 최근 쓴 스폰은 감점, 아군이 가까우면 소폭 가점. 스폰 직후 `protection_ms` 동안 무적이며 **사격하면 즉시 해제**된다(보호를 공격에 쓰지 못하게). 맵에 레인이 없으면 어떤 점수식도 스폰킬을 못 막는다 (README §6 "레인 없는 맵" [10]).
- **공식**: `score = min(d_enemy, cap) + ally_weight × max(0, cap − d_ally) − (recent ? recent_use_penalty : 0)`; 동점이면 시드 RNG로 선택.
- **의사코드**:
```pseudo
function score_spawn(p, enemies, allies, recent): number
    d_enemy = min(dist(p, e) for e in enemies) or cap
    score = min(d_enemy, cap)
    if allies: score += ally_weight * max(0, cap - min(dist(p, a) for a in allies))
    if p in recent: score -= recent_use_penalty
    return score

function pick_spawn(spawns, enemies, allies, recent, rng): spawn
    scored = [(score_spawn(p, enemies, allies, p in recent), p) for p in spawns]
    return rng.choice(p for (s, p) in scored if s == max(scored))   // 동점은 시드 RNG

function is_protected(player, now): bool
    return !player.has_fired and now - player.spawned_at < protection_ms
```
- **함정**: (1) 거리 상한(cap)을 두지 않으면 항상 맵 끝 구석만 뽑혀 교전 공백이 생긴다. (2) 적 수가 0일 때 `min()`이 예외를 던진다 — 기본값 처리. (3) 보호 해제를 "데미지를 받으면"으로 하면 보호 중인 플레이어가 공격하는 역이용이 생긴다.
- **검증** ✅ `test_spawn_prefers_far_from_enemy`, `test_spawn_protection_expires_or_breaks_on_fire`

### 3.6 라운드·매치 상태와 승리 조건
- **규칙**: 데스매치는 **킬 목표 선취** 또는 **제한 시간 만료** 중 먼저 오는 것으로 끝나고, 시간 만료 시 최다 킬이 승자. 택티컬 변형은 MR12: 정규 24라운드에서 13승 선취, 12-12면 6라운드 OT 블록 [32] — 블록 안에서 `overtime_to_win`(예시값 4)승이면 끝, 3-3이면 다음 블록. 승리 판정은 킬이 들어오는 순간과 타이머 틱 두 곳에서만 검사한다.
- **공식**: 데스매치 종료 `= any(kills[p] ≥ kill_target) or elapsed ≥ time_limit`; 택티컬 `rounds_played ≤ 24: score ≥ 13`, 이후 `block[team] ≥ overtime_to_win`, `sum(block) ≥ 6 → block 초기화`.
- **의사코드**:
```pseudo
class DeathmatchState: kills{}, elapsed, state
    add_kill(pid): kills[pid] += 1; check()
    tick(dt): elapsed += dt; check()
    check(): if state != Playing: return
             if max(kills) >= kill_target or elapsed >= time_limit: state = MatchEnd

class TacticalMatch: score{A,B}, block{A,B}, rounds_played, winner
    round_won(team):
        score[team] += 1; rounds_played += 1
        if rounds_played <= rounds_regulation: if score[team] >= rounds_to_win: winner = team; return
        block[team] += 1
        if block[team] >= overtime_to_win: winner = team
        else if block.A + block.B >= overtime_block: block = {0, 0}
```
- **함정**: (1) 승리 조건을 매 프레임 UI에서 검사하면 서버와 클라이언트가 다른 승자를 보여 준다 — 서버 FSM 한 곳. (2) 매치 종료 후 들어온 킬을 집계하면 점수판이 바뀐다 — `state != Playing`이면 무시. (3) 인원 2명 미만이 되면 즉시 종료 (`genres.md` 라운드제 함정).
- **검증** ✅ `test_deathmatch_kill_target_win`, `test_deathmatch_timer_win`, `test_mr12_first_to_13_and_overtime`

### 3.7 무기 경제 변형 (구매 라운드)
- **규칙**: 라운드 시작 `Buy` 상태에서만 구매. 돈은 서버가 단일 함수 `add(amount, reason)`으로만 바꾸고 상한을 지킨다 ([`../../systems/core_systems.md`](../../systems/core_systems.md) §4). 킬 보상, 라운드 승리 보상, 연패 보너스(연패 횟수에 따라 증가, 승리하면 초기화)가 수입원. VALORANT 아스널 20종이 가격대별로 에코/포스/풀바이 라운드와 결합하는 구조 [30]. 수치는 전부 예시값.
- **공식**: `loss_reward = loss_rewards[min(loss_streak, len−1)]`; `money = clamp(money + Δ, 0, max_money)`.
- **의사코드**:
```pseudo
class Wallet: money, loss_streak, log[]        // 서버 전용, 플레이어마다 하나
    add(amount, reason):                       // 모든 증감의 단일 진입점
        money = clamp(money + amount, 0, max_money); log.append((reason, amount))
    try_buy(weapon_id): price = weapons[weapon_id].price
        if state != Buy or price > money: return false
        add(-price, "buy:" + weapon_id); give_weapon(weapon_id); return true
    on_kill(): add(kill_reward, "kill")      // 서버 킬 판정에서만 호출
    round_end(won):
        if won: loss_streak = 0; add(win_reward, "round_win")
        else: add(loss_rewards[min(loss_streak, len-1)], "round_loss"); loss_streak += 1
```
- **함정**: (1) 클라이언트가 가격을 보내게 두면 0원 구매 — 서버가 테이블에서 가격을 읽는다. (2) 상한 없이 더하면 장기 매치에서 돈이 의미를 잃는다. (3) 연패 카운터를 팀이 아니라 개인별로 두면 팀 경제가 어긋난다 (CS류는 팀 단위).
- **검증** ✅ `test_economy_rejects_unaffordable_buy`

### 3.8 배틀로얄 변형 (서클 축소 스케줄)
- **규칙**: 서클은 페이즈 배열 `[wait_s, shrink_s, radius_mult, dps]`로 정의한다. 각 페이즈는 `wait_s` 동안 반지름을 유지한 뒤 `shrink_s` 동안 `현재 반지름 × radius_mult`까지 선형 축소한다. 서클 밖 플레이어는 현재 페이즈의 `dps`만큼 틱마다(여기서는 초당) 피해. 인원은 플랫폼 동접에 맞춘다 — Free Fire 50명·약 10분 (README §2), Apex 60명 [5].
- **공식**: 페이즈 `i` 축소 중 `r(t) = r_i + (r_i·mult_i − r_i) × (t − t_wait_i) / shrink_i`; 밖 판정 `dist(pos, center) > r(t)`.
- **의사코드**:
```pseudo
function circle_radius_at(t): (radius, dps)
    r = start_radius
    for (wait, shrink, mult, dps) in phases:
        if t < wait: return (r, dps)
        t -= wait; target = r * mult
        if t < shrink: return (lerp(r, target, t / shrink), dps)
        t -= shrink; r = target
    return (r, last_dps)

function outside_damage(pos, center, t): (r, dps) = circle_radius_at(t); return dist(pos, center) > r ? dps : 0
```
- **함정**: (1) `mult`를 1보다 크게 넣는 데이터 실수를 막는 검증이 없으면 서클이 커진다 — 로드 시 단조 감소를 확인. (2) 마지막 페이즈 반지름이 0이 아니면 매치가 끝나지 않는다. (3) 서클 중심 이동(다음 서클이 현재 서클 안)을 넣을 때 중심을 클라이언트가 추측하면 어긋난다 — 서버가 시드로 결정해 페이즈 시작 시 전송.
- **검증** ✅ `test_circle_schedule_monotonic`, `test_circle_damage_outside`

## 4. 틱 / 업데이트 순서

서버 한 틱 (권장 주기: 소규모 Roblox 아레나는 엔진 Heartbeat(약 60Hz)를 따르는 것이 **예시값**이고, 128틱 [26]은 서버 프레임을 2ms 미만으로 최적화한 대형 사례 — 틱을 올리기 전에 서브틱 [29]이나 보간 지연을 먼저 본다):

1. **입력 수집**: 플레이어별 InputCmd 큐에서 `seq` 순으로 꺼낸다. 타입·범위 검증 (§5), 레이트 리밋.
2. **이동 시뮬레이션**: `apply_input`을 서버에서 실행. 속도 클램프, 충돌 해결.
3. **위치 기록**: 이번 틱의 모든 위치를 PositionHistory에 `record(tick, …)`.
4. **발사 판정**: 발사 cmd마다 발사 간격(rpm)·탄약·스폰 보호를 확인한 뒤 hitscan은 `rewind_hit_check`, 투사체는 Projectile 생성.
5. **투사체 전진**: 살아 있는 투사체 `step_projectile`, 충돌 시 데미지.
6. **데미지·사망 처리**: HP 차감(보호 중이면 0), HP ≤ 0 → Dead, 킬 집계 `add_kill`, 리스폰 타이머 시작.
7. **리스폰**: 타이머 만료 플레이어에 `pick_spawn`, `spawned_at = now`, `has_fired = false`.
8. **매치 규칙**: `MatchState.tick(dt)` → 승리 조건, 라운드 전이, BR이면 서클 피해.
9. **보상·경제**: 킬 보상 `Wallet.add` (택티컬), 전적 누적 (서버 메모리).
10. **스냅샷 송신**: 플레이어별 `last_acked_seq` + 가시 범위 엔티티 위치·HP. 저장은 매치 종료 시 한 번 (PlayerProfile).

## 5. 신뢰 경계

| 클라이언트가 보내는 것 | 서버가 검증하는 규칙 | 거부 시 처리 |
|---|---|---|
| InputCmd.move (vec) | 각 성분 −1~1, NaN·inf 아님, 틱당 1개 | 클램프, 초과분 폐기 |
| InputCmd.aim_dir (vec) | 단위 벡터로 정규화 가능(길이 > 0) | 해당 cmd 무시 |
| fire + client_tick | `0 ≤ server_tick − client_tick ≤ max_rewind`, 발사 간격 ≥ 60000/rpm, 탄약 > 0, 보호 중 아님 | 발사 무시, 반복 시 레이트 리밋 |
| "맞았다"(hit 결과) | **받지 않는다.** 히트·데미지·킬은 서버 되감기 판정만 | 로그 + 카운트 |
| 구매 요청 (weapon_id) | Buy 상태, 테이블 가격 ≤ money, weapon_id 존재 | 거부 응답, 돈 불변 |
| 리스폰 요청 | Dead 상태 + respawn_delay 경과 | 무시 |
| 점수·돈·킬 수치 | **받지 않는다.** 재화·점수·확률·보상은 전부 서버 ([`../../systems/core_systems.md`](../../systems/core_systems.md) §7) | — |

Roblox 구현은 [`../../platforms/roblox/patterns/SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau)의 타입→범위→상태 순서 검증과 토큰 버킷을 그대로 쓴다.

## 6. 밸런스 다이얼

| 다이얼 | 무엇을 바꾸나 | 기본값 (출처) | 올리면 / 내리면 체감 |
|---|---|---|---|
| `damage.head / body` | 부위별 1발 데미지 → TTK | 160 / 40 (Vandal [19]) | 올리면 "먼저 본 쪽"이 이기는 포지셔닝 게임, 내리면 에임·힐 개입 (README §3 TTK) |
| `fire_rate_rpm` | 발사 간격 → TTK 분모 | 600 (예시값) | 올리면 몸샷 TTK 단축, 내리면 헤드샷 의존 |
| `falloff.end_m / min_mult` | 원거리 데미지 | 40m / 0.6 (예시값, smg) | 내리면(가까이서 끝) 근접 무기 역할 뚜렷, 올리면 무기 역할 겹침 |
| `speed_mps` (투사체) | 리드 필요량 | 40 (예시값) | 올리면 hitscan에 가까워짐 [23], 내리면 숙련 격차 커짐 |
| `max_rewind_ms` | 고핑 플레이어 히트 수락 폭 | 200ms (예시값) | 올리면 사격자 유리("엄폐했는데 죽음"), 내리면 고핑 유저의 총이 안 맞음 |
| `tick_hz` | 판정 해상도·서버 비용 | 128 (VALORANT [26]) | 올리면 반응 시간 확보·서버비 급증 (README §6), 내리면 보간 지연 체감 |
| `kill_target / time_limit_s` | 매치 길이 | 32 (Arsenal, README §2) / 600s (예시값) | 올리면 긴 매치·이탈 증가, 내리면 역전 여지 감소 |
| `spawn.protection_ms` | 스폰킬 방지 | 2000ms (예시값) | 올리면 보호 역이용, 내리면 스폰킬 |
| `economy.loss_rewards` | 연패 팀 복구 속도 | 1400→3400 (예시값) | 올리면 스노우볼 완화, 내리면 한 라운드 패배가 매치를 결정 |
| `circle_phases` | BR 매치 길이·교전 밀도 | 총 310s (예시값) | `wait` 올리면 파밍 길고 교전 적음, `shrink` 내리면 서클 피해 사망 증가 |

## 7. 플랫폼 매핑

| 시스템 | Godot | Roblox |
|---|---|---|
| WeaponDef (§3.1) | `Resource` 서브클래스 `WeaponData.gd`로 `.tres` ([`../../platforms/godot/architecture.md`](../../platforms/godot/architecture.md) §4). 런타임 변경 시 `duplicate()` | `ReplicatedStorage.Shared/Config/Weapons.luau`에 `table.freeze` ([`../../platforms/roblox/architecture.md`](../../platforms/roblox/architecture.md) §4) |
| hitscan / 투사체 (§3.2) | `PhysicsDirectSpaceState3D.intersect_ray` / `ShapeCast3D`; 투사체 노드는 [`../../platforms/godot/patterns/ObjectPool.gd`](../../platforms/godot/patterns/ObjectPool.gd) | `workspace:Raycast` + `RaycastParams`(필터) / 공식 Weapons Kit 투사체 구조 [23] |
| 랙 보상·되감기 (§3.3) | 서버 피어가 `PositionHistory` 보관, `MultiplayerAPI` RPC로 InputCmd 수신 | 서버 Service가 `RunService.Heartbeat`마다 기록, `RemoteEvent`로 cmd 수신 — [`../../platforms/roblox/patterns/SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau) |
| 예측·리컨실 (§3.4) | `MultiplayerSynchronizer` 대신 직접 RPC + `last_acked_seq` (공용 `apply_input`) | Roblox는 캐릭터 이동을 클라이언트 권위로 복제하므로 이동 예측은 엔진이, **히트·HP만 서버** |
| 스폰 (§3.5) | `Marker3D` 그룹 `spawn_points`, 서버가 `pick_spawn` | `SpawnLocation`은 쓰지 않고 서버 `pick_spawn` 후 `Character:PivotTo` |
| 매치 FSM (§3.6) | [`../../platforms/godot/patterns/StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd) + [`State.gd`](../../platforms/godot/patterns/State.gd); 이벤트는 [`EventBus.gd`](../../platforms/godot/patterns/EventBus.gd) | [`../../platforms/roblox/patterns/RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau) 상태를 Attribute로 노출 |
| 경제 (§3.7) | [`../../platforms/godot/patterns/Economy.gd`](../../platforms/godot/patterns/Economy.gd) 단일 진입점 | `EconomyService` + [`../../platforms/roblox/patterns/DataService.luau`](../../platforms/roblox/patterns/DataService.luau) |
| BR 서클 (§3.8) | 서버 `circle_radius_at`, 클라이언트는 `MeshInstance3D` 스케일만 | 서버 계산, `ReplicatedStorage` Attribute(`CircleRadius`, `PhaseStart`)로 복제 |
| 전적 저장 | [`../../platforms/godot/patterns/SaveManager.gd`](../../platforms/godot/patterns/SaveManager.gd) (`version` 필드) | [`../../platforms/roblox/patterns/DataService.luau`](../../platforms/roblox/patterns/DataService.luau) |

오픈소스 출발점: Godot는 TheDahoom/FPS-Multiplayer-Template (MIT, 멀티·리스폰) [37], KenneyNL/Starter-Kit-FPS (MIT/CC0) [34]. GPL인 Quake·Xonotic [38][40]은 구조만 참고.

## 8. 검증 (sim/)

[`sim/shooter_sim.py`](sim/shooter_sim.py)가 검사하는 규칙 (테스트 이름 = §3 ✅ 표기):

1. `test_ttk_vandal_head_oneshot` — 헤드 160 ≥ HP 100 → 1발, TTK 0ms
2. `test_ttk_vandal_body_three_shots` — 몸 40 → 3발, 600rpm에서 200ms, 거리 감쇠 없음
3. `test_falloff_reduces_damage` — 감쇠 구간 밖 25 / 끝 15 / 중간 선형, 원거리 TTK 증가
4. `test_hitscan_nearest_target` — 레이 위 가장 가까운 표적만, 빗나가면 None
5. `test_projectile_lead_hits_moving_target` — 리드 조준점으로 쏘면 이동 표적 명중
6. `test_projectile_no_lead_misses` — 현재 위치를 쏘면 빗나감
7. `test_rewind_accept_within_window` — 10틱(78ms) 되감기 수락, 현재 틱으로는 miss
8. `test_rewind_reject_beyond_window` — 30틱(234ms) > 200ms 거부, 미래 틱 거부
9. `test_reconcile_replays_unacked_inputs` — 확인 안 된 입력 재생 결과 = 전체 입력 적용 결과
10. `test_spawn_prefers_far_from_enemy` — 적 원거리 선호, 최근 사용 감점, 거리 cap 동점은 아군 가점
11. `test_spawn_protection_expires_or_breaks_on_fire` — 2000ms 만료, 사격 시 해제
12. `test_deathmatch_kill_target_win` — 32킬째에 MatchEnd
13. `test_deathmatch_timer_win` — 600s에 종료, 최다 킬 승자
14. `test_mr12_first_to_13_and_overtime` — 13선취, 12-12 → OT, 3-3 블록 초기화, 블록 4승
15. `test_economy_rejects_unaffordable_buy` — 잔액 부족 거부·불변, 연패 보상 증가, 상한
16. `test_circle_schedule_monotonic` — 반지름 단조 감소, 1페이즈 끝 600, 마지막 0
17. `test_circle_damage_outside` — 서클 밖만 현재 페이즈 피해

```bash
cd reference/genres/shooter/sim
python3 -I shooter_sim.py --test   # 종료 코드 = 실패 수
python3 -I shooter_sim.py --demo   # 시드 7, 8인 데스매치 요약
```

실행 결과 (2026-10-17, Python 3.13): `passed 17/17`, 종료 코드 0. `--demo`는 같은 시드에서 같은 출력(결정론 확인).

## 9. 흔한 구현 버그

1. **"벽 뒤에서 죽었다"** → 되감기 상한이 없거나 너무 큼 → `max_rewind_ms` 상한 + 거부 로그 (§3.3). 상한 안이면 설계상 정상이므로 킬캠으로 설명한다.
2. **내 캐릭터가 스냅샷마다 뒤로 튄다** → 서버·클라이언트 이동 코드 불일치(dt·마찰·클램프) → `apply_input`을 한 모듈로 공유, 입력에 dt를 싣지 않는다 (§3.4).
3. **빠른 투사체가 표적을 통과** → 점 충돌 검사 → 이전 위치→현재 위치 선분(스윕) 검사 (§3.2).
4. **3발 맞췄는데 안 죽음** → 데미지 반올림 또는 감쇠 테이블 계단 → `ceil(hp / dmg)`과 선형 보간 (§3.1).
5. **스폰 직후 연속 사망** → 스폰 점수에 적 거리 cap 없음 / 보호 없음 / 레인 없는 맵 → §3.5 점수식 + 보호 + 맵 레인 설계 [10].
6. **매치 종료 뒤 점수판이 바뀜** → 종료 후 킬 집계 → `state != Playing`이면 무시, 승자 판정은 서버 FSM 한 곳 (§3.6).
7. **0원으로 무기 구매** → 클라이언트가 가격 전송 → 서버가 Config 테이블에서 가격을 읽고 `Wallet.add` 한 곳만 거친다 (§3.7).
8. **서버 CPU 폭주** → 틱을 128로 올리고 매 틱 전원 레이캐스트 → 틱은 플랫폼 기본(예시 60Hz)부터, 발사 틱에만 되감기, 가시 범위 밖 스냅샷 생략 (§4, README §6 틱레이트 항목).
