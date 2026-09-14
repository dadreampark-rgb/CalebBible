---
name: churchplan-review-rhythm-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-review-rhythm 대표 스킬 전용. "점검을 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)점검=성과 채찍(신호등 frame·빨강 시나리오에 정죄·문책 어휘) (2)미래 점검값 둔갑(점검 전 status가 채워짐 — 아직 안 일어난 진행을 지어냄) (3)박제된 계획(반기 공식 수정일 누락). 결정론 스크립트로 돌봄 프레이밍·미래값 비움·반기 수정일·signal_only 계승·상속 충실·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-review-rhythm이 review.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_review.py로 (1)스키마·meta.chosen_theme·status·필수 블록(scorecard·schedule) (2)미래값 둔갑 — confirmed 전인데 scorecard.quarters[].indicators[].status가 채워져 있으면 위반(아직 안 일어난 진행 지어냄) (3)돌봄 프레이밍 — scorecard·monthly_checkup·red_signal_scenarios·schedule의 모든 AI 자유텍스트(frame·care_note·glance_question·quarterly_agenda·시나리오)에 정죄·성과 금칙어(실패·미달·부진·문책·추궁·징계·낙제·질책) 있으면 위반(재귀 순회로 검사 표면 자동 망라) (4)반기 수정일 — schedule.midyear_revision 없거나 official≠true면 위반(01 라인 310) (5)signal_only 계승 — 점검 지표에 signal_only 빠지면 경고 (6)상속 충실 — inputs_echo 없이 지표·경고 지어내면 위반 (7)추정 이월 — 신뢰'하'/assumption 지표인데 verify_at_review 아니면 위반(결정론 매핑) (8)확정 게이트 — status=확정인데 confirmed 없으면 위반 (9)분기 무결성 — quarters 정확히 4개·by↔분기 정합 위반 시 차단. 스크립트 밖: 채찍이 된 점검·형식적 어젠다를 사람 눈으로. 실패 시 해당 분석 재실행.
---

# churchplan-review-rhythm-fidelity-guard — 점검을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-review-rhythm`이 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 점검을 지키는 자.** review.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 점검을 검증하지 않는다. **Claude가 점검 리듬을 오염시켰는지** 막는다:
1. **점검=성과 채찍** (ANCHOR #2): 신호등 frame·빨강 시나리오에 정죄·문책 어휘 — 숫자가 채찍이 됨.
2. **미래 점검값 둔갑**: 점검 전인데 status가 채워짐 — 아직 안 일어난 진행을 지어냄.
3. **박제된 계획**: 반기 공식 수정일이 없음 — 계획이 갱신되지 않고 박제됨.

> 이 단계의 최우선 가드레일은 "점검은 돌봄"·"미래값 안 지어냄"·"반기 수정일 못박기"다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_review.py <review.json>
```

스크립트가 검사하는 것:
1. **스키마·표어·status** — 필수 블록(meta·inputs_echo·scorecard·schedule) + `meta.chosen_theme` + `status` ∈ {제안,확정}.
2. **미래값 둔갑** — `confirmed`=null인데 `scorecard.quarters[].indicators[].status`가 채워져 있으면 위반(점검 전 비움).
3. **돌봄 프레이밍** — `scorecard`·`monthly_checkup`·`red_signal_scenarios`·`schedule`의 모든 AI 자유텍스트 leaf(`frame`·`care_note`·`glance_question`·`quarterly_agenda`·시나리오)에 정죄·성과 금칙어(실패·미달·부진·문책·추궁·징계·낙제·질책)가 절 단위 부정 표지 없이 쓰이면 위반(재귀 순회·수치/상속 필드 제외).
4. **반기 수정일** — `schedule.midyear_revision`이 없거나 `official`≠true면 위반(01 라인 310).
5. **signal_only 계승** — 점검 지표에 `signal_only`가 빠지면 경고(성과 등급화 의심).
6. **상속 충실** — `inputs_echo.indicators_from_goals`/`sustainability_from_resource` 없이 지표·경고를 지어내면 위반.
7. **추정 이월** — 신뢰 '하'/assumption 지표인데 `verify_at_review`가 true가 아니면 위반(흐린 지표 또렷한 척 금지 — #3→점검 매핑은 결정론).
8. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.
9. **분기 무결성** — `scorecard.quarters`가 정확히 4개(1Q~4Q)가 아니거나 지표 `by`↔배치 분기가 어긋나면 위반(by→분기 결정론 배치).

## 검증 후 처리
- **통과**: "검증 통과 — 점검은 돌봄, 미래값 비움, 반기 수정일 못박힘" 반환. review.json 완료.
- **실패**: 위반 항목 구체 반환(예: "scorecard.frame에 '미달' — 정죄 어휘 금지", "midyear_revision 없음 — 반기 공식 수정일 못박기"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **채찍이 된 점검**: 어휘는 통과해도 톤이 추궁이면 → 돌봄으로 교정.
- **형식적 어젠다**: 어젠다가 있으나 소진 점검이 빠진 허울 → 목자·일꾼 돌봄을 넣는다.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
