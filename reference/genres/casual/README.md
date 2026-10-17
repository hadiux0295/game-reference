# 캐주얼 (Casual)

> 하위 장르: 매치3 · 블록 퍼즐 · 머지 · 정렬/잼/스크루 퍼즐 · 하이퍼캐주얼 · 하이브리드 캐주얼 · 보드 롤러 · Roblox 캐주얼(수집·훔치기·패션) · 웹 HTML5
> 적합 플랫폼: 📱 앱(주) · 🟥 Roblox · 💻 웹
> 마지막 확인일: 2026-10-17. 수치는 대부분 서드파티 추정(Sensor Tower · AppMagic · 트래커)이라 "추정"으로 읽는다. 확인 못 한 것은 `미검증`. 출처 번호 `[n]`은 맨 아래.
> 정렬 퍼즐 레벨 생성·솔버·2025~26 시장 데이터 상세: [`puzzle_levels.md`](puzzle_levels.md). 매치3·2048 구현 순서와 함정 한 장: [`../../systems/genres.md`](../../systems/genres.md).

## 1. 한 줄 정의
규칙을 3초 안에 이해하고, 한 판이 1~3분이며, "거의 깼다"에서 다시 누르게 되는 게임. 돈은 **실패 직전**(무브·슬롯·목숨)과 **기다림**(에너지·타이머)에서 나오고, 광고는 손실 회복 자리에 붙는다.

## 2. 대표작 (인기 게임)

