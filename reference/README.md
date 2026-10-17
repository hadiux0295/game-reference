# reference/: 메인 색인

시간이 지나도 참인 것만 있습니다. 작업 현황은 없습니다. 각 문서의 숫자에는 출처와 **확인일**이 붙어 있고, 없는 것은 `미검증`입니다.

## 장르 × 플랫폼

| 장르 | 📱 앱 (Godot) | 🟥 Roblox | 💻 PC | 폴더 |
|---|---|---|---|---|
| 전략 | SLG · 카드 전략 · TD | TD · 타이쿤 전략 | RTS · 4X · 오토배틀러 | [`genres/strategy/`](genres/strategy/README.md) |
| 슈팅 | 모바일 BR · 탄막 | RIVALS류 아레나 FPS | CS2 · Valorant · 히어로 슈터 | [`genres/shooter/`](genres/shooter/README.md) |
| 롤 계열 (MOBA) | 모바일 MOBA (10~15분) | 소수 | LoL · Dota 2 | [`genres/moba/`](genres/moba/README.md) |
| 캐주얼 | 하이퍼 · 하이브리드 · 퍼즐 · 정렬/잼 · 머지 | Grow a Garden류 수집·소셜 | 웹 퍼즐 | [`genres/casual/`](genres/casual/README.md) |
| RPG · 방치형 | 방치형 RPG · 가차 · 서바이버류 | 시뮬레이터 · 애니 RPG | 로그라이트 · ARPG | [`genres/rpg/`](genres/rpg/README.md) |
| 호러 · 판별 | 프리미엄 이상현상 | 교대 근무 호러 | Exit 8 · Papers, Please 계열 | [`genres/horror/`](genres/horror/README.md) |
| 아케이드 · Roblox 포맷 | 러너 | Obby · 타이쿤 · .io · 라운드제 | — | [`genres/arcade/`](genres/arcade/README.md) |

## 장르와 무관한 것

| 폴더 | 내용 |
|---|---|
| [`systems/core_systems.md`](systems/core_systems.md) | 게임 루프, FSM, RNG·천장, 경제, 성장 곡선, 저장, 치트 방지, 이벤트, 데이터 주도, AI·길찾기 |
| [`systems/genres.md`](systems/genres.md) | 장르별 루프·시스템·함정 **한 장 요약** (자세한 것은 `genres/`) + 리텐션·수익화 체크리스트 |
| [`platforms/godot/`](platforms/godot/RULES.md) | Godot 4.7 규칙 · 구조 · 라이브러리 카탈로그 · 검증된 GDScript 패턴 6종 · 헤드리스 테스트 |
| [`platforms/roblox/`](platforms/roblox/RULES.md) | Roblox 규칙 · 신뢰 경계 · 라이브러리 카탈로그 · Luau 패턴 4종 |
| [`data/`](data/README.md) | 다른 게임의 실제 수치. 행마다 `source:` 표기. 수집 사다리(R0 공개 자료부터) |
| [`sources.md`](sources.md) | 원전: 패턴 책, 넷코드·AI·절차 생성 아티클, 방치형 수학, 오픈소스 게임 목록 |

## 채움 상태 (2026-10-17)

| 장르 | 2 대표작 | 3 루프 | 4 수치 | 5 원전 | 6 함정 | 7 우리 적용 | 비고 |
|---|---|---|---|---|---|---|---|
| 전략 | | | | | | | |
| 슈팅 | | | | | | | |
| 롤 계열 | | | | | | | |
| 캐주얼 | | | | | | | |
| RPG · 방치형 | | | | | | | |
| 호러 · 판별 | | | | | | | |
| 아케이드 | | | | | | | |

표기: ● 채움 · ◐ 일부 · ○ 비어 있음. 새 장르는 [`genres/_template.md`](genres/_template.md)를 복사해 시작합니다.
