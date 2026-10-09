# Godot 4 앱 게임 아키텍처

우리 앱 게임은 **Godot 4.x**(2026-10 현재 안정판은 4.7)와 **GDScript**를 기준으로 합니다. 엔진과 무관한 로직 원칙은 [`../../logic/core_systems.md`](../../logic/core_systems.md)에 있고, 이 문서는 그 원칙을 Godot에서 **어떻게 구현하는지**를 다룹니다.

## 1. Godot 핵심 개념 ↔ 게임 로직 매핑

| 게임 로직 개념 | Godot 구현 | 비고 |
|---|---|---|
| 전역 매니저 (저장, 경제, 사운드) | **Autoload**(싱글톤) | 프로젝트 설정 → Globals → Autoload |
| 이벤트 버스 | Autoload + **signal** | `patterns/EventBus.gd` |
| 상태 머신 | 노드 기반 FSM 또는 애드온(LimboAI 등) | `patterns/StateMachine.gd` |
| 데이터 주도 설계 | **Resource**(`.tres`) | 인스펙터에서 수치 편집 가능 |
| 게임 루프 | `_process(delta)` / `_physics_process(delta)` | 물리는 고정 틱(기본 60Hz) |
| 오브젝트 풀링 | PackedScene 인스턴스 재사용 | `patterns/ObjectPool.gd` |
| 저장 | `FileAccess` + `user://` + JSON | `patterns/SaveManager.gd` |
| 재화 | Autoload 단일 진입점 + signal | `patterns/Economy.gd` |
| 뽑기·드롭 | `RandomNumberGenerator` | `patterns/Gacha.gd` |

## 2. 권장 폴더 구조

```
res://
├─ project.godot
├─ autoload/              # 전역 싱글톤 (Autoload로 등록)
│  ├─ EventBus.gd
│  ├─ SaveManager.gd
│  ├─ Economy.gd
│  └─ AudioManager.gd
├─ data/                  # Resource 정의(.gd)와 인스턴스(.tres): 밸런스는 여기
│  ├─ defs/EnemyData.gd
│  ├─ enemies/slime.tres
│  └─ levels/level_001.tres
├─ scenes/
│  ├─ main/Main.tscn      # 진입점, 화면 전환 담당
│  ├─ game/Game.tscn
│  ├─ ui/
│  └─ entities/
├─ systems/               # 재사용 로직 (StateMachine, ObjectPool, Gacha…)
├─ addons/                # 서드파티 애드온 (libraries.md 참고)
├─ assets/                # 이미지, 사운드, 폰트
└─ tests/                 # GUT 또는 gdUnit4
```

**원칙**
- **씬은 자기 자식만 직접 제어하고, 바깥과는 signal로 통신합니다.** 이것이 Godot의 "call down, signal up" 원칙입니다.
- `get_node("../../Something")` 같은 경로 의존을 피하세요. 씬 구조가 바뀌면 깨집니다. 필요하면 `@export var target: Node`로 주입하거나 그룹을 사용합니다.
- Autoload는 **진짜 전역인 것만** 둡니다. 남발하면 모든 것이 서로를 아는 스파게티가 됩니다.

## 3. GDScript 코딩 규칙

```gdscript
class_name Player
extends CharacterBody2D

signal died
signal hp_changed(current: int, max_hp: int)

@export var max_hp: int = 100
@export var data: EnemyData          # Resource 주입

@onready var _sprite: Sprite2D = $Sprite2D

var hp: int = max_hp:
	set(value):
		hp = clampi(value, 0, max_hp)
		hp_changed.emit(hp, max_hp)
		if hp == 0:
			died.emit()
```

- **정적 타입을 항상 씁니다** (`var x: int`, 함수 반환 타입). 오류를 미리 잡고 성능도 좋아집니다. 프로젝트 설정의 `debug/gdscript/warnings/untyped_declaration`을 경고나 오류로 올리세요.
- private 멤버는 `_` 접두사, 상수는 `UPPER_SNAKE`를 씁니다.
- 공식 [GDScript 스타일 가이드](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)를 따릅니다.

