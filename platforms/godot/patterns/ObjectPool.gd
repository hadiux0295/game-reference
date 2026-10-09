## ObjectPool: 자주 생성/삭제되는 오브젝트(총알, 코인, 장애물, 이펙트) 재사용
##
## 모바일에서 instantiate()/queue_free() 를 매 프레임 반복하면 끊김(스파이크)이 생긴다.
## 미리 만들어 두고 껐다 켰다 하는 것이 풀링.
##
## 사용법
##   var pool := ObjectPool.new(preload("res://scenes/entities/Coin.tscn"), 30)
##   add_child(pool)
##   var coin := pool.acquire()
##   coin.global_position = spawn_pos
##   ...
##   pool.release(coin)    # queue_free() 대신
##
## 풀링 대상 씬은 다음 두 함수를 구현하면 상태 초기화가 깔끔하다 (선택)
##   func on_acquire() -> void   # 체력/속도 등 리셋
##   func on_release() -> void   # 타이머/트윈 정지
class_name ObjectPool
extends Node

var _scene: PackedScene
var _free: Array[Node] = []
var _max_size: int


func _init(scene: PackedScene, prewarm: int = 10, max_size: int = 200) -> void:
	_scene = scene
	_max_size = max_size
	for i in prewarm:
		_free.append(_create())


func acquire() -> Node:
	var node: Node = _free.pop_back() if not _free.is_empty() else _create()
	_set_active(node, true)
	if node.has_method("on_acquire"):
		node.on_acquire()
	return node


func release(node: Node) -> void:
	if node.has_method("on_release"):
		node.on_release()
	if _free.size() >= _max_size:
		node.queue_free()
		return
	_set_active(node, false)
	_free.append(node)


func _create() -> Node:
	var node := _scene.instantiate()
	_set_active(node, false)
	# 풀 노드의 자식으로 둔다 (풀이 사라지면 함께 정리됨)
	add_child.call_deferred(node)
	return node


func _set_active(node: Node, active: bool) -> void:
	node.process_mode = Node.PROCESS_MODE_INHERIT if active else Node.PROCESS_MODE_DISABLED
	if node is CanvasItem or node is Node3D:
		node.visible = active
	# 충돌체(CollisionObject2D/3D)는 process_mode 가 DISABLED 이면
	# disable_mode(기본 REMOVE)에 따라 물리 시뮬레이션에서 자동으로 빠진다.
