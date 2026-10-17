--!strict
-- RoundService: 라운드제 게임 루프 (대기 → 인터미션 → 플레이 → 결과 → 반복)
-- 미니게임, 서바이벌, 술래잡기, 하이퍼캐주얼 1~2분 세션 게임에 공통으로 쓰는 구조
--
-- 설계 포인트
--  * 상태 머신: 현재 상태를 ReplicatedStorage 의 Attribute 로 노출 → 클라이언트 UI가 구독
--  * 서버만 상태를 바꾼다. 클라이언트는 표시만.
--  * 라운드 중 이탈/사망 처리를 반드시 고려 (남은 인원 0 → 즉시 종료)

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CONFIG = {
	MinPlayers = 2,
	IntermissionSeconds = 15,
	RoundSeconds = 90,
	ResultSeconds = 5,
	WinReward = 50,
	ParticipationReward = 10,
}

type State = "Waiting" | "Intermission" | "Playing" | "Results"

local RoundService = {}
local DataService: any

local roundState = ReplicatedStorage:FindFirstChild("RoundState") or Instance.new("Folder")
roundState.Name = "RoundState"
roundState.Parent = ReplicatedStorage

local function setState(state: State, timeLeft: number?)
	roundState:SetAttribute("State", state)
	roundState:SetAttribute("TimeLeft", timeLeft or 0)
end

local function countdown(seconds: number, state: State, shouldAbort: (() -> boolean)?): boolean
	for t = seconds, 1, -1 do
		setState(state, t)
		task.wait(1)
		if shouldAbort and shouldAbort() then
			return false
		end
	end
	return true
end

local function teleportToArena(player: Player)
	local character = player.Character
	local spawns = workspace:FindFirstChild("ArenaSpawns")
	if character and spawns then
		local points = spawns:GetChildren()
		local spawnPart = points[math.random(1, #points)] :: BasePart
		character:PivotTo(spawnPart.CFrame + Vector3.new(0, 3, 0))
	end
end

local function runRound()
	-- 참가자 확정
	local alive: { [Player]: boolean } = {}
	local participants: { Player } = {}
	for _, player in Players:GetPlayers() do
		if player.Character then
			alive[player] = true
			table.insert(participants, player)
			teleportToArena(player)
			local humanoid = player.Character:FindFirstChildOfClass("Humanoid")
			if humanoid then
				humanoid.Died:Once(function()
					alive[player] = nil
				end)
			end
		end
	end

	local leaveConn = Players.PlayerRemoving:Connect(function(player)
		alive[player] = nil
	end)

	local function aliveCount(): number
		local n = 0
		for _ in alive do
			n += 1
		end
		return n
	end

	-- 생존자 1명 이하이면 조기 종료
	countdown(CONFIG.RoundSeconds, "Playing", function()
		return aliveCount() <= 1
	end)
	leaveConn:Disconnect()

	-- 보상: 계산은 전부 서버에서
	for _, player in participants do
		if player.Parent == Players then
			local reward = if alive[player] then CONFIG.WinReward else CONFIG.ParticipationReward
			DataService:AddCoins(player, reward)
		end
	end

	countdown(CONFIG.ResultSeconds, "Results")
	for _, player in participants do
		if player.Parent == Players then
			player:LoadCharacter() -- 로비로 복귀
		end
	end
end

function RoundService:Init(services: { [string]: any })
	DataService = services.DataService
end

function RoundService:Start()
	while true do
		if #Players:GetPlayers() < CONFIG.MinPlayers then
			setState("Waiting")
			task.wait(1)
			continue
		end
		local ok = countdown(CONFIG.IntermissionSeconds, "Intermission", function()
			return #Players:GetPlayers() < CONFIG.MinPlayers
		end)
		if ok then
			runRound()
		end
	end
end

return RoundService

--[[ 클라이언트 쪽 구독 예시 (StarterPlayerScripts)
local roundState = game.ReplicatedStorage:WaitForChild("RoundState")
local function render()
	local state = roundState:GetAttribute("State")
	local t = roundState:GetAttribute("TimeLeft")
	statusLabel.Text = `{state} - {t}s`
end
roundState:GetAttributeChangedSignal("TimeLeft"):Connect(render)
roundState:GetAttributeChangedSignal("State"):Connect(render)
render()
]]
