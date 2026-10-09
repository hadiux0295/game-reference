# Godot·앱 게임 참고 자료: 걷는 성 · Hearthkeep · snake_survivor · 점집 경영 시뮬

> 대상: [`our_games`](../our_games/README.md)의 **B 걷는 성**, **Hearthkeep**(Godot), **snake_survivor**(Godot), **망한 점집을 물려받았다 / A2 밤의 점집**
> 조사일: **2026-10-09**. 확인하지 못한 항목은 **미검증**으로 표시했습니다. 퍼즐 생성과 난이도 일반론은 [`puzzle_levels.md`](puzzle_levels.md)를 보세요.

---

## 걷는 성 (Wandering Keep): 층 순서 퍼즐 TD

**시사점**
1. **층 순서를 전수 평가합니다.** 5층이면 순열이 5! = 120개뿐입니다. 웨이브마다 120개 순서를 모두 시뮬레이션하고, "이기는 순서의 수"(적을수록 어려움)와 "유일 정답 여부"를 난이도 다이얼로 씁니다. ([Fling! 전수 탐색](https://www.gamedeveloper.com/design/the-saturday-paper---exhausting))
2. **Monster Train의 세로 레인 문법이 가장 가까운 선례입니다.** 3층과 화로로 구성되고, 적이 아래층부터 올라오며, 유닛을 어느 층에 둘지가 퍼즐입니다. MT2는 층 단위 버프(Room Card)를 추가했는데, 우리도 이것을 **두 번째 레이어로 아껴서** 쓰세요. ([Monster Train](https://en.wikipedia.org/wiki/Monster_Train), [리뷰](https://bossrush.net/2023/03/game-review-race-through-rings-of-hell-in-monster-train/), [MT2 발표](https://www.cosmocover.com/newsroom/monster-train-2-announced-for-2025-launch-on-pc-and-consoles-play-the-debut-demo-today-for-a-heavenly-successor-to-the-acclaimed-million-selling-hit))
3. **난이도 스파이크는 한 곳만 바꿔서 만듭니다.** 적 특성 하나나 층 카운터 하나만 바꾸고 120개 순서를 다시 평가해서, 정답이 1~2개만 남는 레벨을 찾습니다. ([Sturtevant AIIDE 2020](https://ojs.aaai.org/index.php/AIIDE/article/view/7421))
4. **적과 타워는 데이터로 정의합니다** ([`../platforms/godot/architecture.md`](../platforms/godot/architecture.md) §4의 Resource 패턴).
5. **아트 전에 도형으로 1~2일 단위 프로토타입을 만듭니다.** Thronefall도 이렇게 약 2개월 동안 프로토타이핑했습니다. ([OwlCast/Thronefall](https://owlcast.substack.com/p/inside-the-code-how-two-developers))

> "층 순서" TD와 정확히 같은 게임은 찾지 못했습니다. 차별점이 될 수 있어요.

## Hearthkeep: 낮엔 마을, 밤엔 방어 (Kingdom Two Crowns · Thronefall 계열)

**시사점**
1. **눈덩이 효과를 보장 수입으로 상쇄합니다.** Thronefall 개발자는 이런 전략 게임이 "아주 아주 눈덩이처럼" 커진다고 했습니다. 그래서 밤의 적이 골드를 떨어뜨리게 해서 약한 경제도 회복할 수 있게 하고, 밸런스도 예측 가능하게 만들었습니다. ([OwlCast](https://owlcast.substack.com/p/inside-the-code-how-two-developers))
2. **단일 재화와 간접 조작**(Kingdom의 동전 던지기)을 씁니다. 밤 웨이브는 점점 커지게 합니다. **오프라인 진행은 낮 경제 수익으로만 제한**해서 밤이 시시해지지 않게 하세요 (우리 제안).
3. **길찾기와 지역 회피를 일찍 해결하세요.** Thronefall에서 가장 어려운 기술 문제였다고 합니다. Godot에서는 NavigationServer의 avoidance를 씁니다.
4. **판매 포인트는 "짧고 완결된 세션"입니다.** Thronefall은 "건전하고 깊지만 시간은 덜 드는" 게임으로 100만 장 이상 팔렸습니다. ([Kotaku](https://kotaku.com/thronefall-islanders-tower-defense-strategy-steam-pc-1850701534))
5. **Dome Keeper**(Godot 제작, 100만 명 이상)가 "캐기·지키기" 페이즈 루프가 Godot으로 상업 출시된 근거입니다. 피칭할 때 레퍼런스로 쓰세요. ([Dome Keeper](https://en.wikipedia.org/wiki/Dome_Keeper))

**Godot 코드 참고**

| 저장소 | 라이선스 | 상태 | 쓸모 |
|---|---|---|---|
| [quiver-dev/tower-defense-godot4](https://github.com/quiver-dev/tower-defense-godot4) | **MIT** (에셋 라이선스는 별도) | 2026-08 | 배치, 타워, 투사체, 적 타입, 길찾기 |
| [ape1121/Godot-4-Tower-Defense-Template](https://github.com/ape1121/Godot-4-Tower-Defense-Template) | **MIT** | 2024-08 | 스타터 템플릿 |
| [Praytic/youtd2](https://github.com/Praytic/youtd2) | 코드 **MIT** / 에셋 **CC-BY-NC** | 활발 | 대형 Godot TD. 데이터 주도 적 설계. **에셋 상업 사용 불가** |
| [lfeq/Kingdom](https://github.com/lfeq/Kingdom) | **MIT** | 소형 | 라이선스가 있는 유일한 Kingdom류 Godot 저장소 |
| [gdquest-demos/godot-2d-tower-defense](https://github.com/gdquest-demos/godot-2d-tower-defense) | MIT | 2021 (Godot 3 추정) | 구조만 참고 |
| Seeds-of-Success, last-chicken-defense | 라이선스 없음 | — | 보기만 가능 |

## snake_survivor: 스네이크 × 서바이버 (동료 열차 + 원정 메타)

**시사점**
1. **진화 규칙을 열차에 대응시킵니다.** 최대 레벨 동료 칸 + 대응 유물 + 상자 = 진화 칸. 칸과 유물은 **최대 6개**로 둬서 선택에 의미가 생기게 합니다. (Vampire Survivors 규칙, 커뮤니티 가이드 기준이라 미검증: [rogueranker](https://rogueranker.com/vampire-survivors-passive-items/))
2. **아슬아슬한 실패를 설계합니다.** VS는 30분 목표를 둬서 모든 실패한 판이 "거의 다 왔다"고 느끼게 합니다. 런 사이에 유지되는 메타 골드와 무료 재분배를 함께 둡니다. ([The Conversation](https://theconversation.com/vampire-survivors-how-developers-used-gambling-psychology-to-create-a-bafta-winning-game-203613))
3. **상자와 레벨업 연출에 공을 들입니다.** 사운드, 애니메이션, 타이밍이 핵심입니다. 개발자의 슬롯머신 업계 경험이 드러난 부분이에요. ([Mechanics of Magic](https://mechanicsofmagic.com/?p=31948))
4. **⚠️ 경쟁작이 있습니다.**
   - **SnekromancY**(2026-08, Steam)가 스네이크 × VS에 자동 사격 하수인 구조입니다.
   - Nimble Quest(2013)가 "줄 서서 자동 공격하는 영웅" 구조의 원조입니다.
   - 따라서 우리의 훅은 꼬리 자체가 아니라 **원정 메타와 칸 시너지**에 둬야 합니다. ([GamingOnLinux](https://gamingonlinux.com/2026/08/snekromancy-is-a-clever-reinvention-of-snake-with-a-survivor-like-tower-escape-style), [Nimble Quest](https://wikipedia.com/wiki/Nimble_Quest))
5. **웨이브 사이 상점**(Brotato, Godot 제작, 200만 장 이상)은 Godot에서 검증된 페이싱 장치입니다.

| 저장소 | 라이선스 | 상태 | 쓸모 |
|---|---|---|---|
| [brannotaylor/SurvivorsClone_Complete](https://github.com/brannotaylor/SurvivorsClone_Complete) | **CC0** | Godot 4 | 퍼블릭 도메인이라 **그대로 가져와도 안전** |
| [Mocas-12/no-survivor-game](https://github.com/Mocas-12/no-survivor-game) | **MIT** | 2026-10 활발 | XP 젬, 빌드 진화, 웹 빌드 |
| [Wadan3/shadow-survivors](https://github.com/Wadan3/shadow-survivors) | **MIT** | **Godot 4.7** | 같은 엔진 버전 |
| [coderKillo/FactorySurvivorsGame](https://github.com/coderKillo/FactorySurvivorsGame) | **MIT** | 2025-06 | 서바이버 × TD (원정 메타 참고) |
| [ape1121/Godot4-Multiplayer-Survivor-IO-Game](https://github.com/ape1121/Godot4-Multiplayer-Survivor-IO-Game) | **MIT** | 2024-08 | HTML5 내보내기, 성능 |
| [DarkRewar/SurvivorsStarterKit](https://github.com/DarkRewar/SurvivorsStarterKit) | MIT · **C#** | 2026-04 | 구조 참고 (우리는 GDScript) |

## 망한 점집을 물려받았다 / 밤의 점집 (앱, 프리미엄 iOS)

**시사점**
1. **손님마다 추리 퍼즐로 만듭니다.** 단서는 게임 속 참고서에 넣습니다 (Strange Horticulture의 백과사전 방식). 튜토리얼 대신 애니메이션으로 놓친 요소에 시선을 유도합니다. ([Deep dive: Strange Horticulture](https://www.gamedeveloper.com/design/deep-dive-strange-horticulture), [Bad Viking 인터뷰](https://www.gamedeveloper.com/design/strange-horticulture---bad-viking))
2. **규칙은 Papers, Please식으로 점진적으로 늘리고, 재미없는 검사는 과감히 뺍니다.** Lucas Pope는 수하물 검사, UV 봉인, 총격전을 잘라냈습니다. ([Kill Screen](https://www.killscreen.com/peek-behind-scenes-papers-please-reveals-baggage-search-and-gun-fights/))
3. **해석에 플레이어의 저자성을 줍니다.** The Cosmic Wheel Sisterhood는 플레이어가 타로 덱을 직접 만들게 해서, 분기가 폭발하지 않으면서도 해석을 플레이어가 만들게 했습니다. ([Wikipedia](https://en.wikipedia.org/wiki/The_Cosmic_Wheel_Sisterhood), [Pocket Tactics](https://www.pockettactics.com/cosmic-wheel-sisterhood/tarot-in-games))
4. **처방 퍼즐도 솔버로 검증합니다.** 모든 손님의 오행 막대에 정답 처방(보충·억제)이 **최소 1개** 있는지 확인하고, 오답 수를 측정해 난이도로 씁니다. 그레이박스 규칙(초록 띠 3~7, 보충 +2 / 생하는 기운 +1, 억제 −2 / −1)이면 처방 11개를 전수 계산할 수 있습니다.
5. **프리미엄 iOS이므로 하이브리드 캐주얼 수익화 데이터는 적용하지 않습니다.** 프리미엄 경영 시뮬 시장 데이터는 찾지 못했습니다(공백).
6. 사주 계산이 필요하면 [`anomaly_shop_roblox.md`](anomaly_shop_roblox.md) §4의 만세력 라이브러리를 참고하세요. ⚠️ `korean_lunar_calendar` 계열은 월주를 음력 기준으로 계산하므로 사용하면 안 됩니다.

---

### 공백 (찾지 못한 것)
- Kingdom과 Monster Train의 GDC 강연
- "층 순서" TD 선례
- VS 공식 위키 (접속 불가로 진화 규칙 미검증)
- 프리미엄 경영 시뮬 시장 데이터
