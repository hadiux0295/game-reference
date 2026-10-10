# 이상현상 점집: 야간 근무 (Roblox): 참고 자료와 설계 시사점

> 대상: [`our_games`](../our_games/README.md)의 **R-A 이상현상 점집: 야간 근무** (Roblox, 호러 교대 근무, 1~4인, 10-09 선택)
> 훅: *손님 중 하나는 사람이 아니다. 복채를 받기 전에 걸러내라.*
> 작업 현황 · 점 보기 기획서 · 조사 요청: [`our_games/anomaly_shop/`](../our_games/anomaly_shop/README.md) (2026-10-10)
> 조사일: **2026-10-09**. 링크는 직접 열어 확인했고, 확인하지 못한 항목은 **미검증**으로 표시했습니다.

---

## ★ 설계 시사점 12가지 (요약)

| # | 시사점 | 근거 |
|---|---|---|
| 1 | **손님 1명당 판정 동사는 하나.** "복채 받기"와 "돌려보내기"만 둡니다. 실수로 누르지 않도록 ProximityPrompt `HoldDuration`을 약 1초로 합니다 | Exit 8 개발자가 사진 찍기, 쏘기를 빼고 "진행/되돌아가기" 둘만 남김 · ProximityPrompt 문서 |
| 2 | **상담석은 단순하게, 손님은 고정 구도로.** 살펴볼 대상은 얼굴, 손, 생년월일 쪽지, 향, 거울 정도로 제한합니다 | Platform 8 기차 프로토타입은 객차가 너무 복잡해서 이상현상을 찾기 어려워 실패 |
| 3 | **사주를 Papers, Please식 서류 대조로 만듭니다.** 손님이 말한 생년월일시와 가게 만세력이 보여주는 실제 사주를 대조합니다. 이상현상은 *사람*(그림자, 거울 반사, 손가락 수)이나 *데이터*(띠·일주 불일치, 미래 출생연도, 절기 경계 시각)에 둡니다 | Papers, Please 인터뷰 · manseryeok |
| 4 | **밤마다 규칙을 1~2개 추가하되 조용히 전달합니다.** "주인의 공지" 형식으로 줍니다. 손님이 말하는 순간에는 새 규칙을 주지 마세요. 밤마다 수작업 손님 2~3명을 두고, 나머지는 그 밤의 규칙으로 생성합니다 | Lucas Pope: 캐릭터가 말하는 순간 나온 새 규칙은 플레이테스터가 무시함. 하루에 스크립트 입국자 2~3명 + 나머지 생성 |
| 5 | **오판 패널티는 단계적으로.** 사람을 돌려보내면 그 손님의 복채를 잃습니다. 밤마다 실수 2회까지는 면제하고 이후 벌점이 커지며, 밤이 바뀌면 리셋합니다. 이상현상을 들여보내면 즉사가 아니라 **위협 게이지**가 오르고, 누적되면 게임 오버입니다 | Papers, Please 벌점 체계 · I'm on Observation Duty |
| 6 | **대부분은 섬뜩하게, 치명적인 경우는 드물게.** 즉사형 이상현상은 드물게 두고 반드시 예고를 줍니다 | Exit 8은 "경계선 호러"로 사망 없음 · Platform 8은 게임 오버 비중을 올렸다가 Steam 평가 하락 |
| 7 | **이해하기 어려운 이상현상에는 게임 속 힌트를 줍니다.** 부적 쪽지, 라디오, 주인의 장부로 "평소와 다른 행동"을 암시합니다 | Platform 8이 "내리지 마세요", "보지 마세요" 안내판을 추가 |
| 8 | **이상현상은 중복 없이 뽑고, 이상현상별 발견률을 기록합니다.** 너무 어렵거나 쉬운 것을 재조정하세요 | Exit 8은 전부 나오기 전까지 반복 없음 · "이상현상 없음 버그" 제보가 실은 너무 미묘한 이상현상이었음 · 894 투표 |
| 9 | **교대 구조.** 한 밤은 8~12분(자정에서 새벽까지)으로 하고 밤마다 공격성이 올라갑니다. 5밤 + 보너스 밤 + 커스텀 밤(손님 직접 설계) 구성 | FNAF 구조 · That's not my Neighbor의 Custom 모드 |
| 10 | **Mild 등급을 목표로 합니다.** 점프스케어는 허용되고 사실적인 피는 쓰지 않습니다. 그래야 Roblox Kids·Select 계정 노출이 가능합니다. 16세 미만 노출 요건도 미리 준비하세요 (아래 §3) | Content Maturity 문서 · Kids & Select 문서 |
| 11 | **복채는 게임 내 재화로만 처리합니다.** 랜덤 운세나 부적을 Robux로 팔지 않습니다(도박 금지, 확률 공개 의무). 실존 종교나 무속인을 조롱하지 말고 허구로 설정합니다 | Community Standards |
| 12 | **협동 배관.** 파티는 `GetPlayersByPartyId` → `TeleportAsync` + `ShouldReserveServer=true`로 보내고, 공개 매칭은 MemoryStore 큐를 씁니다. TeleportData는 클라이언트가 볼 수 있으니 민감한 값을 넣지 마세요. 속삭임과 노크는 `AudioEmitter` 3D 사운드로, 밤 분위기는 Atmosphere `Haze`·`Density`와 Lighting `ClockTime`으로 만듭니다 | Teleport, MemoryStore, Audio, Atmosphere, Lighting 문서 |

