## 패턴 검증 테스트: godot --headless --path platforms/godot  (종료 코드 = 실패 개수)
extends Node

var fails := 0

func check(cond: bool, label: String) -> void:
	if cond:
		print("PASS ", label)
	else:
		fails += 1
		print("FAIL ", label)

func _ready() -> void:
	await get_tree().process_frame
	# Economy
	var start := Economy.get_amount(&"coins")
	check(Economy.add(&"coins", 100, &"test"), "economy add")
	check(Economy.get_amount(&"coins") == start + 100, "economy amount")
	check(not Economy.spend(&"coins", start + 1000, &"test"), "economy refuse overspend")
	check(Economy.spend(&"coins", 40, &"test"), "economy spend")
	check(not Economy.add(&"coins", 5_000_000, &"test"), "economy cap")
	check(not Economy.add(&"bogus", 1, &"test"), "economy unknown currency")
	# Save round-trip
	SaveManager.data["coins"] = 1234
	SaveManager.save_game()
	SaveManager.data["coins"] = 0
	SaveManager.load_game()
	check(SaveManager.data["coins"] == 1234 and typeof(SaveManager.data["coins"]) == TYPE_INT, "save roundtrip int")
	# migration v1
	var f := FileAccess.open(SaveManager.SAVE_PATH, FileAccess.WRITE)
	f.store_string(JSON.stringify({"version": 1, "money": 77}))
	f.close()
	SaveManager.load_game()
	check(SaveManager.data["coins"] == 77 and not SaveManager.data.has("money"), "migration v1->v2")
	check(SaveManager.data["settings"]["sfx"] == true and SaveManager.data["version"] == 2, "fill missing fields")
	# corrupted main -> backup
	SaveManager.save_game()
	SaveManager.save_game()
	f = FileAccess.open(SaveManager.SAVE_PATH, FileAccess.WRITE)
	f.store_string("{broken")
	f.close()
	SaveManager.load_game()
	check(SaveManager.data["coins"] == 77, "backup recovery")
	# offline reward
	SaveManager.data["last_seen_unix"] = int(Time.get_unix_time_from_system()) - 100
	check(Economy.calc_offline_reward(2.0) == 200, "offline reward")
	SaveManager.data["last_seen_unix"] = int(Time.get_unix_time_from_system()) + 1000
	check(Economy.calc_offline_reward(2.0) == 0, "offline time travel")
	SaveManager.data["last_seen_unix"] = 1
	check(Economy.calc_offline_reward(1.0, 8.0) == 8 * 3600, "offline cap")
	# Gacha
	var g := Gacha.new(42)
	var pity := 0
	var legends := 0
	for i in 1000:
		var out := g.roll(pity)
		pity = out.pity_count
		if pity >= Gacha.PITY_LIMIT:
			check(false, "pity bound")
		if out.item.rarity == &"legendary":
			legends += 1
	check(legends >= 1000 / Gacha.PITY_LIMIT, "pity guarantees legendaries (%d)" % legends)
	var table := g.get_probability_table()
	var total := 0.0
	for row in table:
		total += row.percent
	check(is_equal_approx(total, 100.0), "probability table sums 100")
	check(Gacha.new(7).roll(0).item.id == Gacha.new(7).roll(0).item.id, "seeded determinism")
	# ObjectPool
	var pool := ObjectPool.new(load("res://tests/Coin.tscn"), 3, 5)
	add_child(pool)
	await get_tree().process_frame
	var a := pool.acquire()
	check(a.process_mode == Node.PROCESS_MODE_INHERIT and (a as Node2D).visible, "pool acquire active")
	pool.release(a)
	check(a.process_mode == Node.PROCESS_MODE_DISABLED and not (a as Node2D).visible, "pool release inactive")
	check(pool.acquire() == a, "pool reuses")
	# StateMachine
	var host := Node.new()
	var sm := StateMachine.new()
	var s1 := load("res://tests/TestState.gd").new() as State
	s1.name = "Idle"
	var s2 := load("res://tests/TestState.gd").new() as State
	s2.name = "Run"
	sm.add_child(s1); sm.add_child(s2)
	sm.initial_state = s1
	host.add_child(sm)
	sm.owner = host
	add_child(host)
	await get_tree().process_frame
	check(sm.current == s1 and s1.entered == 1, "fsm initial")
	sm.transition_to(&"Run")
	check(sm.current == s2 and s2.entered == 1, "fsm transition")
	sm.transition_to(&"Nope")
	check(sm.current == s2, "fsm unknown ignored")
	print("FAILS=", fails)
	get_tree().quit(fails)
