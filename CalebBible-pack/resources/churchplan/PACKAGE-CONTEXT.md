# CONTEXT — 도메인 용어집 (PastorPlan 2027 church-plan)

아키텍처 리뷰·deepening 논의에서 이 어휘를 일관되게 사용한다. 좋은 seam에 이름을 준다.
(아키텍처 일반 어휘 — Module·Interface·Depth·Seam·Adapter·Locality·Leverage — 는 표준 정의를 따른다.)

## 도메인 Module

- **Skill** — Claude Code가 로드하는 단위 Module. interface = `SKILL.md` frontmatter(triggers·description),
  implementation = SKILL.md 본문 + `scripts/*.py` + `references/*.md`.
- **Master skill (대표 스킬)** — 그룹의 사용자 진입점 Skill. model-invocable. INTERNAL 하위 스킬을 orchestration.
  13개(= 13 그룹).
- **INTERNAL sub-skill (하위 스킬)** — `disable-model-invocation: true`. 자기 master만 호출. 86개.
  세 종류:
  - **Composer** — LLM 추론 하위 스킬(architect·composer·analyzer). 스크립트 없음.
  - **Renderer** — 결정론 출력 Module(`build_*.py`). 그룹 JSON → md/xlsx/docx/html. gate 재강제.
  - **Fidelity-guard** — 결정론 검증 Module(`validate_*.py`). 할루시네이션을 차단. EXIT 0=통과/1=위반/2=오류.
- **Group (그룹)** — master + 그 INTERNAL 하위들. 13 그룹 = 99 스킬.

## 핵심 개념

- **Shared deterministic asset (공유 결정론 자산)** — 여러 스킬이 쓰는 deep Module을 바이트 동일 사본으로
  각 스킬에 이식한 것. 현재 둘:
  - `bible_validator.py` — 66권·1,189장 정경. interface `validate_reference(ref) -> (bool, msg)`.
  - `easter_calculator.py` — Computus(부활절)·교회력. interface `compute_week_date_grid(year)`·`compute_all_week_numbers(year)`.
- **Honesty gate (정직성 게이트)** — fidelity-guard의 검사 중 **error(EXIT 1)** 인 것. 할루시네이션 한 클래스를
  *구조적으로* 차단(성경 가짜장절·절기 오배치·날짜격자·점값둔갑·회상이탈·절대금액·근거추적·정죄어휘 등).
  스펙상 "위반"은 warning이 아니라 error여야 한다.
- **Schema (스키마)** — 한 그룹 JSON의 타입 계약(단일 진실). 현재 `references/*-schema.md`에 **prose**로 존재.
- **Parity (검증기-렌더러 정합)** — 같은 입력에 fidelity-guard와 renderer가 같은 판정(EXIT). 타입검사가 양쪽에
  동일하게 있어야 함. 어긋나면 "검증기는 잡는데 렌더러는 크래시" 버그 클래스 발생.
- **Self-containment (자기완결)** — 스킬은 외부 패키지 런타임 의존 없이 독립 설치·실행 가능해야 한다.
  공유 자산을 import하지 않고 **이식 복사본**으로 가진다. → `docs/adr/0001-self-contained-skills.md`.

## seam 이름 (deepening 논의용)

- **공유 자산 seam** — `validate_reference`·`compute_week_date_grid` interface. canonical 원본 1 + 생성 사본 N.
- **스키마 계약 seam** — "그룹 G의 어느 필드가 dict/list인가". 현재 prose schema + 검증기 + 렌더러에 3중 smear.
- **방어 타이핑 idiom** — `_d(x)`/`_l(x)`/`_ld(x)`: truthy 비-dict를 안전 환원하는 3줄 헬퍼.
