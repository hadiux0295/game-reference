# Godot 4 라이브러리·애드온·오픈소스 게임 카탈로그

> 검증일: **2026-10-09**. 각 GitHub 페이지에서 라이선스, 아카이브 여부, 지원 버전을 확인했습니다.
> ★는 대략적인 수치입니다.

**상태 표기**
- ✅ 활발
- 🗄️ 아카이브
- ⚠️ 초기·불안정

**라이선스 주의**
- MIT·Apache는 자유롭게 사용 가능
- GPL은 코드를 가져오면 우리 게임도 GPL로 공개해야 하므로 **구조만 참고**
- 라이선스가 없으면 읽기만 가능

---

## 🧭 권장 스택 요약 (Godot 4.7 기준)

| 영역 | 선택 | 메모 |
|---|---|---|
| 엔진 | **Godot 4.7 stable** (4.7.1, 2026-07) | 4.8은 개발 스냅샷 단계 |
| 언어 | **GDScript** | 모바일에서 C#은 실험적이고, C#은 웹 내보내기가 불가능합니다 |
| 상태 머신 | 직접 구현(`patterns/StateMachine.gd`) → 복잡해지면 **godot-statecharts** 또는 **LimboAI** | |
| AI (행동트리) | **LimboAI**(BT + HSM, 비주얼 디버거) 또는 **Beehave**(순수 GDScript) | |
| 저장 | JSON / `store_var` (`patterns/SaveManager.gd`) | `.tres` 세이브는 금지. 필요하면 safe-resource-loader 사용 |
| 트윈·현지화 | 내장 `create_tween()`, `TranslationServer`(CSV/PO) | 애드온 불필요 |
| 카메라 | **Phantom Camera** | |
| 대화·튜토리얼 텍스트 | **Dialogue Manager** | |
| 광고 | AdMob 플러그인 **하나만** 선택 (poingstudios 또는 godot-sdk-integrations) | 둘을 섞지 마세요 |
| 결제 | Android **godot-google-play-billing**, iOS **godot-ios-plugins (InAppStore)** | StoreKit2 플러그인은 아직 불안정 |
| 랭킹·업적·클라우드 저장 | **godot-play-game-services** (Android) | |
| 백엔드 | **GodotFirebase** (Auth, Firestore, Functions) | Analytics, Crashlytics, FCM은 미포함 |
| 테스트 | **GUT** 또는 **gdUnit4** | |
| 큰 수(방치형) | break_infinity 방식 (`mantissa × 10^exp`) | Godot용 저장소는 미검증 |

---

