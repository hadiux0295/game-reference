# Roblox(Luau) 오픈소스 라이브러리·레퍼런스 카탈로그

> 검증일: **2026-10-09**. 각 GitHub 페이지를 직접 확인해 아카이브 여부, 라이선스, 후속작을 기록했습니다.
> ★는 대략적인 스타 수입니다. 상태가 바뀔 수 있으니 도입 전에 한 번 더 확인하세요.

**상태 표기**
- ✅ 활발: 아카이브되지 않았고 지원 중단 공지도 없음
- 🗄️ 아카이브: GitHub에서 읽기 전용
- ⚠️ 지원중단: README에 더 이상 지원하지 않는다고 명시됨

**라이선스 주의**
- MIT / Apache-2.0: 자유롭게 사용 가능 (고지 유지)
- MPL-2.0: 수정한 파일만 공개 의무가 있음
- 라이선스 없음: 코드 재사용 불가, 참고만 가능

---

## 🧭 2026 권장 스타터 스택 (요약)

| 영역 | 선택 | 피할 것 |
|---|---|---|
| 툴체인 | Rokit + Rojo 7.7.x + Wally(또는 pesde) + StyLua + Selene + luau-lsp + Lune | Aftman(아카이브) |
| 언어 | Luau `--!strict` (TS 선호 시 roblox-ts + Flamework) | |
| 구조 | 순수 ModuleScript Service/Controller + RbxUtil(Signal, Trove, Comm, Component, Input) | Knit(아카이브) |
| 유틸 | Promise, `t`(런타임 타입 검증), 필요 시 jecs(ECS) | evaera/matter(아카이브, 후속은 matter-ecs) |
| 데이터 | **ProfileStore** + Replica (대안: Lapis) | ProfileService, ReplicaService, DataStore2 |
| 네트워킹 | Blink 또는 Zap(IDL 기반 코드 생성), ByteNet(코드 생성 없음) | BridgeNet2, Red |
| UI·상태 | Fusion / Vide / React-Luau 중 하나 + Charm | Roact(아카이브) |
| 디버그 | Cmdr + Iris | |
| 게임플레이 | ShapecastHitbox, Chickynoid, SimplePath, spr, ZonePlus | RaycastHitbox v4(후속작으로 대체됨) |
| 테스트 | jest-roblox / jest-lua | TestEZ(아카이브) |
| AI 연동 | Studio 내장 MCP 서버 | studio-rust-mcp-server(아카이브) |

---

