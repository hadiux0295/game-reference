# Godot 패턴 예제 (GDScript)

| 파일 | 역할 | 등록 방식 |
|---|---|---|
| `SaveManager.gd` | 버전 관리와 마이그레이션, 원자적 저장, 백업 복구, 백그라운드 자동 저장 | Autoload |
| `Economy.gd` | 재화 증감의 단일 진입점, 1회 지급 상한, 오프라인 보상 | Autoload (SaveManager 다음) |
| `EventBus.gd` | 전역 게임 이벤트 시그널 | Autoload |
| `StateMachine.gd` + `State.gd` | 노드 기반 FSM | 씬에 노드로 추가 |
| `Gacha.gd` | 가중치 뽑기, 천장, 확률표 생성, 시드 고정 | `Gacha.new()` |
| `ObjectPool.gd` | 노드 재사용 (탄, 코인, 이펙트) | `ObjectPool.new(scene)` |

## 검증 상태

**Godot 4.7.1 stable 헤드리스 실행 테스트 22개 항목 통과** (2026-10-09)

`platforms/godot/` 폴더 자체가 테스트용 Godot 프로젝트입니다.

```bash
godot --headless --path platforms/godot      # 종료 코드 = 실패 개수 (0이면 통과)
```

테스트 항목([`../tests/Main.gd`](../tests/Main.gd)):

| 대상 | 확인 내용 |
|---|---|
| Economy | 지급, 소비, 잔액 부족 거부, 1회 상한, 알 수 없는 재화 거부 |
| SaveManager | 저장 후 다시 불러와도 정수형 유지, v1→v2 마이그레이션, 누락 필드 보충, 파일 손상 시 백업 복구 |
| 오프라인 보상 | 정상 계산, 시간 역행 시 0, 8시간 상한 |
| Gacha | 천장으로 최고 등급 보장, 확률표 합 100%, 같은 시드면 같은 결과 |
| ObjectPool | 활성화, 비활성화, 재사용 |
| StateMachine | 초기 상태, 전이, 존재하지 않는 상태 무시 |

**검증하지 않은 것**
- 실제 Android·iOS 기기에서의 동작 (`NOTIFICATION_APPLICATION_PAUSED` 저장 포함)
- 광고와 결제 플러그인 연동
- 대규모 성능
