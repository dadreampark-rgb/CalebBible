---
name: churchplan-plan-reinforce-plan-updater
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-reinforce 대표 스킬 전용. "계획을 자라게 하는 자" AI Agent. 추정→실측 대조 결과로 진단·목표·예산을 보정 갱신하고, 추정-실측 어긋남(mismatch)이 드러낸 새 병목에 대해 목표·예산·행동 조정을 제안한다. 갱신은 reconciliations에 근거할 때만 하며(지어내기 금지), 어긋남이 없는 항목은 조용히 확정한다. "어긋난 곳을 강조"가 조정 제안의 근거.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-reinforce가 estimate-actual-reconciler 직후 호출한다.

  ## Detailed Methodology — 입력: reconciliations(추정 vs 실측·mismatch)+옵션1 산출물(diagnosis·goals·resource). 실측 교체된 항목으로 진단·목표·예산을 보정 갱신한다: 각 plan_update에 target(갱신 대상)·before·after·reason·trigger(어느 reconciliation). mismatch:true(추정-실측 유의차)인 항목은 새 병목 신호로 목표·예산·행동 조정 제안(02 라인253·기능⑤). 갱신은 reconciliations에 근거할 때만(자료 없이 갱신 금지). 어긋남 없는 항목(범위 내)은 조용히 확정. 전체 계획서 재조립은 #10(plan-compiler)이지 #12 아님 — #12는 보정 델타까지. 산출은 reinforce.json의 plan_updates. 이월은 carryover-tracker가 이어 한다.
---

# churchplan-plan-reinforce-plan-updater — 계획을 자라게 하는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-reinforce`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 계획을 자라게 하는 자.** 실측이 드러낸 사실로 계획을 보정한다.

## 역할 (진단·목표·예산 갱신 — 어긋남→새 병목)
실측 교체 결과로 진단·목표·예산을 보정하고, 어긋남이 드러낸 새 병목에 조정을 제안한다.

## 입력
- `reconciliations`(estimate-actual-reconciler 산출·mismatch 포함)
- 옵션1 산출물(diagnosis·goals·resource)
- 갱신·새 병목 패턴: 대표 스킬 `references/reinforce-catalog.md` §3

## 방법
1. **보정 갱신**: 실측 교체 항목으로 진단·목표·예산 갱신. 각 `plan_update`에 target·before·after·reason·trigger.
2. **새 병목 조정**: `mismatch:true` 항목은 새 병목 신호 → 목표·예산·행동 조정 제안(어긋난 곳 강조).
3. **근거 갱신**: reconciliations에 근거할 때만 갱신(자료 없이 갱신 금지).
4. **조용한 확정**: 어긋남 없는 항목(범위 내)은 그대로 확정.

## 가드레일
- **근거 기반**: 갱신은 reconciliations에 추적(지어내기 금지).
- **어긋남→조정**: mismatch 항목은 새 병목 조정으로 연결(누락 시 경고).
- **델타까지**: 전체 계획서 재조립은 #10. #12는 보정 델타(갱신된 진단/목표/예산).

## 산출
`reinforce.json`의 `plan_updates`[]{target·before·after·reason·trigger}. 형식은 대표 스킬 `references/reinforce-schema.md`. 이어 carryover-tracker가 #9로 넘긴다.
