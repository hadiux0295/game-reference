# RPG · 방치형 (RPG / Idle)

> 하위 장르: 가차 RPG · MMORPG(리니지라이크) · 한국 방치형 RPG(키우기) · 서바이버류 · 로그라이트 · Roblox 시뮬레이터·애니 RPG
> 적합 플랫폼: 📱 앱(방치형 · 가차 · 서바이버류) · 🟥 Roblox(시뮬레이터 · 애니 RPG) · 💻 PC(로그라이트 · ARPG)
> 마지막 확인일: 2026-10-17. 숫자·주장마다 `[n]` 출처 번호(맨 아래)와 확인일. 확인 못 한 것은 `미검증`.
> 서바이버류 Godot 오픈소스(CC0·MIT)와 설계 시사점: [`../strategy/defense_management_survivors.md`](../strategy/defense_management_survivors.md) snake_survivor 절. 방치형·전투 공식 한 장: [`../../systems/genres.md`](../../systems/genres.md). 가차 구현: [`../../platforms/godot/patterns/Gacha.gd`](../../platforms/godot/patterns/Gacha.gd).

## 1. 한 줄 정의
**숫자가 커지는 것** 자체가 보상인 게임. 비용은 지수로 오르고 효과는 선형이라 "벽"이 생기며, 벽을 넘는 수단(가차·환생·시간)이 BM이다. 서바이버류·로그라이트는 같은 성장 곡선을 한 판(30분) 안에 압축한 것.

## 2. 대표작 (인기 게임)

