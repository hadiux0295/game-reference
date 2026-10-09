## Economy (Autoload): 재화 증감의 단일 진입점
## 등록 순서: SaveManager 다음에 Economy (Autoload 는 목록 순서대로 로드됨)
##
## 포인트
##  * 모든 재화 변경은 add()/spend() 만 통과 → 로그, UI 갱신, 이상치 탐지 지점이 하나
##  * reason 을 남기면 "재화가 어디서 생기고 어디로 사라지는지" 분석 가능 (Sources & Sinks)
##  * UI 는 currency_changed 시그널만 구독 (Economy 는 UI 를 모름)
extends Node

signal currency_changed(currency: StringName, new_amount: int, delta: int, reason: StringName)

const CURRENCIES: Array[StringName] = [&"coins", &"gems"]
## 1회 지급 상한: 버그나 조작으로 비정상적인 값이 들어오는 것을 막는 안전장치
const MAX_SINGLE_GRANT := {&"coins": 1_000_000, &"gems": 10_000}


func get_amount(currency: StringName) -> int:
	return int(SaveManager.data.get(String(currency), 0))


func add(currency: StringName, amount: int, reason: StringName) -> bool:
	if currency not in CURRENCIES or amount <= 0:
		return false
	if amount > MAX_SINGLE_GRANT.get(currency, 0):
		push_warning("Suspicious grant: %s %d (%s)" % [currency, amount, reason])
		return false
	_apply(currency, amount, reason)
	return true


func can_afford(currency: StringName, cost: int) -> bool:
	return cost >= 0 and get_amount(currency) >= cost


func spend(currency: StringName, cost: int, reason: StringName) -> bool:
	if currency not in CURRENCIES or cost <= 0 or not can_afford(currency, cost):
		return false
	_apply(currency, -cost, reason)
	return true


func _apply(currency: StringName, delta: int, reason: StringName) -> void:
	var key := String(currency)
	var new_amount := get_amount(currency) + delta
	SaveManager.data[key] = new_amount
	SaveManager.mark_dirty()
	currency_changed.emit(currency, new_amount, delta, reason)
	# Analytics.log_event("currency", {currency, delta, reason})  # 분석 연동 지점


## 오프라인 보상: 기기 시간 되돌리기 방어 + 상한
## 호출 시점: SaveManager 가 로드된 직후 (last_seen_unix 가 갱신되기 전에)
func calc_offline_reward(per_second: float, max_hours: float = 8.0) -> int:
	var last := int(SaveManager.data.get("last_seen_unix", 0))
	var now := int(Time.get_unix_time_from_system())
	if last <= 0 or now <= last:
		return 0 # 첫 실행이거나 시간이 뒤로 감 → 지급 없음
	var elapsed := mini(now - last, int(max_hours * 3600.0))
	return int(elapsed * per_second)
