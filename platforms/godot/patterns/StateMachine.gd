## StateMachine: 노드 기반 유한 상태 머신
##
## 씬 구성 예시
##   Player (CharacterBody2D)
##   └─ StateMachine (이 스크립트, initial_state = Idle)
##      ├─ Idle   (State 를 상속한 스크립트)
##      ├─ Run
##      ├─ Jump
##      └─ Hurt
##
## 포인트
##  * 상태마다 enter/exit/update 를 분리 → if 문 폭발 방지
##  * transition_to() 로만 전이. 존재하지 않는 상태로는 이동 불가
##  * 상태가 10개를 넘고 조건이 복잡해지면 행동트리 애드온(LimboAI, Beehave) 검토
##  * 같은 구조를 화면 흐름(Menu/Playing/Paused/GameOver), 라운드 진행에도 그대로 사용
class_name StateMachine
extends Node

signal state_changed(from: StringName, to: StringName)

@export var initial_state: State

var current: State
var _states: Dictionary = {} # StringName -> State


func _ready() -> void:
	for child in get_children():
		if child is State:
			_states[child.name] = child
			child.machine = self
	# 소유자(owner)의 _ready 가 끝난 뒤 시작해야 @onready 참조가 준비되어 있다
	await owner.ready
	current = initial_state
	current.enter({})


func _process(delta: float) -> void:
	if current:
		current.update(delta)


func _physics_process(delta: float) -> void:
	if current:
		current.physics_update(delta)


func _unhandled_input(event: InputEvent) -> void:
	if current:
		current.handle_input(event)


func transition_to(state_name: StringName, msg: Dictionary = {}) -> void:
	var next: State = _states.get(state_name)
	if next == null:
		push_warning("Unknown state: %s" % state_name)
		return
	if next == current:
		return
	var from := current.name
	current.exit()
	current = next
	current.enter(msg)
	state_changed.emit(from, state_name)


# 상태 베이스 클래스는 같은 폴더의 State.gd 참고
#
# ---------------------------------------------------------------------------
# 예: Idle.gd
# ---------------------------------------------------------------------------
# extends State
#
# @onready var player: CharacterBody2D = owner
#
# func physics_update(_delta: float) -> void:
# 	if Input.get_axis("move_left", "move_right") != 0.0:
# 		machine.transition_to(&"Run")
# 	elif Input.is_action_just_pressed("jump"):
# 		machine.transition_to(&"Jump", {"from_ground": true})
