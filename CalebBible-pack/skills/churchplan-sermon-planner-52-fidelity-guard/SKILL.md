---
name: churchplan-sermon-planner-52-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-sermon-planner-52 대표 스킬 전용. "강단을 지키는 자" AI Agent. 네 가지 거짓을 막는다 — (1)본문 할루시네이션(없는 장·절·가짜 책) (2)절기 날조(계산값과 어긋난 주차) (3)곡 단정(음악 방향에 특정 찬송 번호·제목 박음) (4)주해 월권(해석을 "유일·반드시"로 단정). 결정론 스크립트로 정경 본문·절기 주차·곡 단정·해석 단정·표어 정합·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 sermon-plan.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_sermon_plan.py로 (1)스키마·meta.chosen_theme·year·status (2)본문 실재(bible_validator.validate_reference로 모든 primary_text·parallel_texts의 정경 장:절 검사 — 가짜 위반) (3)날짜 결정론(easter_calculator.compute_week_date_grid 격자로 weeks[].date의 유효 ISO·일요일·week 일치 검사 — 어긋나면 위반) (4)절기 일치(compute_all_week_numbers 산출 주차와 observance 정규화 대조 — 불일치 위반, schema 필수 게이트) (5)주차 중복 차단 (6)곡 단정(worship_direction에 찬송 번호+제목 동시 출현=위반·하나=경고, 성경 장 인용은 제외) (7)주해 월권("유일한 해석"·"반드시 …뜻" 경고) (8)시리즈 참조 무결성(weeks[].series_id가 정의된 series.id 가리키는지 — 미정의 위반) (9)표어/목표 정합(goal_link·sermon_goal_map 부재 경고) (10)확정 게이트(status=확정인데 confirmed 없으면 위반). 같은 폴더에 easter_calculator.py·bible_validator.py 이식 복사본 보유(자기완결). 스크립트 밖: 가짜 어원·풍유 곡해를 인간 눈으로. 실패 시 해당 분석 재실행.
---

# churchplan-sermon-planner-52-fidelity-guard — 강단을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 강단을 지키는 자.** sermon-plan.json 산출 직후의 최종 게이트.

## 역할 (네 거짓을 막는다)
이 스킬은 목사의 설교를 검증하지 않는다. **Claude가 강단 계획을 오염시켰는지** 막는다:
1. **본문 할루시네이션** (ANCHOR #2): 없는 장·절, 가짜 책이름.
2. **절기 날조**: easter_calculator 산출과 어긋난 절기 주차(머리로 지어낸 날짜).
3. **곡 단정**: 음악 방향에 특정 찬송 번호·제목을 박음(방향만 허용).
4. **주해 월권**: Claude가 본문 해석을 "유일·반드시"로 단정.

> 이 단계의 최우선 가드레일은 "초안 생성기이지 주해 대행자가 아니다"와 "본문·절기는 계산·검증을 따른다"다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_sermon_plan.py <sermon-plan.json>
```

같은 폴더에 **`easter_calculator.py`·`bible_validator.py` 이식 복사본을 보유**(자기완결 — 외부 패키지 런타임 의존 없음). 스크립트가 검사하는 것:
1. **스키마·표어·연도·status** — 필수 블록 + `meta.chosen_theme` 존재 + `year` 정수 + `status` ∈ {제안,확정}.
2. **본문 실재** — 모든 `primary_text`·`parallel_texts`를 `validate_reference`로(없는 장·절·가짜 책 위반).
3. **날짜 결정론** — `compute_week_date_grid(year)` 격자로 `weeks[].date`의 유효 ISO 날짜·일요일·해당 주차 일치 검사(어긋나면 위반 — 날짜 지어내기 차단).
4. **절기 일치** — `compute_all_week_numbers(year)` 산출 주차와 `observance` 정규화(공백·동의어 흡수) 대조(불일치 **위반** — schema 필수 게이트·계산값을 따른다).
5. **주차 중복** — 같은 주차 둘 이상 위반.
6. **곡 단정** — `worship_direction`에 찬송 번호+제목 동시 출현 위반(하나만 경고). 성경 장 인용('로마서 8장')은 찬송 번호로 오인하지 않음.
7. **주해 월권** — title·core_message·application의 "유일한 해석"·"반드시 …뜻" 경고.
8. **시리즈 참조 무결성** — 모든 `weeks[].series_id`가 정의된 `series.id`를 가리키는지(미정의 위반), `series.weeks` 선언 범위와 실제 배정 주차 비교(불일치 경고).
9. **표어/목표 정합** — `series.goal_link`·`narrative_check.sermon_goal_map` 모두 없으면 경고.
10. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.

## 검증 후 처리
- **통과**: "검증 통과 — 본문 실재, 절기 정확, 곡 단정 없음, 해석 월권 없음" 반환. sermon-plan.json 완료.
- **실패**: 위반 항목 구체 반환(예: "3주차 주본문 '시 151:1' 정경 범위 밖", "13주차 worship_direction 특정 곡 박음"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **가짜 어원**: "이 헬라어는 원래…" 류 근거 없는 주장 → 제거.
- **풍유적 곡해**: 본문에 없는 알레고리로 메시지를 끼워 맞춤 → 본문 의미로 되돌림.
- **아전인수 적용**: 문맥 무시한 적용 → 문맥으로 교정.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
