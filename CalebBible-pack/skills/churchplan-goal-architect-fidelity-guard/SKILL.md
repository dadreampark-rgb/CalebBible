---
name: churchplan-goal-architect-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-goal-architect 대표 스킬 전용. "목표를 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)환원(정성 없는 숫자 또는 정량 없는 영성) (2)근거 없음(진단·표어에 추적 안 되는 목표) (3)허위 정밀·과욕(신뢰 낮은 기준선 위 점값·담임 역량 초과 목표 수). 결정론 스크립트로 정성↔정량 짝·근거·과욕 상한·표어 정합·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-goal-architect가 goals.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_goals.py로 (1)스키마·status(제안/확정)·meta.chosen_theme 존재 (2)정성↔정량 한 쌍 강제(direction_goal+indicators≥1, 하나라도 없으면 환원 위반) (3)근거 추적(각 goal.rationale 필수 + inputs_echo 실재 표어·병목·돌봄점 토큰 부분일치 결정론 대조, 미일치 시 근거위장 위반) (4)성경 본문 실재성(scripture_link·core_scriptures.ref를 bible_validator로 정경 66권 범위 검사, 범위 밖이면 성경허위 위반) (5)과욕 상한(축당 ≤2·전체 ≤6 초과 위반) (6)허위 정밀(신뢰'하' 기준선 위 점값 목표치 경고) (7)허위 정량(measure_real=false·성령충만%류 경고) (8)신호 표기(signal_only) (9)확정 게이트(status=확정인데 confirmed 없으면 위반) (10)입력 무결성(비-dict 최상위·원소는 트레이스백 없이 정직한 종료). 스크립트 밖: 측정 불가의 영적 환원·정죄 프레이밍을 인간 눈으로 점검. 실패 시 해당 분석 재실행.
---

# churchplan-goal-architect-fidelity-guard — 목표를 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-goal-architect`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 목표를 지키는 자.** goals.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 목표를 검증하지 않는다. **Claude가 목표 설계를 오염시켰는지** 막는다:
1. **환원** (ANCHOR #2 핵심): 영적 방향을 숫자로 바꿔치기(정성 없는 숫자) 또는 점검 불가의 영성(정량 없는 방향). 둘 다 "번역하되 환원하지 않음"을 깬다.
2. **근거 없음**: 진단·표어에 추적되지 않는 목표(`rationale` 누락 = garbage-in).
3. **허위 정밀·과욕**: 신뢰 낮은 기준선 위 점값 목표치, 담임 단독 역량을 넘는 목표 수.

> 이 단계의 최우선 가드레일은 "번역하되 환원하지 않음"과 "더하기 전 빼기"다. 이 게이트가 그 경계를 지킨다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_goals.py <goals.json>
```

스크립트가 검사하는 것:
1. **스키마·status·표어** — 필수 블록(meta·inputs_echo·axes) + `meta.status` ∈ {제안, 확정} + **`meta.chosen_theme` 존재**(없으면 표어 미확정 위반).
2. **정성↔정량 한 쌍** — 각 goal에 `direction_goal`(정성) **그리고** `indicators`(정량 ≥1). 하나라도 없으면 환원 위반.
3. **근거 추적** — 각 goal `rationale` 필수(비면 위반) **+ 결정론 출처 대조**: rationale에 `inputs_echo`의 실재 표어·병목·돌봄점(chosen_theme·bottleneck·bottleneck_headline·needs_care·pastor_focus_axis) 어절 토큰이 최소 1개 부분일치해야 함. 미일치 시 **[근거위장] 위반**(지어낸 근거 차단). inputs_echo가 비면 이 대조는 skip.
4. **성경 본문 실재성** — `goal.scripture_link`와 `inputs_echo.core_scriptures[].ref`를 `bible_validator.validate_reference`로 정경 66권 책·장·절 범위 검사. 범위 밖(예 '하박국 12:99')이면 **[성경허위] 위반**(가짜 본문이 #4 sermon-planner-52로 전파되는 것 차단).
5. **과욕 상한** — 축당 goals ≤2, 전체 ≤6 초과 시 위반. 전체 0개도 위반.
6. **허위 정밀** — 기준선 신뢰 '하'(assumption)인데 `target`이 점값(단정 숫자)이면 경고(범위·방향 권장).
7. **허위 정량** — `measure_real:false`·"성령충만 80%"류 측정 불가 정량 경고.
8. **신호 표기** — 지표 `signal_only` 누락 경고.
9. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반(목사 확정 전 월권).
10. **입력 무결성** — 최상위가 객체(dict)가 아니거나 axes·goal 원소가 객체가 아니면 트레이스백 없이 정직한 위반·오류로 종료(종료코드 2/1).

## 검증 후 처리
- **통과**: "검증 통과 — 정성↔정량 짝 맞음, 근거 추적됨, 과욕 상한 이내" 반환. goals.json 완료.
- **실패**: 위반 항목 구체 반환(예: "axes[양육].goals[0] indicators 없음 — 환원", "전체 목표 7개 — 과욕 상한 초과"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **영적 환원**: 측정 불가한 것을 억지 숫자로(예 "거룩 7점") → 셀 수 있는 대리 신호로 교체.
- **정죄 프레이밍**: 목표 미달을 "왜 못 했나"로 쓴 곳 → "어디를 더 돌볼까"로 되돌림.
- **근거 위장(미묘한 경우)**: 토큰은 일치하나 의미가 끼워맞춤인 경우 → 진짜 출처로 교정. (명백한 무관 rationale·범위 밖 성경 본문은 이제 스크립트가 결정론으로 적발.)

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
