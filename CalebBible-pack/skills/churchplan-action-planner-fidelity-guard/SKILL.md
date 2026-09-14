---
name: churchplan-action-planner-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-action-planner 대표 스킬 전용. "실행을 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)지어낸 행동(목표에 추적되지 않는 source_goal·지어낸 캘린더 행사 연계) (2)공백 숨김(owner=TBD인데 flag 없이 채워진 척) (3)부서 위장(departments에 없는 부서 배치). 결정론 스크립트로 근거 추적·공백 정직·캘린더 정합·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-action-planner가 action.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_action.py로 (1)스키마·meta.chosen_theme·departments·status (2)행동 존재 — actions 0개 위반 (3)근거 추적 — 각 action source_goal 필수·from_goals에 추적 안 되면 위반(지어낸 목표 차단) (4)부서 실재 — department가 meta.departments에 없으면 위반(부서 위장) (5)공백 정직 — owner 비거나 TBD인데 flags에 담당미정류 없으면 위반(공백 숨김) (6)캘린더 정합 — linked_event가 inputs_echo.from_calendar.event_weeks에 없으면 위반(지어낸 행사 연계) (7)과잉·중복 경고 — 부서당 5개 초과·owner 3개 이상 (8)확정 게이트 — status=확정인데 confirmed 없으면 위반. 스크립트 밖: 끼워맞춘 근거·가짜 담당을 사람 눈으로. 실패 시 해당 분석 재실행.
---

# churchplan-action-planner-fidelity-guard — 실행을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-action-planner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 실행을 지키는 자.** action.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 계획을 검증하지 않는다. **Claude가 실행계획을 오염시켰는지** 막는다:
1. **지어낸 행동** (ANCHOR #2): 목표에 추적되지 않는 `source_goal`·지어낸 캘린더 행사 연계 — "어느 목표를 이루나"에 답 없는 행동.
2. **공백 숨김**: `owner`=TBD인데 `flags` 없이 채워진 척 — 가짜로 메운 공백.
3. **부서 위장**: `departments`에 없는 부서 배치 — 없는 자리를 지어냄.

> 이 단계의 최우선 가드레일은 "빈칸을 지어내지 않는다(공백은 드러낸다)"와 "목표에서 추적되는 행동만"이다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_action.py <action.json>
```

스크립트가 검사하는 것:
1. **스키마·표어·부서·status** — 필수 블록(meta·inputs_echo·actions) + `meta.chosen_theme` + `meta.departments`(비어있지 않음) + `status` ∈ {제안,확정}.
2. **행동 존재** — `actions` 0개 위반.
3. **근거 추적** — 각 action `source_goal` 필수, `inputs_echo.from_goals`에 추적 안 되면 **위반(error·EXIT 1)**(지어낸 목표 차단). 매칭은 약한 substring이 아니라 토큰 기반 — axis 토큰이 모두 등장하고 direction_goal 핵심 토큰이 하나 이상 동반되어야 통과(축 글자만 섞인 우회 차단).
4. **부서·목적 실재** — `department`가 `meta.departments`에 없으면 위반(부서 위장). `purpose`(목적)가 비면 위반 — schema 필수 블록상 source_goal·department과 동급 필수.
5. **공백 정직(세 공백)** — `owner` 비거나 "TBD"·`resources` 빈 배열·`timing` 빈 값인데 `flags`에 담당미정/자원미정/시기미정이 없으면 위반(공백 숨김). 또한 `gaps[]` 정합 교차검증 — `gaps.type`∈{담당미정,자원미정,시기미정}, 채워진 행동을 공백이라 거짓 보고(공백 오보)·실제 공백을 gaps에 누락(공백 누락)하면 위반.
6. **캘린더 정합** — `linked_event`가 `inputs_echo.from_calendar.event_weeks`에 없으면 위반(지어낸 행사 연계).
7. **과잉·중복 경고** — 부서당 action 5개 초과·같은 owner 3개 이상(경고).
8. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.

## 검증 후 처리
- **통과**: "검증 통과 — 모든 행동이 목표에서 왔고, 공백 정직히 표시, 부서 실재" 반환. action.json 완료.
- **실패**: 위반 항목 구체 반환(예: "A3 source_goal 'X' — from_goals에 없음(지어낸 목표)", "A5 owner=TBD인데 flag 없음(공백 숨김)"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **끼워맞춘 근거**: source_goal은 있으나 실제 목표와 무관한 사후 정당화 → 진짜 목표로 교정하거나 행동 정리.
- **가짜 담당**: owner에 실재하지 않는 이름을 채운 경우 → TBD로 되돌려 정직하게 드러낸다.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