| 게임 | 플랫폼 | 하위 장르 | 핵심 루프 한 줄 | 왜 팔리나 (훅·BM) | 규모 근거 (출처·확인일) |
|---|---|---|---|---|---|
| Royal Match (Dream Games) | iOS/Android | 매치3 (레벨형) | 4색·평균 25무브 보드에서 목표 달성 → 다음 레벨, 실패하면 목숨 차감 | 코인 단일 하드커런시로 목숨 리필·부스터·"무브 5개 추가" 컨티뉴를 모두 묶음. 유료 UA 비중이 압도적(2023년 설치의 61.5%가 유료, Sensor Tower) | Sensor Tower 추정 연매출 2021 $172M → 2022 $428M → 2023 $851M → 2024 $1.46B → 2025 $1.37B(첫 감소) [1]. AppMagic: 누적 총매출 $6B(2025-05), 순IAP $3.6B, 누적 DL 351M, RpD $15.6 [2][3]. 2026-10-17 |
| Candy Crush Saga (King) | iOS/Android/웹 | 매치3 | 15,000+ 레벨을 순차 진행, "거의 깼다" 상태에서 유료 추가 무브 | 레벨 난이도 데이터 튜닝의 원조. 레벨 65("너무 어려운 레벨")가 역대 최고 전환·최고 매출·최고 이탈 레벨(King GDC 2024) [35] | 2023-07 Royal Match에 월매출·DL 모두 역전당함($104M vs $112M, Sensor Tower) [4]. 2025 연매출은 출처별 상이($876.5M TechSpot 보도 등) → `미검증`. 2026-10-17 |
| Block Blast! (Hungry Studio) | iOS/Android | 블록 퍼즐 (무한·광고형) | 8×8 보드에 조각 배치, 줄 완성 시 제거, 못 놓으면 게임오버 | 실패해도 손실이 없는 "무한 세션" + 배너·전면·리바이브 보상형 광고 = 거의 순수 IAA 모델 | 2025년 전 세계 DL 1위 356.2M(AppMagic, 1/1–12/22) [5]. 광고매출 추정: 2025-06 Android 일 ~$584K(월 ~$17.5M, 추정, 출처 미명시) [6]; 2026년 1–5월 광고매출 ~$127M(Sensor Tower, DoF 인용) [7]. 2026-10-17 |
| Gossip Harbor (Microfun) | iOS/Android | 머지-2 + 스토리 | 에너지로 제너레이터 탭 → 아이템 머지 → 주문 납품 → 코인으로 스토리/리노베이션 진행 | 에너지 한도가 핵심 과금 레버, 보드 공간 압박, 월 단위 시즌·이벤트 겹치기 [9] | AppMagic: 2022-06 출시 후 누적 IAP $723M+, DL 92.4M, 2025-10 월 IAP ~$62M(머지2 장르 월간 최고) [8]. 2026-10-17 |
| Hexa Sort (Lion Studios → Cheer Games) | iOS/Android | 정렬(Sort) 퍼즐, 하이브리드 캐주얼 | 색깔 육각 타일 스택을 보드에 놓아 같은 색 10개 모으면 제거 | 하이퍼캐주얼 수준의 광고 소재 적합성 + 레벨·보드 확장 메타 | Sensor Tower: 누적 IAP $47M+, 활성 유저 ~800만(2026-02) [13]; 스튜디오 자체 주장 IAP $50M [12]; 2025년 Sort 하위장르 매출 ~$280M 중 ~$20M(~7%) [10]. 2026-10-17 |
| Screw Jam (Rollic) / Screwdom (iKame) | iOS/Android | 스크루(Screw) 퍼즐 | 층층이 쌓인 판에서 색 나사를 빼서 같은 색 박스에 채움, 도크(임시 보관) 슬롯 제한 | 레벨 구조 자체가 과금 포인트(도크 확장·박스 추가·유리 깨기), Screwdom은 수 분 투자 뒤 "레벨 살리기" 엔드게임 오퍼 [11] | Screw Jam 2024 IAP ~$25M; Screwdom 2025 IAP $75M+(매 레벨 전면광고 병행) [11]. Screw 하위장르 2025 매출 $206M+(전년 대비 ~2배), DL ~399M [10]. 2026-10-17 |
| Bus Jam / Color Block Jam (Rollic 등) | iOS/Android | 잼(Jam) 정렬 퍼즐 | 색 승객을 줄 세워 같은 색 버스에 태움 / 색 블록을 같은 색 문으로 빼냄, 대기 슬롯 제한 | 교착(choke point) 설계 + 실패 직전 "슬롯 추가" 과금 | Block 하위장르 2025 매출 ~$183M, 매출 ~2,900% 급증, Color Block Jam이 ~75% 점유 [10]. Bus Jam 개별 수치: 2024-12 기준 DL 14.6M+·매출 $7M+(costcenter.net, 약한 출처) [44] → `미검증`. 2026-10-17 |
| Monopoly GO! (Scopely) | iOS/Android | 캐주얼 보드(주사위 롤러) | 주사위 굴려 보드 한 바퀴 → 돈·스티커·이벤트 토큰 획득 → 랜드마크 건설 | 실시간 이벤트 겹치기·친구 선물·스티커 교환 등 소셜 라이브옵스. "70%가 매일 복귀"(Scopely 주장) [14] | Sensor Tower: 2025년 중 누적 IAP $6B 돌파, 1,275일 소요(Royal Match 1,868일, Clash of Clans 2,206일) [14][15]. 2025-09 전 세계 매출 2위 [16]. 2026-10-17 |
| Last War: Survival (FirstFun/FUNFLY) — 포인터 | iOS/Android | SLG(4X), 미니게임 광고로 유입 | 광고에서 본 레인 러너 미니게임 → 본편은 기지 건설·영웅·동맹전 | "광고 속 가짜 게임을 진짜로 만들었다"는 캠페인으로 오해 광고 논란을 정면 돌파(2024 Q4, 12.5M DL 주장) [17]. 캐주얼 아님 — 캐주얼 훅을 SLG 깔때기로 쓰는 사례로만 참조 | 2025-07/08/09 전 세계 모바일 매출 1위(Sensor Tower) [16]; 2025-02 누적 $2B+ [17]. 2026-10-17 |
| Grow a Garden (BMWLux / Splitting Point / Do Big) | Roblox | 방치형 농장 | 씨앗 구매 → 오프라인에도 성장 → 수확·판매 → 더 비싼 씨앗, 주간 한정 아이템·펫 알 | 오프라인 성장(Roblox에서 새로운 개념), 주간 업데이트 라이브서비스, Robux로 대기 단축·타인 작물 훔치기 [18][19] | 2025-03-26 출시, 2025-08-23 동접 ~22.3M(Roblox 기록, 당시 역대 최다), 누적 방문 35.3B+(2026-05) [18]; 인수 시점 CCU ~500 → 1개월 내 1M [19]. 2026-10-17 |
| Steal a Brainrot (SpyderSammy / Do Big) | Roblox | 수집·훔치기 타이쿤 | 컨베이어에서 Brainrot 구매(패시브 수입) ↔ 남의 베이스에서 훔치기, 쉴드·트랩으로 방어, 리버스로 리셋 | "훔치기" PvP 소셜 훅 + 희귀도 등급 + 밈 IP(이탈리안 브레인롯) | 2025-05-16 출시, 2025-10 동접 25.4M(역대 모든 게임 중 최다, Roblox 플랫폼 동접 47.4M 견인) [20][21]; 2025-07 누적 방문 7B [21]. 2026-10-17 |
| Adopt Me! (Uplift Games) | Roblox | 펫 수집·육성·거래 | 펫 알 부화 → 돌봄으로 Bucks 획득 → 거래로 희귀 펫 수집 | 거래 경제·희귀도가 핵심. 사기(trust trade) 대응으로 2020-11 거래 라이선스 도입 [22] | 2017-07 출시, 누적 방문 40.8B+(2025-11), 동접 최고 1.92M(2021-04), 연매출 ~$60M 보도 [22]. 2026-10-17 |
| Dress to Impress (Gigi) | Roblox | 패션 대결 | 6분 안에 테마 의상 조합 → 런웨이 → 1~5성 투표 → 상위 3명 포디움, 14단계 커리어 | 유저 생성 경쟁 콘텐츠, 셀럽 콜라보(Lady Gaga 2025-08), VIP 아이템(P2W 논란) [23] | 2023-11-11 출시, 누적 방문 9.7B, 동접 최고 ~1.5M(트래커, 날짜 미상) [23]. 2026-10-17 |
| Blade Ball (Wiggity) | Roblox | 피지컬 캐주얼(반사 액션) | 공이 날아올 때 타이밍 맞춰 쳐내기, 마지막 생존자 승리 | 한 버튼 반사 스킬 + 스킨·능력 가챠 | 2023-06 출시, 62일 만에 1B 방문(당시 Roblox 최단 기록) [24]. 2026-10-17 |
| Poki 웹 히트 (Plonky, SnapStyle Dress Up 등) | 웹/HTML5 | 웹 캐주얼 | 설치 없이 즉시 플레이, 짧은 세션 | 웹 광고 수익 + 포털 추천 알고리즘 | Poki 2025: 플레이어 625M, 플레이 11.1B, 최고 성과작 Plonky(Gametornado)·SnapStyle Dress Up(PlayCap) [25]. 2026-10-17 |

