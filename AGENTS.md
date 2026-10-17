# AGENTS.md: AI 팀 작업 규칙

이 저장소는 **게임 레퍼런스 지식 베이스**입니다. AI 팀(Lumi, Sunsu, Sage, Blitz, Scout)이 게임을 기획하거나 구현할 때 기준으로 삼는 자료입니다.

## 둘로 나뉜다 (가장 중요한 규칙)
- [`reference/`](reference/README.md) = **메인**. 시간이 지나도 참인 것만 둔다. 다른 게임의 사실, 공식, 수치, 원전, 오픈소스, 플랫폼 규칙.
  - 여기에는 **작업 현황 · 일정 · 시안 · 결정 · 할 일**을 두지 않는다. 그런 것은 `our_games/` 또는 각 프로젝트 저장소로.
  - 각 문서에는 "언제 확인했나"(확인일)를 적는다. "언제 할 것인가"는 적지 않는다.
- [`our_games/`](our_games/README.md) = **우리 것**. 우리가 만든 게임의 스냅샷과 작업물. 레퍼런스에서 "이미 해본 것"을 찾는 색인으로만 쓴다.
- 장르 문서의 마지막 절 "우리 게임 적용"만이 둘을 잇는 다리다. 그 절에는 링크와 한 줄 시사점만 둔다.

## 읽는 순서
1. [`README.md`](README.md)의 시작점 표에서 장르를 고른다 → `reference/genres/<장르>/README.md`
2. [`reference/systems/core_systems.md`](reference/systems/core_systems.md): 엔진과 무관한 공통 시스템
3. 해당 플랫폼 폴더
   - Roblox: [`reference/platforms/roblox/`](reference/platforms/roblox/), 반드시 `RULES.md`를 먼저 읽기
   - 앱 게임(Godot): [`reference/platforms/godot/`](reference/platforms/godot/), 반드시 `RULES.md`를 먼저 읽기
4. 외부 원전이 필요하면 [`reference/sources.md`](reference/sources.md)

## 공통 규칙
- **판정은 권위 측(서버)에서** 합니다. 재화, 점수, 확률, 보상을 클라이언트가 결정하게 두지 않습니다.
- **재화 증감은 단일 함수**를 거칩니다 (`addCurrency(player, type, amount, reason)`).
- **저장 데이터에는 `version` 필드**를 넣고 마이그레이션을 작성합니다.
- **결제는 영수증 ID로 멱등 처리**합니다.
- **밸런스 수치는 데이터(Config, JSON)로 분리**합니다.
- **라이선스를 확인한 뒤 코드를 재사용**합니다. 라이선스가 없는 코드나 GPL 코드는 구조만 참고하고 복사하지 않습니다.
- 라이브러리를 도입하기 전에 카탈로그에서 **아카이브·지원중단 여부를 확인**합니다.

## 이 저장소에 자료를 추가할 때
- 장르별 자료는 `reference/genres/<장르>/`에. 새 장르 폴더는 [`reference/genres/_template.md`](reference/genres/_template.md)를 복사해 시작한다. 절의 순서와 번호를 바꾸지 않는다.
- 엔진과 무관한 로직은 `reference/systems/`에, 특정 엔진이나 플랫폼의 구현은 `reference/platforms/<플랫폼>/`에 둡니다.
- 외부 저장소를 추가할 때는 **링크, 라이선스, 상태(활발/아카이브), 확인 날짜**를 함께 적습니다. 확인하지 못했으면 "미검증"이라고 표시합니다.
- 예제 코드를 실제로 실행해 검증했는지 여부를 반드시 적습니다.
- 다른 게임의 수치는 `reference/data/`에 두고, **행마다 `source: wiki | measured | extracted | decompiled | inferred`**와 URL·확인일을 적습니다. 수집은 R0(공개 자료)부터 하고, 온라인 게임 클라이언트(Roblox 포함)는 절대 역분석하지 않습니다. 규칙 전문: [`reference/data/README.md`](reference/data/README.md)
- SEO 목록 글은 후보를 찾는 데만 쓰고, 숫자는 공식 페이지·개발자 블로그·차트·GitHub 저장소 페이지에서 다시 확인합니다.
- 채움 상태는 [`reference/README.md`](reference/README.md)의 표를 갱신합니다 (어느 절이 비었는지).
