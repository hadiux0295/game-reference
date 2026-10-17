# strategy_sim.py: 전략(TD + 경제 루프) 규칙 시뮬레이션

- **무엇을 검사하나**: [`../logic.md`](../logic.md) §3의 규칙 — 재화 단일 진입점·웨이브 보너스·패배 보상·KR 별, 비용 사다리(BTD6/KR/Thronefall 4~8배), 웨이브 테이블 → 스폰 큐, 타겟팅 First/Last/Strongest/Closest, 웨이포인트 진행·누출·목숨, 건설 요청 거부, SLG 타이머·가속·동맹 도움 상한, 오토배틀러 공유 풀 확률·소진·이자, 락스텝 체크섬·결정론.
- **실행**: `python3 -I strategy_sim.py --test` → 마지막 줄 `passed 18/18`, 종료 코드 = 실패 수. `python3 -I strategy_sim.py --demo` → 시드 11로 5웨이브 한 판 요약.
- **의존성**: Python 3 표준 라이브러리만 (`math`, `random`, `zlib`). 밸런스는 파일 상단 `CONFIG`(logic.md §2 JSON과 같은 값).
- **검증하지 않는 것**: 렌더·입력·UI, 실제 네트워크(지연·패킷 손실·NAT), 실기기 성능, 플로우 필드·회피 길찾기, 수백 유닛 성능, 서버 저장소(DataStore·파일)와 결제, 실제 게임의 밸런스 "재미".
- **확인일**: 2026-10-17, Python 3 로컬 실행.
