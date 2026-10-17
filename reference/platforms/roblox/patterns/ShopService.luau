--!strict
-- ShopService: 게임패스(1회 구매, 영구) + 개발자 상품(반복 구매, 소모성) 처리
--
-- ⚠️ 가장 흔한 실수
--  * ProcessReceipt 를 여러 스크립트에서 지정 → 마지막 하나만 동작. 반드시 한 곳에서만.
--  * 데이터 저장 전에 PurchaseGranted 반환 → 서버 크래시 시 돈만 나가고 아이템 없음
--  * PurchaseId 중복 체크 누락 → 같은 영수증이 재전달되면 이중 지급

local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local ShopService = {}
local DataService: any

-- 상품 정의는 데이터로 관리 (ID는 Creator Hub 에서 발급)
local GAME_PASSES = {
	VIP = 0, -- TODO: 실제 GamePass ID
	DoubleCoins = 0,
}

local DEV_PRODUCTS: { [number]: (Player, any) -> () } = {
	-- [ProductId] = 지급 함수
	-- [123456] = function(player, data) data.Gems += 100 end,
}

local MAX_STORED_PURCHASE_IDS = 50

--== 게임패스 ==--
local ownedCache: { [Player]: { [number]: boolean } } = {}

function ShopService:OwnsPass(player: Player, passId: number): boolean
	local cache = ownedCache[player]
	if not cache then
		cache = {}
		ownedCache[player] = cache
	end
	if cache[passId] == nil then
		local ok, owns = pcall(MarketplaceService.UserOwnsGamePassAsync, MarketplaceService, player.UserId, passId)
		cache[passId] = ok and owns or false
	end
	return cache[passId]
end

--== 개발자 상품 영수증 처리 ==--
local function processReceipt(receipt): Enum.ProductPurchaseDecision
	local player = Players:GetPlayerByUserId(receipt.PlayerId)
	if not player then
		return Enum.ProductPurchaseDecision.NotProcessedYet -- 재접속 시 Roblox가 다시 호출
	end

	local data = DataService:GetData(player)
	if not data then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	local purchaseId = tostring(receipt.PurchaseId)
	if table.find(data.PurchaseIds, purchaseId) then
		return Enum.ProductPurchaseDecision.PurchaseGranted -- 이미 지급됨
	end

	local grant = DEV_PRODUCTS[receipt.ProductId]
	if not grant then
		warn(`[ShopService] unknown product {receipt.ProductId}`)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	local ok, err = pcall(grant, player, data)
	if not ok then
		warn(`[ShopService] grant failed: {err}`)
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	table.insert(data.PurchaseIds, purchaseId)
	while #data.PurchaseIds > MAX_STORED_PURCHASE_IDS do
		table.remove(data.PurchaseIds, 1)
	end
	-- ProfileStore 는 주기적으로 자동 저장하며, 세션 잠금 덕분에 다른 서버가 덮어쓰지 않음.
	-- 고가 상품이라면 즉시 저장(profile:Save())까지 고려.
	return Enum.ProductPurchaseDecision.PurchaseGranted
end

function ShopService:Init(services: { [string]: any })
	DataService = services.DataService
end

function ShopService:Start()
	MarketplaceService.ProcessReceipt = processReceipt

	MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, passId, purchased)
		if purchased then
			local cache = ownedCache[player]
			if cache then
				cache[passId] = true
			end
		end
	end)
	Players.PlayerRemoving:Connect(function(player)
		ownedCache[player] = nil
	end)
end

ShopService.GAME_PASSES = GAME_PASSES
return ShopService
