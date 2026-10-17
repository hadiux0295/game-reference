# game-reference

**어떤 게임을 만들든, 여기서 시작합니다.** 참고할 것이 어디 있는지 한 화면에서 찾는 저장소입니다.
사람과 AI 팀(Lumi, Sunsu, Sage, Blitz, Scout)이 함께 씁니다. 작업 규칙은 [`AGENTS.md`](AGENTS.md).

## 둘로 나뉩니다

| | 폴더 | 무엇 | 성격 |
|---|---|---|---|
| **① 메인** | [`reference/`](reference/README.md) | 장르별 인기 게임 · 핵심 루프 · 수치 · 원전 · 오픈소스 · 플랫폼 규칙 | 시간이 지나도 참인 것. 날짜가 아니라 **확인일**이 붙는다 |
| ② 우리 것 | [`our_games/`](our_games/README.md) | 우리가 만든 게임 스냅샷, 진행 중인 작업물 | 바뀌는 것. 참고용 색인("이미 해본 것")으로만 쓴다 |

## 시작점: 무슨 게임을 만드나?

| 장르 | 폴더 | 안에 있는 것 |
|---|---|---|
| 전략 (RTS · 4X · 모바일 SLG · 카드 전략 · 오토배틀러 · 타워 디펜스) | [`reference/genres/strategy/`](reference/genres/strategy/README.md) | 대표작 · 루프 · TD 수치 · 락스텝 원전 |
| 슈팅 (FPS · TPS · 배틀로얄 · 히어로 슈터 · Roblox 슈터) | [`reference/genres/shooter/`](reference/genres/shooter/README.md) | 대표작 · TTK · 넷코드 원전 |
| 롤 계열 (MOBA) | [`reference/genres/moba/`](reference/genres/moba/README.md) | 대표작 · 3레인 경제 · 매치 길이 |
| 캐주얼 (하이퍼 · 하이브리드 · 퍼즐 · 정렬/잼 · 머지 · Roblox 캐주얼) | [`reference/genres/casual/`](reference/genres/casual/README.md) | 대표작 · 레벨 생성 · 시장 수치 |
| RPG · 방치형 (액션 · 가차 · 방치형 · 서바이버류 · 로그라이트 · Roblox 시뮬레이터) | [`reference/genres/rpg/`](reference/genres/rpg/README.md) | 대표작 · 성장 곡선 · 천장 |
| 호러 · 판별 (이상현상 · 검문 · 교대 근무) | [`reference/genres/horror/`](reference/genres/horror/README.md) | 대표작 · 판별 설계 원전 · Roblox 호러 등급 |
| 아케이드 · Roblox 포맷 (Obby · 러너 · 타이쿤 · .io · 라운드제 파티) | [`reference/genres/arcade/`](reference/genres/arcade/README.md) | 대표작 · 포맷별 루프 · 미로/물리 자료 |

장르 폴더마다 `README.md`(무엇이 팔리고 왜) · `logic.md`(**기본 베이스 로직**: 구현 뼈대) · `sim/`(파이썬 규칙 시뮬레이션, `--test`로 검증)가 있습니다.

장르와 무관한 공통 시스템(게임 루프, FSM, RNG, 경제, 저장, 치트 방지)은 [`reference/systems/`](reference/systems/core_systems.md),
엔진별 규칙과 검증된 패턴 코드는 [`reference/platforms/godot/`](reference/platforms/godot/RULES.md) · [`reference/platforms/roblox/`](reference/platforms/roblox/RULES.md),
다른 게임의 실제 수치는 [`reference/data/`](reference/data/README.md), 원전·학습 자료는 [`reference/sources.md`](reference/sources.md).

## 구조

```
game-reference/
├─ README.md                  ← 이 파일. 시작점
├─ AGENTS.md                  ← AI 팀 규칙
├─ reference/                 ← ① 메인: 시간이 지나도 참인 것
│  ├─ README.md               ← 장르 × 플랫폼 색인 + 채움 상태
│  ├─ genres/                 ← 장르별 폴더 (같은 틀)
│  │  ├─ strategy/  shooter/  moba/  casual/  rpg/  horror/  arcade/
│  │  │   ├─ README.md        ← 대표작 · 루프 · 수치 · 원전 · 함정 · 우리 적용
│  │  │   ├─ logic.md         ← 기본 베이스 로직 (MVP · 상태 머신 · 데이터 모델 · 시스템 · 틱 · 신뢰 경계 · 다이얼 · 플랫폼 매핑)
│  │  │   └─ sim/             ← 파이썬 규칙 시뮬레이션 (python3 -I <장르>_sim.py --test)
│  │  └─ _template.md
│  ├─ systems/                ← 엔진 무관 공통 시스템 (core_systems.md · genres.md 한 장 요약)
│  ├─ platforms/godot/        ← Godot 4 규칙 · 구조 · 라이브러리 · 검증된 GDScript 패턴 (+ 헤드리스 테스트)
│  ├─ platforms/roblox/       ← Roblox 규칙 · 구조 · 라이브러리 · Luau 패턴
│  ├─ data/                   ← 참고 게임 수치 (행마다 source: 출처)
│  └─ sources.md              ← 원전: 책 · 아티클 · 오픈소스 · 큐레이션 목록
└─ our_games/                 ← ② 우리 것: 게임 목록 스냅샷 · 작업물 (anomaly_shop/ …)
```

## 핵심 원칙
1. **판정은 서버(권위 측)가.** 클라이언트는 요청만 합니다.
2. **저장은 버전 관리와 멱등 처리.** 데이터가 꼬이지 않게, 결제가 두 번 지급되지 않게 합니다.
3. **수치는 데이터로.** 밸런스 조정이 코드 수정 없이 끝나야 합니다.
4. **라이선스 확인 후 재사용.** 라이선스가 없거나 GPL인 코드는 구조만 참고합니다.
5. **출처 없는 숫자는 적지 않습니다.** 확인하지 못한 것은 `미검증`.

## 상태
- 2026-10-17: 저장소를 `reference/`(메인)와 `our_games/`(우리 것) 둘로 나누고 장르 폴더 7개를 세웠다. 채움 상태는 [`reference/README.md`](reference/README.md)의 표에 있다.
- 외부 저장소 정보(라이선스, 아카이브 여부)는 각 문서의 **확인일** 기준으로 GitHub 페이지를 직접 확인한 것입니다.
- `reference/platforms/godot/patterns/`의 GDScript 코드는 **Godot 4.7.1 헤드리스 테스트 22개 항목을 통과**했습니다 (`godot --headless --path reference/platforms/godot`). 실제 모바일 기기 테스트는 아직 하지 않았습니다.
- `reference/platforms/roblox/patterns/`의 Luau 코드는 `luau-compile`로 **문법 검사만 통과**했습니다. Roblox Studio에서 실행 검증은 아직 하지 않았습니다.
