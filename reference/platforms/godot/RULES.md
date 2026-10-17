# Godot 개발 규칙 (AI 에이전트용)

우리 앱 게임(Godot 4.x)의 코드를 작성하는 모든 AI 에이전트가 따르는 규칙입니다.

## 반드시
- **Godot 4.7 + GDScript**를 씁니다. C#은 모바일에서 실험적이고 웹 내보내기가 불가능하므로 쓰지 않습니다.
- **정적 타입**을 씁니다. 모든 변수, 인자, 반환값에 타입을 적습니다 (`var hp: int`, `-> void`).
- **"call down, signal up"**: 자식은 직접 호출하고, 부모나 형제에게는 signal로 알립니다. 전역 이벤트는 `EventBus`로 보냅니다.
- **재화 변경은 `Economy.add()` / `Economy.spend()`만** 사용하고, `reason`을 반드시 넘깁니다.
- **저장은 `SaveManager`**를 씁니다. 세이브 구조를 바꾸면 `CURRENT_VERSION`을 올리고 마이그레이션 단계를 **추가**합니다 (기존 단계는 수정 금지).
- 모바일에서는 `NOTIFICATION_APPLICATION_PAUSED`에서 저장합니다.
- 밸런스 수치는 **Resource(`.tres`) 또는 JSON**에 두고, 코드에 숫자를 하드코딩하지 않습니다.
- 자주 생성되는 오브젝트(탄, 코인, 이펙트)는 **ObjectPool**을 씁니다.
- 뽑기 확률표는 **실제 뽑기 데이터에서 생성**합니다 (`Gacha.get_probability_table()`).
- 애드온을 도입하기 전에 [`libraries.md`](libraries.md)에서 상태, 라이선스, Godot 버전 호환성을 확인합니다.

## 금지
- 세이브 파일을 `.tres`나 `.res`로 저장하거나 로드하지 않습니다 (스크립트 실행 위험).
- `get_node("../../..")` 같은 상위 경로에 의존하지 않습니다. `@export`로 주입하거나 그룹을 씁니다.
- 매 프레임 `instantiate()`나 `queue_free()`를 반복하지 않습니다.
- 결제 지급을 클라이언트 판단만으로 확정하지 않습니다. 영수증 ID로 멱등 처리하고, 가능하면 서버에서 검증합니다.
- 기기 시간을 그대로 믿지 않습니다. 오프라인 보상은 시간 역행을 무시하고 상한을 둡니다.
- GPL 게임(Mindustry, Shattered PD, Thrive 등)이나 라이선스가 없는 코드는 복사하지 않습니다. 구조만 참고합니다.

## 스타일
- [공식 GDScript 스타일 가이드](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)를 따릅니다 (탭 들여쓰기, `snake_case` 함수와 변수, `PascalCase` 클래스).
- 린트와 포맷은 [gdtoolkit](https://github.com/Scony/godot-gdscript-toolkit)(`gdlint`, `gdformat`)을 사용합니다.
- 테스트는 GUT 또는 gdUnit4를 쓰고, `res://tests/`에 둡니다. 경제, 저장, 뽑기 로직은 테스트를 필수로 작성합니다.