## 1. 툴체인

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [rojo-rbx/rojo](https://github.com/rojo-rbx/rojo) ~1.8k★ | MPL-2.0 | ✅ v7.7.1 | 파일 ↔ Studio 동기화, Git 워크플로우의 핵심 |
| [rojo-rbx/rokit](https://github.com/rojo-rbx/rokit) | MIT | ✅ | 툴 버전 고정 (foreman/aftman 설정 호환) |
| [LPGhatguy/aftman](https://github.com/LPGhatguy/aftman) | MIT | 🗄️ 2025-07 | 레거시, Rokit으로 대체 |
| [Roblox/foreman](https://github.com/Roblox/foreman) | MIT | ✅ (실사용은 Rokit 우세) | 원조 툴 매니저 |
| [UpliftGames/wally](https://github.com/UpliftGames/wally) | MPL-2.0 | ✅ | 패키지 매니저 (wally.run) |
| [pesde-pkg/pesde](https://github.com/pesde-pkg/pesde) | MIT | ✅ | Roblox + Lune 겸용 신형 패키지 매니저 |
| [Kampfkarren/selene](https://github.com/Kampfkarren/selene) | MPL-2.0 | ✅ | 린터 |
| [JohnnyMorganz/StyLua](https://github.com/JohnnyMorganz/StyLua) | MPL-2.0 | ✅ | 포매터 |
| [luau-lang/luau](https://github.com/luau-lang/luau) ~6k★ | MIT | ✅ | Luau 언어 본체, RFC·스펙 |
| [JohnnyMorganz/luau-lsp](https://github.com/JohnnyMorganz/luau-lsp) | MIT | ✅ | VS Code 자동완성·타입 검사 |
| [lune-org/lune](https://github.com/lune-org/lune) | MPL-2.0 | ✅ | 독립 Luau 런타임 (빌드 스크립트, CI, 오프라인 테스트) |
| [seaofvoices/darklua](https://github.com/seaofvoices/darklua) | MIT | ✅ | 코드 변환·번들링 |
| [roblox-ts/roblox-ts](https://github.com/roblox-ts/roblox-ts) | MIT | ✅ | TypeScript → Luau |
| [rbxts-flamework/core](https://github.com/rbxts-flamework/core) | MIT | ✅ | roblox-ts 전용 프레임워크 |

## 2. Roblox 공식

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [Roblox/creator-docs](https://github.com/Roblox/creator-docs) | CC-BY-4.0 / 코드 MIT | ✅ | 공식 문서 원본. 예제 코드는 MIT |
| [Roblox/react-luau](https://github.com/Roblox/react-luau) | MIT | ✅ 읽기 전용 미러 | 공식 React 17 Luau 포트 |
| [jsdotlua/react-lua](https://github.com/jsdotlua/react-lua) | MIT | ✅ | 커뮤니티 배포판 (Wally/npm) |
| [Roblox/roact](https://github.com/Roblox/roact) | Apache-2.0 | 🗄️ 2023-12 → react-luau | 레거시 UI |
| [Roblox/rodux](https://github.com/Roblox/rodux) | Apache-2.0 | ✅ | Redux 스타일 스토어 |
| [Roblox/signals](https://github.com/Roblox/signals) | MIT | ✅ | 선언적 시그널·상태 |
| [Roblox/jest-roblox](https://github.com/Roblox/jest-roblox) | MIT | ✅ | 공식 Jest 포트 (Open Cloud CI 지원) |
| [jsdotlua/jest-lua](https://github.com/jsdotlua/jest-lua) | MIT | ✅ | 커뮤니티 배포판 |
| [Roblox/testez](https://github.com/Roblox/testez) | Apache-2.0 | 🗄️ 2024-09 | 레거시 테스트 |
| [Roblox/studio-rust-mcp-server](https://github.com/Roblox/studio-rust-mcp-server) | MIT | 🗄️ 2026-04 → [Studio 내장 MCP](https://create.roblox.com/docs/studio/mcp) | AI ↔ Studio 연결 |
| [Roblox/open-game-eval](https://github.com/Roblox/open-game-eval) | MIT | ✅ | LLM 에이전트의 Roblox 개발 과제 평가 프레임워크 |
| [Roblox/place-ci-cd-demo](https://github.com/Roblox/place-ci-cd-demo) | MIT | 🗄️ 2024-09 | Rojo + Open Cloud CI/CD 예시 |
| [Roblox/gear](https://github.com/Roblox/gear) | Roblox Limited Use (비 OSI) | "as-is archive" | 실제 무기·도구 스크립트 읽기용 |

> **공식 템플릿 게임**(Laser Tag, Platformer, Racing 등)은 GitHub에 없습니다. Studio 시작 화면에서 여는 언카피락 플레이스로 제공됩니다 ([템플릿 문서](https://create.roblox.com/docs/resources/templates)). GitHub에서 "공식 템플릿"이라고 주장하는 저장소는 의심하세요.

## 3. 프레임워크·유틸

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [Sleitnick/Knit](https://github.com/Sleitnick/Knit) | MIT | 🗄️ 2024-07 | 레거시. ARCHIVAL.md에서 순수 ModuleScript와 얇은 Remote 래퍼를 권장 |
| [Sleitnick/RbxUtil](https://github.com/Sleitnick/RbxUtil) | MIT | ✅ | Signal, Trove, Comm, TypedRemote, Component, Input, Timer, TableUtil, Spring, Shake 등 약 30종 |
| [Quenty/NevermoreEngine](https://github.com/Quenty/NevermoreEngine) | MIT | ✅ | 대형 프로덕션급 모노레포 (Binder, Maid, Rx 등) |
| [evaera/roblox-lua-promise](https://github.com/evaera/roblox-lua-promise) | MIT | ✅ | Promise |
| [howmanysmall/Janitor](https://github.com/howmanysmall/Janitor) | MIT | ✅ | 정리(cleanup)·수명 관리 |
| [osyrisrblx/t](https://github.com/osyrisrblx/t) | MIT | ✅ | 런타임 타입 검사 (Remote 인자 검증) |

## 4. ECS

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [Ukendio/jecs](https://github.com/Ukendio/jecs) | MIT | ✅ | 고성능 ECS (타워디펜스처럼 대량 유닛에 적합) |
| [matter-ecs/matter](https://github.com/matter-ecs/matter) | MIT | ✅ 커뮤니티 포크 | 디버거와 스케줄러 포함 |
| [evaera/matter](https://github.com/evaera/matter) | MIT | 🗄️ 2024-07 | 원본 |

## 5. 데이터 저장·복제

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [MadStudioRoblox/ProfileStore](https://github.com/MadStudioRoblox/ProfileStore) | Apache-2.0 | ✅ | **표준 선택.** 세션 잠금과 자동 저장 (`patterns/DataService.luau`) |
| [MadStudioRoblox/Replica](https://github.com/MadStudioRoblox/Replica) | Apache-2.0 | ✅ | 서버 상태 → 특정 클라이언트 복제 |
| [nezuo/lapis](https://github.com/nezuo/lapis) | MIT | ✅ (대형 게임 검증은 아직이라고 자체 명시) | 마이그레이션·검증 지원 대안 |
| [Data-Oriented-House/Squash](https://github.com/Data-Oriented-House/Squash) | MIT | ✅ | 직렬화·압축 |
| [MadStudioRoblox/ProfileService](https://github.com/MadStudioRoblox/ProfileService) | Apache-2.0 | ⚠️ → ProfileStore | 레거시 |
| [MadStudioRoblox/ReplicaService](https://github.com/MadStudioRoblox/ReplicaService) | Apache-2.0 | ⚠️ → Replica | 레거시 |
| [Kampfkarren/Roblox](https://github.com/Kampfkarren/Roblox) (DataStore2) | 커스텀 (수정본 공개 의무) | 레거시 | 신규 사용 비추천 |

## 6. 네트워킹

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [1Axen/blink](https://github.com/1Axen/blink) | MIT | ✅ v0.18.x (v1.0 프리릴리스) | IDL → 타입 지정·버퍼 압축 Remote 코드 생성 |
| [red-blox/zap](https://github.com/red-blox/zap) | MIT | ✅ v0.6.x (재작성 진행 중) | 같은 계열의 대안 |
| [ffrostfall/ByteNet](https://github.com/ffrostfall/ByteNet) | MIT | ✅ | 코드 생성 없는 버퍼 직렬화 |
| [ffrostfall/BridgeNet2](https://github.com/ffrostfall/BridgeNet2) | MIT | ⚠️ → ByteNet | 레거시 |
| [red-blox/Red](https://github.com/red-blox/Red) | MIT | 🗄️ 2025-12 | 레거시 |

## 7. UI·상태 관리

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [dphfox/Fusion](https://github.com/dphfox/Fusion) | MIT | ✅ v0.3 | 반응형 선언적 UI |
| [centau/vide](https://github.com/centau/vide) | MIT | ✅ | Solid 스타일의 세밀한 반응형 UI |
| [littensy/charm](https://github.com/littensy/charm) | MIT | ✅ | 원자(atom) 단위 상태 관리 (Vide, React, Fusion 호환) |
| [littensy/reflex](https://github.com/littensy/reflex) | MIT | ✅ | Rodux 계열 상태 컨테이너 |
| [SirMallard/Iris](https://github.com/SirMallard/Iris) | MIT | ✅ | 즉시 모드 디버그 UI (ImGui 스타일) |
| [1ForeverHD/TopbarPlus](https://github.com/1ForeverHD/TopbarPlus) | MPL-2.0 + 크레딧 조항 | ✅ | 상단바 아이콘·메뉴 |

## 8. 명령어·디버깅

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [evaera/Cmdr](https://github.com/evaera/Cmdr) | MIT | ✅ | 관리자·디버그 콘솔 |

## 9. 게임플레이 시스템

| 저장소 | 라이선스 | 상태 | 용도 |
|---|---|---|---|
| [easy-games/chickynoid](https://github.com/easy-games/chickynoid) | MIT | ✅ | 서버 권위 캐릭터 컨트롤러 (이동 치트 방지) |
| [TeamSwordphin/ShapecastHitbox](https://github.com/TeamSwordphin/ShapecastHitbox) | MIT | ✅ (RaycastHitbox의 후속작) | 근접 공격 히트박스 |
| [Swordphin/raycastHitboxRbxl](https://github.com/Swordphin/raycastHitboxRbxl) | MIT | 후속작으로 대체됨 | RaycastHitbox v4 |
| [Pyseph/ClientCast](https://github.com/Pyseph/ClientCast) | MIT | ✅ | 클라이언트 레이캐스트 히트박스 |
| [ahmicy/simplepath](https://github.com/ahmicy/simplepath) | MIT | ✅ | NPC 길찾기 래퍼 |
| [fraktality/spr](https://github.com/fraktality/spr) | MIT | ✅ | 스프링 애니메이션 (카메라·UI 손맛) |
| [1ForeverHD/ZonePlus](https://github.com/1ForeverHD/ZonePlus) | MIT | ✅ | 영역 진입·이탈 감지 |
| FastCast (EtiTheSpirit) | — | **미검증**: GitHub 소스 저장소 없음 (Creator Store / DevForum 배포) | 투사체 시뮬레이션 |

## 10. 통째로 읽어볼 만한 게임·템플릿

| 저장소 | 라이선스 | 상태 | 볼 포인트 |
|---|---|---|---|
| [Kampfkarren/zombie-strike](https://github.com/Kampfkarren/zombie-strike) | MPL-2.0 | 🗄️ 2023-04 | 실제 출시된 게임의 전체 소스. 대형 프로젝트 구조를 보기 좋음 |
| [littensy/slither](https://github.com/littensy/slither) | MIT | ✅ | roblox-ts + React로 만든 완성형 캐주얼 게임 (하이퍼캐주얼 참고에 적합) |
| [grilme99/roblox-project-template](https://github.com/grilme99/roblox-project-template) | MIT | ✅ | Rojo, Darklua, Wally, Selene, StyLua, CI 스캐폴드 |
| [MonzterDev/Roblox-Game-Template](https://github.com/MonzterDev/Roblox-Game-Template) | **라이선스 없음** | ✅ | 구조 참고만 가능 (코드 복사 불가) |
| [Roblox/gear](https://github.com/Roblox/gear) | Roblox Limited Use | 아카이브 성격 | 무기·도구 스크립트 |

## 11. 큐레이션 목록 현황

잘 관리되는 "awesome-roblox" 목록은 2026년 기준으로 **없습니다** ([JodeRBX/awesome-roblox](https://github.com/JodeRBX/awesome-roblox)는 방치 상태).
대신 아래에서 찾는 것을 추천합니다.
- [wally.run](https://wally.run): 패키지 검색
- DevForum "Community Resources" 카테고리
- 이 문서

---

### 미발견(404) 기록
- `Swordphin123/raycasthitboxv4` → 실제 위치는 `Swordphin/raycastHitboxRbxl`
- `EtiTheSpirit/FastCastRedux` → 존재하지 않음. 문서 저장소(FastCastAPIDocs)만 있음
- `grayzcale/simplepath` → 현재 `ahmicy/simplepath`로 연결됨
