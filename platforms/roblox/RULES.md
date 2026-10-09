# Roblox 개발 규칙 (AI 에이전트용)

이 저장소를 참고해 Roblox(Luau) 코드를 작성하는 모든 AI 에이전트가 따르는 규칙입니다.

## 반드시
- 모든 Luau 파일 첫 줄에 `--!strict`를 붙입니다.
- 클라이언트에서 온 Remote 인자는 **타입, 범위, 게임 상태** 순서로 서버에서 검증합니다 (`patterns/SecureRemote.luau`).
- 재화, 점수, 뽑기 확률, 보상량은 **서버에서만** 계산합니다.
- 플레이어 데이터는 ProfileStore로 저장하고, 재화 변경은 `DataService`의 단일 함수를 통해서만 합니다.
- `ProcessReceipt`는 게임 전체에서 **한 곳에서만** 지정하고, PurchaseId로 중복 지급을 막습니다.
- 밸런스 수치는 `shared/Config`에 두고 `table.freeze`로 고정합니다.
- 라이브러리를 새로 도입하기 전에 `libraries.md`에서 상태(아카이브 여부)와 라이선스를 확인합니다.

## 금지
- Knit, Roact, ProfileService, ReplicaService, DataStore2, TestEZ, BridgeNet2, Aftman을 신규 도입하지 않습니다 (아카이브 또는 지원 중단).
- 서버에서 `RemoteFunction:InvokeClient`를 쓰지 않습니다 (서버가 멈출 수 있음).
- 클라이언트가 보낸 숫자를 그대로 재화에 더하지 않습니다.
- 라이선스가 없는 저장소의 코드를 복사하지 않습니다 (구조 참고만 허용).
- 폐기된 API를 쓰지 않습니다: `wait()`, `spawn()`, `delay()` 대신 `task.wait`, `task.spawn`, `task.delay`를 씁니다.

## 코드 스타일
- 포맷은 StyLua, 린트는 Selene을 따릅니다 (기본 설정, 탭 들여쓰기).
- 모듈 구조는 Service(서버) / Controller(클라이언트) + `Init()` / `Start()` 2단계 부팅입니다.
- 문자열 보간은 `` `{value}` `` 백틱 문법을 사용합니다.
