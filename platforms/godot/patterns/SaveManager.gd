## SaveManager (Autoload): 버전 관리, 원자적 저장, 마이그레이션, 모바일 백그라운드 자동 저장
## 등록: Project Settings → Globals → Autoload → 이름 "SaveManager"
##
## 포인트
##  * user:// 경로 사용 (앱별 쓰기 가능한 영역. res:// 는 내보낸 앱에서 읽기 전용)
##  * 임시 파일에 쓴 뒤 rename → 저장 도중 앱이 죽어도 이전 세이브 보존
##  * version 필드 + 순차 마이그레이션, 템플릿에 새로 생긴 필드는 자동 보충
##  * JSON 파싱 시 모든 숫자가 float 로 돌아온다 → 정수 필드는 int() 로 변환
##  * .tres 로 세이브하지 않음 (Resource 로딩은 스크립트 실행 위험)
extends Node

signal saved
signal loaded

const SAVE_PATH := "user://save.json"
const TMP_PATH := "user://save.json.tmp"
const BACKUP_PATH := "user://save.json.bak"
const CURRENT_VERSION := 2
const AUTOSAVE_INTERVAL_SEC := 60.0

## 기본 세이브 템플릿. 필드를 추가하면 기존 유저 데이터에 자동 보충된다.
const TEMPLATE := {
	"version": CURRENT_VERSION,
	"coins": 0,
	"gems": 0,
	"level": 1,
	"best_score": 0,
	"inventory": {},
	"settings": {"music": true, "sfx": true, "haptics": true},
	"processed_purchase_ids": [],
	"last_seen_unix": 0,
	"pity_count": 0,
}

## 정수로 되돌릴 키 (JSON 은 숫자를 float 로 파싱함)
const INT_KEYS := ["version", "coins", "gems", "level", "best_score", "last_seen_unix", "pity_count"]

var data: Dictionary = {}
var _dirty := false


func _ready() -> void:
	load_game()
	var timer := Timer.new()
	timer.wait_time = AUTOSAVE_INTERVAL_SEC
	timer.autostart = true
	timer.timeout.connect(_on_autosave_timeout)
	add_child(timer)


func _on_autosave_timeout() -> void:
	if _dirty:
		save_game()


func _notification(what: int) -> void:
	# 모바일: 홈 버튼/앱 전환 시 PAUSED 가 온다. 이후 OS 가 앱을 죽여도 데이터 보존.
	if what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_WM_CLOSE_REQUEST:
		save_game()


## 값이 바뀌면 호출 → 다음 자동 저장 때 기록
func mark_dirty() -> void:
	_dirty = true


func save_game() -> void:
	data["last_seen_unix"] = int(Time.get_unix_time_from_system())
	var file := FileAccess.open(TMP_PATH, FileAccess.WRITE)
	if file == null:
		push_error("Save failed: %s" % error_string(FileAccess.get_open_error()))
		return
	file.store_string(JSON.stringify(data))
	file.close()

	# 이전 세이브를 백업으로 보관한 뒤 교체
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.copy_absolute(SAVE_PATH, BACKUP_PATH)
	var err := DirAccess.rename_absolute(TMP_PATH, SAVE_PATH)
	if err != OK:
		push_error("Save rename failed: %s" % error_string(err))
		return
	_dirty = false
	saved.emit()


func load_game() -> void:
	var raw: Variant = _read_json(SAVE_PATH)
	if raw == null:
		raw = _read_json(BACKUP_PATH) # 본 파일 손상 시 백업으로 복구
	if raw == null or not (raw is Dictionary):
		data = TEMPLATE.duplicate(true)
	else:
		data = _migrate(raw)
		_fill_missing(data, TEMPLATE)
		for key in INT_KEYS:
			data[key] = int(data[key])
	loaded.emit()


func _read_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return null
	var text := FileAccess.get_file_as_string(path)
	return JSON.parse_string(text) # 실패 시 null


## 버전별 순차 변환. 절대 기존 단계를 수정하지 말고 새 단계를 추가할 것.
func _migrate(d: Dictionary) -> Dictionary:
	var v := int(d.get("version", 1))
	while v < CURRENT_VERSION:
		match v:
			1:
				# 예: v1 의 "money" 를 v2 의 "coins" 로 이름 변경
				if d.has("money"):
					d["coins"] = d["money"]
					d.erase("money")
		v += 1
	d["version"] = CURRENT_VERSION
	return d


func _fill_missing(target: Dictionary, template: Dictionary) -> void:
	for key in template:
		if not target.has(key):
			var value: Variant = template[key]
			target[key] = value.duplicate(true) if (value is Dictionary or value is Array) else value
		elif template[key] is Dictionary and target[key] is Dictionary:
			_fill_missing(target[key], template[key])
