# cys-claude-church-plan-skills — PastorPlan 2027 목회계획 스킬 패키지

담임목사가 워크샵에서 자료 없이(기억·추정·범위값) 2027 신년 목회계획을
완성하도록 돕는 Claude 스킬 묶음. **99개 스킬 = 대표 13 + INTERNAL 하위 86.**

## 아키텍처
- 13개 그룹: vision-discernment·goal-architect·diagnostics·sermon-planner-52★·
  signature-events★·ministry-calendar·action-planner·resource-aligner·review-rhythm·
  plan-compiler·prayer-scripture-kit·plan-reinforce·guided-recall (★=심장)
- 각 그룹 = 대표 스킬 1 (사용자 진입점) + INTERNAL 하위 스킬들
  (frontmatter `disable-model-invocation: true`, 대표만 호출)
- 하위 스킬 유형: LLM추론(composer/architect) · 렌더러(`build_*.py`) · fidelity-guard(`validate_*.py`)
- 진실의 단일 출처: 각 스킬 `SKILL.md` + `<그룹>/references/*-schema.md` + `resources/00_스킬패키지_마스터정리.md`

## 명령 (스킬은 입력 JSON을 받는 파이썬 스크립트로 검증·렌더)
```bash
# 검증기: EXIT 0=통과 / 1=위반 / 2=파일·JSON 오류
python3 skills/<그룹>-fidelity-guard/scripts/validate_*.py <input.json> [recall.json]
# 렌더러: md/xlsx/docx/html 산출 (게이트 재강제)
python3 skills/<그룹>-renderer/scripts/build_*.py <input.json> [outdir]
# 전-파일 무결성 검증 (CI·회귀 가드 — 컴파일·프론트매터·교차참조·import·드리프트·위생·적대실행·마스터정합 C1~C8)
python3 scripts/verify_integrity.py    # EXIT 0=통과 / 1=결함
```

## 결정론 인프라 (할루시네이션 구조적 차단 — 수정 시 주의)
- `bible_validator.py` — 66권·1,189장 정경 + `validate_reference()`(장·절·범위·쉼표절). 9개 스킬에 이식 사본
- `easter_calculator.py` — Computus 부활절 + `compute_week_date_grid()`(주차→일요일). 5개 스킬에 이식 사본
- **공유자산 수정 워크플로우 (ADR-0001)**: canonical은 `shared/`에 단 1부. 거기서 사본을 *생성*한다.
  ```bash
  vi shared/bible_validator.py          # canonical만 편집
  python3 scripts/sync_shared_assets.py # 14개 사본으로 전파 (멱등)
  python3 scripts/sync_shared_assets.py --check  # 드리프트·orphan 검사 (CI)
  ```
  스킬 사본을 직접 편집하지 말 것 — sync가 덮어쓴다. 새 소비자는 `sync_shared_assets.py`의 MANIFEST에 추가.

## 비자명 규칙 (GOTCHAS)
- **공유자산 드리프트 금지**: bible_validator·easter_calculator는 사본이 모두 동일해야 함
  (`find skills -name bible_validator.py -exec md5 -q {} \; | sort -u | wc -l` == 1)
- **schema = 단일 진실**: 타입·필드는 `references/*-schema.md`를 따름. 검증기·렌더러를 함께 변경
- **truthy 비-dict 방어**: 모든 검증기·렌더러는 `_d(x)`/`_l(x)`/`_ld(x)` 헬퍼로 하위 필드 타입 가드
  (`(x or {}).get()` 금지 — truthy 비-dict(meta="str", series=7 등)에서 raw traceback 크래시)
- **검증기-렌더러 parity**: 같은 입력에 같은 판정(EXIT). 렌더러 gate는 검증기와 동일 수준 형식검사
- **정직성 게이트는 errors(EXIT 1)**: 스펙상 "위반"은 warning이 아닌 error.
  성경 가짜장절·절기 오배치·날짜격자·점값둔갑·회상이탈·절대금액(숫자/코드선행 양방향)·근거추적·정죄어휘 등
- 프론트매터: 대표=3-Layer(`## TLDR`/`## Triggers`/`## Detailed Methodology`) · 하위=`disable-model-invocation: true`
- `__pycache__`·`*.pyc`·`.DS_Store`는 `.gitignore` 처리

## 검증 방법론
신규 입력 JSON으로 검증기·렌더러를 end-to-end 실행: 정상→EXIT 0+산출물, 위반→EXIT 1 차단,
적대(깨진 JSON·최상위 비-dict·하위필드 truthy 비-dict·비-dict 리스트 원소)→raw traceback 없이 EXIT 1/2.
검증 라운드 반복 시 **매번 이전과 다른 신선 프롬프트**로 (테스트 통과 흉내 차단).
