# TD 진행 수치: 인게임 업그레이드 · 수입 · 메타 진행

대상: **B 걷는 성** 6단계(레벨링) · 7단계(경제·저장). 수집 R0(공개 위키·가이드만), 확인일 **2026-10-15**. 게임 파일·도구 다운로드 없음.
`source:` 표기는 [`README.md`](README.md) 규칙을 따릅니다. 출처 번호는 맨 아래 목록입니다.
교차 확인: Thronefall 레벨 XP 표를 원문 페이지에서 다시 열어 일치 확인(2026-10-15). Fandom 페이지는 HTTP 402라 위키 `api.php`로 읽었습니다.

## 1. 인게임 업그레이드 비용

### Bloons TD 6 (Medium, 단계별 비용 $)
| 타워 · 경로 | 기본 | T1 | T2 | T3 | T4 | T5 | T3까지 합 ÷ 기본 | source |
|---|---|---|---|---|---|---|---|---|
| Dart · 1번 | 200 | 140 | 200 | 320 | 1,800 | 15,000 | 4.3× | wiki [B1] |
| Tack · 2번 | 260 | 100 | 225 | 550 | 2,700 | 15,000 | 4.4× | wiki [B2] |
| Bomb · 3번 | 375 | 200 | 300 | 700 | 2,500 | 30,000 | 4.2× | wiki [B3] |
| Ninja · 1번 | 400 | 350 | 350 | 900 | 2,750 | 35,000 | 5.0× | wiki [B4] |
| 4종 12경로 중앙값 (단계 ÷ 기본) | 1 | 0.60 | 0.97 | 2.28 | 10.3 | 84 | ≈4.9× | inferred |

- 난이도 보정: Easy ≈ −15%, Hard ≈ +8%, Impoppable ≈ +20% (Medium 대비). source: wiki [B1][B6]

### Kingdom Rush 1 (단계별 비용 gold)
| 계열 | L1 | L2 | L3 | L4 전직 (A / B) | L3까지 합 ÷ L1 | L4까지 합 ÷ L1 | source |
|---|---|---|---|---|---|---|---|
| 궁수 | 70 | 110 | 160 | 230 / 230 | 4.9× | 8.1× | wiki [K1–K5] |
| 병영 | 70 | 110 | 160 | 230 / 230 | 4.9× | 8.1× | wiki [K6–K10] |
| 마법사 | 100 | 160 | 240 | 300 / 300 | 5.0× | 8.0× | wiki [K11–K15] |
| 포병 | 125 | 220 | 320 | 400 / 375 | 5.3× | 8.5× | wiki [K16–K20] |

- L4 스킬은 따로 구매 (예: 레인저 독 250/250/250). source: wiki [K2][K19]

### Thronefall (건설 · 업그레이드 gold)
| 건물 | 건설 | Lv2 | Lv3 | 효과 | source |
|---|---|---|---|---|---|
| 집 | 2 | 2 | — | 밤마다 1 → 2 gold | wiki [T1] |
| 방앗간 | 3 | 4 | 6 | 밤마다 1 → 2 → 6 gold, 밭 해금 | wiki [T3] |
| 밭 (방앗간 필요) | 1 | — | — | 밤마다 1 gold | wiki [T2] |
| 어항 | 3 | 7 | — | 밤마다 배 +1 (최대 5), 배당 1 → 2 gold | wiki [T4] |
| 금광 | 5 | — | — | 6 gold부터 밤마다 −1 (다른 가이드는 8부터) | wiki [T5] · 미검증 [T16] |
| 성 중심 | 3 | 7 | 20 | 기본 수입 미검증 | wiki [T6] |
| 탑 | 3 | 5 | 15 | HP 100/250, Lv3에서 특성 선택 | wiki [T7] |
| 병영 · 궁술장 | 4 | 8 | 16 | 유닛 4 / 8 / 12 | wiki [T8][T9] |
| 영웅 숙소 | 5 | 9 | 18 | 영웅 ×1 / ×2 / ×4 | wiki [T10] |
| 대장간 | 4 | 9 | 16 | 연구 선택 1 / 2 / 3 | wiki [T11] |