---

## 1. 이상현상·검문 게임 설계 원전

| 링크 | 종류 | 핵심 내용 |
|---|---|---|
| [AUTOMATON: Exit 8의 기원](https://automaton-media.com/en/news/20240214-27192/) (2024-02-14) | 개발자 인터뷰 요약 | 이상현상 개념은 *I'm on Observation Duty*, 루프는 *Twelve Minutes*에서 왔습니다. 사진 찍기, 쏘기 프로토타입은 톤에 맞지 않고 비용이 커서 빼고 "진행/되돌아가기" 이진 판정만 남겼습니다. 사망 없는 "경계선 호러". 기획·프로토 6개월, 제작 3개월이 걸렸고 스톡 에셋을 많이 썼습니다 |
| [AUTOMATON: Kotake Create 인터뷰, Platform 8](https://automaton-media.com/en/interviews/interview-the-exit-8-developer-kotake-create-on-the-perks-of-being-a-solo-dev-and-how-platform-8-came-to-be/) (2024-06-28) | 인터뷰 | 기차판은 앉아서 판정하는 흐름이 끊기고, 복잡한 객차 탓에 이상현상 찾기가 너무 어려워 실패. 너무 어려운 이상현상은 삭제. "치사한" 것에는 안내판 힌트를 추가. 894 이상현상 투표: 쉬움 47.7%, 어려움 30.3%, 답을 찾아봄 22%. 게임 오버형 비중을 바꾼 후속작은 평가가 하락. 플레이테스터는 약 4명 |
| [AUTOMATON: "Exit 8-like" 장르명](https://automaton-media.com/en/news/20231225-24850/) (2023-12-25) | 뉴스 | 같은 배경과 시스템만 아니면 모방작도 괜찮다는 입장. I'm on Observation Duty의 신고 시스템을 1인칭으로 재배치 |
| [Designing the bleak genius of Papers, Please](https://www.gamedeveloper.com/design/designing-the-bleak-genius-of-i-papers-please-i-) (Game Developer, 2013) | 기사 | 스크립트 입국자와 절차적 입국자를 섞음. 생성기 검증용으로 수천 명을 자동 생성. 규칙끼리 얽혀서 하나를 추가하면 다른 것이 깨짐. **캐릭터가 말하는 동시에 나온 새 규칙은 무시됨** |
| [Road to the IGF: Papers, Please](https://www.gamedeveloper.com/design/road-to-the-igf-lucas-pope-s-i-papers-please-i-) (2014) | 인터뷰 | 총 30일, 하루에 스크립트 2~3명 + 그날 규칙으로 생성. 규칙이 쌓여 "적당히 미칠 지경"이 됨. 가장 어려운 일은 **지루한 구간 없이 스크립트 인물을 배치하는 페이싱** |
| [Lucas Pope devlog](https://dukope.com/devlogs/papers-please/) | 1차 개발 로그 | 현지화, 모바일 포팅 기록. Papers, Please 단독 GDC 강연은 찾지 못함(미검증) |
| [Papers, Please 벌점 정리](https://www.ludo.guide/guide/papers-please/citations) | 팬 가이드 | 잘못 승인, 잘못 거부, 사유 도장 없는 거부(18일차부터)가 벌점 대상. 해당 입국자 수수료 상실. 하루 2회 면제 후 5, 5, 10, 15, 20…으로 증가하고 매일 리셋 |
| [Design details in Papers, Please](https://mechanicsofmagic.com/2021/06/05/design-details-in-papers-please/) (2021) | 블로그 | 시간 압박은 원할 때만 의도적으로 사용. 책상 공간과 서류 수가 곧 난이도. 규칙이 쌓일수록 업그레이드(검사 모드, 단축키)가 가치를 가짐 |
| [That's not my Neighbor](https://store.steampowered.com/app/3431040/) (Nachosama, 2025-03) | Steam | 1955년 아파트 경비원. 허가, 거부, D.D.D. 신고의 3택. 캠페인(멀티 엔딩), 아케이드, 나이트메어, **커스텀(세입자 직접 설계)** 모드. 개발자 인터뷰는 찾지 못함 |
| [I'm on Observation Duty 5](https://store.steampowered.com/app/1850550) (Notovia) | Steam | 위치와 종류를 골라 신고. **미신고 이상현상이 너무 많으면 게임 오버** |
| [FNAF 1 (Wikipedia)](https://en.wikipedia.org/wiki/Five_Nights_at_Freddy%27s_(video_game)) | 2차 자료 | 0시~6시를 실제 약 10분으로 압축. 공유 전력 예산(카메라, 문, 조명). 밤마다 적 공격성 증가. 5밤 + 6밤 + 커스텀 7밤 |
| [Adrian Hon: The Exit 8](https://adrianhon.substack.com/p/the-exit-8) (2023-12) | 비평 | 메뉴와 설명이 없음. 대부분 미묘하고 점프스케어는 드묾. 한 번 실수하면 0/8로 리셋 |
| [Year of the 8-like](https://scrmbl.com/post/year-of-the-8-like-japans-indie-game-anomaly) (2025-01) | 장르 개관 | 반복되는 좁은 실사 공간, 무작위 이상현상, 1시간 이내 분량. 2D, VR, 협동, 코미디 변형이 쏟아짐 |

> 이상현상 게임 붐(2023~26)을 다룬 학술 논문은 찾지 못했습니다.

## 2. Roblox 구현 자료

### 공식 문서

| 문서 | 이 게임에서의 용도 |
|---|---|
| [Pathfinding](https://create.roblox.com/docs/characters/pathfinding) | 뒷방 추격자. `Costs`에 `math.huge`를 주면 통행 불가 처리, `Blocked`는 앞쪽이 막혔을 때만 재계산. 3,000 studs 또는 약 20,000 노드를 넘으면 실패 |
| [ProximityPrompt](https://create.roblox.com/docs/reference/engine/classes/ProximityPrompt) · [가이드](https://create.roblox.com/docs/ui/proximity-prompts) | "복채 받기", "돌려보내기". `HoldDuration`, `RequiresLineOfSight`(기본 켜짐), `ProximityPromptService`로 중앙에서 처리 |
| [Atmosphere](https://create.roblox.com/docs/environment/atmosphere) · [Lighting](https://create.roblox.com/docs/environment/lighting) | 안개는 Haze + Color, 낮과 밤 전환은 `ClockTime`, `ExposureCompensation` |
| [Audio objects](https://create.roblox.com/docs/audio/objects) | `AudioPlayer → Wire → AudioEmitter(3D) → AudioListener`. 등 뒤 속삭임 같은 위치 사운드 |
| [Camera](https://create.roblox.com/docs/workspace/camera) | 카메라는 클라이언트에서 제어. `Scriptable`과 `FieldOfView`로 점프스케어 연출 |
| [Teleport](https://create.roblox.com/docs/projects/teleport) | `ShouldReserveServer=true`로 1~4인 전용 서버. pcall로 감싸고 재시도. **TeleportData는 암호화되지 않고 클라이언트가 볼 수 있음**. Studio에서는 테스트 불가 |
| [MemoryStore](https://create.roblox.com/docs/cloud-services/memory-stores) | 공개 매칭 큐(FIFO, TTL) |

### 오픈소스

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [Sleitnick/RbxCameraShaker](https://github.com/Sleitnick/RbxCameraShaker) | MIT | 유지 | 점프스케어, 문 쾅 소리 같은 카메라 흔들림 |
| [simplepath](https://github.com/ahmicy/simplepath) (구 grayzcale/simplepath) | MIT | 유지 | 추격자 길찾기 래퍼 (Gloamrun에도 사용 가능) |
| [1ForeverHD/ZonePlus](https://github.com/1ForeverHD/ZonePlus) | MIT | 유지 | 상담석, 뒷방, 문간 진입 감지 |
| [ReRand/RENTED_old_rbx](https://github.com/ReRand/RENTED_old_rbx) | Apache-2.0 | 미완성 (README 명시) | **가장 비슷한 장르**: 햄버거 가게에 앉아서 버티는 호러. Rojo 기반. 작지만 라이선스가 허용적 |
| [kalebtaylor3/RobloxCoopHorror-NetcodeFramework](https://github.com/kalebtaylor3/RobloxCoopHorror-NetcodeFramework) | **라이선스 없음** | 커밋 3개 | 4인 협동 호러 넷코드. **읽기만 가능** |
| ~~MarkExKiana/ProjectStarFallCodebase~~ | GPL-3.0과 MIT 표기 충돌 | — | 사용하지 마세요 |

> ⚠️ 이상하게 스타가 많고, 라이선스가 없고, 오늘 푸시된 "horror companion", "DOORS archive" 류 저장소는 **SEO나 악성코드 허브로 보이니 피하세요.** 잘 알려진 오픈소스 Roblox 협동 호러 게임이나 Doors식 방 생성기는 없습니다.

## 3. Roblox 정책: 호러 등급과 노출 범위

| 항목 | 내용 | 출처 |
|---|---|---|
| **Mild** | "가벼운 공포": 거친 숨소리, 심장 소리, 비명, 섬뜩한 NPC, **점프스케어** | [Content Maturity](https://create.roblox.com/docs/production/promotion/content-maturity) |
| **Moderate** | "중간 공포": 사실적인 피가 묻은 일그러진 입 등. **비사실적인 피**(픽셀, 비현실 색)는 Mild 이하 | 같은 문서 |
| 도박 | 플레이 가능하거나 시뮬레이션된 도박은 **모든 등급에서 금지** | 같은 문서 · [Community Standards](https://about.roblox.com/community-standards) |
| 민감 이슈 | 종교 등 **현재 양극화된 사회 이슈가 주제**면 16+로 분류되고 노출되지 않음. 사주나 점술은 예시에 없음. 단순히 등장하는 정도는 신고 불필요 | 같은 문서 (사주 해석은 우리 판단, 미검증) |
| 계정 등급 (2026~) | **Roblox Kids(5~8세)**는 Minimal·Mild만, **Select(9~15세)**는 Moderate까지 노출. 16세 미만에게 노출하려면 ID 인증, 2FA, Plus/Premium 2개월(또는 환불형 수수료), 그리고 16+ 연령 인증 유저 **60일 안에 고참여 유니크 플레이 250회** 시범 통과 필요. 50,000 Robux 유료 신속 심사 있음 | [Kids & Select](https://create.roblox.com/docs/production/publishing/kids-and-select) · [뉴스룸 2026-04](https://about.roblox.com/newsroom/2026/04/introducing-roblox-kids-and-select-accounts) |
| 설문 의무 | Maturity & Compliance 설문 마감 **2025-09-30**. 미응답 경험은 비공개 처리. 부정확한 답변은 제재 대상 | [뉴스룸 2025-08](https://about.roblox.com/newsroom/2025/08/extending-roblox-policy-on-romantic-and-sexual-content) |
| 유료 랜덤 아이템 | 확률을 숫자로 공개해야 하고, 지역별로 `ArePaidRandomItemsRestricted` 처리 | Community Standards · Content Maturity |
| IARC 전환 | ESRB, PEGI, GRAC(한국) 등급으로 "올해 안" 전환 예정이라고 발표. 현재 상태는 미검증 | 뉴스룸 2026-04 |

## 4. 사주(만세력) 계산

정확한 사주에는 다음 네 가지가 필요합니다.
- ① **연주**는 입춘 *시각*에 바뀝니다 (음력 설이나 1월 1일 아님)
- ② **월주**는 12절(입춘, 경칩, 청명…)에 바뀝니다
- ③ **시간대 정책**: KST, 과거 서머타임(1948~51, 1954~61, 1987~88), 경도 보정 여부
- ④ **자시(子時) 처리 규칙**

| 라이브러리 | 라이선스 | 상태 | 평가 |
|---|---|---|---|
| [yhj1024/manseryeok](https://github.com/yhj1024/manseryeok) (npm `manseryeok` 2.0) | **MIT** | 유지 | **최적.** 천문연(KASI) 기준. 입춘 *순간*에 연주, 절기 경계에 월주가 바뀜. 1800~2300년 절기표 내장(분 단위 일치), KST, 과거 오프셋과 서머타임, 진태양시 옵션 |
| [urstory/manseryeok-js](https://github.com/urstory/manseryeok-js) (`@fullstackfamily/manseryeok`) | **MIT** | 활발 (v1.0.8, 2026-03) | KASI 기준 1900~2050. v1.0.7부터 월주를 절기 기준으로 계산. 기본으로 경도 보정 적용 |
| [0ssw1/sajupy](https://github.com/0ssw1/sajupy) | **MIT** | 커밋 3개 | Python. **테스트용 정답 비교 도구**로 적합 |
| [6tail/lunar-javascript](https://github.com/6tail/lunar-javascript) | **MIT** | 유지, ~1.7k★ | 중국 팔자. 절기를 중국 시간(UTC+8) 기준으로 계산할 가능성이 있어 경계에서 1시간 오차 위험(미검증) |
| [usingsky/korean_lunar_calendar_py](https://github.com/usingsky/korean_lunar_calendar_py) | MIT | 유지 | ⚠️ **간지를 음력 연월로 계산** (절기가 아님). 사주의 연주와 월주에는 **사용 금지**, 일주만 사용 가능 |
| [lua-calendrica](https://ctan.org/pkg/lua-calendrica) | Apache-2.0 | 신규 (2026-07) | 유일한 Lua 구현. 원저(*Calendrical Calculations*) 코드의 상업 이용 제한 여부를 확인해야 함(미검증) |

**Roblox 적용 방법:** Luau 사주 라이브러리는 없습니다. 오프라인에서 `manseryeok`(MIT, 출처 표기 유지)으로 **필요한 연도 범위의 절기표와 일주표를 생성**하고, Luau ModuleScript 데이터로 넣으세요. 게임 안에서 천문 계산을 하지 않아도 됩니다.

---

## 출처
위 표의 링크가 전부입니다. 미검증 항목은 다음과 같습니다.
- Papers, Please GDC 강연 존재 여부
- Nacho Sama, Notovia, Scott Cawthon의 1차 인터뷰
- IARC 전환 현황
- lua-calendrica 원저 라이선스
- 사주가 Roblox "민감 이슈"에 해당하지 않는다는 판단 (우리 해석)
