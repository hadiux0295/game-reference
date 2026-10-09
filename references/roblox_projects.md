# 우리 Roblox 프로젝트별 참고 자료

> 대상: [`our_games`](../our_games/README.md) §3의 Roblox 프로젝트. 조사일은 **2026-10-09**입니다.
> 이상현상 점집은 [`anomaly_shop_roblox.md`](anomaly_shop_roblox.md)에 따로 정리했습니다.

## Gloamrun: 90초 탈출 (미로 생성, 출구 경로 비율 55~72%)

| 자료 | 종류 | 적용 |
|---|---|---|
| [Mazes for Programmers](https://pragprog.com/titles/jbmaze/mazes-for-programmers/) (Jamis Buck) | 책 | 알고리즘 10여 종, **Dijkstra 거리 지도**로 미로를 분석하고 풀기, "어려운 미로 만들기", **브레이딩**(막다른 길 제거) |
| [Maze generation algorithm recap](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap) | 블로그 | 알고리즘별 성격이 다릅니다. Recursive backtracker는 막다른 길이 적고 길고 구불구불합니다. Prim과 Kruskal은 짧은 막다른 길이 많습니다. Binary tree는 대각선 편향이 있습니다. **추격전의 느낌에 맞춰 고르세요** |
| [Rooms and Mazes](https://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/) (Bob Nystrom) | 블로그 | 방 배치 → 미로 채우기 → 신장 트리 연결 → **소량의 추가 연결로 루프 생성** → 막다른 길 정리. 루프 비율이 경로 길이를 조정하는 손잡이입니다 |
| [Red Blob: A* 입문](https://www.redblobgames.com/pathfinding/a-star/introduction.html) | 인터랙티브 | BFS, Dijkstra, 거리장. 출구 거리 측정과 추격자 플로우필드 |
| [simplepath](https://github.com/ahmicy/simplepath) | MIT | 추격자 길찾기 |

**적용 레시피:**
1. 미로를 생성합니다.
2. BFS로 출구 최단거리를 측정합니다.
3. 경로 비율이 55~72% 범위를 벗어나면 버리고 다시 생성하거나 브레이딩합니다.

이 기준은 서버에서 시드와 함께 기록해 두면 문제가 된 미로를 재현할 수 있습니다.

## Devour: .io 계열 삼키기 (커질수록 카메라가 물러남)

| 자료 | 라이선스 | 적용 |
|---|---|---|
| [Luka967/OgarII](https://github.com/Luka967/OgarII) (Agar.io 오픈소스 서버) | Apache-2.0 | 실제 공식이 들어 있습니다 (아래 표) |

| 항목 | 공식 |
|---|---|
| 속도 | `88 × size^-0.4396754 × moveMult` |
| 질량 | `size² / 100` |
| 줌 | `s = min(64/size, 1)^0.4`, 시야 폭 `1920 / s / 2` |

→ "커질수록 느려지고 넓게 본다"는 곡선을 그대로 가져와 수치만 조정하면 됩니다.

- 판정(누가 누구를 먹는가)은 **서버에서** 크기를 비교해서 합니다. 클라이언트가 보낸 크기를 믿지 마세요.

## Ruinstack: 발파 설계, 잔해를 구역에 떨어뜨리기 (물리)

| 자료 | 적용 |
|---|---|
| [Network ownership](https://create.roblox.com/docs/physics/network-ownership) | 점수 판정에 쓰이는 잔해는 `SetNetworkOwner(nil)`로 **서버가 소유**하게 하세요. 클라이언트가 소유한 물리는 검증할 수 없고 Touched도 위조될 수 있습니다 |
| [Assemblies](https://create.roblox.com/docs/physics/assemblies) | 용접된 파트는 하나의 강체입니다. 루트 파트만 Anchor하고, 속도를 직접 넣기보다 VectorForce나 LinearVelocity를 쓰세요 |
| [Explosion](https://create.roblox.com/docs/reference/engine/classes/Explosion) | `DestroyJointRadiusPercent = 0`으로 두고, `Hit`에서 직접 조인트를 끊어 제어합니다. `ExplosionType.NoCraters` |
| [Model:BreakJoints](https://create.roblox.com/docs/reference/engine/classes/Model#BreakJoints) | **Deprecated.** 대신 해당 `WeldConstraint`를 Destroy하거나 Enabled를 끄세요 (대체 방식은 미검증) |

- 점수는 잔해가 **멈춘 뒤**(속도 임계값 이하가 N초 유지) 서버에서 구역별 질량이나 개수로 계산합니다.

## Brinkfall: 체크포인트 없는 탑 오르기

| 자료 | 적용 |
|---|---|
| [Bennett Foddy 인터뷰 (Getting Over It)](https://design.google/library/bennett-foddy-getting-over-it-interview) | 좌절을 의도된 표현 재료로 씁니다. "소프트웨어식 친절함"에 대한 반발 |
| [Jump King (Wikipedia)](https://en.wikipedia.org/wiki/Jump_King) | 체크포인트가 없고, 한 번 떨어지면 크게 손실되는 구조 |

- 설계 포인트:
  - 떨어진 *거리*나 *최고 높이*를 기록하고 보여주세요. 손실도 하나의 이야깃거리가 됩니다.
  - 다른 플레이어가 떨어지는 모습이 보이게 하세요. 사회적 구경거리가 됩니다.
- Tower of Hell 등 Roblox 탑 오비 개발자의 1차 인터뷰는 찾지 못했습니다.

## 공통 도구
카메라 흔들림 [RbxCameraShaker](https://github.com/Sleitnick/RbxCameraShaker) (MIT), 영역 감지 [ZonePlus](https://github.com/1ForeverHD/ZonePlus) (MIT). 그 밖의 라이브러리는 [`../platforms/roblox/libraries.md`](../platforms/roblox/libraries.md)를 참고하세요.
