# game-reference

**게임 로직 지식 베이스.** 여러 게임의 로직을 분석해 정리하고, 그 결과를 우리 **앱 게임**과 **Roblox 게임**에 적용할 때 참고하는 저장소입니다.
사람과 AI 팀(Lumi, Sunsu, Sage, Blitz, Scout)이 함께 씁니다. 작업 규칙은 [`AGENTS.md`](AGENTS.md)를 보세요.

## 구조

```
game-reference/
├─ logic/                  # 엔진 무관: 어떤 게임에도 통하는 로직
│  ├─ core_systems.md      # 게임 루프, FSM, RNG·천장, 경제, 성장 곡선, 저장, 치트 방지, AI
│  └─ genres.md            # 장르별 루프와 함정 (하이퍼캐주얼, 퍼즐, 방치형, 러너, Obby, 타이쿤, TD, RPG…)
├─ platforms/
│  ├─ app/                 # 앱 게임: 엔진 선택, 라이브러리, 읽어볼 오픈소스 게임
│  └─ roblox/              # Roblox(Luau)
│     ├─ RULES.md          # AI가 Roblox 코드 작성 시 지킬 규칙
│     ├─ architecture.md   # 서버·클라이언트 신뢰 경계, Rojo 구조, Service/Controller
│     ├─ libraries.md      # 검증된 오픈소스 카탈로그와 2026 권장 스택
│     └─ patterns/         # Luau 예제: 데이터 저장, Remote 검증, 라운드, 결제
├─ sources.md              # 원전: 책, 아티클, 오픈소스 게임, 큐레이션 목록
└─ AGENTS.md
```

## 핵심 원칙
1. **판정은 서버(권위 측)가.** 클라이언트는 요청만 합니다.
2. **저장은 버전 관리와 멱등 처리.** 데이터가 꼬이지 않게, 결제가 두 번 지급되지 않게 합니다.
3. **수치는 데이터로.** 밸런스 조정이 코드 수정 없이 끝나야 합니다.
4. **라이선스 확인 후 재사용.** 라이선스가 없거나 GPL인 코드는 구조만 참고합니다.

## 상태
- 외부 저장소 정보(라이선스, 아카이브 여부)는 **2026-10-09 기준**으로 GitHub 페이지를 직접 확인한 것입니다.
- `platforms/roblox/patterns/`의 Luau 코드는 **참고용 예제이며 아직 Roblox Studio에서 실행 검증하지 않았습니다.**
