---
name: churchplan-plan-reinforce-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-reinforce 대표 스킬 전용. "정직을 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)실측 날조(status=실측교체인데 actual_source 없음·자료 근거 없는 실측) (2)추정 삭제(estimate 미보존·추정→실측 이력 상실) (3)부족 비난(자료가 이것밖에·왜 없 류 책망). 결정론 스크립트로 실측 근거·추정 보존·비난 어휘·어긋남 조정 연결·이월 #9·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-reinforce가 reinforce.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_reinforce.py로 (1)스키마·status·필수 블록(meta·verify_targets·reconciliations) (2)실측 날조 — reconciliations[].status=실측교체인데 actual_source 없으면 위반(자료 근거 없는 실측) (3)추정 보존 — reconciliations[].estimate 없으면 위반(추정→실측 이력 상실) (4)있는 만큼만 — extracted_data 근거 없는데 실측교체면 경고(자료 없는 항목은 이월) (5)부족 비난 — 산출 전반에 비난 어휘(자료가 이것밖에·왜 없·부실·게을·성의)가 부정 표지 없이 있으면 위반 (6)어긋남→조정 — mismatch:true인데 plan_updates 연결 없으면 경고 (7)이월 — carryovers[].to에 review-rhythm(#9) 없으면 경고 (8)확정 게이트 — status=확정인데 confirmed 없으면 위반. 스크립트 밖: 자료 오독·과잉 갱신을 사람 눈으로. 실패 시 해당 분석 재실행.
---

# churchplan-plan-reinforce-fidelity-guard — 정직을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-reinforce`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 정직을 지키는 자.** reinforce.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 자료를 검증하지 않는다. **Claude가 보강을 오염시켰는지** 막는다:
1. **실측 날조** (ANCHOR #2): status=실측교체인데 actual_source 없음 — 자료에 없는 값을 실측인 척.
2. **추정 삭제**: estimate 미보존 — 추정→실측 이력 상실(투명성 깨짐).
3. **부족 비난**: "자료가 이것밖에·왜 없나" — 빈손으로 와도 되는 철학 위배.

> 이 단계의 최우선 가드레일은 "실측 날조 금지"·"추정 보존"·"부족 비난 금지"다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_reinforce.py <reinforce.json>
```

스크립트가 검사하는 것:
1. **스키마·status** — 필수 블록(meta·verify_targets·reconciliations) + `status` ∈ {제안,확정}.
2. **실측 날조** — `reconciliations[].status:"실측교체"`인데 `actual_source`가 없으면 위반.
3. **추정 보존** — `reconciliations[].estimate`가 없으면 위반(이력 상실).
4. **있는 만큼만** — `extracted_data` 근거가 없는데 실측교체면 경고(자료 없는 항목은 이월).
5. **부족 비난** — 비난 어휘(자료가 이것밖에·왜 없·부실·게을·성의)가 *부정 표지* 없이 있으면 위반.
6. **어긋남→조정** — `mismatch:true`인데 `plan_updates` 연결이 없으면 경고(새 병목 누락).
7. **이월** — `carryovers[].to`에 review-rhythm(#9) 언급이 없으면 경고.
8. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.

## 검증 후 처리
- **통과**: "검증 통과 — 실측 근거 있음, 추정 보존, 비난 없음" 반환. reinforce.json 완료.
- **실패**: 위반 항목 구체 반환(예: "정착 실측교체인데 actual_source 없음 — 날조", "estimate 없음 — 이력 상실"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **자료 오독**: source는 있어도 값을 잘못 읽었으면 → 자료 재확인(목사 HITL).
- **과잉 갱신**: 작은 차이를 큰 병목으로 부풀리면 → delta에 맞게 절제.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
