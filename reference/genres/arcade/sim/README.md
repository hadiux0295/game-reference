# arcade_sim.py: 아케이드 · Roblox 포맷 규칙 시뮬레이션

- **무엇을 검사하나.** [`../logic.md`](../logic.md) §3의 7개 시스템: Obby 체크포인트 `stage == current + 1` 검증, 타이쿤 버튼 선행 트리·구매 ID 저장/재구성 왕복·오프라인 수입 상한, 러너 청크 티어 단조 증가·속도 상한, .io OgarII 공식(속도 감소·시야 확대·여유 있는 크기 비교·질량 보존), 미로 생성(recursive backtracker)+BFS+경로 비율 창 필터·시드 재현, 라운드 매니저 전이(최소 인원·조기 종료·맵 로테이션), 등반 추락 거리·최고 높이. 테스트 15개, 이름은 logic.md §3의 "검증 ✅"와 같다.
- **실행.** `python3 -I arcade_sim.py --test` (마지막 줄 `passed k/n`, 종료 코드 = 실패 수) · `python3 -I arcade_sim.py --demo` (시드 42 한 판 요약). 표준 라이브러리만, 외부 의존 없음.
- **밸런스.** 파일 상단 `CONFIG` dict가 logic.md §2 JSON과 같은 값이다. OgarII 상수만 README §4 출처이고 나머지는 예시값.
- **검증하지 않는 것.** 렌더·카메라 연출, 네트워크 지연과 복제, Roblox/Godot 실기기 동작(Touched·물리·ProfileStore), 물리 발파 채점, 브레이딩(막다른 길 제거)은 구현하지 않고 재생성만 검사, 경로 비율의 분모 정의는 예시(최장 거리 대비)이며 게임마다 다를 수 있다.
- **결과.** 2026-10-17 `passed 15/15`.
