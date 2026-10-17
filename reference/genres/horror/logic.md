# 호러 · 판별 기본 베이스 로직

> 엔진 무관. 구현 전에 읽는 설계 뼈대. 숫자는 README §4에서만. 시뮬레이션으로 검증한 규칙에는 ✅ 표시.
> 확인일 2026-10-17. 원전·수치는 [`README.md`](README.md) §3·§4, 설계 근거 ★1~12는 [`anomaly_detection.md`](anomaly_detection.md). 공통 시스템(FSM·RNG·경제·저장·신뢰 경계)은 [`../../systems/core_systems.md`](../../systems/core_systems.md)에 있으므로 여기서는 링크만 한다.

기본형은 **교대 근무 검문 게임**이다: 손님이 줄을 서고, 각 손님은 정상이거나 이상현상 **하나**를 지니며, 플레이어는 **들이기/돌려보내기** 둘 중 하나로 판정한다. 틀리면 벌점·위협이 쌓이고, 밤이 바뀔수록 규칙이 늘고 이상현상 비율이 오른다. 8-like(복도 루프)와 검문형(서류 대조)은 §1 변형으로 다룬다.

## 0. 최소 플레이 가능 단위 (MVP 루프)

한 판이 성립하는 최소 요소. 도형 그래픽으로 1~2일 프로토타입 범위.

| 구분 | 최소 요소 |
|---|---|
| 엔티티 | 손님 큐(밤마다 N명) · 이상현상 풀(사람형 + 데이터형, 각각 3개 이상) · 규칙 목록(밤 번호 붙음) · 밤 상태(타이머·실수 수·위협) · 복채(정수 재화) |
| 규칙 | ① 밤 시작 공지에서 규칙 전달 ② 손님마다 판정 동사 둘 중 하나 ③ 정답이면 복채, 오답이면 벌점 사다리(2회 면제) ④ 이상현상을 들이면 위협 +1, 누적 시 게임 오버 ⑤ 이상현상은 전부 나오기 전 중복 없음 ⑥ 밤마다 비율 상승 |
| 화면 | 고정 구도 상담석 1장(★2): 손님 사각형 + 속성 텍스트(손가락 수·그림자·쪽지), 거울 사각형, 공지판, 타이머, 위협 게이지, 버튼 2개(길게 누르기) |
| 입력 | 살펴보기 대상 선택(얼굴·손·쪽지·거울) · 판정 버튼 2개 |

**넣지 않는 것:** 뒷방 추격자·길찾기 AI, 점프스케어 연출, 협동·매칭, 커스텀 밤, 실제 만세력 라이브러리(절기 경계를 고정 날짜 예시 공식으로 대체), 상점·Robux, 음성·3D 사운드, 저장(한 판은 메모리에서 끝남).

## 1. 게임 흐름 상태 머신

공통 뼈대 (구현: [`core_systems.md` §2](../../systems/core_systems.md)의 FSM).

```
Lobby ──start──▶ NightNotice(n) ──ack──▶ Shift(n) ──timer 만료 | 큐 소진──▶ NightEnd(n)
                      ▲                     │                                  │
                      │                     │ threat ≥ threat_max              ├─ n < nights ──▶ NightNotice(n+1)
                      │                     ▼                                  └─ n == nights ─▶ Results
                      └────retry────── GameOver                                   (보너스·커스텀 밤은 nights 뒤에 추가)

Shift(n) 내부 (손님 1명 단위):
  VisitorArrive ──(예고가 있으면 먼저 재생)──▶ Inspect ──hold 완료──▶ Verdict ──▶ Resolve ──▶ 다음 손님 | 밤 종료
```

| 상태 | 들어갈 때 | 허용 입력 | 나갈 조건 |
|---|---|---|---|
| Lobby | 밤 번호·재화 로드 | 시작, (협동) 파티 초대 | start |
| NightNotice | 그 밤의 새 규칙 1~2개를 "주인의 공지"로 표시. **손님 없음, 대사 없음**(★4) | 확인(ack) | ack |
| Shift · Inspect | 손님 스폰, 서류·거울 등 살펴볼 대상 활성 | 살펴보기, 판정 버튼 hold | hold 완료 → Verdict |
| Shift · Resolve | 복채·벌점·위협 정산, 발견률 기록 | 없음 | 자동 → 다음 손님 |
| NightEnd | 결산(복채 − 벌점), 벌점 카운터·(옵션) 위협 리셋 | 다음 밤 | 자동 |
| GameOver | 위협 누적 또는 치명형 들임 | retry(같은 밤부터, 예시) | retry |
| Results | 총 재화·밤별 발견률 | 로비로 | home |

