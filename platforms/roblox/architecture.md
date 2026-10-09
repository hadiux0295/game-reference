# Roblox 게임 아키텍처 기본

## 1. 신뢰 경계 (가장 중요)

Roblox는 **서버 권위(server-authoritative)** 모델입니다.

| 위치 | 실행 주체 | 신뢰 여부 | 둘 것 |
|---|---|---|---|
| `ServerScriptService` | 서버 | ✅ 신뢰 | 게임 규칙, 점수/재화 계산, 데이터 저장, 결제 처리 |
| `ServerStorage` | 서버 전용 저장소 | ✅ | 서버만 쓰는 모듈·에셋 (클라이언트에 복제 안 됨) |
| `ReplicatedStorage` | 양쪽 공유 | ⚠️ 클라이언트도 읽음 | 공유 모듈, 설정값, RemoteEvent/RemoteFunction |
| `StarterPlayerScripts` / `StarterGui` | 클라이언트 | ❌ 불신 | 입력, UI, 카메라, 이펙트 |

**원칙:** 클라이언트는 "요청"만 보내고, 서버가 "판정"합니다.
- ❌ `RemoteEvent:FireServer(coinsToAdd)` → 클라이언트가 숫자를 정함 (해킹 가능)
- ✅ `RemoteEvent:FireServer("CollectCoin", coinId)` → 서버가 거리·쿨다운·존재 여부 검증 후 지급

## 2. 권장 폴더 구조 (Rojo 기준)

```
my-game/
├─ default.project.json        # Rojo 매핑
├─ wally.toml                  # 패키지 의존성
├─ rokit.toml                  # 툴체인 버전 고정 (rojo, wally, selene, stylua)
├─ selene.toml / stylua.toml   # 린트·포맷
└─ src/
   ├─ server/                  → ServerScriptService
   │  ├─ init.server.luau      # 부트스트랩: 서비스 로드 & 시작
   │  └─ Services/
   │     ├─ DataService.luau   # 플레이어 데이터 (ProfileStore)
   │     ├─ RoundService.luau  # 라운드/게임 루프
   │     ├─ EconomyService.luau
   │     └─ ShopService.luau   # 게임패스·개발자상품 (ProcessReceipt)
   ├─ client/                  → StarterPlayer.StarterPlayerScripts
   │  ├─ init.client.luau
   │  └─ Controllers/
   │     ├─ InputController.luau
   │     ├─ UIController.luau
   │     └─ CameraController.luau
   └─ shared/                  → ReplicatedStorage.Shared
      ├─ Config/               # 밸런스 수치 (데이터 주도 설계)
      ├─ Net.luau              # Remote 정의 한 곳에 모으기
      └─ Util/
```

`default.project.json` 예시:

```json
{
  "name": "my-game",
  "tree": {
    "$className": "DataModel",
    "ReplicatedStorage": {
      "Shared": { "$path": "src/shared" },
      "Packages": { "$path": "Packages" }
    },
    "ServerScriptService": {
      "Server": { "$path": "src/server" }
    },
    "ServerStorage": {
      "ServerPackages": { "$path": "ServerPackages" }
    },
    "StarterPlayer": {
      "StarterPlayerScripts": {
        "Client": { "$path": "src/client" }
      }
    }
  }
}
```

## 3. Service / Controller 패턴

- **Service(서버)**와 **Controller(클라이언트)**를 각각 하나의 모듈로 만듭니다.
- 모든 모듈은 `Init()`(서로 참조 연결)과 `Start()`(실제 동작 시작) 2단계로 부팅합니다. 이렇게 하면 순환 참조와 로딩 순서 문제를 피할 수 있습니다.
- 과거 표준은 **Knit** 프레임워크였지만 현재는 유지보수가 중단되었습니다(상세는 [`libraries.md`](libraries.md)). 아래처럼 직접 짜는 경량 로더로도 충분합니다.

```lua
-- src/server/init.server.luau
local ServerScriptService = game:GetService("ServerScriptService")

local services = {}
for _, module in ServerScriptService.Server.Services:GetChildren() do
	if module:IsA("ModuleScript") then
		services[module.Name] = require(module)
	end
end

for _, service in services do
	if service.Init then service:Init(services) end
end
for _, service in services do
	if service.Start then task.spawn(service.Start, service) end
end
```

## 4. 데이터 주도 설계 (밸런스 분리)

수치는 코드에 하드코딩하지 말고 `shared/Config`에 모읍니다. 그러면 기획자나 AI 에이전트가 코드를 건드리지 않고 밸런스를 조정할 수 있습니다.

```lua
-- src/shared/Config/Economy.luau
return table.freeze({
	CoinValue = 1,
	CoinRespawnSeconds = 5,
	RebirthCost = function(rebirths: number): number
		return math.floor(1000 * 1.5 ^ rebirths)
	end,
})
```

## 5. 네트워킹 원칙

1. Remote는 `shared/Net.luau` 한 곳에서 생성·정의합니다.
2. 서버에서는 **모든 인자를 타입과 범위까지 검증**합니다. `typeof`로 타입을 확인하고, NaN과 inf를 걸러내고, 거리와 쿨다운도 확인합니다.
3. 플레이어별 **레이트 리밋**을 둡니다.
4. 대량·고빈도 통신에는 Zap, Blink, ByteNet 같은 직렬화 라이브러리를 고려합니다. 클라이언트와 서버 간 대역폭을 줄여 줍니다.
5. `RemoteFunction`으로 **서버가 클라이언트를 호출(InvokeClient)하는 것은 금지**입니다. 클라이언트가 응답하지 않으면 서버 스레드가 영원히 멈출 수 있습니다.