## 3. 핵심 루프·시스템

- **레벨 기반 진행 + "거의 깰 뻔"(near-miss) 난이도 조절** — King은 레벨별 "포기까지 시간 / 클리어까지 시간 / 퍼즐다움(puzzliness)"을 분리 측정해 "어렵지만 재미있는" 레벨과 "그냥 어려운" 레벨을 구분하고, 가장 재미없는 100개 레벨을 상시 재작업한다. 레벨 65 A/B 테스트: 더 어렵게 하면 단기 전환↑, 쉽게 하면 장기 리텐션↑ 및 이후 지출↑ [35]. 근거 연구: Candy Crush에서 near-miss는 패배보다 심박·각성 높고 "가장 짜증나지만 가장 계속하고 싶은" 결과(Waterloo 석사논문, n=60) [36]. 다음 세대(Royal Match)는 4색·평균 25무브로 캐스케이드 빈도를 올려 "거의 깼다" 상황을 더 자주 만든다(Homescapes도 2021-06 35→25무브, 5→4색으로 추종) [47].
- **부스터·목숨·무브 BM** — 세 가지 과금 지점: (1) 레벨 시작 전 부스터(Royal Match의 로켓/TNT/라이트볼), (2) 레벨 중 부스터(해머/화살), (3) 실패 시 "무브 +5" 컨티뉴. 목숨(5개)은 세션 길이를 제한해 리필 과금을 만든다 [46]. 스크루 퍼즐은 같은 구조를 "도크 슬롯 추가·박스 추가·유리 깨기"로 번역했고, Screwdom은 플레이어가 수 분 투자한 뒤에만 엔드게임 오퍼를 띄워 매몰비용을 과금에 쓴다 [11].
- **하이브리드 캐주얼 = 캐주얼 코어 + 메타(수집·장식·배틀패스)** — Voodoo 정의: "하이퍼캐주얼 코어 + 캐주얼/미드코어의 단순화된 메타"로 중장기 목표를 추가해 LTV를 올림 [48]. Supersonic × FutureBright 'Backyard Master' 사례: 먼저 코어 복잡도를 올려 리텐션 연장 → 집 꾸미기·펫 메타 추가 [31]. Supersonic이 제시한 끈끈함 신호: D1 ~40%, D7 15–20%(자사 블로그 기준, 업계 표준 아님) [30]. Sensor Tower: 2024년 하이브리드캐주얼 IAP 매출 +37% YoY(전 카테고리 중 최고 성장) [28].
- **광고(보상형·전면) 수익 비율** — Homa(2023): 하이브리드캐주얼 매출의 약 50%가 광고, LTV의 30% 이상은 IAP에서 나오게 설계 권장 [29]. Sensor Tower 광고 리포트(2026): 19개국 모바일 게임 광고매출 2025년 $12B(=순IAP ~$40B 대비 ~23%), 미국은 IAP 73% / 웹스토어 14% / 광고 13%; IAP-우선 하이브리드 상위작이 IAA-우선 상위작의 ~4배 매출 [7][49]. Block Blast는 배너+짧은 전면+세션당 1회 보상형이라는 가벼운 광고 로드로 2026년 1–5월 ~$127M [7]. 하이퍼캐주얼은 UA 공급원이기도 하다: 캐주얼·퍼즐 게임 신규 유저의 29%가 하이퍼캐주얼 게임 광고에서 유입(Liftoff/Singular, 2024-02~2025-02) [27].
- **정렬/잼 퍼즐의 레벨 생성(역순 생성·솔버)** — Ball/Water Sort는 일반적으로 NP-완전이며 최단 해 찾기도 NP-완전(Ito et al., FUN 2022) [38] → 상용 게임은 "해결 가능한 상태에서 역으로 섞기" 또는 "랜덤 생성 → 솔버 검증 → 불합격 폐기" 파이프라인을 쓴다. 오픈소스 예: wricardo/colorsortgame은 `cmd/gen`으로 생성 후 `solvable`(BFS 완전탐색)로 검증해야 levels.json에 추가 [41]. 스크루 퍼즐은 정적 레이어 구조라 "어떤 나사부터 빼느냐"의 choke point를 의도적으로 심고, 정보 은닉(Screw Jam은 반투명 유리, Screwdom은 80% 이상 숨김)으로 난이도를 조절 [11]. King은 CNN 모방학습 봇으로 신규 레벨 난이도를 예측(MCTS보다 상관 높고 연산 적음) [34].
- **머지 보드 경제** — Gossip Harbor 분석 [9]: 에너지(제너레이터 탭당 소모)가 핵심 과금 레버, 리필 가격은 사용할수록 상승; 레벨 15 아이템 하나에 레벨 1 아이템 ~16,000개 필요(드롭 100% 가정); 10% 드롭 체인은 레벨 7 하나에 600+ 에너지; 보드 공간의 ~15%를 주문용 제너레이터가 점유해 공간 압박; 코인은 용도가 스토리/리노베이션 하나뿐, 젬은 다용도; 월 시즌(~21일) + 일일·다일 이벤트 겹치기. 이 공식이 Microfun 3개 머지 게임의 2025년 165% 매출 성장을 견인(Sensor Tower, 2차 보도) → 수치 `미검증`.
- **Roblox 캐주얼의 거래·희귀도·"훔치기" 소셜 훅** — Adopt Me: 펫 희귀도 + 유저 간 거래가 경제의 중심, 사기 대응으로 거래 라이선스(2020-11) [22]. Steal a Brainrot: 패시브 수입 생성기(Brainrot)를 타인이 훔칠 수 있고 쉴드/트랩으로 방어 → 세션 중 항상 긴장, 리버스(리셋)로 영구 배율 [21]. Grow a Garden: 오프라인 성장(복귀 동기) + 주간 한정 아이템(온라인 강제) + 펫 루트박스 + Robux로 타인 작물 훔치기, 트레이드 없음·선물만 [18][19]. 세 게임 모두 Do Big Studios가 지분·운영에 관여하며 "과도한 과금" 비판을 받음 [18].