- 맵당 밤 수: 8 · 12 · 12 · 13 · 13 · 13. source: wiki [T13–T15]
- 밤을 버틴 건물만 다음 날 수입을 냄. source: wiki [T16]
- 맵 시작 gold: 미검증 · 적 처치 gold: 밤에 적이 gold를 드롭함(적 1마리당 액수 미검증). source: Steam 개발자 글 https://steamcommunity.com/app/2239150/discussions/0/5971271658111960813/ · 1.7 패치노트(SteamDB, 2차 출처) https://steamdb.info/patchnotes/14977238/ (확인 2026-10-19)

## 2. 인게임 수입

| 게임 | 항목 | 값 | source |
|---|---|---|---|
| BTD6 | 시작 자금 | $650 | wiki [B7] |
| BTD6 | 라운드 종료 보너스 | $100 + 라운드 번호 | wiki [B5] |
| BTD6 | 누적 자금 (시작 포함) r10 / r20 / r30 / r40 | 2,443 / 4,868 / 8,283 / 17,506 | wiki [B5] + inferred 합산 |
| BTD6 | 라운드당 수입 r10 / r20 / r40 | 212 / 247 / 1,158 | inferred [B5] |
| KR1 | Pagras(11웨이브) 시작 300, 처치 수입 합 1,624 (초반 4웨이브 평균 78 → 후반 4웨이브 234) | — | wiki [K22] |
| KR1 | Southport(7웨이브) 시작 265 > 처치 수입 합 216 | — | wiki [K21] |

## 3. 메타 진행 (판과 판 사이)

### Tower Defense Simulator (Roblox)
| 항목 | 값 | source |
|---|---|---|
| 승리 보상 Easy(20웨이브) / Casual(25) / Intermediate(30, Lv5) / Molten(35, Lv15) / Fallen(40, Lv30) | 코인 300 / 450 / 600 / 950 / 1,350 · XP 50 / 90 / 120 / 185 / 250 | wiki [1–5] |
| 패배 시 보상 | 기본 ÷ (1 + (W/w − 1)^p), 완주 보너스는 클리어 때만. 코인 p = 1.3(Easy~Intermediate) · 2.4 · 3.5 | wiki [1–6] |
| 다음 레벨 XP | 45 + 3.5n (n ≤ 10) · 8n (11~40) · 260 + 1.5n (41~) | wiki [7] |
| 누적 XP | Lv15 1,162 · Lv30 3,922 · Lv50 10,045 · Lv100 28,708 | inferred [7] |
| 코인 상점 29종 | 100에서 35,000까지, 평균 약 ×1.2씩 (구간별로 평평함), 합 127,850. 상위는 레벨 조건도 있음 | wiki [8] · 비율 inferred |
| VIP 패스 | 300 R$ (+25% XP 등) | wiki [9] |
| 레벨 잠금 타워를 Robux로 판매 | 168~1,500 R$ — **우리 규칙상 금지 (P2W)** | wiki [9] |
| 출석 28일 | 코인 합 7,350 (Easy 약 5~6판) | wiki [11] |
| 일일 퀘스트 | 개당 코인 100~200 + XP 50~100 | wiki [12] |

### 기타 Roblox TD
| 게임 · 항목 | 값 | source |
|---|---|---|
| TDX 랭크 XP | r2 2,500 → r30 5,950(+100~200씩), 이후 약 ×1.025씩 (r100 40,002) | wiki [14] |
| TDX 상점 gold | 450 · 1,250 · 1,650 · 5,500 · 8,750 · 38,500 · 75,000 | wiki [15] |
| TTD 게임패스 | 코인 2배 99 · 행운 199 · 보관함 199 · VIP 299 · 샤이니 499 · 특성 699 R$ | wiki [17] |