## 4. Resource로 데이터 주도 설계

```gdscript
# res://data/defs/EnemyData.gd
class_name EnemyData
extends Resource

@export var id: StringName
@export var max_hp: int = 10
@export var speed: float = 100.0
@export var reward: int = 1
@export_range(0, 100) var spawn_weight: int = 50
```

- 에디터에서 `New Resource → EnemyData`로 `.tres`를 만들고 인스펙터에서 수치를 편집합니다. 코드 수정이 필요 없습니다.
- ⚠️ Resource는 **기본적으로 공유**됩니다. 같은 `.tres`를 로드한 적 두 마리가 같은 객체를 가리켜요. 런타임에 값을 바꿀 거라면 `data.duplicate()`를 하거나, 런타임 상태는 노드 변수에 따로 둡니다.
- ⚠️ **세이브 파일로 `.tres`를 쓰지 마세요.** Resource 로딩은 임의 스크립트를 실행할 수 있어서, 조작된 세이브가 코드 실행으로 이어질 수 있습니다. 세이브는 JSON이나 `FileAccess.store_var`(객체 비허용)로 저장합니다.

## 5. 모바일 특화 체크리스트

- [ ] **백그라운드 전환 시 저장**: `NOTIFICATION_APPLICATION_PAUSED`(Android/iOS)를 처리합니다 (`SaveManager.gd`에 구현)
- [ ] **해상도 대응**: Project Settings → Display → Window → Stretch Mode `canvas_items`, Aspect `expand`. 노치 대응은 `DisplayServer.get_display_safe_area()`로 합니다.
- [ ] **렌더러**: 모바일은 `Mobile` 또는 `Compatibility` 렌더러를 씁니다. 저사양 Android나 웹까지 고려하면 Compatibility가 안전합니다.
- [ ] **터치 입력**: `InputEventScreenTouch`, `InputEventScreenDrag`. 마우스 에뮬레이션 설정을 확인하세요.
- [ ] **배터리·발열**: 정적인 화면에서는 `Engine.max_fps`를 낮추고, `OS.low_processor_usage_mode`도 검토합니다.
- [ ] **햅틱**: `Input.vibrate_handheld(ms)`
- [ ] **광고와 결제**: Godot 코어에 없으므로 플러그인을 씁니다 (AdMob, Google Play Billing, iOS StoreKit). [`libraries.md`](libraries.md)를 참고하세요.
- [ ] **C# 주의**: Godot 4의 C# 모바일 내보내기 지원 범위는 버전마다 다릅니다. 모바일 출시가 목표면 **GDScript 사용을 권장**합니다. 상세 상태는 [`libraries.md`](libraries.md)에 있습니다.

## 6. 신뢰 경계: 앱 게임은 Roblox와 다릅니다

| 상황 | 판정 주체 | 해야 할 일 |
|---|---|---|
| 오프라인 싱글 | 기기 | 세이브 변조는 사실상 막을 수 없습니다. 과도한 방어보다 게임성에 집중하세요 |
| 랭킹·리더보드 | **서버** | 점수 제출 시 플레이 시드와 로그로 재검증하거나, 최소한 상한 체크를 합니다 |
| 인앱결제 | **서버**(권장) | 구글·애플 영수증을 서버에서 검증한 뒤 지급하고, 영수증 ID로 멱등 처리합니다 |
| 오프라인 보상 | 기기 시간 | 시간을 되돌린 경우를 무시하고 상한을 둡니다. 가능하면 서버 시간을 씁니다 |

> 서버가 없는 초기 단계라면 최소한 **결제 영수증 검증**만큼은 Firebase Functions 같은 서버리스로 처리하는 것을 권장합니다.
