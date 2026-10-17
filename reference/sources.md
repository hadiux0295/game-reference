# 원전·학습 자료 (엔진 무관)

게임 로직을 공부할 때 기준이 되는 자료입니다. 검증일은 **2026-10-09**입니다.
플랫폼별 라이브러리는 [`platforms/godot/libraries.md`](platforms/godot/libraries.md)와 [`platforms/roblox/libraries.md`](platforms/roblox/libraries.md)를 보세요.

## 1. 패턴·구조

| 자료 | 라이선스 | 다루는 내용 |
|---|---|---|
| [Game Programming Patterns](https://gameprogrammingpatterns.com/) ([GitHub](https://github.com/munificent/game-programming-patterns)) | 코드 MIT, 본문 CC BY-NC-ND | Command, State, Observer, Game Loop, Update Method, Component, Event Queue, Object Pool, Dirty Flag. **필독** |
| [Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/) (Glenn Fiedler) | 아티클 | 고정 타임스텝과 보간 |
| [Fast-Paced Multiplayer](https://www.gabrielgambetta.com/client-server-game-architecture.html) (Gabriel Gambetta) | 아티클 | 서버 권위, 클라이언트 예측, 보정, 보간, 랙 보상 |
| [SanderMertens/ecs-faq](https://github.com/SanderMertens/ecs-faq) | 명시 없음 | ECS 개념과 데이터 지향 설계 |
| [SanderMertens/flecs](https://github.com/SanderMertens/flecs) | MIT | 프로덕션 ECS 구현 (C/C++) |

## 2. AI·길찾기·절차적 생성

| 자료 | 라이선스 | 다루는 내용 |
|---|---|---|
| [Red Blob Games](https://www.redblobgames.com/) | 사이트 | [A* 입문](https://www.redblobgames.com/pathfinding/a-star/introduction.html), [헥스 그리드](https://www.redblobgames.com/grids/hexagons/), [타워디펜스 플로우필드](https://www.redblobgames.com/pathfinding/tower-defense/). 인터랙티브 설명 |
| [Amit's A* Pages](https://theory.stanford.edu/~amitp/GameProgramming/) | 사이트 | A*와 휴리스틱 심화 |
| [Game AI Pro](https://www.gameaipro.com/) 1~3권 + 온라인판 | **무료 PDF** | 행동트리 스타터킷, 유틸리티 AI, HTN, JPS+ |
| [Three States and a Plan: F.E.A.R.의 AI](https://pages.cs.wisc.edu/~dyer/cs540/handouts/gdc2006_orkin_jeff_fear.pdf) (Orkin, GDC 2006) | 논문 | GOAP 원전 |
| [libgdx/gdx-ai](https://github.com/libgdx/gdx-ai) | Apache-2.0 | 조향, 계층형 길찾기, 행동트리, FSM의 읽기 쉬운 구현 (Java) |
| [mxgmn/WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse) | MIT | 예시 기반 타일·맵 절차적 생성 |
| [redblobgames/mapgen4](https://github.com/redblobgames/mapgen4) | 미확인 | 절차적 지형 생성 |

## 3. 경제·밸런스·방치형 수학

| 자료 | 형태 | 다루는 내용 |
|---|---|---|
| [The Math of Idle Games, Part I](https://www.gamedeveloper.com/design/the-math-of-idle-games-part-i) / [Part II](https://www.gamedeveloper.com/disciplines/the-math-of-idle-games-part-ii) (Anthony Pecorella, Kongregate) | 아티클 | 성장·비용 곡선, 생산자 밸런스, 프레스티지 |
| [Idle Games: The Mechanics and Monetization of Self-Playing Games](https://gdcvault.com/play/1022065/Idle-Games-The-Mechanics-and) (GDC 2015) | 강연 | 방치형 설계와 수익화 |
| [Machinations.io](https://machinations.io/) | 상용 (무료 시작 가능) | 경제 루프 시뮬레이션 |

## 4. 오픈소스 게임 목록

| 목록 | 라이선스 | 상태 |
|---|---|---|
| [bobeff/open-source-games](https://github.com/bobeff/open-source-games) | CC0 | ✅ 추천 |
| [ellisonleao/magictools](https://github.com/ellisonleao/magictools) | MIT | ✅ 게임 개발 도구와 자료 |
| [Calinou/awesome-gamedev](https://github.com/Calinou/awesome-gamedev) | CC-BY-SA-4.0 | ✅ 자유 소프트웨어 중심 |
| [godotengine/awesome-godot](https://github.com/godotengine/awesome-godot) | CC-BY-4.0 | ✅ Godot 전용 |
| [leereilly/games](https://github.com/leereilly/games) | CC BY-NC-SA | 🗄️ 2025-09 아카이브 (bobeff 목록 권장) |

## 5. 고전 소스 (구조 참고 전용, GPL)
- [id-Software/DOOM](https://github.com/id-Software/DOOM), [id-Software/Quake](https://github.com/id-Software/Quake): 게임 루프와 엔진 구조의 교과서
- [OpenTTD/OpenTTD](https://github.com/OpenTTD/OpenTTD): 대규모 경제 시뮬레이션
- 0 A.D.: GitHub 저장소는 아카이브되었고 현재는 gitea.wildfiregames.com에 있음. RTS
