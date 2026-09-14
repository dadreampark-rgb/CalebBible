---
name: churchplan-resource-aligner-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-resource-aligner 대표 스킬 전용. "정렬을 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)절대 금액 환상(비율·증감만 다뤄야 하는데 원·만원 등 지어냄) (2)무한 자원 가정(새 수요가 있는데 빼기 없음) (3)목자 소진(담임 시간에 기도·쉼 보호 자원 누락). 결정론 스크립트로 절대금액 금지·더하기 전 빼기·목자 자원·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-resource-aligner가 resource.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_resource.py로 (1)스키마·meta.chosen_theme·status·필수 블록(budget_plan·pastor_time) (2)절대금액 금지 — budget_plan 전체에 "원·만원·억·₩·달러·$·won" 통화/절대금액 패턴 검출 시 위반(비율·증감만) (3)더하기 전 빼기 — demand_gaps에 증액·증원·시간추가 수요가 있는데 subtractions 비면 위반 (4)목자 자원 — pastor_time.blocks에 protected:true(기도/쉼) 항목 0개면 위반(소진 방지) (5)상속 충실 — org_plan.leader_gaps가 inputs_echo.from_action.gaps와 연결되는지 경고 (6)확정 게이트 — status=확정인데 confirmed 없으면 위반. 스크립트 밖: 끼워맞춘 비율·형식적 빼기를 사람 눈으로. 실패 시 해당 분석 재실행.
---

# churchplan-resource-aligner-fidelity-guard — 정렬을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-resource-aligner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 정렬을 지키는 자.** resource.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 자원을 검증하지 않는다. **Claude가 자원 정렬을 오염시켰는지** 막는다:
1. **절대 금액 환상** (ANCHOR #2): 비율·증감만 다뤄야 하는데 "원·만원·억"을 지어냄 — 자료 없이 작동 원칙 위배.
2. **무한 자원 가정**: 새 수요(증액·증원)가 있는데 빼기(`subtractions`) 없음 — "목표는 늘었는데 멈출 건 없다".
3. **목자 소진**: 담임 시간에 기도·쉼(보호 자원)이 없음 — 100% 사역으로 채움.

> 이 단계의 최우선 가드레일은 "비율만(절대 금액 금지)"·"더하기 전 빼기"·"목자도 자원"이다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_resource.py <resource.json>
```

스크립트가 검사하는 것:
1. **스키마·표어·status** — 필수 블록(meta·inputs_echo·budget_plan·pastor_time) + `meta.chosen_theme` + `status` ∈ {제안,확정}.
2. **절대 금액 금지** — `budget_plan`뿐 아니라 `demand_gaps`·`subtractions`·`warnings`·`pastor_time`까지 "원·만원·천원·억·백만·₩·달러·$·won·USD·KRW" 등 통화/절대금액 패턴이 있으면 위반(비율·증감만). `*.note` 경로만 경고로 완화.
3. **더하기 전 빼기** — `demand_gaps`에 증액·증원·강화·보강·부족 등 새 수요 키워드가 있거나 `subtract_candidate`가 채워진 항목이 있는데 `subtractions`가 비면 위반(어휘 운에 의존하지 않는 구조 신호 병행).
4. **목자 자원** — `pastor_time.blocks`에 `protected:true`(기도/쉼) 항목이 0개면 위반(소진 방지·가드레일 ④).
5. **상속 충실** — `org_plan.leader_gaps`가 `inputs_echo.from_action.gaps`(담당미정)와 연결되는지 점검(경고) + `leader_gaps[].from_action_gap`이 실제 #7 gaps의 action_id/text에서 상속됐는지 cross-check(불일치 시 위반 — 지어낸 부서/gap 차단).
6. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.

## 검증 후 처리
- **통과**: "검증 통과 — 비율만 다룸, 더하기 전 빼기 있음, 목자 기도·쉼 보호" 반환. resource.json 완료.
- **실패**: 위반 항목 구체 반환(예: "budget_plan에 '500만원' — 절대 금액 금지(비율만)", "demand_gaps 증액 있는데 subtractions 비어 있음"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **끼워맞춘 비율**: 근거 없이 그럴듯해 보이는 재배분 → 표어·목표·갭에 추적되게 교정.
- **형식적 빼기**: subtractions가 있으나 실제 자원을 회수하지 못하는 허울 → 진짜 멈출 것으로.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