### Battle Cats
| 항목 | 값 | source |
|---|---|---|
| 일꾼 고양이(지갑) | Lv1~8, 업그레이드 비용 = Lv1 비용 × 현재 레벨 (선형) | wiki [18][19] |
| 일꾼 고양이 Lv1 비용 · 레벨별 지갑 상한 | (일본편 보물 전부 최고 + 일꾼 효율·지갑 Lv20+10 기준) Lv1→2 비용 560 (×현재 레벨: 1,120 … 3,920) · 지갑 상한 Lv1 6,000 / 7,500 / 9,000 / 10,500 / 12,000 / 13,500 / 15,000 / MAX 16,500 (레벨당 +1,500); 지갑 업그레이드 1레벨당 시작 지갑 +100, 일꾼 레벨당 +50; 효율 업그레이드 1레벨당 레벨업 비용 +20 · 무강화 기본 Lv1 비용·기본 지갑 상한은 미검증 | game8 (공략 사이트) · wiki (Miraheze, Fandom) |
| 기본 고양이 XP Lv1→10 | 400, 700, 1,100, 1,600, 2,200, 2,900, 3,700, 4,600, 5,600 (합 22,800) | wiki [21] |
| 레어 고양이 XP Lv1→10 | 8,000 … 80,800 (합 340,800) | wiki [23] |
| Lv11 이후 | 10레벨 묶음마다 ×2(11~20), ×3(21~30), 이후 +0.5씩 | wiki [20] |

### Kingdom Rush 1 · Thronefall
| 게임 · 항목 | 값 | source |
|---|---|---|
| KR 별 | 남은 목숨 18~20 → 3개 / 6~17 → 2개 / 1~5 → 1개, 영웅·철인 도전 +1씩 (레벨당 최대 5) | wiki [25] |
| KR 업그레이드 트리 | 6계열 합 65개, 단계마다 1 → 3~4개 (선형), 환불 후 재분배 가능 | wiki [28] |
| Thronefall 레벨당 XP | 1,500(Lv1~8) · 2,000(9~13) · 2,500(14~25) · 3,000(26~54) · 54 이후 100,000 (트로피만) | wiki [29] · 원문 재확인 |
| Thronefall 해금 | 레벨마다 특성 1개 (54개). 무기·유닛은 레벨이 아니라 특정 맵 클리어로 해금 | wiki [29] |
| Thronefall 밤당 점수 | 생존 100 + 건물 보존 최대 250 + 시간 보너스 최대 250 + 남은 gold당 10, 난이도 배율 ×0.6~1.75 | wiki [31] |

## 4. 계산으로 얻은 비율 (모두 inferred)
| 사다리 | 단계 ÷ 기본 | 형태 |
|---|---|---|
| BTD6 T1~T3 | 0.6 / 1.0 / 2.3 | 지수, r ≈ 2.0 |
| BTD6 T4~T5 | 10 / 84 | 급격한 벽 (60~100라운드용) |
| KR L1~L4 | 1 / 1.57 / 2.29 / 3.29 | 거의 선형 (+40 / +50 / +70) |
| Thronefall 전투 건물 Lv1~3 | 1 / 1.7~2.3 / 3.6~6.7 | 약 ×2씩 |
| TDS 레벨 누적 XP | Lv40까지 레벨²에 비례, 이후 선형 | 다항 p ≈ 2 |
| Battle Cats 유닛 XP | 단계 차이가 고정폭으로 늘어남 | 레벨당 2차, 누적 3차 |
| Thronefall 레벨 XP | 1.5k → 3k로 계단 | 누적은 거의 선형 |

- **3단계 도달 총비용은 세 게임 모두 기본가의 약 4~8배** (BTD6 T3 ≈ 4.9×, KR L3 ≈ 5×, Thronefall ≈ 6~8×).
- 단계 가격을 수입으로 환산하면 Lv2 ≈ 1~1.5웨이브, Lv3 ≈ 2~3웨이브 (KR Pagras 1.4 / 2.0, BTD6 T2/T3 ≈ 1.5 / 3~5라운드).
- 시간 환산(가정: TDS Casual 20분, Thronefall 1판 20분): TDS 상점 전부 ≈ 67시간, TDX r100 ≈ 110시간, Thronefall 특성 54개 ≈ 8~15시간.

## 5. 걷는 성 적용 초안 (Sage 판단, 아직 미적용)
현재 설계: 판 안에서는 화폐 없이 행진마다 카드 1장(층 추가 또는 레벨업), 레벨당 DPS +50% · HP +40% (선형), 최대 Lv3 · 6층.