## 1. 엔진·공식 자료

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [godotengine/godot](https://github.com/godotengine/godot) ~118k★ | MIT | ✅ 4.7 stable | 4.7의 모바일 관련 개선: 내장 **VirtualJoystick** 노드, Android 빌드 안정화, 스플래시 커스터마이즈 ([릴리스 노트](https://godotengine.org/releases/4.7/)) |
| [godotengine/godot-demo-projects](https://github.com/godotengine/godot-demo-projects) ~9.6k★ | MIT | ✅ | **`mobile/` 폴더**: android_iap, 멀티터치, 센서. 버전별 브랜치가 있음 |
| [godotengine/awesome-godot](https://github.com/godotengine/awesome-godot) ~10.9k★ | CC-BY-4.0 | ✅ | 공식 큐레이션 목록 (애드온, 게임) |
| [Godot 문서: 게임 저장](https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html) | | | JSON, `store_var` 가이드. ConfigFile은 설정 전용 |
| [Godot 문서: C#](https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/index.html) | | | 모바일 C#은 **실험적**, 웹 내보내기 불가 |

> **에셋 라이브러리 변화:** 새 [Godot Asset Store](https://store.godotengine.org/roadmap)가 기존 AssetLib을 대체하는 중입니다. 애드온의 최신 버전은 **GitHub 저장소를 기준**으로 확인하세요.

## 2. 게임 로직 애드온

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [limbonaut/limboai](https://github.com/limbonaut/limboai) ~3.0k★ | MIT | ✅ 1.8.x (4.7 대응) | **행동트리 + 계층형 상태머신**, 에디터와 비주얼 디버거. C++ GDExtension |
| [bitbrain/beehave](https://github.com/bitbrain/beehave) ~3.3k★ | MIT | ✅ 2.10+ (4.5+) | 순수 GDScript 행동트리 |
| [derkork/godot-statecharts](https://github.com/derkork/godot-statecharts) ~1.6k★ | MIT | ✅ | 스테이트차트(계층형·병렬 상태). 게임 흐름과 UI 흐름에 적합 |
| [nathanhoad/godot_dialogue_manager](https://github.com/nathanhoad/godot_dialogue_manager) ~3.9k★ | MIT | ✅ v4 (4.6+) | 스크립트형 분기 대화. 튜토리얼과 퀘스트 텍스트에 유용 |
| [dialogic-godot/dialogic](https://github.com/dialogic-godot/dialogic) ~6.0k★ | MIT | ✅ Dialogic 2 (4.5+), API 변경 경고 있음 | 비주얼노벨 스타일 대화 에디터 |
| [ramokz/phantom-camera](https://github.com/ramokz/phantom-camera) ~3.6k★ | MIT | ✅ (4.4+) | Cinemachine 스타일 2D/3D 카메라 |
| [AdamKormos/SaveMadeEasy](https://github.com/AdamKormos/SaveMadeEasy) ~220★ | MIT | ✅ | 간편 저장 + 암호화 |
| [derkork/godot-safe-resource-loader](https://github.com/derkork/godot-safe-resource-loader) ~210★ | MIT | ✅ | `.tres`를 안전하게 로드 (악성 스크립트 차단) |
| [sempitern0/match3-board](https://github.com/sempitern0/match3-board) ~61★ | MIT | ✅ (4.4) | **매치-3 보드 로직** 라이브러리 |

## 3. 모바일 수익화·플랫폼 연동

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [poingstudios/godot-admob-plugin](https://github.com/poingstudios/godot-admob-plugin) ~632★ | MIT | ✅ (4.5+) | AdMob (GDScript, C#) |
| [godot-sdk-integrations/godot-admob](https://github.com/godot-sdk-integrations/godot-admob) ~114★ | MIT | ✅ | AdMob 대안. Android와 iOS를 단일 API로 지원하고 미디에이션, UMP 동의, ATT 지원 |
| [godot-sdk-integrations/godot-google-play-billing](https://github.com/godot-sdk-integrations/godot-google-play-billing) ~264★ | MIT | ✅ (4.2+) | **Android 인앱결제** |
| [godot-sdk-integrations/godot-ios-plugins](https://github.com/godot-sdk-integrations/godot-ios-plugins) ~199★ | MIT | ✅ | iOS 플러그인 모음 (**InAppStore** = 결제) |
| [godot-sdk-integrations/godot-storekit2](https://github.com/godot-sdk-integrations/godot-storekit2) ~19★ | MIT | ⚠️ API 불안정 | StoreKit 2. 아직 프로덕션 비추천 |
| [godot-sdk-integrations/godot-play-game-services](https://github.com/godot-sdk-integrations/godot-play-game-services) ~279★ | MIT | ✅ | Google Play 게임즈: 리더보드, 업적, 클라우드 저장 |
| [GodotNuts/GodotFirebase](https://github.com/GodotNuts/GodotFirebase) ~686★ | MIT | ✅ | Firebase Auth, Firestore, Realtime DB, Functions, Storage |
| [GodotSteam/GodotSteam](https://github.com/GodotSteam/GodotSteam) | — | 🗄️ 2026-10 → codeberg.org/godotsteam | Steam 전용 (모바일과 무관) |

> 결제 영수증 검증은 클라이언트에서 끝내지 말고 **Firebase Functions 같은 서버에서** 하세요. 자세한 내용은 [`architecture.md`](architecture.md) §6을 참고하세요.

## 4. 테스트

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [bitwes/Gut](https://github.com/bitwes/Gut) ~2.8k★ | MIT | ✅ 9.7.1 (4.7 대응) | GDScript 단위 테스트 |
| [godot-gdunit-labs/gdUnit4](https://github.com/godot-gdunit-labs/gdUnit4) ~1.3k★ | MIT | ✅ v6.2.2 | GDScript와 C# 테스트, IDE 연동 |

## 5. 읽어볼 Godot 오픈소스 게임

| 저장소 | 라이선스 | 상태 | 볼 포인트 |
|---|---|---|---|
| [TinyTakinTeller/GodotProjectZero](https://github.com/TinyTakinTeller/GodotProjectZero) ("A Dark Forest") ~205★ | 코드 MIT (에셋은 별도) | ✅ Godot 4.4 | **방치형·증분 게임**. 캐주얼 앱 게임과 가장 가까운 사례 |
| [gdquest-demos/godot-open-rpg](https://github.com/gdquest-demos/godot-open-rpg) ~3.0k★ | MIT | ✅ Godot 4.6 | 턴제 전투, 필드 이동, 컷신. GDQuest 수준의 코드 품질 |
| [max99x/wutw-public](https://github.com/max99x/wutw-public) (Worlds Upon The Wind) ~239★ | CC0 (오디오 제외) | ✅ Godot 4.7 | **실제 출시작**. 로그라이트 덱빌더의 카드·런 로직 |
| [P1X-in/tanks-of-freedom-ii](https://github.com/P1X-in/tanks-of-freedom-ii) ~431★ | MIT (일부 오디오 CC) | ✅ Godot 4.2+ | 턴제 전략, AI |
| [Revolutionary-Games/Thrive](https://github.com/Revolutionary-Games/Thrive) ~3.7k★ | **GPL-3.0** | ✅ | 대형 **C#** Godot 프로젝트. 구조만 참고 |
| [kidscancode/circle_jump](https://github.com/kidscancode/circle_jump) ~155★ | MIT | Godot **3.x** | 소형 모바일 하이퍼캐주얼. 패턴은 유효하지만 API는 구버전 |

## 6. 다른 엔진·언어의 참고 게임 (로직만 참고)

| 저장소 | 라이선스 | 볼 포인트 |
|---|---|---|
| [gabrielecirulli/2048](https://github.com/gabrielecirulli/2048) | MIT | 그리드 병합 퍼즐의 최소 구현 (JS) |
| [jakesgordon/javascript-tetris](https://github.com/jakesgordon/javascript-tetris) | MIT | 테트리스 루프: 회전, 충돌, 라인 클리어 |
| [IvarK/AntimatterDimensionsSourceCode](https://github.com/IvarK/AntimatterDimensionsSourceCode) | MIT | **실제 출시 방치형**: 프레스티지 다층 구조, 큰 수 |
| [Patashu/break_infinity.js](https://github.com/Patashu/break_infinity.js) | MIT | 방치형 큰 수 표현. GDScript로 포팅할 때 참고 |
| [Anuken/Mindustry](https://github.com/Anuken/Mindustry) | GPL-3.0 | 모바일 자동화와 타워디펜스 출시작 |
| [00-Evan/shattered-pixel-dungeon](https://github.com/00-Evan/shattered-pixel-dungeon) | GPL-3.0 | 모바일 로그라이크 출시작 |
| [yairm210/Unciv](https://github.com/yairm210/Unciv) | MPL-2.0 | 모바일 4X: 턴과 AI 로직 |
| [NoelFB/Celeste](https://github.com/NoelFB/Celeste) | MIT (해당 코드만) 🗄️ | `Player.cs`: 코요테 타임, 점프 버퍼 등 조작감 |
| [CleverRaven/Cataclysm-DDA](https://github.com/CleverRaven/Cataclysm-DDA) | CC BY-SA 3.0 | JSON 데이터 주도 설계의 극단적 사례 |
| [chrisboyle/sgtpuzzles](https://github.com/chrisboyle/sgtpuzzles) | MIT | 퍼즐 약 40종의 생성기와 솔버 (Android 포트) |

## 7. 다른 엔진 한눈에 보기 (참고용)

| 엔진 | 라이선스 | 한 줄 |
|---|---|---|
| [Defold](https://github.com/defold/defold) | Defold License (게임 제작은 자유, 무로열티) | 초경량 빌드, Lua |
| [Cocos](https://github.com/cocos/cocos-engine) | MIT | 중국과 미니게임 시장에 강함 |
| [Phaser](https://github.com/phaserjs/phaser) | MIT | HTML5 (v4). Capacitor로 앱 패키징 |
| [Flame](https://github.com/flame-engine/flame) | MIT | Flutter 2D 엔진 |
| [libGDX](https://github.com/libgdx/libgdx) | Apache-2.0 | Java/Kotlin. Mindustry, Shattered PD가 이 엔진 사용 |
| Unity | 비공개 (UnityCsReference는 열람만 가능) | 업계 표준이지만 소스 재사용 불가 |
| [Bevy](https://github.com/bevyengine/bevy) | MIT/Apache | 모바일에는 아직 미성숙 |

---

### 미검증·제외
- Godot용 break_infinity 포트("break-nihility"): 에셋 라이브러리에는 있지만 저장소는 미확인
- Unity open-project-1: 404 (삭제 또는 비공개)
- [boeledi/flutter_crush](https://github.com/boeledi/flutter_crush): 라이선스 없음, 읽기만 가능