## 4. 수치 (data)

| 게임 | 항목 | 값 | source | URL | 확인일 |
|---|---|---|---|---|---|
| Royal Match | 연매출 2024 / 2025 (Sensor Tower 추정) | $1.46B / $1.37B (첫 연간 감소) | inferred (서드파티 추정, Gamigion 인용) | [1] | 2026-10-17 |
| Royal Match | 누적 총매출 / 순IAP / DL (AppMagic, 2025-05) | $6B / $3.6B / 351M, RpD $15.6 | inferred | [2] | 2026-10-17 |
| Block Blast! | 2025 전 세계 DL (AppMagic, 1/1–12/22) | 356.2M (전체 1위; 2위 Roblox 286M) | measured(서드파티 추정) | [5] | 2026-10-17 |
| Block Blast! | 2026-01~05 광고매출 (Sensor Tower) | ~$127M | inferred | [7] | 2026-10-17 |
| Gossip Harbor | 누적 IAP / DL (AppMagic, 2025-12) | $723M+ / 92.4M, 2025-10 월 IAP ~$62M | inferred | [8] | 2026-10-17 |
| Monopoly GO! | 누적 IAP $6B 도달 소요일 (Sensor Tower) | 1,275일 (Royal Match 1,868일) | inferred | [15] | 2026-10-17 |
| Grow a Garden | 동접 최고 | ~22.3M (2025-08-23) | wiki (트래커 기반) | [18] | 2026-10-17 |
| Steal a Brainrot | 동접 최고 | 25.4M (2025-10, 역대 최다) | wiki + PG.biz | [20][21] | 2026-10-17 |
| Sort / Screw / Block 하위장르 | 2025 IAP 매출 (Sensor Tower, Naavik 분석) | ~$280M / $206M+ / ~$183M; 합산 ~$0.7B, +222% YoY | inferred | [10] | 2026-10-17 |
| 모바일 전체 (GameAnalytics, 2024 데이터, 11,600앱) | D1 상위 25% / D7 중앙값 / D7 상위 25% | 26.5–27.7% / 3.4–3.9% / 7–8% (클래식 리텐션; 퍼즐·보드·카드가 중장기 리텐션 최상위) | measured | [26] | 2026-10-17 |
| 캐주얼 (Liftoff/Singular, 2024-02~2025-02) | CTR / D30 ROAS / 하이퍼캐주얼 유입 비중 | CTR Android 9.4%·iOS 8.8%; D30 ROAS iOS 47%·Android 15%; 캐주얼·퍼즐 신규유저의 29%가 하이퍼캐주얼 광고 유입 | measured | [27] | 2026-10-17 |
| 하이퍼캐주얼 CPI | 최신 공개 벤치마크 | 중앙값 iOS $0.42 / Android $0.20 (Tenjin×GameAnalytics, **2022 Q4** — 이후 공개 벤치마크 없음) | measured(구데이터) | [45] | 2026-10-17 |
| Poki (웹) | 2025 플레이어 / 플레이 수 | 625M / 11.1B | 공식 블로그 | [25] | 2026-10-17 |