| 게임 | 플랫폼 | 하위 장르 | 핵심 루프 한 줄 | 왜 팔리나 (훅·BM) | 규모 근거 (출처·확인일) |
|---|---|---|---|---|---|
| 원신 (Genshin Impact) | PC·모바일·PS | 오픈월드 액션 가차 RPG | 탐험·원소 전투 → 원석 획득 → 기원(가차) → 캐릭터 육성 → 상위 콘텐츠 | 캐릭터 한정 가차(기본 0.6%, 90뽑 천장, 50/50) + 배틀패스·월정액 + 레진(스태미나) | 모바일 누적 $37억 (출시 2년, Sensor Tower) [30] 2026-10-17 |
| 붕괴: 스타레일 (Honkai: Star Rail) | PC·모바일·PS | 턴제 가차 RPG | 스토리·던전 자동전투 → 성옥 → 워프(가차) → 캐릭터·광추 육성 | 원신과 동일 천장 구조(캐릭 90, 광추 80) + 자동전투로 세션 짧음 | 모바일 누적 $20억 돌파 (출시 2년 미만, AppMagic 추정) [48] 2026-10-17 |
| Fate/Grand Order | 모바일 | 턴제 가차 RPG (IP) | 스토리 챕터 → 성정석 → 서번트 가차 → 재료 파밍 | IP 서사·서번트 수집, 천장 없음(2023년까지), 일본 매출 81.1% | 전세계 누적 $70억 (2023-08 중순, Sensor Tower) [29] 2026-10-17 |
| 리니지M | 모바일 | 리니지라이크 MMORPG | 자동사냥 → 집행검·변신·마법인형 뽑기 → 혈맹 공성 | 경쟁(PvP)·과시 기반 고액 결제, 변신/인형 뽑기 | 누적 $42.3억 (2023-02-14 기준, Sensor Tower) [26]; 한국 비중 89.5% (2019) [27] 2026-10-17 |
| 오딘: 발할라 라이징 | 모바일·PC | MMORPG (리니지라이크 변형) | 자동사냥·필드 보스 → 장비·아바타 뽑기 → 길드 쟁탈 | 북유럽 신화 비주얼 + 전통 BM | 누적 $9억 (2023-07, Sensor Tower), 한국 91.4% [25] 2026-10-17 |
| 로스트아크 | PC | 핵앤슬래시 MMORPG | 레이드 → 재련(강화) → 아이템레벨 → 상위 레이드 | 레이드 콘텐츠 + 재련 확률·펫·스킨 | Steam 동접 최고 1,325,305명 (2022-02, SteamDB) [28] 2026-10-17 |
| 나 혼자만 레벨업: 어라이즈 | 모바일·PC | 액션 가차 RPG (IP) | 스토리 던전 → 헌터·무기 가차 → 장비 파밍 | 웹툰 IP + 가차 + 배틀패스 | 출시 3개월 만에 매출 $1억 돌파 (2024-07, Sensor Tower), 한국 33%·미국 19% [22] 2026-10-17 |
| 버섯커 키우기 | 모바일 | 한국 시장 방치형 RPG (중국 Joy Nice/4399) | 방치 사냥 → 램프 장비 뽑기 → 전투력 → 스테이지 | 장비 뽑기 도파민(램프)·과금 패키지, 매우 짧은 세션 | 누적 $9,700만 중 한국 $6,400만(66%) (2024-03, Sensor Tower) [18]; 2025-06 기준 한국 방치형 매출 2위 [21] 2026-10-17 |
| 세븐나이츠 키우기 | 모바일 | 한국 방치형 RPG (넷마블) | 방치 사냥 → 영웅 뽑기·강화 → 스테이지·탑 | 기존 IP + 저사양·저피로 방치 + 소과금 패키지 | 출시 45일 만에 누적 $4,000만 (2023-10, Sensor Tower), 한국 매출 2위 [19]; 출시 8시간 만에 앱스토어 매출 1위 [20] 2026-10-17 |
| 갓깨비 키우기 | 모바일 | 한국 방치형 RPG (조이게임즈·카카오게임즈 IP) | 방치 사냥 → 장비·동료 뽑기 → 성장 | 버섯커 공식의 한국형 변주 | 한국 방치형 RPG 매출 1위, 약 $1,000만·다운로드 100만 (2025-06, Sensor Tower) [21] 2026-10-17 |
| 나 혼자 만렙 키우기 | 모바일 | 방치형 RPG (웹툰 IP, 닷투 개발·디오리진 퍼블리싱) | 방치 사냥 → 성장 → 스테이지 | 웹툰 IP(나 혼자 만렙 귀환자) | 매출 `미검증` (앱스토어 등록 확인 [23]; 매출 자료 없음) 2026-10-17 |
| Vampire Survivors | PC·콘솔·모바일 | 서바이버류 로그라이트 | 자동 공격 → 경험치 젬 → 레벨업 3택1 → 30분 생존 → 메타 언락 | $4.99 프리미엄 + 소액 DLC, "한 판 더" 근접 실패 설계 | Steam 리뷰 128,290개·98% 긍정 (2026-10-17) [9]; 출시 2~3개월 내 100만 장 (CEO 발언) [8] |
| Survivor.io | 모바일 | 서바이버류 F2P | 스테이지 생존 → 장비 뽑기·강화 → 챕터 | 광고+IAP 하이브리드, 장비 가차 | IAP 누적 $5억 이상 (2024-04, Sensor Tower), 2023년 $1.823억 [24] 2026-10-17 |
| Hades | PC·콘솔·모바일(Netflix) | 액션 로그라이트 | 런 → 사망 → 하우스에서 영구 강화 → 재도전 | 무기 6종×4 어스펙트, 서사가 죽음마다 진행 | 얼리액세스 70만 + 정식 3일 30만 = 100만 장 (2020) [14] 2026-10-17 |
| Slay the Spire | PC·콘솔·모바일 | 덱빌딩 로그라이크 | 카드 3택1 → 층 등반 → 사망 → 카드 언락 | 프리미엄 단품, 중국 매출 30% | 150만 장 (2019-03, GDC 포스트모템) [15]; 속편 얼리액세스 1주 300만 장 (2026-03) [16] |
| Balatro | PC·콘솔·모바일 | 포커 덱빌딩 로그라이크 | 핸드 → 조커 구매 → 점수 지수 성장 → 앤티 상승 | 프리미엄 단품, 1인 개발 | 전 플랫폼 500만 장 (2025-01-20, Playstack CEO) [17] 2026-10-17 |
| Blox Fruits | Roblox | 애니(원피스풍) 액션 RPG | 사냥·레벨업 → 악마열매 뽑기 → 섬 진행·PvP | 게임패스·열매 뽑기, 무료 접근 | 누적 방문 649.9억, 즐겨찾기 2,008만 (Roblox API) [31] 2026-10-17 |
| Pet Simulator 99 | Roblox | 펫 수집 시뮬레이터 | 코인 수집 → 알(펫 뽑기) → 더 좋은 구역 → 리버스 | 알 뽑기·게임패스·한정 패키지, 펫 트레이드 | 누적 방문 26.7억, 즐겨찾기 221만 (Roblox API) [31] 2026-10-17 |
| Anime Vanguards | Roblox | 애니 유닛 가차 타워디펜스 | 스테이지 → 보석 → 유닛 소환(가차) → 진화 | 유닛 소환 가차가 주 수익 [33] | 누적 방문 20.8억 (Roblox API) [31]; 2024-09 Roblox Top Earning 1위 보도 [33] 2026-10-17 |