- **판 안: 카드를 그대로 둔다.** 12장으로 층 추가 3장 + 레벨업 9장이면 6층 × 2레벨(12칸)을 거의 채웁니다. 화폐를 넣어야 할 때만 위 사다리를 씁니다(합 ≈ 기본가 5배, 예 100 / 150 / 250).
- **메타: XP 트랙 하나 + 꾸미기 화폐 하나.** Thronefall처럼 레벨 XP를 계단식으로 완만하게 해 "전부 해금 ≈ 10~15시간"에 맞추고, 이후는 트로피 등급으로 둡니다. TDS·TDX의 60시간 이상 노가다 구조는 짧은 판 게임에 맞지 않습니다.
- **패배해도 일부 보상.** TDS 공식에 W = 12, p ≈ 1.3을 넣으면 6행진 도달 시 50%, 9행진 도달 시 약 80%. 완주 보너스는 클리어 때만 줍니다.
- **첫 30분에 해금 2~3개.** 첫 해금은 1판 보상 이하, 다섯 번째는 3~4판, 그 뒤는 ×1.2씩.
- **숙련도 별.** KR처럼 12행진 후 남은 성 HP로 별 3/2/1개 + 도전 조건 2개 → 새 콘텐츠 없이 재도전 이유가 생깁니다.
- **일일 보상은 하루 1판 보상 이하.** (TDS 28일 출석 합 ≈ Easy 5~6판)
- **판매는 시간·외형만.** VIP(+XP, TDS 300 R$급), 꾸미기 화폐 2배(TTD 99 R$급, 협동 로비에서 P2W로 읽히면 제외), 자동 진행 같은 편의, 스킨. 레벨 잠금 해제나 타워 판매는 하지 않습니다.

## 출처 (모두 2026-10-15 확인)
- **BTD6** [B1] bloonswiki.com/Dart_Monkey_(BTD6) · [B2] Tack_Shooter_(BTD6) · [B3] Bomb_Shooter_(BTD6) · [B4] Ninja_Monkey_(BTD6) · [B5] List_of_rounds_in_BTD6 · [B6] Medium · [B7] Cash
- **Kingdom Rush** kingdomrushtd.fandom.com/wiki/ — [K1] Archer_Tower · [K2] Rangers_Hideout · [K3] Marksmen_Tower · [K4] Sharpshooter_Tower · [K5] Musketeer_Garrison · [K6] Militia_Barracks · [K7] Footmen_Barracks · [K8] Knights_Barracks · [K9] Holy_Order · [K10] Barbarian_Mead_Hall · [K11] Mage_Tower · [K12] Adept_Tower · [K13] Wizard_Tower · [K14] Arcane_Wizard · [K15] Sorcerer_Mage · [K16] Dwarven_Bombard · [K17] Dwarven_Artillery · [K18] Dwarven_Howitzer · [K19] Big_Bertha · [K20] Tesla_x104 · [K21] Southport · [K22] Pagras — 별·업그레이드: kingdomrush.fandom.com/wiki/ [25] Star · [26] Campaign · [28] Upgrades · [27] steamcommunity.com/app/246420/discussions/0/2261314050777056345
- **Thronefall** [T1–T12] throne-fall.github.io/game-content/buildings/{house,field,mill,fishing-harbour,gold-mine,castle-center,tower,barracks,archery-range,heros-quarter,blacksmith,wall}.html · [T13–T15] …/maps/{neuland,durststein,uferwind,nordfels,frostsee,sturmklamm}.html · [T16] gamerant.com/thronefall-how-to-build-better-economy-get-more-gold/ · games.gg/thronefall/ · [29] game.wiki/thronefall/leveling · [30] en.namu.wiki/w/Thronefall · [31] game.wiki/thronefall/scoring
- **TDS** tds.fandom.com/wiki/ — [1] Easy_Mode · [2] Casual_Mode · [3] Intermediate_Mode · [4] Molten_Mode · [5] Fallen_Mode · [6] Hardcore_Mode · [7] Level · [8] Towers · [9] Gamepasses · [11] Daily_Rewards · [12] Quests
- **TDX** tdx.fandom.com/wiki/ — [14] Ranks · [15] Shotgunner 외 타워 페이지 · **TTD** [17] toilet-tower-defense-game.fandom.com/wiki/Gamepasses
- **Battle Cats** [18] battle-cats.fandom.com/wiki/Worker_Cat · [19] battlecats.miraheze.org/wiki/Worker_Cat · [20] battlecats.miraheze.org/wiki/Upgrade_Menu, /Level-up · [21] battle-cats.fandom.com/wiki/Cat_(Normal_Cat) · [23] Bishop_Cat_(Rare_Cat), Balrog_Cat_(Rare_Cat)
