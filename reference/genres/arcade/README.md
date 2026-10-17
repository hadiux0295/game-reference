# 아케이드 · Roblox 포맷 (Arcade / Roblox Formats)

> 하위 장르: Obby(장애물 코스) · 러너 · 타이쿤 · .io 삼키기 · 라운드제(미니게임·서바이벌·술래잡기·파티) · 미로 탈출 · 물리 파괴 · 무체크포인트 등반
> 적합 플랫폼: 🟥 Roblox(주) · 📱 러너
> 마지막 확인일: 2026-10-09 (자료) · 2026-10-17 (구조). 숫자는 출처가 있는 것만. 확인하지 못한 것은 `미검증`.

## 1. 한 줄 정의
규칙이 한 문장이고 한 판이 짧으며(30초~3분), 반복 자체가 재미인 포맷들. Roblox에서는 "포맷"이 곧 장르다.

## 2. 대표작 (인기 게임)
| 게임 | 플랫폼 | 하위 장르 | 핵심 루프 한 줄 | 왜 팔리나 (훅·BM) | 규모 근거 (출처·확인일) |
|---|---|---|---|---|---|
| Tower of Hell | 🟥 | 무체크포인트 Obby | 랜덤 탑 → 체크포인트 없이 오르기 → 시간 제한 | 떨어지는 구경거리, 스킵·속도 패스 | 1차 인터뷰 없음 `미검증` |
| Agar.io (원조) | 💻 웹 | .io 삼키기 | 먹고 커지기 → 느려지고 시야 확대 | 규칙 한 줄, 즉시 입장 | 공식 공식은 [OgarII](https://github.com/Luka967/OgarII) (Apache-2.0) |
| Getting Over It · Jump King | 💻 | 무체크포인트 등반 | 떨어지면 크게 손실 | 좌절을 표현 재료로 | [Foddy 인터뷰](https://design.google/library/bennett-foddy-getting-over-it-interview) · [Jump King](https://en.wikipedia.org/wiki/Jump_King) |
| (Roblox 타이쿤 · 라운드제 · 러너 대표작) | 🟥 📱 | | | | `비어 있음` — 다음 채움 때 Roblox 차트에서 읽는다 |

## 3. 핵심 루프·시스템
한 장 요약은 [`../../systems/genres.md`](../../systems/genres.md). 포맷별 자료는 [`roblox_formats.md`](roblox_formats.md).
- **Obby.** 점프 → 체크포인트 → 다음 스테이지. 체크포인트 순서를 **서버에서 검증**(`stage == current + 1`) 하지 않으면 스킵 치트가 가능. 수익: 스테이지 스킵(소모성), 속도·점프 패스.
- **타이쿤.** 드로퍼 생산 → 수집 → 버튼 구매 → 확장. 버튼·가격·선행 조건은 Config 테이블, 저장은 **구매한 버튼 ID 목록만**, 접속 시 플롯 재구성.
- **라운드제.** 로비 → 인터미션 → 라운드 → 결과. 상태 머신, 맵 로테이션, 팀 배정, 관전. 남은 인원 1명 이하면 즉시 종료. 구현: [`RoundService.luau`](../../platforms/roblox/patterns/RoundService.luau).
- **러너.** 청크 기반 맵(난이도별 조각 이어 붙이기), 오브젝트 풀링, 상한 있는 속도 곡선. 히트박스는 보이는 것보다 **살짝 작게**.
- **.io 삼키기.** 속도 `88 × size^-0.4396754`, 질량 `size²/100`, 줌 `min(64/size,1)^0.4` (OgarII). 누가 누구를 먹는지는 **서버가 크기 비교**.
- **미로 탈출.** 생성 → BFS로 출구 최단거리 → 경로 비율(예: 55~72%) 벗어나면 재생성 또는 브레이딩. 시드를 서버에 기록해 재현.
- **물리 파괴.** 점수에 쓰이는 잔해는 `SetNetworkOwner(nil)`로 서버 소유. 멈춘 뒤(속도 임계 N초) 서버에서 구역별 계산.
- **무체크포인트 등반.** 떨어진 거리·최고 높이를 기록해 보여주고, 다른 플레이어가 떨어지는 모습이 보이게.

## 4. 수치 (data)
| 게임 | 항목 | 값 | source | URL | 확인일 |
|---|---|---|---|---|---|
| Agar.io(OgarII) | 속도 공식 | `88 × size^-0.4396754 × moveMult` | extracted(오픈소스) | [OgarII](https://github.com/Luka967/OgarII) | 2026-10-09 |
| Agar.io(OgarII) | 줌 공식 | `s = min(64/size, 1)^0.4`, 시야 폭 `1920/s/2` | extracted | 같은 저장소 | 2026-10-09 |
| (Roblox Obby·타이쿤 가격·세션 수치) | | | | | `비어 있음` |

## 5. 원전·오픈소스 (라이선스 포함)
| 자료 | 종류 | 라이선스 | 다루는 것 | 확인일 |
|---|---|---|---|---|
| [Mazes for Programmers](https://pragprog.com/titles/jbmaze/mazes-for-programmers/) (Jamis Buck) | 책 | 상용 | 알고리즘 10여 종, Dijkstra 거리 지도, 브레이딩 | 2026-10-09 |
| [Maze generation algorithm recap](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap) | 블로그 | 글 | 알고리즘별 성격(막다른 길·편향) | 2026-10-09 |
| [Rooms and Mazes](https://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/) (Nystrom) | 블로그 | 글 | 방 → 미로 → 신장 트리 → 루프 추가 | 2026-10-09 |
| [Luka967/OgarII](https://github.com/Luka967/OgarII) | GitHub | Apache-2.0 | Agar.io 서버 공식 | 2026-10-09 |
| [ahmicy/simplepath](https://github.com/ahmicy/simplepath) | GitHub | MIT | Roblox 추격자 길찾기 | 2026-10-09 |
| [Sleitnick/RbxCameraShaker](https://github.com/Sleitnick/RbxCameraShaker) · [1ForeverHD/ZonePlus](https://github.com/1ForeverHD/ZonePlus) | GitHub | MIT | 카메라 흔들림 · 영역 감지 | 2026-10-09 |
| Roblox 공식: [Network ownership](https://create.roblox.com/docs/physics/network-ownership) · [Assemblies](https://create.roblox.com/docs/physics/assemblies) · [Explosion](https://create.roblox.com/docs/reference/engine/classes/Explosion) | 문서 | 문서 | 물리 소유권·강체·폭발 제어 | 2026-10-09 |

## 6. 함정 (흔한 실패)
- **체크포인트·점수를 클라이언트가 보고한다.** Obby 스킵, 타이쿤 재화 위조. 전부 서버 검증.
- **러너 히트박스가 보이는 것보다 크다.** 불공정하게 느껴져 이탈.
- **라운드 중 인원 1명 이하를 처리 안 함.** 빈 라운드가 끝까지 돈다.
- **물리 잔해를 클라이언트가 소유.** Touched 위조, 점수 검증 불가.
- **미로가 너무 쉽거나 어렵다.** 경로 비율을 재지 않고 생성만 한다.
- **`Model:BreakJoints` 같은 Deprecated API 사용.** 대체 방식까지 확인(현재 `미검증`).

## 7. 우리 게임 적용
[`our_games/README.md`](../../../our_games/README.md) §3 엔진 프로젝트.
- **Gloamrun**(90초 탈출) → 미로 생성 + 경로 비율 55~72% 레시피.
- **Devour**(.io 삼키기) → OgarII 공식 그대로, 수치만 조정. 판정은 서버.
- **Ruinstack**(발파) → 서버 소유 잔해, 멈춘 뒤 채점.
- **Brinkfall**(무체크포인트 등반) → 손실을 이야깃거리로, 추락 구경거리.
- **Roblox 타이쿤**(큐브 도감) → 구매 버튼 ID 목록 저장 패턴.

## 채움 상태
| 절 | 상태 | 마지막 갱신 |
|---|---|---|
| 2 대표작 | ◐ Roblox 차트 대표작 비어 있음 | 2026-10-17 |
| 3 루프 | ● | 2026-10-17 |
| 4 수치 | ◐ | 2026-10-17 |
| 5 원전 | ● | 2026-10-17 |
| 6 함정 | ● | 2026-10-17 |
| 7 우리 적용 | ● | 2026-10-17 |
