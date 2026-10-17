--!strict
-- DataService: ProfileStore 기반 플레이어 데이터 저장
-- 패키지: MadStudioRoblox/ProfileStore (ProfileService의 후속작)
-- 위치: ServerScriptService.Server.Services
--
-- 핵심 포인트
--  * 세션 잠금(session lock)으로 서버 두 곳에서 동시에 같은 데이터를 쓰는 사고(아이템 복사 버그)를 방지
--  * Reconcile()로 템플릿에 새로 추가한 필드를 기존 유저 데이터에 자동 보충
--  * 클라이언트에는 절대 profile 객체를 넘기지 말 것. 필요한 값만 복제(leaderstats, Attribute, Replica 등)

local Players = game:GetService("Players")
local ServerStorage = game:GetService("ServerStorage")

local ProfileStore = require(ServerStorage.ServerPackages.ProfileStore)

local PROFILE_TEMPLATE = {
	Coins = 0,
	Gems = 0,
	Rebirths = 0,
	Inventory = {} :: { [string]: number },
	Settings = { Music = true, Sfx = true },
	PurchaseIds = {} :: { string }, -- 개발자 상품 중복 지급 방지용 (ShopService 참고)
	FirstJoin = 0,
}
export type PlayerData = typeof(PROFILE_TEMPLATE)

-- 스튜디오 테스트 시 실데이터 오염 방지: 키 이름을 분리
local STORE_NAME = if game:GetService("RunService"):IsStudio() then "PlayerStore_Studio" else "PlayerStore_v1"
local PlayerStore = ProfileStore.New(STORE_NAME, PROFILE_TEMPLATE)

local DataService = {}
local profiles: { [Player]: any } = {}

local function setupLeaderstats(player: Player, data: PlayerData)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	coins.Value = data.Coins
	coins.Parent = leaderstats
	leaderstats.Parent = player
end

local function onPlayerAdded(player: Player)
	local profile = PlayerStore:StartSessionAsync(`{player.UserId}`, {
		-- 로딩 중 플레이어가 나가면 세션 시작을 취소
		Cancel = function()
			return player.Parent ~= Players
		end,
	})

	if profile == nil then
		player:Kick("데이터를 불러오지 못했습니다. 다시 접속해 주세요.")
		return
	end

	profile:AddUserId(player.UserId) -- GDPR 삭제 요청 대응
	profile:Reconcile()

	profile.OnSessionEnd:Connect(function()
		profiles[player] = nil
		player:Kick("다른 서버에서 데이터가 열렸습니다. 다시 접속해 주세요.")
	end)

	if player.Parent ~= Players then
		profile:EndSession()
		return
	end

	if profile.Data.FirstJoin == 0 then
		profile.Data.FirstJoin = os.time()
	end
	profiles[player] = profile
	setupLeaderstats(player, profile.Data)
end

--== 공개 API ==--

function DataService:GetData(player: Player): PlayerData?
	local profile = profiles[player]
	return profile and profile.Data
end

-- 재화 변경은 반드시 이 함수 한 곳을 통해서만 (감사 로그, UI 동기화 지점을 하나로)
function DataService:AddCoins(player: Player, amount: number): boolean
	local data = self:GetData(player)
	if not data or amount ~= amount or math.abs(amount) == math.huge then
		return false -- 데이터 없음 / NaN / inf
	end
	if data.Coins + amount < 0 then
		return false
	end
	data.Coins += amount
	local leaderstats = player:FindFirstChild("leaderstats")
	local coins = leaderstats and leaderstats:FindFirstChild("Coins") :: IntValue?
	if coins then
		coins.Value = data.Coins
	end
	return true
end

function DataService:Start()
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end
	Players.PlayerAdded:Connect(onPlayerAdded)
	Players.PlayerRemoving:Connect(function(player)
		local profile = profiles[player]
		if profile then
			profile:EndSession()
		end
	end)
end

return DataService