주의: CPI 2025 수치로 떠도는 "캐주얼 iOS $1.41 / Android $0.14"는 Liftoff 원문 페이지에서 확인되지 않음 → `미검증`. 하이브리드캐주얼 전용 D1/D7 공개 벤치마크도 없음(Supersonic 블로그의 40%/15–20%는 자사 기준).

## 5. 원전·오픈소스 (라이선스 포함)

| 자료 | 종류 | 라이선스 | 다루는 것 | 확인일 |
|---|---|---|---|---|
| GDC Europe 2016 "How King Uses AI in Candy Crush" (Andelkovic, Freyr) [32] | GDC Vault 강연 | 무료 공개(free content 태그) | AI(MCTS·NEAT 등)로 신규 레벨 회귀 테스트·난이도 평가 | 2026-10-17 |
| GDC Summer 2020 "Blockers: Analyzing Difficulty Drivers in Candy Crush Games" (Lucien Yen-Chu Chen, King) [33] | GDC 강연(공지 페이지) | Vault 접근권 `미검증` | 블로커 16종(nature/destruction)의 공통 스탯 언어로 난이도 드라이버 분석 | 2026-10-17 |
| GDC 2024 King 세션 — mobilegamer.biz 요약 [35] | 강연 요약 기사 | 기사 저작권 | "좋은 레벨" 지표(포기까지 시간, 퍼즐다움), 레벨 65 A/B, 최악 100레벨 상시 재작업 | 2026-10-17 |
| Gudmundsson et al., "Human-Like Playtesting with Deep Learning" (IEEE CIG 2018, King AI R&D) [34] | 논문 | IEEE 저작권(PDF 미러 공개) | CNN 모방학습 봇으로 레벨 난이도 예측, MCTS 대비 상관↑·연산↓ | 2026-10-17 |
| Larche, "Examining the Physiological and Subjective Effects of Near-misses in Smartphone Games" (U. Waterloo, 2017) [36] | 석사논문 | 대학 리포지토리 공개 | Candy Crush near-miss의 생리·주관 반응 | 2026-10-17 |
| Eckmann, Schiesser, von Mammen, "The Royal Crush: Analysis of Match-3 Mechanics" (IEEE CoG 2024) + Match3Toolkit [37] | 논문 + Godot 툴킷 | 레포에 라이선스 파일 **없음**(미표기) | 스왑 vs 콜랩스 조작의 난이도 차이, 스페셜 피스 수와 난이도 | 2026-10-17 |
| Ito et al., "Sorting Balls and Water: Equivalence and Computational Complexity" (FUN 2022, arXiv:2202.09495) [38] | 논문 | arXiv/LIPIcs 오픈액세스 | 볼/워터 정렬 퍼즐 NP-완전성, 빈 통 개수 상하한 | 2026-10-17 |
| LibraStack/Match3-SDK [39] | GitHub (Unity, C#) | MIT (API 확인) | 매치3 SDK, 561★, 마지막 push 2024-06 | 2026-10-17 |
| ninetailsrabbit/match3-board [40] | GitHub (Godot 4.7) | MIT | 보드·규칙·이벤트 기반 매치3 툴킷, 61★ | 2026-10-17 |
| wricardo/colorsortgame [41] | GitHub (Go) | MIT | 워터소트 엔진 + `cmd/gen` 생성기 + BFS 솔버 검증 | 2026-10-17 |
| gabrielecirulli/2048 [42] | GitHub (JS) | MIT (API 확인) | 타일 머지의 원형, 13.4k★ | 2026-10-17 |
| daltonbr/Match3 (Unity) | GitHub | 라이선스 **미표기**(API에 license 없음) | 매치3 샘플, 469★ — 상용 참고 주의 | 2026-10-17 |
| Deconstructor of Fun "The Screw Puzzle Gold Rush" (2026-02) [11] | 블로그 분석 | 저작권 | 스크루 퍼즐 레벨 구조·정보 은닉·과금 지점 | 2026-10-17 |
| Deconstructor of Fun "Finding Genre Success: the Case of Gossip Harbor" (2024-08) [9] | 블로그 분석 | 저작권 | 머지 보드 경제 수치 분해 | 2026-10-17 |
| Naavik "How Niche Subgenres are Reshaping the Mobile Puzzle Market" (2026-02) [10] | 리서치 다이제스트 | 저작권 | Sort/Screw/Block 2025 매출·점유 | 2026-10-17 |
| Homa Academy "Hybridcasual takes the stage" (2023-07) + Sensor Tower×Homa Hybridcasual Playbook [29] | 퍼블리셔 블로그 | 저작권 | 하이브리드캐주얼 정의, 광고 ~50% 비중 | 2026-10-17 |
| Supersonic Learn 블로그·케이스스터디 [30][31] | 퍼블리셔 블로그 | 저작권(마케팅 자료) | 메타 레이어·동기 설계, Backyard Master·Merge Miners 사례 | 2026-10-17 |
| Roblox DevForum: "How To Make ROBLOX 'Grow a Garden' Game — Tutorial Series", "Reproducing Grow A Garden Offline System" [43] | 커뮤니티 튜토리얼/Q&A | 포럼 게시물 | 성장 시스템·오프라인 성장(타임스탬프 계산)·데이터 저장·펫/알 재현. 원 개발자 글은 아님 | 2026-10-17 |
| GamesBeat Jandel 인터뷰 (2025-09) [19] | 개발자 인터뷰 | 저작권 | 인수 경위, CCU 추이, 오프라인 성장·주간 업데이트 결정 | 2026-10-17 |

## 6. 함정 (흔한 실패)

- **광고 소재와 실제 게임의 괴리** — "Pull the pin" 류 가짜 게임플레이 광고는 설치는 늘려도 D1을 깎는다. Last War는 아예 광고 속 미니게임을 본편에 넣고 "가짜 광고의 게임을 진짜로 만들었다"는 캠페인으로 돌아섰다 [17]. 광고가 약속한 루프가 첫 세션 안에 나오지 않으면 UA 비용만 태운다.
- **단기 전환을 위해 난이도를 올리기** — King의 레벨 65 A/B: 어렵게 하면 당장 전환↑, 쉽게 하면 장기 리텐션↑·이후 지출↑ [35]. "어려움"과 "재미없음"을 같은 지표로 보면 안 되며, 포기까지 시간과 퍼즐다움을 따로 재야 한다.
- **정렬/잼 퍼즐에서 해결 가능성 미검증 레벨 출시** — Water/Ball Sort는 NP-완전이라 랜덤 생성 레벨은 풀 수 없을 수 있다 [38]. 생성 → 솔버 검증 → 폐기 파이프라인이 없으면 "운빨 레벨"로 리뷰가 무너진다(colorsortgame도 생성물을 반드시 solvable 체크 [41]).
- **하이퍼캐주얼 + 메타만 붙이면 하이브리드라는 착각** — DoF/Supersonic이 공통으로 지적: 리텐션은 출시 후가 아니라 코어 단계에서 확보해야 하고, 깊이 ≠ 복잡도. Backyard Master는 메타 전에 코어 복잡도부터 올렸다 [31]. 하이브리드는 D1보다 D7/D14가 판단 기준 [30].
- **광고 로드 과다로 세션 파괴** — Block Blast는 배너+짧은 전면+세션당 보상형 1회라는 가벼운 로드로도 월 $20M+ 광고매출(추정) [6][7]. 매 레벨 전면광고(Screwdom 방식 [11])는 IAP 강한 타이틀에서만 버틴다. 리바이브 보상형을 "손실 회복"에 붙이는 것이 가장 자연스러운 자리다.
- **머지 보드 공간·에너지 밸런스 붕괴** — 주문용 제너레이터가 보드의 15%를 먹고, 희귀 체인은 600+ 에너지를 요구한다 [9]. 보드 확장을 너무 비싸게 두면 이탈, 에너지를 너무 싸게 주면 과금 레버가 사라진다. 코인 용도를 하나(스토리)로 묶어 "다음 할 일"을 항상 보여주는 것이 Gossip Harbor식 해법.
- **Roblox 거래 경제의 사기·인플레이션** — Adopt Me는 trust trade 사기 때문에 거래 라이선스를 도입해야 했다 [22]. Grow a Garden은 아예 트레이드를 두지 않고 선물만 허용 [19] — 거래 시스템은 자동으로 "희귀도 경제"와 사기 대응 비용을 함께 가져온다.
- **동접 기록 = 지속 가능성이 아니다** — Steal a Brainrot은 25.4M 피크 후 수개월 만에 ~215K(피크 대비 -99%, 트래커 수치, `미검증`)로 떨어졌다는 보도. 밈·"훔치기" 훅은 폭발적이지만 주간 업데이트 체력이 없으면 급락한다.

## 7. 우리 게임 적용
[`our_games/README.md`](../../../our_games/README.md) 기준. 우리 게임의 절반 이상이 이 장르다.
- **A 등불 항구 (Lantern Harbor)** · **로직 연구 #19 Bus Traffic Fever** → 방향 해제(잼) 퍼즐. 레벨은 생성 → 솔버 검증 → 폐기 파이프라인이 필수(§3 정렬/잼, §6 셋째). 상세 [`puzzle_levels.md`](puzzle_levels.md) ★ 등불 항구 절.
- **A1 오행 정리** → 정렬 퍼즐(Hexa Sort · Screw 계열). NP-완전이므로 역순 생성. 하위장르 2025 매출(§4)이 선반 크기.
- **C 픽셀 피크닉 · 캐주얼 구상 G~K (#14~#19)** → 하이브리드 캐주얼. 코어 리텐션 먼저, 메타는 뒤(§6 넷째).
- **Hole/Money Sort/Pixel Flow/Food Hunt 로직 연구 (#15~#18)** → 2025년 "hole" 클론 215개 출시(puzzle_levels §4)가 경쟁 밀도의 근거.
- Roblox 캐주얼(Grow a Garden · Steal a Brainrot)은 우리 프로젝트에 없다. 오프라인 성장 + 주간 한정 + 훔치기 훅은 [`../rpg/`](../rpg/README.md) 시뮬레이터 항목과 겹친다.

## 채움 상태
| 절 | 상태 | 마지막 갱신 |
|---|---|---|
| 2 대표작 | ● 15행 (Royal Match 연매출 · Bus Jam 개별 수치 미검증) | 2026-10-17 |
| 3 루프 | ● | 2026-10-17 |
| 4 수치 | ● 13행 (CPI 벤치마크는 2022 Q4가 최신 공개치) | 2026-10-17 |
| 5 원전 | ● 19행 (머지-2 오픈소스는 못 찾음, 2048이 원형) | 2026-10-17 |
| 6 함정 | ● | 2026-10-17 |
| 7 우리 적용 | ● | 2026-10-17 |

## 출처

1. https://www.gamigion.com/?p=32992 (Royal Match 연매출, Sensor Tower 추정; 페이지 직접 로드 실패, 검색 요약으로 확인)
2. https://wnhub.io/news/other/item-47827 (AppMagic, 2025-05-20)
3. https://mobilegamer.biz/data-digest-royal-match-hits-6bn-aprils-top-games-midcore-insights-plus-funding-and-financial-news/
4. https://sensortower.com/blog/royal-match-surpasses-candy-crush-saga-in-revenue-and-downloads-for-the
5. https://www.pocketgamer.biz/the-most-downloaded-mobile-games-of-2025/
6. https://felixbraberg.substack.com/p/the-top-6-android-games-making-a
7. https://www.deconstructoroffun.com/blog/5-numbers-hiding-in-plain-sight-sensor-towers-ad-monetization-report
8. https://mobilegamer.biz/data-digest-fallout-shelter-where-winds-meet-gossip-harbor-2026-predictions-more/
9. https://www.deconstructoroffun.com/blog/2024/8/19/finding-genre-success-the-case-of-gossip-harbor
10. https://naavik.co/digest/how-niche-subgenres-are-reshaping-the-mobile-puzzle-market/
11. https://www.deconstructoroffun.com/blog/the-screw-puzzle-gold-rush
12. https://mobilegamer.biz/hexa-sort-creators-cheer-games-raise-4-5m/
13. https://www.forbesargentina.com/negocios/crearon-juego-ya-facturo-us-47-millones-levantaron-us-45-millones-reinventar-puzzles-mobile-n87499/amp
14. https://www.scopely.com/en/news/sensor-tower-scopelys-monopoly-go-hit-6-billion-revenue-milestone-in-2025-in-record-time
15. https://www.pocketgamer.biz/scopelys-monopoly-go-fastest-mobile-game-to-hit-6-billion/
16. https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-september-2025
17. https://en.wikipedia.org/wiki/Last_War:_Survival_Game
18. https://en.wikipedia.org/wiki/Grow_a_Garden
19. https://gamesbeat.com/janzen-madsen-interview/
20. https://www.pocketgamer.biz/robloxs-steal-a-brainrot-becomes-first-game-to-surpass-25m-concurrent-players/
21. https://en.wikipedia.org/wiki/Steal_a_Brainrot
22. https://en.wikipedia.org/wiki/Adopt_Me!
23. https://rowatcher.com/news/dress-to-impress-how-a-teen-developer-s-fashion-game-hit-9-7-billion-visits
24. https://www.pockettactics.com/blade-ball/one-billion-visits
25. https://poki.com/blog/2025-at-poki-a-year-in-review
26. https://gamedevreports.substack.com/p/gameanalytics-mobile-gaming-benchmarks
27. https://gamedevreports.substack.com/p/liftoff-and-singular-casual-games
28. https://sensortower-china.com/blog/state-of-mobile-gaming-2025
29. https://www.homagames.com/blog/hybridcasual-takes-the-stage
30. https://supersonic.com/learn/blog/player-motivations-boost-retention/
31. https://supersonic.com/learn/case-studies/supersonic-and-futurebright-partner-to-create-hybrid-winner-backyard-master/
32. https://www.gdcvault.com/play/1023858/How-King-Uses-AI-in
33. https://gdconf.com/news/come-gdc-summer-and-learn-kings-new-method-balancing-match-3-game-difficulty
34. https://www.gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf
35. https://mobilegamer.biz/how-king-defines-a-good-candy-crush-saga-level-and-why-it-constantly-prunes-the-bad-ones/
36. https://uwspace.uwaterloo.ca/handle/10012/12522
37. https://downloads.hci.informatik.uni-wuerzburg.de/2024-CoG-RoyalCrush.pdf / https://github.com/DanielEckmann/Match3Toolkit
38. https://arxiv.org/abs/2202.09495
39. https://github.com/LibraStack/Match3-SDK
40. https://github.com/ninetailsrabbit/match3-board
41. https://github.com/wricardo/colorsortgame
42. https://github.com/gabrielecirulli/2048
43. https://devforum.roblox.com/t/how-to-make-roblox-grow-a-garden-game-tutorial-series/3769116 / https://devforum.roblox.com/t/reproducing-grow-a-garden-offline-system/3912089
44. https://costcenter.net/post/sort-jam-competitor-analysis (약한 출처)
45. https://gamedevreports.substack.com/p/tenjin-and-gameanalytics-hypercasual-6e4
46. https://en.wikipedia.org/wiki/Royal_Match (부스터·목숨 구조)
47. https://wnhub.io/news/analytics/item-2393 / Playrix Homescapes 2021 리밸런스는 검색 요약 기반 → 세부 수치 `미검증`
48. https://www.pocketgamer.biz/interview/77247/corentin-selz-voodoo-from-hypercasual-to-hybrid-casual/
49. https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report
