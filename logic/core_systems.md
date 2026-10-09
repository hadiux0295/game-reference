# 핵심 시스템 (엔진 무관)

어떤 엔진이나 플랫폼에서도 똑같이 쓰이는 게임 로직의 뼈대입니다.
코드는 **의사코드(pseudo)**로 적었습니다. 플랫폼별 실제 구현은 `../platforms/`를 참고하세요.

| # | 시스템 | 한 줄 요약 |
|---|---|---|
| 1 | 게임 루프 | 고정 타임스텝으로 로직을 돌리고, 렌더는 보간 |
| 2 | 상태 머신 | 화면, 라운드, 캐릭터 상태를 명시적 전이로 관리 |
| 3 | 난수(RNG) | 시드 고정, 서버 판정, 가중치·천장 |
| 4 | 경제 | 재화 증감은 단일 함수에서, 수입원과 소비처 균형 |
| 5 | 성장 곡선 | 지수·다항 비용 곡선, 리버스(프레스티지) |
| 6 | 저장 | 버전 필드와 마이그레이션, 원자적 저장, 중복 지급 방지 |
| 7 | 신뢰 경계 | 클라이언트는 요청만, 판정은 권위 측이 |
| 8 | 이벤트 / 디커플링 | 시스템 간 직접 호출 대신 이벤트 |
| 9 | 데이터 주도 설계 | 밸런스는 코드가 아니라 테이블에 |
| 10 | AI / 길찾기 | FSM → 행동트리 → 유틸리티 AI, A* |

---

## 1. 게임 루프: 고정 타임스텝

프레임레이트가 기기마다 다르면 물리나 판정 결과도 달라집니다. 그래서 **로직은 고정 간격으로**, **렌더는 가능한 만큼** 돌립니다 (Glenn Fiedler, "Fix Your Timestep").

```pseudo
const DT = 1/60
accumulator = 0
loop:
    frameTime = min(now() - last, 0.25)   // 죽음의 나선 방지
    last = now()
    accumulator += frameTime
    while accumulator >= DT:
        previous = state
        update(state, DT)                   // 게임 로직
        accumulator -= DT
    alpha = accumulator / DT
    render(lerp(previous, state, alpha))    // 부드러운 화면
```

- 하이퍼캐주얼처럼 물리가 단순한 게임은 가변 `dt`로도 충분합니다. 다만 **리플레이, 멀티플레이, 물리 퍼즐**에는 고정 스텝이 필요합니다.
- Roblox는 엔진이 루프를 관리합니다. `RunService.Heartbeat`에서 `dt`를 받아 쓰면 됩니다.

## 2. 상태 머신 (FSM)

```pseudo
states = {
  Menu:     { onEnter, onExit, transitions: { play: "Playing" } },
  Playing:  { ..., transitions: { die: "GameOver", pause: "Paused" } },
  Paused:   { ..., transitions: { resume: "Playing", quit: "Menu" } },
  GameOver: { ..., transitions: { retry: "Playing", home: "Menu" } },
}
function send(event):
    next = states[current].transitions[event]
    if next == nil: return            // 허용되지 않은 전이 무시 → 버그 방지
    states[current].onExit()
    current = next
    states[current].onEnter()
```

- 쓰이는 곳: 화면 흐름, 라운드 진행, 캐릭터 상태(대기, 이동, 공격, 피격), 튜토리얼 단계
- **if문을 늘리는 대신 상태를 추가하세요.** 상태 조합이 폭발하면 계층형 FSM이나 행동트리로 넘어갑니다.

## 3. 난수 (RNG)

| 상황 | 규칙 |
|---|---|
| 리플레이, 일일 퍼즐, 같은 맵 공유 | **시드 고정** RNG (`Random(seed)`). 같은 시드면 같은 결과 |
| 보상, 뽑기, 드롭 | **권위 측(서버)에서** 계산. 클라이언트 RNG는 조작 가능 |
| 체감 공정성 | 순수 랜덤보다 **셔플 백**(테트리스 7-bag)이나 **천장(pity)**을 사용 |

가중치 뽑기 + 천장:

```pseudo
function roll(pool, player):
    player.pityCount += 1
    if player.pityCount >= PITY_LIMIT:          // 예: 90회 내 최고 등급 보장
        player.pityCount = 0
        return pickFrom(pool.filter(r => r.rarity == "Legendary"))
    total = sum(pool.weight)
    r = rng.next(0, total)
    for item in pool:
        r -= item.weight
        if r <= 0:
            if item.rarity == "Legendary": player.pityCount = 0
            return item
```

> ⚠️ 유료 확률형 아이템은 국가와 플랫폼 정책상 **확률 공개 의무**가 있습니다. 한국은 2024년부터 법적 의무입니다. 확률표는 코드와 같은 데이터에서 생성해 불일치를 막으세요.

## 4. 경제 (Sources & Sinks)

```
수입원(Source): 플레이 보상, 일일 보상, 광고 시청, 결제
소비처(Sink):   업그레이드, 뽑기, 소모품, 꾸미기, 리버스
```

- 수입원만 많으면 인플레이션이 생기고 재화 가치가 사라집니다. 소비처만 많으면 유저가 막혀서 이탈합니다.
- **재화 증감은 반드시 하나의 함수**(`addCurrency(player, type, amount, reason)`)를 거치게 합니다. 로그와 UI 갱신, 치트 탐지 지점이 하나로 모입니다.
- `reason`을 로그로 남기면 "재화가 어디서 얼마나 생기고 사라지는가"를 대시보드로 볼 수 있습니다.
- 정수 재화를 쓰고 부동소수점은 피하세요. 방치형처럼 수치가 큰 게임은 큰 수 라이브러리나 `mantissa × 10^exponent` 표현을 씁니다.

