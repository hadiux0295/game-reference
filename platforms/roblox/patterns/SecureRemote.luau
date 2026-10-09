--!strict
-- SecureRemote: 클라이언트 요청을 안전하게 받는 서버 측 패턴
-- 위치: ServerScriptService.Server.Services (또는 Util)
--
-- 규칙
--  1) 클라이언트가 보낸 값은 전부 "거짓말일 수 있다"고 가정
--  2) 타입 → 범위 → 게임 상태(거리, 쿨다운, 소유권) 순서로 검증
--  3) 플레이어별 레이트 리밋
--  4) 판정 결과(지급량 등)는 서버가 계산

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SecureRemote = {}

--== 레이트 리밋 (토큰 버킷) ==--
local function makeRateLimiter(maxTokens: number, refillPerSecond: number)
	local buckets: { [Player]: { tokens: number, last: number } } = {}
	Players.PlayerRemoving:Connect(function(p)
		buckets[p] = nil
	end)
	return function(player: Player): boolean
		local now = os.clock()
		local b = buckets[player]
		if not b then
			b = { tokens = maxTokens, last = now }
			buckets[player] = b
		end
		b.tokens = math.min(maxTokens, b.tokens + (now - b.last) * refillPerSecond)
		b.last = now
		if b.tokens < 1 then
			return false
		end
		b.tokens -= 1
		return true
	end
end

--== 값 검증 헬퍼 ==--
local function isFiniteNumber(v: any): boolean
	return typeof(v) == "number" and v == v and math.abs(v) ~= math.huge
end

local function getRootPart(player: Player): BasePart?
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

--[[
	SecureRemote.connect(remote, options, handler)
	options.rate = { max = 10, refill = 5 }  -- 초당 5회, 순간 최대 10회
	options.validate = function(player, ...) -> boolean   -- 타입/범위 검증
]]
function SecureRemote.connect(
	remote: RemoteEvent,
	options: { rate: { max: number, refill: number }?, validate: ((Player, ...any) -> boolean)? },
	handler: (Player, ...any) -> ()
)
	local rate = options.rate or { max = 10, refill = 5 }
	local allow = makeRateLimiter(rate.max, rate.refill)
	remote.OnServerEvent:Connect(function(player, ...)
		if not allow(player) then
			return -- 조용히 무시 (로그 남기고 누적되면 킥하는 것도 방법)
		end
		if options.validate and not options.validate(player, ...) then
			warn(`[SecureRemote] invalid args from {player.Name} on {remote.Name}`)
			return
		end
		handler(player, ...)
	end)
end

--== 사용 예: 코인 줍기 ==--
-- 클라이언트: Net.CollectCoin:FireServer(coinPart)
-- 서버는 "몇 코인" 인지 절대 클라이언트에게 묻지 않는다.
function SecureRemote.exampleCollectCoin(DataService: any)
	local remote = ReplicatedStorage:WaitForChild("Net"):WaitForChild("CollectCoin") :: RemoteEvent
	local MAX_PICKUP_DISTANCE = 12
	local collected: { [Instance]: boolean } = {}

	SecureRemote.connect(remote, {
		rate = { max = 8, refill = 4 },
		validate = function(_player, coin)
			return typeof(coin) == "Instance"
				and coin:IsA("BasePart")
				and coin:IsDescendantOf(workspace.Coins)
		end,
	}, function(player, coin: BasePart)
		local root = getRootPart(player)
		if not root or collected[coin] then
			return
		end
		if (root.Position - coin.Position).Magnitude > MAX_PICKUP_DISTANCE then
			return -- 순간이동/원격 수집 차단
		end
		collected[coin] = true
		coin.Transparency = 1
		DataService:AddCoins(player, coin:GetAttribute("Value") or 1)
		task.delay(5, function()
			collected[coin] = nil
			coin.Transparency = 0
		end)
	end)
end

SecureRemote.isFiniteNumber = isFiniteNumber
return SecureRemote
