# 호러 · 판별 (Horror / Anomaly Detection)

> 하위 장르: 이상현상 판별(8-like) · 검문·서류 대조(Papers, Please 계열) · 교대 근무 호러(FNAF 계열) · Roblox 호러 교대 근무
> 적합 플랫폼: 🟥 Roblox · 📱 프리미엄 앱 · 💻 PC
> 마지막 확인일: 2026-10-09 (원전·정책) · 2026-10-17 (구조). 숫자는 출처가 있는 것만. 확인하지 못한 것은 `미검증`.

## 1. 한 줄 정의
반복되는 좁은 공간에서 "평소와 다른 하나"를 찾아 **진행/되돌아가기** 같은 이진 판정을 내리고, 틀리면 손실·위협이 쌓이는 게임.

## 2. 대표작 (인기 게임)
| 게임 | 플랫폼 | 하위 장르 | 핵심 루프 한 줄 | 왜 팔리나 (훅·BM) | 규모 근거 (출처·확인일) |
|---|---|---|---|---|---|
| The Exit 8 | 💻 PC(Steam) · 콘솔 | 이상현상 판별 | 지하도 반복 → 이상현상 유무 판정 → 8번 연속 정답 | 메뉴·설명 없음, 1시간 분량, 사망 없는 "경계선 호러". 프리미엄 단품 | [AUTOMATON 2024-02](https://automaton-media.com/en/news/20240214-27192/) · 규모 수치 `미검증` |
| Platform 8 | 💻 PC | 이상현상 판별(기차) | 객차 이동 → 판정 | 전작 팬층. 게임 오버 비중을 올렸다가 평가 하락 | [AUTOMATON 2024-06](https://automaton-media.com/en/interviews/interview-the-exit-8-developer-kotake-create-on-the-perks-of-being-a-solo-dev-and-how-platform-8-came-to-be/) |
| Papers, Please | 💻 PC · 📱 | 검문·서류 대조 | 입국자 서류 대조 → 승인/거부 → 벌점·급여 → 가족 생계 | 규칙이 매일 쌓이는 압박, 도덕 선택. 프리미엄 | [Game Developer 2013](https://www.gamedeveloper.com/design/designing-the-bleak-genius-of-i-papers-please-i-) |
| I'm on Observation Duty 1~5 | 💻 PC | 이상현상 신고 | CCTV 감시 → 위치·종류 골라 신고 → 미신고 누적 시 게임 오버 | 8-like의 원조 신고 시스템 | [Steam](https://store.steampowered.com/app/1850550) |
| That's not my Neighbor | 💻 PC · 📱 | 검문 + 호러 | 세입자 확인 → 허가/거부/신고 3택 → 캠페인·아케이드·커스텀 | 커스텀(세입자 직접 설계) 모드로 UGC 재생산 | [Steam](https://store.steampowered.com/app/3431040/) |
| Five Nights at Freddy's | 💻 · 📱 | 교대 근무 생존 | 0시~6시(실제 약 10분) 전력 예산 관리 → 5밤 + 보너스 + 커스텀 밤 | 공유 자원(전력) 한 개로 긴장 생성. 프리미엄 + IP | [Wikipedia](https://en.wikipedia.org/wiki/Five_Nights_at_Freddy%27s_(video_game)) |
| Animal Hospital (Anomaly) | 🟥 Roblox | 교대 근무 판별 | 환자 줄에서 괴물 하나 걸러내기 | 2026 Roblox 호러 1위 포맷. 등급 Minimal이라 Kids 노출 | 10-09 Roblox API: 동접 약 4.4만 · 방문 24억 ([`our_games/anomaly_shop`](../../../our_games/anomaly_shop/README.md) 기록, 이후 수치 `미검증`) |

## 3. 핵심 루프·시스템
자세한 근거는 [`anomaly_detection.md`](anomaly_detection.md) ★ 설계 시사점 12가지.
- **판정 동사는 하나(이진).** Exit 8은 사진 찍기·쏘기 프로토타입을 버리고 "진행/되돌아가기"만 남겼다. 동사가 늘수록 톤이 깨지고 비용이 는다.
- **살펴볼 대상을 제한한 고정 구도.** Platform 8의 기차 객차는 너무 복잡해 이상현상 찾기가 실패했다. 얼굴·손·쪽지·거울 정도.
- **서류 대조형은 데이터 이상현상.** Papers, Please식으로 "말한 것"과 "기록된 것"을 대조. 이상현상은 사람(그림자·반사·손가락 수)과 데이터(날짜·띠 불일치)에 둔다.
- **규칙은 밤마다 1~2개, 조용히.** 캐릭터가 말하는 순간 준 새 규칙은 플레이테스터가 무시한다(Lucas Pope). 하루 스크립트 인물 2~3명 + 나머지 생성.
- **오판 패널티는 단계적.** 하루 2회 면제 → 5, 5, 10, 15, 20… 매일 리셋(Papers, Please). 즉사 대신 위협 게이지 누적.
- **대부분 섬뜩하게, 치명은 드물게 + 예고.** 게임 오버 비중을 올린 후속작은 평가가 떨어졌다.
- **이상현상은 중복 없이 뽑고 발견률을 기록.** "이상현상 없음 버그" 제보가 실은 너무 미묘한 이상현상이었다(Exit 8, 894 투표: 쉬움 47.7% · 어려움 30.3% · 답 찾아봄 22%).
- **교대 구조.** 한 밤 8~12분, 밤마다 공격성 상승, 5밤 + 보너스 + 커스텀.
- **Roblox 협동 배관.** 파티 → `TeleportAsync` + 예약 서버, 공개 매칭은 MemoryStore 큐. TeleportData는 클라이언트가 보므로 민감 값 금지.

## 4. 수치 (data)
| 게임 | 항목 | 값 | source | URL | 확인일 |
|---|---|---|---|---|---|
| The Exit 8 | 개발 기간 | 기획·프로토 6개월 + 제작 3개월 | wiki(인터뷰) | [AUTOMATON](https://automaton-media.com/en/news/20240214-27192/) | 2026-10-09 |
| Platform 8 | 이상현상 난이도 투표 | 894표: 쉬움 47.7% · 어려움 30.3% · 답 찾아봄 22% | wiki(인터뷰) | [AUTOMATON](https://automaton-media.com/en/interviews/interview-the-exit-8-developer-kotake-create-on-the-perks-of-being-a-solo-dev-and-how-platform-8-came-to-be/) | 2026-10-09 |
| Platform 8 | 플레이테스터 수 | 약 4명 | wiki(인터뷰) | 같은 글 | 2026-10-09 |
| Papers, Please | 캠페인 길이 · 하루 구성 | 30일 · 스크립트 2~3명 + 생성 | wiki(인터뷰) | [Road to the IGF](https://www.gamedeveloper.com/design/road-to-the-igf-lucas-pope-s-i-papers-please-i-) | 2026-10-09 |
| Papers, Please | 벌점 | 하루 2회 면제 후 5, 5, 10, 15, 20… 매일 리셋 | wiki(팬 가이드) | [ludo.guide](https://www.ludo.guide/guide/papers-please/citations) | 2026-10-09 |
| FNAF 1 | 한 밤 실제 시간 | 약 10분 (0시~6시 압축) | wiki | [Wikipedia](https://en.wikipedia.org/wiki/Five_Nights_at_Freddy%27s_(video_game)) | 2026-10-09 |
| Animal Hospital | 동접 · 방문 | 약 4.4만 · 24억 | measured(Roblox API) | our_games 기록 | 2026-10-09 |

## 5. 원전·오픈소스 (라이선스 포함)
전체 표는 [`anomaly_detection.md`](anomaly_detection.md) §1(설계 원전) · §2(Roblox 구현 자료·오픈소스) · §4(만세력 계산). 핵심만:

| 자료 | 종류 | 라이선스 | 다루는 것 | 확인일 |
|---|---|---|---|---|
| AUTOMATON: Exit 8의 기원 / Platform 8 인터뷰 | 인터뷰 | 기사 | 이진 판정으로 좁힌 이유, 실패한 프로토, 난이도 투표 | 2026-10-09 |
| Designing the bleak genius of Papers, Please · Road to the IGF | 기사·인터뷰 | 기사 | 스크립트+생성 혼합, 규칙 얽힘, 페이싱 | 2026-10-09 |
| Lucas Pope devlog | 1차 개발 로그 | 블로그 | 현지화·모바일 포팅 | 2026-10-09 |
| Roblox Content Maturity · Kids & Select | 공식 문서 | 문서 | Mild/Moderate 기준, 16세 미만 노출 요건 | 2026-10-09 |
| Year of the 8-like (scrmbl) | 장르 개관 | 기사 | 8-like 변형(2D·VR·협동·코미디) 흐름 | 2026-10-09 |

## 6. 함정 (흔한 실패)
- **판정 동사를 늘린다.** 톤이 깨지고 제작비가 는다. Exit 8이 버린 길.
- **살펴볼 공간이 넓다.** 이상현상을 못 찾는 게 아니라 "어디를 봐야 하는지"를 모르게 된다(Platform 8 기차).
- **새 규칙을 대사 중에 준다.** 플레이어가 놓친다.
- **즉사 비중을 올린다.** 평가 하락. 섬뜩함이 주, 치명은 드물게.
- **이상현상 재사용.** 전부 나오기 전 반복이 생기면 "또 그거네"가 된다.
- **Roblox에서 등급을 Moderate로 올린다.** 사실적인 피 한 장면이 Kids·Select 노출을 막는다.
- **Robux로 운세·부적을 판다.** 도박 금지 + 확률 공개 의무에 걸린다. 복채는 게임 내 재화로만.

## 7. 우리 게임 적용
- **R-A 이상현상 점집: 야간 근무** (Roblox, 선택작) → [`our_games/anomaly_shop/`](../../../our_games/anomaly_shop/README.md). 시사점: 판정 동사 둘(복채 받기/돌려보내기), 사주 = 서류 대조, Mild 등급 목표.
- **A2 밤의 점집** (앱, 프리미엄 16+) → [`our_games/README.md`](../../../our_games/README.md) §1. 시사점: 프리미엄 단품이면 Exit 8식 "1시간 분량 + 설명 없음"이 선례.

## 채움 상태
| 절 | 상태 | 마지막 갱신 |
|---|---|---|
| 2 대표작 | ◐ 규모 수치 미검증 많음 | 2026-10-17 |
| 3 루프 | ● | 2026-10-17 |
| 4 수치 | ◐ | 2026-10-17 |
| 5 원전 | ● (상세는 anomaly_detection.md) | 2026-10-17 |
| 6 함정 | ● | 2026-10-17 |
| 7 우리 적용 | ● | 2026-10-17 |