## 5. 성장 곡선

| 곡선 | 식 | 느낌 | 쓰임 |
|---|---|---|---|
| 선형 | `base + k·n` | 금방 지루함 | 초반 튜토리얼 |
| 다항 | `base · n^p` (p≈1.5~2.5) | 완만한 증가 | RPG 레벨 경험치 |
| 지수 | `base · r^n` (r≈1.07~1.15) | 빠르게 벽 | 방치형 업그레이드 비용 |

- 방치형의 정석: **비용은 지수, 생산량은 선형 또는 배수**로 늘립니다. 그러면 언젠가 벽에 부딪히고, 그 벽을 **리버스(프레스티지)**로 넘깁니다. 진행을 초기화하는 대신 영구 배율을 줍니다.
- N개 일괄 구매 비용(등비수열 합): `base · r^n · (r^k − 1) / (r − 1)`
- 밸런스는 **스프레드시트로 먼저 시뮬레이션**한 뒤 코드에 반영합니다. "N분 플레이 시 레벨"을 표로 만들어 보세요.

## 6. 저장 (Save)

```pseudo
save = {
  version: 3,                 // 스키마 버전: 반드시 넣기
  coins: 0, level: 1, items: {}, settings: {},
  processedPurchaseIds: [],   // 결제 중복 지급 방지
}
function load(raw):
    data = raw ?? defaultSave()
    while data.version < CURRENT_VERSION:
        data = migrations[data.version](data)   // v1→v2→v3 순차 변환
    return fillMissingFields(data, defaultSave()) // 새 필드 자동 보충
```

- **원자적 저장**: 임시 파일에 쓴 뒤 rename합니다. 쓰는 도중 앱이 죽어도 이전 세이브가 살아 있습니다.
- **자동 저장 시점**: 앱이 백그라운드로 갈 때(모바일 필수), 주요 진행 직후, 주기적으로(30~60초)
- **동시성**: 여러 서버나 기기가 같은 데이터를 쓰면 **세션 잠금**이 필요합니다 (Roblox의 ProfileStore 방식).
- **결제 멱등성**: 영수증 ID를 저장해 두고, 같은 영수증이 다시 와도 한 번만 지급합니다.

## 7. 신뢰 경계 (치트 방지)

- **싱글 오프라인 게임**: 클라이언트가 곧 권위입니다. 세이브 변조는 막기 어려우니 랭킹이나 결제와 엮일 때만 신경 씁니다.
- **온라인, 랭킹, 결제가 있는 게임**: 서버가 권위입니다.
  - 클라이언트는 `"코인 주워도 돼?"`라고 요청만 하고, `"코인 +100 해줘"`라고 명령할 수 없습니다.
  - 서버는 타입, 범위, 거리, 쿨다운, 소유권을 검증합니다.
  - 점수 제출은 **플레이 로그나 시드를 함께 받아 재검증**하거나, 최소한 이론상 최대치를 넘는지 확인합니다.
  - 요청마다 레이트 리밋을 둡니다.

## 8. 이벤트로 시스템 분리

```pseudo
events.emit("EnemyKilled", { enemy, killer })
// 각 시스템이 독립적으로 구독
quests.on("EnemyKilled", ...)      // 퀘스트 진행
achievements.on("EnemyKilled", ...)
audio.on("EnemyKilled", ...)
analytics.on("EnemyKilled", ...)
```

- 전투 코드가 퀘스트나 업적을 몰라도 되므로, 기능을 추가해도 기존 코드를 수정하지 않습니다.
- 구독 해제를 잊으면 메모리 누수가 생깁니다. Trove나 Janitor 같은 정리 도구를 쓰세요.

## 9. 데이터 주도 설계

```pseudo
// config/enemies.json  ← 기획자와 AI가 수정하는 곳
{ "slime": { "hp": 10, "speed": 2, "reward": 1, "spawnWeight": 60 },
  "bat":   { "hp": 6,  "speed": 5, "reward": 2, "spawnWeight": 30 } }
```

- 코드는 "어떻게 동작하는가"만 담고, 수치와 목록은 데이터에 둡니다.
- 원격 설정(Remote Config)과 결합하면 **앱 업데이트 없이 밸런스를 조정하고 A/B 테스트**를 할 수 있습니다.

## 10. AI와 길찾기

| 단계 | 기법 | 언제 |
|---|---|---|
| 1 | FSM | 적 행동 3~5개 수준 |
| 2 | 행동 트리 (Behavior Tree) | 조건 분기가 많고 재사용이 필요할 때 |
| 3 | 유틸리티 AI | "가장 점수가 높은 행동" 선택, 자연스러운 의사결정 |
| 4 | GOAP | 목표 기반 계획. 복잡하므로 정말 필요할 때만 |

- 길찾기: 그리드나 내비메시에서 **A\***를 씁니다. 같은 목적지로 대량의 유닛이 움직이면 **플로우 필드**를 씁니다 (타워디펜스, RTS).
- 길찾기는 매 프레임 하지 말고, 목표가 바뀌거나 일정 주기마다만 다시 계산합니다.

---

## 참고 원전
- Robert Nystrom, *Game Programming Patterns*: 게임 루프, 상태, 이벤트 큐, 컴포넌트
- Glenn Fiedler, "Fix Your Timestep!": 고정 타임스텝
- Amit Patel (Red Blob Games): A*, 그리드, 절차적 생성
- Gabriel Gambetta, "Fast-Paced Multiplayer": 클라이언트 예측과 서버 권위
- 방치형 게임 수학: Kongregate "The Math of Idle Games" 시리즈

> 각 자료의 링크와 라이선스는 [`../sources.md`](../sources.md)에 정리합니다.
