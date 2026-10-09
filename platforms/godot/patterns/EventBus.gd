## EventBus (Autoload): 시스템 간 결합을 끊는 전역 시그널 허브
##
## 사용법
##   발신: EventBus.enemy_killed.emit(enemy, reward)
##   수신: EventBus.enemy_killed.connect(_on_enemy_killed)
##
## 포인트
##  * 전투 코드는 퀘스트/업적/사운드/분석을 몰라도 된다 → 기능 추가 시 기존 코드 수정 없음
##  * "전역으로 알릴 가치가 있는 게임 이벤트" 만 둔다. 부모-자식 간 통신은 일반 signal 로.
##  * 노드가 queue_free 되면 그 노드의 메서드에 연결된 Callable 은 자동 해제된다.
##    람다(익명 함수)로 연결한 경우는 직접 disconnect 해야 누수가 없다.
extends Node

# --- 게임 흐름 ---
signal game_started(level: int)
signal game_over(score: int, is_new_best: bool)
signal level_cleared(level: int, stars: int)

# --- 전투 / 플레이 ---
signal enemy_killed(enemy: Node, reward: int)
signal player_damaged(amount: int)
signal combo_changed(combo: int)

# --- 메타 ---
signal item_acquired(item_id: StringName, count: int)
signal achievement_unlocked(achievement_id: StringName)

# --- 수익화 ---
signal purchase_completed(product_id: String)
signal rewarded_ad_finished(placement: StringName)