**변형 1 · 8-like 루프형(Exit 8):** `Shift`가 "복도 1회 통과"로 바뀌고, 판정 동사는 진행/되돌아가기, 밤 대신 **연속 정답 카운터**(정답이면 +1, 오답이면 0으로 리셋, 목표 도달 시 Results). 벌점·위협 없음, 사망 없음.
**변형 2 · 검문형 3동사(That's not my Neighbor):** Verdict에 "신고"가 추가된다. 기본형은 ★1에 따라 **2동사 유지**를 권장하고, 신고는 "돌려보내기 + 추가 보상"으로 흡수한다.

## 2. 엔티티와 데이터 모델

| 엔티티 | 핵심 필드(타입) | 소유 | 저장 |
|---|---|---|---|
| AnomalyDef | `id: str` · `kind: "person"\|"data"` · `rule: str`(해금 규칙) · `lethal: bool` · `cue: str`(힌트 문구, ★7) · `visibility: float`(테스트 봇용) | 서버(정적 데이터) | 데이터 파일 |
| RuleDef | `id: str` · `night: int` · `text: str` | 서버(정적) | 데이터 파일 |
| VisitorDef(수작업) | `night: int` · `name: str` · `anomaly: str\|null` | 서버(정적) | 데이터 파일 |
| Visitor(런타임) | `index: int` · `anomaly_id: str\|null` · `scripted: bool` · `telegraph: bool` · `record: Record` · `stated: Record` | **서버** | 아니오 |
| Record | `year, month, day, hour: int` · 파생 `zodiac, year_pillar, day_pillar: str` | 서버 (stated만 클라이언트에 복제) | 아니오 |
| NightState | `n: int` · `elapsed: float` · `mistakes: int` · `fees, penalties: int` · `lethal_used: int` | **서버** | 밤 단위 스냅샷 |
| Session | `money: int` · `threat: int` · `active_rules: [str]` · `bag_remaining: [str]` · `nights_done: int` · `version: int` | **서버** | 예 (밤 끝마다) |
| DetectionLog | `rows: {anomaly_id: {night: [shown, detected]}}` | 서버 → 분석 | 예 (집계용) |

밸런스 Config 예시 (`sim/horror_sim.py`의 `CONFIG`와 같은 값. 출처가 README §4인 것만 표시, 나머지는 **예시값**):

```json
{
  "nights": 5,
  "night_seconds": 600,
  "visitor_seconds": 45,
  "visitors_per_night": 12,
  "scripted_per_night": [2, 3],
  "rules_per_night": [1, 2],
  "anomaly_ratio_by_night": [0.25, 0.30, 0.35, 0.40, 0.50],
  "lethal_cap_per_night": 1,
  "free_mistakes_per_night": 2,
  "penalty_ladder": [5, 5, 10, 15, 20],
  "penalty_step_after_ladder": 5,
  "fee_per_visitor": 10,
  "threat_per_admit": 1,
  "threat_max": 3,
  "threat_reset_per_night": true,
  "too_subtle_threshold": 0.30,
  "too_subtle_window_nights": 3,
  "too_subtle_min_shown": 4,
  "bot_false_reject_rate": 0.05,
  "current_year": 2026,
  "ipchun_month_day": [2, 4]
}
```

- README §4 출처: `night_seconds` 600 (FNAF 1, 한 밤 약 10분) · `scripted_per_night` `[2, 3]` (Papers, Please 하루 스크립트 2~3명) · `free_mistakes_per_night` 2 와 `penalty_ladder` `[5, 5, 10, 15, 20]` (Papers, Please 벌점, 매일 리셋).
- 나머지는 전부 **예시값**. `penalty_step_after_ladder`는 원전의 "20…"을 +5씩 연장한 해석. `ipchun_month_day`는 절기를 고정 날짜로 둔 프로토타입용 단순화이며, 실제 서비스는 만세력 절기표를 쓴다([`anomaly_detection.md`](anomaly_detection.md) §4).

## 3. 핵심 시스템

### 3.1 이상현상 풀: 무중복 뽑기와 발견률 로그
- **규칙:** 풀의 이상현상은 **나올 수 있는 것이 전부 나오기 전에는 다시 뽑지 않는다**(Exit 8, ★8). "나올 수 있는 것"은 현재 전달된 규칙으로 해금된 것으로 한정한다. 소진되면 가방을 다시 채우되, 같은 밤에 이미 나온 것은 후순위로 민다. 이상현상이 노출될 때마다 `(밤, 노출, 발견)`을 기록하고, 최근 N밤 동안 충분히 노출됐는데 발견률이 임계 미만이면 "너무 미묘"로 표시해 재조정 대상으로 올린다(Exit 8의 "이상현상 없음 버그" 제보가 실은 너무 미묘한 이상현상이었음).
- **공식:** `rate(a) = detected(a) / shown(a)` (최근 `too_subtle_window_nights`밤 합산). 플래그 조건: `shown(a) ≥ too_subtle_min_shown AND rate(a) < too_subtle_threshold`.
- **의사코드:**
```pseudo
class AnomalyBag(all_ids):  remaining = copy(all_ids)
function draw(allowed: Set<id>, rng, avoid: Set<id>) -> id
    repeat 2 times:
        pool  = [i for i in remaining if i in allowed]
        cands = [i for i in pool if i not in avoid] or pool      // 같은 밤 중복은 후순위
        if cands: pick = rng.choice(cands); remaining.remove(pick); return pick
        remaining = copy(all_ids)                                 // 소진 → 리필
    error "해금된 이상현상이 없음"
function consume(id): remaining.remove(id) if present           // 수작업 손님이 쓴 것도 뺀다

function too_subtle(log, last_night, cfg) -> [id]
    nights = [last_night - cfg.window + 1 .. last_night]
    return sorted(a for a in log if shown(a, nights) >= cfg.min_shown
                                 and detected(a, nights) / shown(a, nights) < cfg.threshold)
```
- **함정:** ① 수작업 손님의 이상현상을 가방에서 빼지 않으면 같은 밤에 절차 생성으로 또 나온다. ② 해금 안 된 것까지 가방에 넣고 "뽑았는데 못 쓰니 버림"을 하면 가방이 조기 소진된다. 허용 집합으로 **걸러서** 뽑는다. ③ 발견률을 밤 구분 없이 누적하면 초반 밤의 낮은 발견률이 영원히 남는다. 창(window)을 둔다.
- **검증:** ✅ `test_anomaly_no_repeat_until_exhausted` · ✅ `test_anomaly_draw_only_unlocked` · ✅ `test_detection_log_flags_too_subtle`

### 3.2 손님 생성기: 수작업 + 절차 혼합
- **규칙:** 밤마다 수작업 손님 2~3명(README §4, Papers, Please)을 **고르게 퍼뜨려** 배치하고(지루한 구간 없는 페이싱이 가장 어려운 일이었다는 Lucas Pope의 말), 남은 자리는 그 밤의 비율만큼 이상현상 자리를 무작위로 고른 뒤 3.1의 가방에서 뽑아 채운다. 정상 손님도 서류를 **일치하게** 생성한다(데이터형 이상현상의 대조군). 생성은 전부 서버·시드 고정 RNG에서 한다.
- **공식:** 수작업 i번째 자리 `slot_i = round((i+1) · total / (k+1)) − 1` (k = 수작업 수). 절차 이상현상 수 `n_anom = round(free · ratio[n])`.
- **의사코드:**
```pseudo
function generate_visitors(n, cfg, rng, bag, active_rules, scripted[n]) -> [Visitor]
    visitors = [null] * cfg.visitors_per_night ; lethal_used = 0
    for i, (name, aid) in enumerate(scripted[n]):
        slot = round((i+1) * total / (len(scripted[n]) + 1)) - 1
        visitors[slot] = Visitor(name, aid, scripted=true)
        if aid: bag.consume(aid); lethal_used += is_lethal(aid)
    free = [i for i in 0..total-1 if visitors[i] == null]
    anomaly_slots = rng.sample(free, round(len(free) * cfg.anomaly_ratio_by_night[n-1]))
    for i in free:
        aid = null
        if i in anomaly_slots:
            allowed = unlocked(active_rules)
            if lethal_used >= cfg.lethal_cap_per_night or i == 0: allowed -= lethal_ids
            aid = bag.draw(allowed, rng, avoid = ids_already_in(visitors)); lethal_used += is_lethal(aid)
        visitors[i] = Visitor("손님"+i, aid, scripted=false)
    for v in visitors: v.record = make_record(rng); v.stated = make_stated(v.record, v.anomaly_id, rng)
    return visitors
```
- **함정:** ① `round(2.5)`가 언어마다 다르다(파이썬은 짝수로). `floor(x + 0.5)`로 고정한다. ② 수작업 손님을 큐의 맨 앞이나 맨 뒤에 몰아 두면 "스크립트 손님은 늘 첫 손님"이 학습된다. ③ 절차 생성 수천 명을 자동으로 돌려 생성기 자체를 검증한다(Papers, Please 방식). 시뮬레이션 `--demo`가 그 최소형이다.
- **검증:** ✅ `test_visitor_mix_scripted_and_procedural`

### 3.3 규칙 누적과 전달
- **규칙:** 규칙은 밤 번호를 달고 있고, 밤마다 1~2개(★4)가 **NightNotice 상태에서만** 전달된다. 손님이 말하는 중에 새 규칙을 주면 플레이테스터가 무시한다(Lucas Pope). 전달된 규칙은 사라지지 않고 누적되며, 이상현상은 **자기 해금 규칙이 활성일 때만** 생성된다. 그래서 "아직 배우지 않은 걸로 벌점"이 생기지 않는다.
- **의사코드:**
```pseudo
function enter_night_notice(n):
    state = NIGHT_NOTICE                                   // 손님 없음
    new_rules = [r for r in RULES if r.night == n]
    assert 1 <= len(new_rules) <= 2
    active_rules += new_rules.ids
    show_notice_board(new_rules)                           // 대사·음성이 아니라 공지판
    wait_for(ack)
function unlocked(active_rules) -> Set<id>
    return {a.id for a in ANOMALY_POOL if a.rule in active_rules}
```
- **함정:** ① 규칙끼리 얽혀서 하나를 추가하면 다른 것이 깨진다(Papers, Please). 규칙 하나가 이상현상 집합 하나에만 대응하도록 1:N으로 둔다. ② 해금 규칙 없이 풀에 넣은 이상현상은 영원히 나오지 않는다. 로드 시 풀 전체의 `rule`이 RULES에 있는지 검사한다.
- **검증:** ✅ `test_rules_accumulate_per_night` · ✅ `test_rules_delivered_outside_dialogue`

### 3.4 판정 · 벌점 사다리 · 위협 게이지
- **규칙:** 판정은 둘뿐(★1). 정상을 들이면 복채, 정상을 돌려보내면 그 복채를 잃고 실수 1회, 이상현상을 돌려보내면 안전(복채 없음), 이상현상을 들이면 실수 1회 + **위협 게이지 상승**. 실수는 밤마다 2회까지 면제, 이후 5, 5, 10, 15, 20…(README §4), **밤이 바뀌면 리셋**. 위협이 `threat_max`에 닿으면 즉시 GameOver. 치명형을 들이면 위협을 한 번에 최대치로 올린다(= 즉사이지만 반드시 예고가 선행, 3.7). 재화 증감은 `resolve` 한 함수만 거친다([`core_systems.md` §4](../../systems/core_systems.md)).
- **공식:** k번째 실수의 벌점 `P(k) = 0 (k ≤ free) · ladder[k−free−1] (사다리 안) · ladder[-1] + step·(k−free−len(ladder)) (사다리 밖)`.
- **의사코드:**
```pseudo
function penalty_for(k, cfg) -> int
    idx = k - cfg.free_mistakes_per_night - 1
    if idx < 0: return 0
    if idx < len(cfg.penalty_ladder): return cfg.penalty_ladder[idx]
    return cfg.penalty_ladder[-1] + cfg.penalty_step_after_ladder * (idx - len(cfg.penalty_ladder) + 1)

function resolve(night, v, verdict, session, cfg) -> bool
    correct = (verdict == REJECT) == v.is_anomaly
    if correct and verdict == ACCEPT: night.fees += cfg.fee_per_visitor
    else if not correct:
        night.mistakes += 1 ; night.penalties += penalty_for(night.mistakes, cfg)
        if v.is_anomaly: session.threat += v.lethal ? cfg.threat_max : cfg.threat_per_admit
    if v.is_anomaly: detection_log.record(night.n, v.anomaly_id, verdict == REJECT)
    emit VisitorResolved(v, verdict, correct)
    return correct
// 밤 종료: session.money += night.fees - night.penalties ; night.mistakes = 0 ; threat는 cfg.threat_reset_per_night면 0
```
- **함정:** ① 벌점을 "실수 수 × 단가"로 구현하면 사다리가 아니다. 사다리는 **k번째 실수에 대한 값**이다. ② 위협 체크를 밤 끝에서만 하면 치명형을 들여도 손님을 계속 받는다. `resolve` 직후에 검사한다. ③ 실수 카운터와 위협 게이지의 리셋 시점을 섞지 않는다(벌점은 원전상 매일 리셋, 위협 리셋은 다이얼).
- **검증:** ✅ `test_penalty_ladder_two_free_then_escalate` · ✅ `test_penalty_resets_each_night` · ✅ `test_threat_gauge_game_over` · ✅ `test_threat_resets_each_night`

### 3.5 데이터 이상현상: 서류 대조
- **규칙:** 손님이 **말한 것**(stated)과 가게 기록에서 **파생한 것**(record → 띠·연주·일주)을 필드 단위로 대조한다(★3, Papers, Please 인터뷰). 정상 손님은 stated가 record와 파생값까지 완전히 일치하도록 만들고, 데이터형 이상현상은 **정확히 한 필드**만 어긋나게 만든다. 검사기는 어긋난 필드 목록을 돌려주며, 비어 있으면 일치다. 이상현상 종류: 날짜 불일치, 미래 출생연도, 띠 불일치, 일주 불일치, **입춘 경계**(입춘 전 출생인데 달력 연도의 연주를 말함).
- **공식(예시):** `pillar_year = year if (month, day) ≥ ipchun else year − 1` · `zodiac = ZODIAC[(pillar_year − 4) mod 12]` · `year_pillar = GANJI[(pillar_year − 4) mod 60]` · `day_pillar = GANJI[ordinal(date) mod 60]`. 실제 서비스는 절기 **시각**과 시간대 정책이 필요하므로 만세력 라이브러리의 표를 쓴다([`anomaly_detection.md`](anomaly_detection.md) §4).
- **의사코드:**
```pseudo
function derive(record) -> {zodiac, year_pillar, day_pillar}      // 위 공식
function make_stated(record, anomaly_id, rng) -> Record
    stated = record + derive(record)
    switch anomaly_id:
        "date_mismatch":       stated.day = random day != record.day
        "future_birth_year":   stated.year = current_year + rand(1, 30)
        "zodiac_mismatch":     stated.zodiac = ZODIAC[index ± 1]
        "day_pillar_mismatch": stated.day_pillar = GANJI[index + rand(1, 59)]
        "ipchun_boundary":     record.date = (ipchun.month, day < ipchun.day) ; stated = record + derive(record)
                               stated.year_pillar = GANJI[(record.year - 4) mod 60]   // 달력 연도로 잘못 말함
    return stated
function cross_check(stated, record) -> [field]
    flags = ["date"] if any(stated[f] != record[f] for f in year, month, day, hour) else []
    if stated.year > current_year: flags += ["future_year"]
    real = derive(record)
    return flags + [f for f in zodiac, year_pillar, day_pillar if stated[f] != real[f]]
```
- **함정:** ① 정상 손님의 서류를 "대충 비슷하게" 만들면 오탐이 생기고 플레이어는 검사기를 못 믿게 된다. 정상은 **파생값까지 같은 함수로** 만든다. ② 띠를 음력 설이나 1월 1일 기준으로 계산하면 입춘 경계 이상현상이 성립하지 않는다(간지는 절기 기준). ③ 클라이언트에 `record`를 보내면 메모리 읽기로 정답을 알 수 있다. `stated`만 복제하고 `record`는 서버에 둔다.
- **검증:** ✅ `test_document_crosscheck_flags_exactly_inconsistent` (정상 300건 오탐 0, 이상 종류별 100건 모두 해당 필드 적발)

### 3.6 밤 타이머와 상승 곡선
- **규칙:** 한 밤은 약 10분(FNAF 1, README §4; 0시~6시로 환산해 표시)이다. 손님 한 명이 `visitor_seconds`를 쓰고, 다음 손님을 받을 시간이 남지 않으면 밤이 끝난다(큐가 먼저 비어도 끝). 밤마다 이상현상 비율이 오르고(공격성 상승, ★9), 규칙이 누적되며(3.3), 치명형이 해금된다(3.7). 5밤 뒤 보너스 밤·커스텀 밤은 같은 루프에 `ratio`와 풀만 바꿔 붙인다.
- **공식:** `ratio[n] = anomaly_ratio_by_night[min(n, len) − 1]` (배열을 넘는 밤은 마지막 값 유지). 밤 안 시계 표시 `clock = 0시 + 6h · elapsed / night_seconds`.
- **의사코드:**
```pseudo
function run_shift(n, visitors, cfg):
    elapsed = 0
    for v in visitors:
        if elapsed + cfg.visitor_seconds > cfg.night_seconds: night.timer_ended = true; break
        elapsed += cfg.visitor_seconds           // 실제 구현은 Heartbeat dt 누적 + 손님별 제한 시간
        verdict = await_player_verdict(v)        // hold 완료까지 대기, 제한 시간 넘기면 '돌려보내기'로 처리(예시)
        resolve(night, v, verdict)
        if session.threat >= cfg.threat_max: transition(GAME_OVER); return
    transition(NIGHT_END)
```
- **함정:** ① 시간 압박은 "원할 때만 의도적으로"(Papers, Please 분석). 손님별 제한 시간을 빡빡하게 두면 서류 대조형이 망가진다. 밤 전체 타이머만 두고 손님별 제한은 넉넉히. ② `visitors_per_night × visitor_seconds > night_seconds`면 뒤쪽 수작업 손님이 영원히 안 나온다. 로드 시 검사한다. ③ 밤 번호가 배열 길이를 넘을 때 인덱스 오류(보너스 밤).
- **검증:** ✅ `test_night_timer_ends_shift` · ✅ `test_night_escalation_anomaly_ratio_rises`

### 3.7 공포 페이싱: 미묘 다수, 치명 드물게 + 예고
- **규칙:** 이상현상 대부분은 섬뜩하되 치명적이지 않고, 치명형(들이면 즉시 게임 오버급)은 **밤마다 상한**(예시 1)을 두며 **반드시 예고**가 선행한다(★6: 게임 오버 비중을 올린 Platform 8의 평가 하락). 예고는 치명형 손님 **직전 손님** 차례에 재생되는 노크·라디오 잡음 같은 신호다. 그래서 치명형은 첫 손님이 될 수 없다. 이해하기 어려운 이상현상에는 게임 안 힌트(부적 쪽지·장부, ★7)를 `cue`로 둔다.
- **의사코드:**
```pseudo
// generate_visitors 안에서
if lethal_used >= cfg.lethal_cap_per_night or slot == 0: allowed -= lethal_ids
...
for i, v in enumerate(visitors):
    if v.lethal: visitors[i-1].telegraph = true          // 직전 손님 차례에 예고 재생
// 클라이언트 연출: VisitorArrive 시 v.telegraph면 예고 사운드·조명 변화 → 다음 손님이 치명형
```
- **함정:** ① 예고를 치명형 손님 **자신**의 등장 연출로 넣으면 판정 전에 이미 늦다. 한 손님 앞에 둔다. ② 수작업 손님의 치명형을 상한에 세지 않으면 한 밤에 둘이 나온다. ③ Roblox Mild 등급(★10): 치명형 연출에 사실적 피를 쓰지 않는다.
- **검증:** ✅ `test_lethal_rare_and_telegraphed` (20시드 × 5밤: 밤당 치명형 ≤ 1, 모두 직전 손님에 예고, 첫 손님 아님)

### 3.8 협동 변형 (포인터만)
- **규칙:** 1~4인 협동은 **같은 상담석을 여러 명이 보되 판정은 한 번**으로 둔다: 판정 버튼은 누구나 hold할 수 있지만 서버는 손님당 첫 번째 완료된 hold만 받는다(나머지는 무시). 역할 분담(한 명은 거울, 한 명은 쪽지)은 살펴보기 대상을 클라이언트별로 다르게 보여 주는 것으로 충분하다. 파티는 예약 서버로 이동하고, 공개 매칭은 큐로 한다(★12). 자세한 API는 §7.
- **의사코드:**
```pseudo
on VerdictRequest(player, visitor_id, verb):
    if visitor_id != current.id or current.resolved: return     // 늦은 요청 무시
    current.resolved = true ; resolve(night, current, verb)
```
- **함정:** ① TeleportData에 밤 번호·시드를 넣으면 클라이언트가 읽고 바꿀 수 있다. 서버 저장소(세션 데이터)에서 다시 읽는다. ② 두 플레이어가 동시에 반대 판정을 완료하면 "먼저 도착한 것"이 정답이 되는데, 이는 네트워크 지연에 좌우된다. 손님당 **판정 잠금**을 명시한다.
- **검증:** — (네트워크·텔레포트는 시뮬레이션 범위 밖)

## 4. 틱 / 업데이트 순서

권위 측(서버) 한 틱. 물리가 없으므로 판정은 **이벤트 기반**, 타이머·게이지만 틱으로 돈다.

1. 입력 수집: 클라이언트 요청 큐(살펴보기, 판정 hold 완료, 공지 ack)를 비운다. 타입·범위·상태 검증(§5)에서 떨어지면 버린다.
2. 타이머 갱신: `elapsed += dt`. 남은 시간이 `visitor_seconds` 미만이면 다음 손님을 받지 않는다.
3. 상태 머신 전이 검사: 타이머 만료·큐 소진 → NightEnd, ack → Shift.
4. 현재 손님 판정 처리: 검증된 요청 하나만 `resolve`로 넘긴다(손님당 1회 잠금).
5. 정산: 복채·벌점·위협을 **단일 함수**에서 바꾼다.
6. 게임 오버 검사: `threat ≥ threat_max`면 즉시 전이, 이 틱의 나머지 단계는 건너뛴다.
7. 이벤트 발행: `VisitorResolved(visitor, verdict, correct)` → UI·오디오·분석·발견률 로그가 각자 구독.
8. 다음 손님 스폰: 큐에서 pop, `telegraph`면 예고 신호를 먼저 보낸다. `stated`만 복제한다.
9. 저장·스냅샷: NightEnd에서 Session(밤 번호·재화·가방 잔량·활성 규칙·`version`)을 저장. Shift 중에는 저장하지 않는다(손님 단위 재시작은 지원하지 않음).

틱 주기 **예시값**: 타이머·게이지 갱신은 엔진 프레임(Roblox `Heartbeat` dt, Godot `_process`)에서 누적하고, 클라이언트로의 상태 복제는 **1초 단위**면 충분하다. 근거: 한 밤이 약 10분(README §4)이고 초 단위 표시라 더 잦을 이유가 없다. 공통 루프 원칙은 [`core_systems.md` §1](../../systems/core_systems.md).

## 5. 신뢰 경계

재화·점수·확률·보상은 모두 서버. 원칙은 [`core_systems.md` §7](../../systems/core_systems.md), 플랫폼별은 §7.

| 클라이언트가 보내는 것 | 서버가 검증하는 규칙 | 거부 시 처리 |
|---|---|---|
| `Ack(night)` | 상태가 NightNotice이고 `night == current` | 무시 |
| `Inspect(visitor_id, target)` | 상태 Shift·Inspect, `visitor_id == current`, `target ∈ {face, hands, note, mirror}` | 무시 (살펴보기는 연출일 뿐 판정에 영향 없음) |
| `Verdict(visitor_id, verb)` | `verb ∈ {accept, reject}` · `visitor_id == current` · 손님당 미해결 · hold 시작 시각부터 `hold_seconds` 경과(서버 시계) · 플레이어별 레이트 리밋 | 무시 + 로그. 반복되면 세션 종료 |
| (협동) `JoinParty`, `Ready` | 파티 인원 ≤ 4, 중복 참가 아님 | 거부 응답 |
| 보내지 **않는** 것 | 이상현상 여부, 정답, `record`, 복채·벌점·위협 수치, 시드, 밤 번호 | — (서버 전용) |

클라이언트가 받는 것은 `stated` 서류, 손님의 **보이는** 속성(손가락 수 등 연출 데이터), 공지 텍스트, 타이머·게이지 표시값뿐이다. 정답(`anomaly_id`)은 `resolve` 뒤에야 내려보낸다(결과 연출용).

## 6. 밸런스 다이얼

| 다이얼 | 무엇을 바꾸나 | 기본값(출처) | 올리면 / 내리면 체감 |
|---|---|---|---|
| `visitors_per_night` | 한 밤 손님 수 | 12 (예시값) | 올리면 밤이 빽빽해지고 수작업 손님 비중이 줄어듦 / 내리면 손님 하나하나가 무거워짐 |
| `visitor_seconds` | 손님당 평균 소요(타이머 예산) | 45 (예시값) | 올리면 뒤쪽 손님이 타이머에 잘림 / 내리면 시간 압박이 사라짐 |
| `anomaly_ratio_by_night` | 밤별 이상현상 비율 | 0.25→0.50 (예시값) | 올리면 "다 돌려보내기"가 최적이 됨 / 내리면 지루한 구간 발생 |
| `free_mistakes_per_night` | 면제 실수 수 | 2 (README §4) | 올리면 관대, 벌점이 거의 안 쌓임 / 0이면 첫 실수부터 처벌 |
| `penalty_ladder` | 실수별 벌점 | 5,5,10,15,20 (README §4) | 가파르게 하면 밤 후반 실수가 치명적 / 평평하면 실수 수가 의미 없음 |
| `threat_per_admit`·`threat_max` | 들인 이상현상당 위협·한계 | 1·3 (예시값) | `threat_max` 3은 시뮬 봇(평균 발견률 약 0.55)으로 10시드 중 8시드가 GameOver. 실제 플레이어 기준으로 재조정 필요 |
| `threat_reset_per_night` | 위협이 밤마다 리셋되는지 | true (예시값) | false면 5밤 누적이라 FNAF식 장기 긴장 / true면 밤마다 새 출발 |
| `lethal_cap_per_night` | 밤당 치명형 상한 | 1 (예시값) | 올리면 게임 오버 비중 증가(Platform 8 사례) / 0이면 Exit 8식 무사망 |
| `scripted_per_night` | 수작업 손님 수 | 2~3 (README §4) | 올리면 페이싱 통제력↑, 제작비↑ / 내리면 밤마다 비슷해짐 |
| `too_subtle_threshold` | "너무 미묘" 임계 발견률 | 0.30 (예시값) | 올리면 재조정 대상이 늘어남 / 내리면 미묘한 이상현상이 방치됨 |

## 7. 플랫폼 매핑

| 시스템 | Godot | Roblox |
|---|---|---|
| 상태 머신(§1) | [`StateMachine.gd`](../../platforms/godot/patterns/StateMachine.gd) + [`State.gd`](../../platforms/godot/patterns/State.gd): Lobby/NightNotice/Shift/NightEnd/GameOver/Results를 State 노드로 | [`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau)의 라운드 FSM을 밤 FSM으로. 현재 상태는 Attribute로 복제 |
| 정적 데이터(AnomalyDef·RuleDef·VisitorDef) | Resource(`.tres`) — [`architecture.md` §4](../../platforms/godot/architecture.md). 런타임 값은 `duplicate()` 또는 노드 변수로 | `ReplicatedStorage.Shared.Config` ModuleScript(`table.freeze`) — [`architecture.md` §4](../../platforms/roblox/architecture.md). `record`·정답은 `ServerStorage`에 |
| 손님 생성·가방(3.1~3.2) | 시드 고정 `RandomNumberGenerator` ([`Gacha.gd`](../../platforms/godot/patterns/Gacha.gd)의 시드 처리 참고) | 서버 `Random.new(seed)`. 클라이언트 RNG 금지 |
| 판정 요청(3.4, §5) | 싱글은 로컬 호출. 랭킹을 붙이면 플레이 로그 재검증 ([`architecture.md` §6](../../platforms/godot/architecture.md)) | [`SecureRemote.luau`](../../platforms/roblox/patterns/SecureRemote.luau): 타입→범위→상태 검증 + 레이트 리밋. 버튼은 `ProximityPrompt`(HoldDuration, `ProximityPromptService`) |
| 정산·재화 | [`Economy.gd`](../../platforms/godot/patterns/Economy.gd) 단일 진입점 | 단일 `addCurrency` 함수. 복채는 게임 내 재화만(★11), 운세·부적 Robux 판매 금지 |
| 이벤트(틱 7) | [`EventBus.gd`](../../platforms/godot/patterns/EventBus.gd) `visitor_resolved` 시그널 | `BindableEvent` 또는 Signal 모듈. 분석·발견률 로그가 구독 |
| 저장(틱 9) | [`SaveManager.gd`](../../platforms/godot/patterns/SaveManager.gd): `version`·마이그레이션·원자적 저장 | [`DataService.luau`](../../platforms/roblox/patterns/DataService.luau)(ProfileStore 세션 잠금) |
| 예고·분위기(3.7) | `AudioStreamPlayer3D`, 조명 트윈 | `AudioEmitter` 3D, `Atmosphere` Haze·Density, `Lighting.ClockTime` ([`anomaly_detection.md`](anomaly_detection.md) §2) |
| 협동(3.8) | 범위 밖(싱글) | `GetPlayersByPartyId` → `TeleportAsync` + `ShouldReserveServer=true`, 공개 매칭은 MemoryStore 큐. TeleportData에 민감 값 금지 ([`anomaly_detection.md`](anomaly_detection.md) ★12) |
| 등급 | — | Mild 유지(점프스케어 허용, 사실적 피 금지) ([`anomaly_detection.md`](anomaly_detection.md) §3) |

플랫폼 규칙 전문: [`../../platforms/godot/RULES.md`](../../platforms/godot/RULES.md) · [`../../platforms/roblox/RULES.md`](../../platforms/roblox/RULES.md).

## 8. 검증 (sim/)

[`sim/horror_sim.py`](sim/horror_sim.py) (표준 라이브러리만, 시드 고정)이 검사하는 규칙:

| # | 테스트 | 한 줄 |
|---|---|---|
| 1 | `test_anomaly_no_repeat_until_exhausted` | 풀 12개를 12번 뽑으면 전부 다르고, 리필 뒤 한 바퀴도 중복 없음. 리필 뒤에는 같은 밤에 안 나온 것을 먼저 |
| 2 | `test_anomaly_draw_only_unlocked` | 해금 집합 밖의 이상현상은 절대 안 나옴 |
| 3 | `test_visitor_mix_scripted_and_procedural` | 밤마다 손님 12명, 수작업 2~3명이 맨 앞·맨 뒤가 아닌 자리에 분산, 나머지는 절차 생성 |
| 4 | `test_rules_accumulate_per_night` | 밤마다 규칙 1~2개 추가·누적, 그 밤의 이상현상은 전부 활성 규칙으로 해금된 것 |
| 5 | `test_rules_delivered_outside_dialogue` | 규칙 전달 이벤트는 모두 NightNotice 상태, 손님 판정은 모두 Shift 상태 |
| 6 | `test_penalty_ladder_two_free_then_escalate` | 실수 1~8회 벌점 = 0, 0, 5, 5, 10, 15, 20, 25 |
| 7 | `test_penalty_resets_each_night` | 전부 돌려보내는 봇: 1밤 실수가 면제를 넘어도 2밤 벌점은 1회부터 다시 계산 |
| 8 | `test_threat_gauge_game_over` | 전부 들이는 봇: 1밤 안에 GameOver, 그 뒤 손님을 받지 않음 |
| 9 | `test_threat_resets_each_night` | 위협 2로 시작해도 밤이 시작되면 0 |
| 10 | `test_document_crosscheck_flags_exactly_inconsistent` | 정상 서류 300건 오탐 0, 데이터 이상현상 5종 × 100건 모두 해당 필드 적발 |
| 11 | `test_night_escalation_anomaly_ratio_rises` | 비율 배열이 단조 증가, 생성된 절차 이상현상 수도 밤마다 비감소 |
| 12 | `test_night_timer_ends_shift` | 손님당 100초면 600초 안에 6명만 받고 밤이 끝남, 45초면 12명 전부 |
| 13 | `test_lethal_rare_and_telegraphed` | 20시드: 밤당 치명형 ≤ 1, 첫 손님 아님, 직전 손님에 예고 |
| 14 | `test_detection_log_flags_too_subtle` | 3밤 창에서 노출 ≥ 4·발견률 < 0.3인 것만 플래그, 창 밖 밤은 제외, 노출 부족은 보류 |
| 15 | `test_full_run_deterministic` | 같은 시드 두 판의 요약과 이벤트 로그가 동일 |

```bash
python3 -I reference/genres/horror/sim/horror_sim.py --test     # 종료 코드 = 실패 수
python3 -I reference/genres/horror/sim/horror_sim.py --demo --seed 2026
```

실행 결과 (2026-10-17, Python 3 표준 라이브러리): **`passed 15/15`**, 종료 코드 0.

`--demo --seed 2026` 요약: 밤 1~5 각 12명, 이상현상 4·4·5·6·6명, 새 규칙 2·2·1·2·2개, 5밤에 위협 3 도달로 GameOver, 재화 330, "너무 미묘" 없음(노출 수 부족). 10시드 중 2시드만 Results 도달 → §6 `threat_max` 참고.

## 9. 흔한 구현 버그

1. **"이상현상 없음" 제보가 쏟아진다** → 발견률 로그가 없어서 너무 미묘한 이상현상을 구분 못 함 → 3.1의 로그와 `too_subtle` 플래그를 붙이고, 플래그된 것은 힌트(★7)를 추가하거나 삭제한다.
2. **같은 밤에 같은 이상현상이 두 번** → 수작업 손님의 이상현상을 가방에서 빼지 않았거나, 리필 뒤 같은 밤 회피가 없음 → `bag.consume(scripted.anomaly)` + `draw(avoid=이 밤에 나온 것)`.
3. **밤 2에 아직 안 배운 거울 이상현상이 나온다** → 해금 규칙 필터 없이 전체 풀에서 뽑음 → `allowed = unlocked(active_rules)`로 걸러서 뽑는다.
4. **벌점이 3회째부터 5, 10, 15로 뛴다** → 사다리를 "실수 수 × 5"나 누적 합으로 구현 → k번째 실수에 `ladder[k − free − 1]`을 적용한다(§3.4).
5. **치명형을 들였는데 다음 손님이 나온다** → 위협 검사를 밤 끝에서만 함 → `resolve` 직후 `threat ≥ threat_max` 검사 후 즉시 GameOver 전이.
6. **치명형이 첫 손님으로 나와 예고 없이 죽는다** → 예고를 "직전 손님"에 붙이는데 직전이 없음 → 첫 자리에서는 치명형을 허용 집합에서 뺀다.
7. **정상 손님인데 검사기가 띠 불일치를 낸다** → 정상 서류의 띠를 달력 연도로, 검사기는 입춘 기준으로 계산 → 정상·이상 모두 같은 `derive()`로 파생값을 만든다.
8. **클라이언트가 판정 버튼을 연타해 복채가 두 번 들어온다** → 손님당 판정 잠금 없음 → `visitor_id == current && !resolved` 검사, 레이트 리밋(§5).