## 3. 핵심 루프·시스템

- **성장 곡선 — 지수 비용 vs 선형 효과.** 방치형의 표준식은 `다음 비용 = 기본비용 × 성장률^보유수`, 산출은 `기본산출 × 보유수 × 배율`(선형). 비용이 지수, 산출이 선형이라 반드시 정체가 오고, 그 정체를 새 생성기·배율·프레스티지로 푼다. 예: AdVenture Capitalist 레모네이드 스탠드 성장률 1.07, 기본비용 4(실제 3.738), 기본산출 1.67/초, 25·50개 보유 시 x2 배율 [4] 2026-10-17. 대량구매 공식 `b·r^k(r^n−1)/(r−1)`도 같은 글.
- **가차와 천장(pity).** 기본 확률은 낮게(원신 5★ 0.6%), 하드 천장(90뽑)과 "픽업 50/50 → 실패 시 다음 확정"을 결합해 최악 180뽑을 보장 [1] 2026-10-17. 기원 1·기원 2는 천장 카운트를 공유(공식 공지) [2]. 스타레일은 캐릭터 90/광추 80, 광추 기본 0.8%로 품목별 차등 [3]. FGO는 2023년까지 천장 없이 IP 서사로 지탱 [29].
- **방치형의 오프라인 수익·프레스티지(환생).** 오프라인 보상은 "돌아올 이유"를 만들고 상한을 두어 접속을 유도한다(상한 수치는 게임별 상이: AFK 아레나 12시간[Fandom 위키·afk.global, 2차]; Melvor Idle 최대 24시간[wiki.melvoridle.com] — Steam 커뮤니티 글은 18시간으로 보고, 출처 불일치 2026-10-19 확인. 한국 방치형(버섯커·세븐나이츠 키우기)의 상한은 `미검증`). 프레스티지는 "대부분 리셋 + 영구 배율/통화 지급"으로, 매 환생마다 비용 곡선에서 더 멀리 가게 하는 장치 [4]. 2부는 "생성기가 생성기를 만드는" 미분 체인(Derivative Clicker: 비용 5×1.1^n, 티어 부스트 0.05%/개)으로 e^x에 근접하는 대안 성장 모델을 다룬다 [5] 2026-10-17.
- **장비·강화·돌파 깊이.** 한국 방치형(버섯커·세븐나이츠 키우기)은 "뽑기 → 합성/강화 → 돌파" 3단 깊이로 수집·전투력 숫자를 끊임없이 올린다. 버섯커는 한국 매출 66% 집중으로 이 공식이 한국 시장에서 특히 잘 먹힘을 보여줌 [18]. 로스트아크는 재련(강화) 확률이 엔드게임 루프 그 자체 [28] — 재련 단계별 기본 성공률 차등, 실패 시 재료 소모(장비 하락·파괴 없음)·재시도 성공률 상승(상한 있음), 실패마다 성공률 비례로 '장인의 기운' 누적 → 최대 시 해당 단계 100% 성공(공식 게임 가이드 '재련', https://lostark.game.onstove.com/GameGuide/Pages/재련) 2026-10-19 확인 (단계별 확률·실패 시 상승폭·장인의 기운 적립 비율 수치 `미검증`).
- **스태미나와 세션 길이.** 원신 레진: 8분당 1 회복, 상한 160→200 (2024-05 개발자 공지 기준) [45] 2026-10-17. 스태미나는 일일 세션을 15~30분으로 자르고, 재화 판매(레진 충전)와 "내일 또" 리텐션을 동시에 만든다. 방치형은 반대로 스태미나 대신 "오프라인 보상 상한"으로 같은 효과를 낸다.
- **서바이버류의 3택1과 밀도 곡선.** Vampire Survivors는 레벨업마다 무기/패시브 3~4택1, 최대 레벨(보통 8) 무기 + 짝 패시브 보유 시 진화 선택지 노출. 스테이지별 15/20/30분 소프트 제한, 시간 도달 시 리퍼 등장(매분 추가) — "30분 = 성공" 정의가 근접 실패(near-miss)를 만들어 재도전 유도 [8][10] 2026-10-17. 개발자 갈란테는 도박 업계 경험(슬롯 연출)을 상자 열기에 적용 [8][10]; 원형은 안드로이드 게임 Magic Survival [11].
- **로그라이트의 메타 진행(영구 언락).** Hades: 런 중 오볼은 소멸, 다크니스·타이탄의 피는 하우스에서 영구 강화·무기 어스펙트(6무기×4어스펙트) 언락에 사용, 실패 후 서사가 진행되고 God Mode로 사망마다 강해짐 [13][14]. Slay the Spire: 초기 3일 800장 → 카드 언락·승천으로 장기화, 150만 장 [15]. Balatro: 조커 언락 + 지수 점수 체계 [17].
- **Roblox 시뮬레이터의 펫·리버스·게임패스 BM.** 루프: 코인 → 알(펫 가차) → 상위 구역 → 리버스(환생 배율). 수익은 Robux 게임패스·개발자 상품(인게임 판매 창작자 몫 약 70%), 환전은 DevEx 10,000 Robux = $38, 최소 30,000 Robux [34] 2026-10-17. Pet Simulator 99는 한정 패키지·이벤트 타이틀 교체(BLOOD MOON 등)로 재방문 유도 [31]. Anime Vanguards처럼 애니 IP 유사 유닛 가차가 매출 1위를 차지하기도 함 [33].

## 4. 수치 (data)

| 게임 | 항목 | 값 | source | URL | 확인일 |
|---|---|---|---|---|---|
| 원신 | 캐릭터 이벤트 기원 5★ 기본 확률 / 하드 천장 / 4★ 천장 / 최악 | 0.6% / 90뽑 / 10뽑 / 180뽑 (50/50) | wiki/guide (공식 공지는 JS 렌더로 직접 열람 실패; 공식 "기원 2" 공지가 천장 공유·동일 확률 명시) | [1][2] | 2026-10-17 |
| 붕괴: 스타레일 | 캐릭터 / 광추 이벤트 워프 | 캐릭 0.6%·90뽑, 광추 0.8%·80뽑 | guide (공식 미확인) | [3] | 2026-10-17 |
| 원신 | 레진 회복·상한 | 8분당 1, 상한 160→200 | news (개발자 공지 인용) | [45] | 2026-10-17 |
| Vampire Survivors | 스테이지 소프트 제한 / 가격 / Steam 리뷰 | 15·20·30분 / $4.99 / 128,290개·98% 긍정 | wiki + Steam 상점 | [8][9] | 2026-10-17 |
| Hades | 무기(Infernal Arms) 수 × 어스펙트 | 6 × 4 | wiki (Fextralife) | [13] | 2026-10-17 |
| Hades | 판매 | 얼리액세스 70만 + 정식 3일 30만 | wiki (Wikipedia) | [14] | 2026-10-17 |
| Slay the Spire | 판매 / 중국 비중 | 150만 장 (2019-03) / 30% | measured (GDC 포스트모템 보도) | [15] | 2026-10-17 |
| Balatro | 판매 | 500만 장 (2025-01-20) | measured (퍼블리셔 발표) | [17] | 2026-10-17 |
| 버섯커 키우기 | 누적 매출 / 한국 비중 | 약 $9,700만 / $6,400만 (66%), 2024-03 | inferred (Sensor Tower 추정) | [18] | 2026-10-17 |
| 세븐나이츠 키우기 | 출시 45일 누적 | 약 $4,000만 (2023-10) | inferred (Sensor Tower 추정) | [19] | 2026-10-17 |
| 나 혼자만 레벨업: 어라이즈 | 출시 3개월 매출 | $1억+ (2024-07) | inferred (Sensor Tower 추정) | [22] | 2026-10-17 |
| Survivor.io | IAP 누적 / 2023년 | $5억+ (2024-04) / $1.823억 | inferred (Sensor Tower 추정) | [24] | 2026-10-17 |
| Fate/Grand Order | 누적 매출 / 일본 비중 | $70억 (2023-08) / 81.1% | inferred (Sensor Tower 추정) | [29] | 2026-10-17 |
| 리니지M | 누적 매출 | $42.3억 (2023-02-14) | inferred (Sensor Tower 추정) | [26] | 2026-10-17 |
| 로스트아크 | Steam 동접 최고 | 1,325,305 (2022-02) | measured (SteamDB) | [28] | 2026-10-17 |
| Blox Fruits / Pet Sim 99 / Anime Vanguards | 누적 방문 | 649.9억 / 26.7억 / 20.8억 | measured (Roblox 공식 API) | [31] | 2026-10-17 |
| Roblox | DevEx 환율 / 인게임 판매 창작자 몫 | 10,000 Robux = $38 / 약 70% | official docs | [34] | 2026-10-17 |

> 2026-10-19 배치 보강 (G-ref, 출처 URL은 Sage가 2026-10-24에 직접 열어 수치 대조):
- 가챠 소프트 천장(5★ 캐릭터 이벤트): **원신** 기본 확률 0.6%, 천장 포함 평균 1.6%, 89회 연속 미획득 시 90회차 5★ 확정(하드 천장 90) — https://genshin-impact.fandom.com/wiki/Wish (위키, 확인 2026-10-19); 소프트 천장 약 74회차부터 시작, 이후 90회차에 100%까지 선형 상승(커뮤니티 통계 모델) — https://www.hoyolab.com/article/497840 (커뮤니티 분석, 확인 2026-10-19), 표본 규모 `미검증`(약 2.6억 회 paimon.moe 데이터 분석 게시물 존재: https://genshin-impact.fandom.com/f/p/4400000000000308779, 본문 수치 `미검증`). **붕괴: 스타레일** 기본 0.6%, 천장 포함 평균 1.6% — https://honkai-star-rail.fandom.com/wiki/Stellar_Warp (위키, 확인 2026-10-19); 90회차 5★ 확정 — https://game8.co/games/Honkai-Star-Rail/archives/408765 (확인 2026-10-19); 소프트 천장 시작(약 74회차)·표본 규모 `미검증`

## 5. 원전·오픈소스 (라이선스 포함)

| 자료 | 종류 | 라이선스 | 다루는 것 | 확인일 |
|---|---|---|---|---|
| The Math of Idle Games Part I (A. Pecorella, Game Developer, 2016-10-13) [4] | 글 | 저작권 (무료 열람) | 지수 비용·선형 산출 공식, 대량구매·최대구매 공식, 프레스티지 정의, AdCap 수치 | 2026-10-17 |
| The Math of Idle Games Part II (2016-12-14) [5] / Part III (2017-02-01) [6] | 글 | 저작권 (무료 열람) | II: 생성기 체인(미분형) 성장 모델, 생성기 relevancy; III: 프레스티지 루프 — 재화 산정 기준(최대·누적 수익 vs 리셋 후 수익·업그레이드 수), 게임별 공식(Realm Grinder 제곱근·이차방정식, AdCap 150·√(c_L/10¹⁵), Cookie Clicker 세제곱근, Egg, Inc. 지수 0.14)과 2배 획득 필요 배율(약 4×/3–4×/8×/128×), 프레스티지 시뮬레이션 스프레드시트(시트 3a) | 2026-10-17 (III: 2026-10-19) |
| GDC 2015 "Idle Games: The Mechanics and Monetization of Self-Playing Games" (Pecorella, F2P Summit) [7] | 강연 | GDC Vault 무료 콘텐츠 태그 | 코어·메타 루프, 리텐션, Kongregate 지표 | 2026-10-17 |
| Vampire Survivors 설계 자료: The Conversation 분석 (2023-04-13) [10], Noclip 미니 다큐 (2023-07) [11][12], Wikipedia [8] | 기사·영상 | 저작권 | 근접 실패·도박 심리, 30분 구조, Magic Survival 원형, DLC 전략 | 2026-10-17 |
| Flare engine (flareteam/flare-engine) [35] | 엔진 | GPL-3.0 (코드; 에셋 별도) | 싱글 2D 액션 RPG 엔진, C++ | 2026-10-17 |
| Veloren (veloren/veloren) [36] | 게임 | GPL-3.0 | 복셀 오픈월드 RPG, Rust | 2026-10-17 |
| Cataclysm: Dark Days Ahead [37] | 게임 | CC BY-SA 3.0 (본체; 일부 컴포넌트 Apache-2.0/OFL 등) | 턴제 로그라이크 생존, 1,000명+ 기여 | 2026-10-17 |
| RPG Paper Maker [38] | 엔진 | **오픈소스 아님** — 자체 EULA(2023-10-04): 비상업 무료, 상업 판매는 유료 에디션 | 2.5D(2D 스프라이트+3D 월드) RPG 제작기 | 2026-10-17 |
| Survivors Starter Kit (DarkRewar, Godot 4.6 C#) [39] | 템플릿 | MIT | 서바이버류 스타터(이동·스탯·스폰·업그레이드) | 2026-10-17 |
| Godot Open RPG (gdquest-demos) [40] | 데모 | MIT | 턴제 전투 RPG 데모, Godot 4.7.2+ | 2026-10-17 |
| 일본 JOGA 가이드라인 [41] | 업계 자율규제 | — | 2012-08 "랜덤 아이템 판매 표시·운영 가이드라인"(가챠), 회원사(정회원)에만 구속, 일부 비공개; 개정 연혁: 2012-08-02 제정·2012-09-01 시행 → 2016-01-28 개정(PC·스마트폰 가이드라인 통합, 명칭에 '아이템 판매' 추가)·2016-04-01 시행 → 2024-06-07 개정·2024-06-27 시행 (2016 개정 발표일은 보도상 2016-02-19); 2024 개정 내용은 `미검증` | 2026-10-18 |
| 중국 문화부 통지 (2016-12 공포, 2017-05-01 시행) [42] | 법규 | — | 뽑기 아이템 이름·속성·수량·확률 공개 의무; 보도는 비공식 번역 기반 | 2026-10-17 |
| 한국 게임산업진흥법 시행령 §19-2·별표 3-2 (2024-03-22 시행) [43][44] | 법규 | — | 캡슐형/강화형/합성형 확률 표시 의무, 3년 평균 매출 1억 이하 소기업 제외, 위반 시 2년 이하 징역 또는 2천만원 이하 벌금 | 2026-10-17 |
| DiGRA 비교연구: 동아시아 가챠 확률 공개 규제 준수 [46] | 논문 | — | 중국이 동아시아 첫 법적 의무화, 일본은 자율규제 지속 | 2026-10-17 |

## 6. 함정 (흔한 실패)

- **비용은 지수인데 보상도 지수로 놓기.** 산출이 비용을 따라가면 정체(벽)가 사라져 "다음 목표"가 없어진다. 방치형의 긴장은 지수 비용 vs 선형 산출의 격차에서 나온다 [4].
- **프레스티지 타이밍 미설계.** 환생 배율이 너무 크면 1회 환생 후 이전 콘텐츠가 무의미해지고, 너무 작으면 리셋 손실만 느껴진다. 환생마다 "조금 더 멀리"가 되게 곡선을 맞춰야 한다 [4][5].
- **천장 없는 가차.** FGO는 IP로 버텼지만 [29], 신규 IP가 천장 없이 가면 이탈·규제 리스크가 동시에 온다. 한국은 2024-03부터 확률 미표시·거짓 표시가 형사처벌 대상 [43][44], 중국은 2017부터 공개 의무 [42].
- **스태미나/오프라인 상한을 '벌'로 설계.** 상한은 "돌아올 이유"여야지 "못 하게 막기"가 되면 안 된다. 원신이 160→200으로 올린 것도 레진 상한이 불만의 중심이었기 때문 [45].
- **서바이버류에서 선택지가 선택이 아닐 때.** 3택1의 가치는 빌드 분기에 있다. 진화 조건(최대 레벨+짝 패시브)처럼 "지금 고르면 나중에 터진다"가 없으면 그냥 랜덤 보너스가 된다 [8].
- **로그라이트 메타 진행이 런을 대체.** 영구 강화만 쌓이면 런 내 결정이 의미를 잃는다. Hades는 서사·God Mode로 실패를 보상하되 런 내 선택(보온·어스펙트)을 유지했다 [13][14].
- **Roblox 시뮬레이터의 리버스 인플레이션.** 환생 배율이 겹겹이 쌓이면 숫자 표기(1e30)만 커지고 체감이 사라진다. BIG Games는 이벤트 타이틀·구역을 계속 교체해 "새 구역" 자체를 보상으로 쓴다 [31].
- **한국 방치형 공식의 과포화.** 버섯커 → 갓깨비 → 여러 "키우기"가 같은 램프·뽑기 공식을 반복, 2025년엔 IP 결합이 차별 요소로 떠올랐다 [21]. 공식만 복제하면 UA 비용만 남는다.

## 7. 우리 게임 적용
[`our_games/README.md`](../../../our_games/README.md) 기준.
- **로직 연구 #5 나 혼자 만렙 키우기 · #13 Loop King** → 방치형 RPG·소환 가차. 천장·확률 공개 의무(§5 규제 행)는 한국 출시 시 법적 요건.
- **snake_survivor** (Godot) · **Rescue Run #10** → 서바이버류. 30분 "거의 다 왔다" 설계, 3택1 빌드, 웨이브 사이 상점(Brotato). 오픈소스 CC0/MIT 목록은 위 링크.
- **Wayward Ember** (영웅 존재감 파일럿: 허브 · 소환 · 탐험) → 가차 RPG의 허브 구조. 성장 곡선 공식은 §3 첫 항목.
- **Roblox 시뮬레이터**는 우리 프로젝트에 없다. 펫·리버스·게임패스 BM과 DevEx 환율(§4)은 Roblox 타이쿤(`our_games` §3)의 수익 추정에 쓴다.

## 채움 상태
| 절 | 상태 | 마지막 갱신 |
|---|---|---|
| 2 대표작 | ● 19행 (나 혼자 만렙 키우기 매출 미검증) | 2026-10-17 |
| 3 루프 | ● | 2026-10-17 |
| 4 수치 | ● 17행 (HoYoverse 공식 확률 페이지는 가이드 사이트 경유) | 2026-10-17 |
| 5 원전 | ● 14행 (RPG Paper Maker는 비오픈소스 EULA) | 2026-10-17 |
| 6 함정 | ● | 2026-10-17 |
| 7 우리 적용 | ● | 2026-10-17 |

## 출처

1. https://www.highgroundgaming.com/genshin-impact-wishing-guide-pity/ (2023-08-16, 갱신 2024-05-31) — 원신 0.6%/90/10/180
2. https://genshin.hoyoverse.com/en/news/detail/17072 — 공식 "Character Event Wish-2" 메커니즘 공지 (검색 스니펫으로 천장 공유·동일 확률 확인; 본문 JS 렌더)
3. https://primagames.com/tips/how-does-the-pity-and-gacha-work-in-honkai-star-rail-answered — 스타레일 90/80, 0.6/0.8% (검색 스니펫)
4. https://www.gamedeveloper.com/design/the-math-of-idle-games-part-i (2016-10-13)
5. https://www.gamedeveloper.com/disciplines/the-math-of-idle-games-part-ii (2016-12-14)
6. https://www.gamedeveloper.com/design/the-math-of-idle-games-part-iii
7. https://gdcvault.com/play/1022065/Idle-Games-The-Mechanics-and (GDC 2015)
8. https://en.wikipedia.org/wiki/Vampire_Survivors
9. https://store.steampowered.com/app/1794680/Vampire_Survivors/
10. https://theconversation.com/vampire-survivors-how-developers-used-gambling-psychology-to-create-a-bafta-winning-game-203613 (2023-04-13)
11. https://www.gamingonlinux.com/2023/07/check-out-the-mini-vampire-survivors-documentary/ (Noclip 다큐, 2023-07)
12. https://80.lv/articles/vampire-survivors-developer-on-its-design-sudden-success (2023-07-21)
13. https://hades.wiki.fextralife.com/Infernal+Arms
14. https://en.wikipedia.org/wiki/Hades_(video_game)
15. https://www.gamedeveloper.com/business/after-a-worrisome-start-i-slay-the-spire-i-has-sold-more-than-1-5-million-copies (2019-03-20)
16. https://fullcleared.com/news/slay-the-spire-2-confirms-3m-sold-in-first-week/ (2026-03-13)
17. https://www.pocketgamer.biz/balatro-exceeds-5-million-in-sales-on-all-platforms/ (2025-01-20)
18. https://sensortower.com/ko/blog/Growing-Mushroom-has-earned-64-million-dollars-in-revenue (2024-03)
19. https://sensortower.com/ko/blog/Seven-Knights-Idle-Adventure-achieved-40M-securing-the-second-spot-in-revenue (2023-10)
20. https://news.bizwatch.co.kr/article/mobile/2023/09/11/0001 (2023-09-11)
21. https://sensortower.com/ko/blog/God-Goblin-Raising-ranks-No-1-in-idle-RPG-revenue (2025-06)
22. https://sensortower.com/blog/solo-leveling-arise-revenue-surpasses-usd100-million-in-3-months (2024-07)
23. https://apps.apple.com/kr/app/%EB%82%98-%ED%98%BC%EC%9E%90-%EB%A7%8C%EB%A0%99-%ED%82%A4%EC%9A%B0%EA%B8%B0/id6566177585 — 나 혼자 만렙 키우기 앱스토어 (제공자: (주)펀치라인게임즈 / Punchline Games Co., Ltd., 저작권 표기 Punchline Games & DOTTWO Corp., 2026-10-19 확인) (퍼블리싱 보도: https://www.webtoonguide.com/ko/board/news-column/19584 (2024-09-03) — 디오리진이 개발사 닷투(DOTTWO)와 글로벌 퍼블리싱 계약; 출시 보도: https://www.ajunews.com/view/20241105082851067 (2024-11-05, 175개국 출시·AOS 선출시); 디오리진→펀치라인게임즈 퍼블리셔 변경 경위 `미검증`)
24. https://wnhub.io/news/finance/item-43301 (2024-04-16, Sensor Tower 인용)
25. https://sensortower.com/ko/blog/Odin-Vallhalla-Rising-dominates-the-Korean-gaming-market-with-900M-in-cumulative-revenue (2023-07)
26. https://gameworldobserver.com/?p=17923 (2023-03-07, Sensor Tower 2023-02-14 기준)
27. https://sensortower.com/blog/lineage-mobile-games-revenue-4-billion (2019-10)
28. https://www.thesixthaxis.com/2022/02/13/lost-ark-steam-download-records-player-count/ (2022-02-13, SteamDB 인용)
29. https://www.siliconera.com/?p=983312 (2023-09-08, Sensor Tower 인용)
30. https://wnhub.io/news/analytics/item-220 (2022-09-29, Sensor Tower 인용)
31. https://games.roblox.com/v1/games?universeIds=994732206,3317771874,5578556129 (Roblox 공식 API, 2026-10-17 조회)
32. https://www.blog.udonis.co/mobile-marketing/mobile-games/most-popular-roblox-games (Statista 2025-07 수치, 교차 확인용)
33. https://beebom.com/anime-vanguards-surpasses-blox-fruits-top-earning-roblox-game/ (2024-09-18)
34. https://create.roblox.com/docs/production/earning-on-roblox (Roblox 공식 문서)
35. https://github.com/flareteam/flare-engine (GPL-3.0)
36. https://github.com/veloren/veloren (GPL-3.0)
37. https://github.com/CleverRaven/Cataclysm-DDA / https://raw.githubusercontent.com/CleverRaven/Cataclysm-DDA/master/LICENSE.txt (CC BY-SA 3.0)
38. https://github.com/RPG-Paper-Maker/RPG-Paper-Maker / https://raw.githubusercontent.com/RPG-Paper-Maker/RPG-Paper-Maker/develop/LICENSE (EULA 2023-10-04)
39. https://github.com/DarkRewar/SurvivorsStarterKit (MIT)
40. https://github.com/gdquest-demos/godot-open-rpg (MIT)
41. https://japanonlinegame.org/joga_guideline/joga-guideline/?lang=en
42. https://www.pcgamesn.com/loot-box-odds-china (2017-04-27)
43. https://www.ajunews.com/view/20240102104711033 (2024-01-02)
44. https://newstomato.com/ReadNews.aspx?no=1224130 (2024-03-21)
45. https://mein-mmo.de/en/genshin-impact-increases-the-limit-for-original-resin-the-community-is-excited,1130141/ (2024-05-24)
46. https://dl.digra.org/index.php/dl/article/view/2749 (DiGRA, 가챠 확률 공개 규제 준수 비교연구)
47. https://www.hoyolab.com/article/497840 — HoYoLAB 통계 모델 글 (검색 스니펫: 데이터가 공지된 0.6% 기본 확률과 일치)
48. https://www.pocketgamer.biz/honkai-star-rail-rockets-past-2bn-on-mobile-in-under-two-years (AppMagic 추정, 검색 스니펫)
