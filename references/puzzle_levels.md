# 퍼즐 레벨 생성, 난이도, 하이브리드 캐주얼: 등불 항구 · 오행 정리

> 대상: [`our_games`](../our_games/README.md)의 **A 등불 항구 (Lantern Harbor)** 와 **A1 오행 정리**
> 조사일: **2026-10-09**. "라이선스 없음"은 모든 권리가 보호된다는 뜻이라 **읽기만** 가능합니다. 확인하지 못한 항목은 **미검증**으로 표시했습니다.

---

## ★ 등불 항구: 설계·구현 시사점

1. **솔버를 2단계로 나눕니다.** (우리 쪽 도출)
   - 정박지 없이 화살표만 빼내는 경우는 *단조적*입니다. 배 하나를 빼도 다른 배를 막지 않습니다. 그래서 "막힘 그래프"에 순환이 없으면 풀리고, 빠져나갈 수 있는 배를 아무거나 계속 빼면 해가 됩니다.
   - 정박지 5칸이 붙으면 **순서가 중요해집니다.** 상태 `(남은 배 비트마스크, 정박지 내용, 바람 사용 여부)`를 DFS/BFS로 탐색하고, 전치표(방문 기록)로 중복을 줄입니다.
   - 근거: [goarrows](https://github.com/sergev/goarrows), [defnull Snek!](https://defnull.de/snek/)
2. **역순으로 생성하고, 매 빌드마다 CI에서 검증합니다.**
   - 제거 순서의 역순으로 배를 놓으면 풀 수 있음이 보장됩니다.
   - **바람 레벨 생성법:** 바람 이후의 탈출 순서를 먼저 만듭니다 → 남은 배를 반시계 90°로 되돌려 바람 이전 배치를 얻습니다 → 그 앞에 바람 전 제거 단계를 붙입니다.
   - **"바람 필수" 판정:** `solve(바람 없음)`은 실패하고 `solve(바람)`은 성공해야 합니다.
   - 근거: [Rhythm Themes Arrow Escape 개발기](https://rhythm-themes.onrender.com/blog/arrow-escape-puzzle-game) (빌드마다 전 레벨 솔버 테스트), [Taylor & Parberry](https://ianparberry.com/techreports/LARC-2011-01.pdf) ("역방향으로 도달 가능한 상태는 정방향으로 풀린다")
3. **바람 필수 39판은 힐클라이밍으로 다듬습니다.** 배 하나의 방향, 색, 위치만 바꿔 보고, 다음 두 조건을 만족하는 변경만 남깁니다.
   - 여전히 바람 없이는 풀리지 않는다
   - 해의 깊이나 막다른 수가 늘어난다
   - 근거: [Sturtevant AIIDE 2020](https://ojs.aaai.org/index.php/AIIDE/article/view/7421) (타일 하나만 바꿔도 해의 길이가 크게 늘고, 플레이어는 흥미롭게 느낌)
4. **난이도 지표를 조합한 뒤 플레이 데이터로 회귀합니다.**
   - 의존 트리의 크기, 깊이, 폭 ([defnull](https://defnull.de/snek/))
   - 지는 첫 수의 개수와 상태 공간 크기 ([Fling!](https://www.gamedeveloper.com/design/the-saturday-paper---exhausting))
   - 최선 경로에서 정박지가 가장 많이 찬 순간의 점유 수
   - 탭 수 대신 **색 그룹 전환 횟수** (Sokoban의 "box lines" 개념 응용)
   - 같은 깊이에 대안 해가 많은 "형제 해"에 대한 패널티
   - 위 지표를 플레이어 평가나 실패율에 회귀 ([van Kreveld 외](https://ics-websites.science.uu.nl/docs/vakken/mscip/assignments/CIG2015-AutomatedPuzzleDifficultyEstimation.pdf), 10점 척도에서 오차 약 1점)
5. **제약 하나에 부스터 하나를 대응시킵니다.**
   - 부스터: 정박지 +1칸, 되돌리기(배를 판으로 복귀), 두 번째 바람 카드
   - 정박지가 넘쳐 실패하는 순간 **엔드게임 오퍼**를 띄웁니다.
   - 근거: [Deconstructor of Fun](https://www.deconstructoroffun.com/blog/the-screw-puzzle-gold-rush), [AppMagic Q2'25](https://gamedevreports.substack.com/p/appmagic-top-10-hybrid-casual-games)
6. **레벨은 결정적으로 만듭니다.** 재시작해도 같은 판이 나와야 합니다.
   - 실패율 목표: 일반 레벨 약 50%(평균 2회 시도), 난이도 스파이크도 평균 5회 이하. 시도 횟수의 꼬리 분포를 따로 감시하세요.
   - **60판은 공개 테스트 권장치(약 100판)보다 적습니다.** D7/D14를 보려면 약 200판이 필요합니다.
   - 근거: [Gamigion](https://www.gamigion.com/?p=18694), [SayGames](https://blog.say.games/posts/how-to-work-with-difficulty-in-hybrid-puzzles-so-players-dont-leave--but-stay-and-pay)

## ★ 오행 정리: 설계·구현 시사점

1. **풀 수 있는지 판정하는 문제는 NP-완전입니다.** Ball sort와 water sort는 NP-완전이고 서로 동치입니다. 공식으로 판정할 수 없으니 **노드 예산을 둔 탐색 솔버**로 검증하세요.
   - 검증에는 탐욕 탐색으로 충분합니다. 거의 즉시 끝나고, 최적해보다 보통 1수 정도만 깁니다.
   - 별점 기준을 정할 때만 최적해 탐색을 씁니다.
   - 근거: [Ito 외 FUN 2022](https://arxiv.org/abs/2202.09495), [kuking](https://github.com/kuking/WaterSortPuzzleSolver)
2. **합법적인 역방향 수로만 생성합니다.** 정방향으로 합법인 수에 대응하는 "되돌리기"만 적용하세요. 상극 잠금은 합쳐진 물처럼 되돌릴 수 없으므로, **역 스크램블을 마친 뒤에 잠금을 추가하고 다시 검증**합니다.
3. **빈 칸(빈 병) 수를 주 난이도 손잡이로 씁니다.** 논문이 필요한 빈 병 수의 경계를 제시합니다. 보조 지표로 해 길이와 막다른 상태 비율을 씁니다.
4. **상극 잠금은 Hole People의 "막힘 색"과 같은 역할입니다.** 고전 정렬 위에 깊이를 더하는 장치예요.
   - 정렬 퍼즐은 하이브리드 캐주얼 퍼즐 중 **가장 빠르게 성장한 하위 장르**입니다 (2025년 1분기 전년 대비 5.6배).
5. **수익화 우선순위:** 병 추가 부스터 → 실패 오퍼 → 광고 제거 → 배틀패스(IAP의 5~7%)
6. **Godot 시작점:** [Matswm86/water-sort](https://github.com/Matswm86/water-sort) (MIT, Godot 4.6). 레벨 번호별 시드로 생성하고, 보여주기 전에 솔버로 검증하는 패턴입니다.

---

## 1. 화살표·정박지 퍼즐 구현체

| 링크 | 라이선스 · 언어 | 상태 | 쓸모 |
|---|---|---|---|
| [sergev/goarrows](https://github.com/sergev/goarrows) | **MIT** · Go | 2026-05 | "Arrows – Puzzle Escape" 클론. **수용 기준 두 가지를 그대로 가져올 수 있습니다**: (a) 시작 시 바로 빠질 수 있는 화살표가 절반을 넘으면 너무 쉬우니 거부, (b) 첫 번째로 가능한 화살표를 반복 발사해서 판이 비면 승인 |
| [defnull Snek!](https://defnull.de/snek/) | 글 + JS, **라이선스 없음** | — | **가장 좋은 설계 글.** 제거 순서대로 판을 구성해 풀 수 있음을 보장하고, 나중에 경로가 막힐 수 있는 후보는 버립니다. 난이도는 의존 트리의 크기, 깊이, 폭으로 측정 |
| [Rhythm Themes Arrow Escape 개발기](https://rhythm-themes.onrender.com/blog/arrow-escape-puzzle-game) | 블로그 (비공개 앱) | 2026-07 | 역 제거 순서 배치 + **빌드마다 전 레벨 솔버 단위 테스트** |
| [fogleman/rush](https://github.com/fogleman/rush) + [해설](https://michaelfogleman.com/rush/) | **MIT** · Go/C++/JS | ~339★ | Rush Hour 전수 열거(약 258만 퍼즐). 담금질 생성이 불만족스러워 전수 열거로 전환. 난이도 = 최적해 길이. 모든 조각이 필요한지 보는 "최소성" 검사 |
| [robmat/arrows_game](https://github.com/robmat/arrows_game) | **GPL-3.0** · Kotlin | 활발 | GameGenerator와 SolvabilityChecker가 있음. 보상형 광고로 목숨 회복, 30회 시청 시 광고 제거. **참고만 가능** |
| [sidhant947/ArrowEscape](https://github.com/sidhant947/ArrowEscape) | **GPL-3.0** · Flutter | 활발 | 무한 절차 생성 (알고리즘 설명 없음) |
| [PanAkatsuki/…LevelGenerator](https://github.com/PanAkatsuki/ArrowsPuzzleEscape-LevelGenerator) | README에는 MIT라고 되어 있지만 LICENSE 파일 없음 · Unity | 2025-10 | 생성 파라미터(판 크기, 화살표 길이, 꺾임 확률) 참고 |
| [dinghaoluo/arrows-puzzle-web](https://github.com/dinghaoluo/arrows-puzzle-web) | 라이선스 없음 · JS | 2026-06 | 웹 MVP의 터치, 줌 UX 참고 |
| [sdurlanik/BusJam](https://github.com/sdurlanik/BusJam) | **MIT** · Unity | 2025-07 | Bus Jam 정박지 구조 (채용 과제용 클론, 솔버 없음) |
| [cemtas81/ParkingJam](https://github.com/cemtas81/ParkingJam) | **MIT** · Unity | 2025-10 | Parking Jam 구현 |
| [increpare/PuzzleScript](https://github.com/increpare/PuzzleScript) | **MIT** · JS | 활발 | 바람 카드나 정박지 변형 규칙을 GDScript로 옮기기 전에 빠르게 프로토타입 |

> 라이선스가 쓸 만한 **Godot용 화살표 탈출이나 Bus Jam 구현체는 없습니다.** 직접 구현해야 합니다.

## 2. 정렬 퍼즐 솔버·생성기

| 링크 | 라이선스 · 언어 | 쓸모 |
|---|---|---|
| [Ito 외, Sorting Balls and Water](https://arxiv.org/abs/2202.09495) (FUN 2022) | 논문 | NP-완전성, ball과 water의 동치, 필요한 빈 병 수의 경계 |
| [kuking/WaterSortPuzzleSolver](https://github.com/kuking/WaterSortPuzzleSolver) | **MIT** · Go | 전수 탐색(상태당 약 56바이트). 탐욕 탐색이 거의 최적 |
| [pkositsyn/water-sort-puzzle-solver](https://github.com/pkositsyn/water-sort-puzzle-solver) | **MIT** · Go | 대안 솔버 |
| [octo/watersort](https://github.com/octo/watersort) | **ISC** · Go | JSON 레벨 포맷 + 솔버 |
| [hamidh100/Water-Sort-Solver-Editor](https://github.com/hamidh100/Water-Sort-Solver-Editor) | **MIT** · Python | **숨은 색** 지원. "안개" 메커닉 후보 |
| [Matswm86/water-sort](https://github.com/Matswm86/water-sort) | **MIT** · Godot 4.6 | 시드 생성 + 솔버 게이트 |
| [1shevelov/test-tubes](https://github.com/1shevelov/test-tubes) | **MIT** · Godot 3 | UI와 JSON 임포터 아이디어 |
| [hkociemba/WaterBallSortPuzzleOptimalSolver](https://github.com/hkociemba/WaterBallSortPuzzleOptimalSolver) | 라이선스 없음 | 최적 솔버(14색×6). 읽기만 가능 |
| [cemasma/…](https://github.com/cemasma/water-sort-puzzle-solver), [SigridJ/berzelius-game](https://github.com/SigridJ/berzelius-game) | GPL-3.0 | 참고만 가능 |

## 3. 레벨 생성·난이도 연구

| 자료 | 핵심 |
|---|---|
| [Taylor & Parberry, Sokoban 절차 생성](https://ianparberry.com/techreports/LARC-2011-01.pdf) (2011) | 역방향 구성, 목표에서 **가장 먼 상태**를 선택. 난이도는 **box lines**(같은 상자를 같은 방향으로 연속해서 민 것은 1회로 셈)로 측정. 형제 해에 패널티 |
| [Sturtevant, Fling! 대규모 BFS](https://www.gamedeveloper.com/design/the-saturday-paper---exhausting) | 조각 하나 적은 풀리는 판을 확장해서 DB 구축. **탐색 트리 상태 수가 디자이너가 의도한 난이도와 맞음.** 모든 레벨의 정답 첫 수가 하나 |
| [Sturtevant 외, AIIDE 2020](https://ojs.aaai.org/index.php/AIIDE/article/view/7421) | 타일 하나 변경 + BFS로 최적해 길이를 재측정. 작은 수정이 해를 크게 늘림 |
| [Kartal 외, MCTS Sokoban 생성](https://ojs.aaai.org/index.php/AIIDE/article/view/12859) (AIIDE 2016) | 시뮬레이션 플레이로 생성해서 풀 수 있음이 보장됨. 사용자 연구 기반 난이도 함수 |
| [van Kreveld 외, 자동 난이도 추정](https://ics-websites.science.uu.nl/docs/vakken/mscip/assignments/CIG2015-AutomatedPuzzleDifficultyEstimation.pdf) (CIG 2015) | 레벨 특징의 가중합을 플레이어 평가에 맞춤. 오차 약 1점/10점 |
| [Jarušek & Pelánek](https://www.fi.muni.cz/~xpelanek/publications/stairs2010-final.pdf) (2010) | 상태 공간 크기나 해 길이만으로는 체감 난이도를 설명할 수 없음. **병목 구조**가 중요 |
| [SayGames: 하이브리드 퍼즐 난이도](https://blog.say.games/posts/how-to-work-with-difficulty-in-hybrid-puzzles-so-players-dont-leave--but-stay-and-pay) (2026-07) | 실패율 50%면 평균 2회, 80%면 5회 시도지만 꼬리는 10~50회. 첫 공개 약 100판, D7/D14 판독에는 약 200판. 새 레벨 묶음은 일부 유저에게 먼저 배포. **아슬아슬한 승리** 설계 |

**Godot 적용 방법:** 생성기와 솔버는 오프라인에서 돌립니다 (Godot 헤드리스 `--script`, 또는 위 MIT Go 솔버 재사용). 레벨은 JSON이나 Resource로 배포하고, CI에는 GDScript 검증기를 둡니다 ([`../platforms/godot/tests/`](../platforms/godot/tests/)와 같은 방식).

## 4. 하이브리드 캐주얼 시장 데이터 (2025~2026)

| 출처 | 시점 | 핵심 수치 |
|---|---|---|
| [AppMagic 하이브리드 캐주얼 Q1 2025](https://gameindustrylibrary.com/documents/hybdrid-casual-games-in-q1-2025/read) | 2025 Q1 | 상위 10개 순 IAP $87M (+67% YoY). 퍼즐 48%. **정렬 퍼즐 5.6배 성장.** Color Block Jam 분기 $25M |
| [AppMagic Q2'25 (GameDev Reports)](https://gamedevreports.substack.com/p/appmagic-top-10-hybrid-casual-games) | 2025-09 | **실패 오퍼가 핵심 수익원.** Hole People은 광고 제거 + 실패 오퍼가 약 30%. 배틀패스 5~7%. 저금통 $1.99~14.99. 2025년 1~7월 "hole" 클론 215개 출시 |
| [Deconstructor of Fun: Screw Puzzle Gold Rush](https://www.deconstructoroffun.com/blog/the-screw-puzzle-gold-rush) | ~2026-02 | 제약마다 부스터 하나. 막히는 지점에 엔드게임 오퍼. **정박지 칸은 첫 실수를 완화하되 여유는 짧게.** Screwdom IAP $75M 이상(2025) |
| [Gamigion: Color Block Jam](https://www.gamigion.com/?p=18694) | 2025(추정) | 레벨은 결정적. 사전 부스터 2종 + 5단계 연승 보너스 |
| [Liftoff × Singular 2025](https://gamedevreports.substack.com/p/liftoff-and-singular-casual-games) | 2025 | 캐주얼 CTR 9.4%(Android). 퍼즐 유입은 하이퍼캐주얼에서 29%, 다른 퍼즐에서 25% |
| [GameAnalytics 2026 벤치마크](https://gamedevreports.substack.com/p/gameanalytics-mobile-and-pc-game) | 2026-06 | 모바일 D1 상위 25%는 30% 초과, 상위 10%는 40%. D7 중앙값 4% 미만, 상위 10%는 11~12%. D30 중앙값 약 0.7~0.8% (퍼즐 장르별 수치는 없음) |

> 미검증: Sensor Tower의 "하이브리드 캐주얼 IAP +20%, $4.2B"(2차 인용), 출처가 불분명한 퍼즐 리텐션 표. Bus Jam과 Parking Jam의 1차 포스트모템은 없습니다.
