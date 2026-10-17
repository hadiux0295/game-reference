## Gacha: 가중치 뽑기 + 천장(pity) + 확률표 자동 생성
##
## 포인트
##  * 확률표(get_probability_table)를 "실제 뽑기에 쓰는 같은 데이터" 에서 생성
##    → 공개 확률과 실제 확률 불일치 방지 (한국: 확률형 아이템 확률 공개 법적 의무)
##  * 천장 카운트는 세이브에 저장 (앱 재시작으로 초기화되면 안 됨)
##  * 유료 뽑기 + 온라인 게임이면 이 로직은 서버에서 실행해야 한다 (클라이언트 RNG 는 조작 가능)
##  * 테스트/리플레이용으로 시드 고정 가능
class_name Gacha
extends RefCounted

const PITY_LIMIT := 90 # 90회 안에 최고 등급 보장

## 풀 정의 (실제로는 Resource/JSON 으로 분리 권장)
var pool: Array[Dictionary] = [
	{"id": &"common_sword", "rarity": &"common", "weight": 700},
	{"id": &"rare_shield", "rarity": &"rare", "weight": 250},
	{"id": &"epic_bow", "rarity": &"epic", "weight": 45},
	{"id": &"legend_staff", "rarity": &"legendary", "weight": 5},
]

var _rng := RandomNumberGenerator.new()


func _init(seed_value: int = -1) -> void:
	if seed_value >= 0:
		_rng.seed = seed_value
	else:
		_rng.randomize()


## pity_count 는 호출 측(세이브)에서 관리: 결과와 갱신된 카운트를 함께 반환
func roll(pity_count: int) -> Dictionary:
	pity_count += 1
	var result: Dictionary
	if pity_count >= PITY_LIMIT:
		result = _pick_weighted(pool.filter(func(e: Dictionary) -> bool: return e.rarity == &"legendary"))
	else:
		result = _pick_weighted(pool)
	if result.rarity == &"legendary":
		pity_count = 0
	return {"item": result, "pity_count": pity_count}


func _pick_weighted(entries: Array) -> Dictionary:
	var total := 0
	for e in entries:
		total += int(e.weight)
	var r := _rng.randi_range(1, total)
	for e in entries:
		r -= int(e.weight)
		if r <= 0:
			return e
	return entries[-1]


## 공개용 확률표 (천장 미적용 기본 확률, %)
func get_probability_table() -> Array[Dictionary]:
	var total := 0
	for e in pool:
		total += int(e.weight)
	var table: Array[Dictionary] = []
	for e in pool:
		table.append({"id": e.id, "rarity": e.rarity, "percent": snappedf(100.0 * e.weight / total, 0.01)})
	return table


# 사용 예 (SaveManager / Economy 와 연동)
# func _on_pull_pressed() -> void:
# 	if not Economy.spend(&"gems", 160, &"gacha_pull"):
# 		return
# 	var gacha := Gacha.new()
# 	var out := gacha.roll(SaveManager.data.pity_count)
# 	SaveManager.data.pity_count = out.pity_count
# 	SaveManager.mark_dirty()
# 	EventBus.item_acquired.emit(out.item.id, 1)
