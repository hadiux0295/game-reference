## State: StateMachine 의 상태 베이스 클래스. 각 상태는 이 클래스를 상속해 필요한 함수만 오버라이드.
class_name State
extends Node

var machine: StateMachine

func enter(_msg: Dictionary) -> void: pass
func exit() -> void: pass
func update(_delta: float) -> void: pass
func physics_update(_delta: float) -> void: pass
func handle_input(_event: InputEvent) -> void: pass
