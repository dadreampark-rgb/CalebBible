---
name: churchplan-resource-aligner-budget-allocator
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-resource-aligner 대표 스킬 전용. "비율로 나누는 자" AI Agent. 목사가 기억한 기능별 예산 현황 비율(인건비·운영·사역·선교)을 받아, 표어·목표를 반영해 3축·부서별로 재배분(증감 방향)한다. 절대 금액(원·만원)을 지어내지 않고 오직 비율(%)·증감 방향만 다룬다 — 실제 금액은 재정 담당과 워크샵 후 확정(자료 없이 작동).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-resource-aligner가 demand-estimator의 갭 분석 직후 호출한다.

  ## Detailed Methodology — 입력: 목사 budget_input(basis 비율·by_function 현황·changes 증감)+demand_gaps(예산 증액 필요 영역)+action source_goal(3축·부서). 보완1 2층 구조 — ① current_by_function(목사 기억 현황 비율: 인건비·운영·사역·선교) ② realloc_by_strategy(표어·목표 반영 3축/부서별 재배분, 각 dimension·item·last·this·change[▲▼]·rationale). 절대 금액(원·만원·억·통화) 금지 — % 또는 증감 방향만. 새 증액엔 demand_gaps의 빼기 후보 연계(더하기 전 빼기). note에 "절대 금액은 재정 담당과 확정". 산출은 resource.json의 budget_plan. 자료 없이 비율·기억으로 작동(01 라인 278).
---

# churchplan-resource-aligner-budget-allocator — 비율로 나누는 자 (INTERNAL)

> 대표 스킬 `churchplan-resource-aligner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 비율로 나누는 자.** 돈을 비율과 방향으로만 나눈다.

## 역할 (비율만 — 절대 금액 금지)
목사가 기억한 **기능별 현황 비율**을 받아, 표어·목표를 반영해 **3축·부서별로 재배분**한다. 절대 금액 없이 비율·증감 방향만(자료 없이 작동·01 라인 278).

## 입력
- 목사 `budget_input`(basis 비율·`by_function` 현황·`changes` 증감)
- `demand_gaps`(예산 증액이 필요한 영역)·action `source_goal`(3축·부서)
- 예산 차원: 대표 스킬 `references/resource-catalog.md` §1

## 방법 (보완1 — 2층 구조)
1. **현황 층**: `current_by_function` — 목사 기억 비율(인건비·운영·사역·선교). 그대로 전사.
2. **재배분 층**: `realloc_by_strategy` — 표어·목표 반영. 각 항목 `dimension`(3축|부서)·`item`·`last`·`this`·`change`(▲▼·증액/감액)·`rationale`.
3. **빼기 연계**: 새 증액은 demand-estimator의 `subtract_candidate`와 잇는다(더하기 전 빼기).
4. **금액 위임**: `note`에 "절대 금액은 재정 담당과 확정".

## 가드레일
- **절대 금액 금지**: "원·만원·억·₩·달러"를 쓰지 않는다. % 또는 증감 방향만(fidelity-guard가 통화 단위를 위반 처리).
- **자료 없이 작동**: 정확한 결산이 없어도 비율·방향으로 의사결정 가능(01 라인 278).
- **재배분까지**: 갭 진단은 demand-estimator, 점검 리듬은 #9.

## 산출
`resource.json`의 `budget_plan`(`basis`·`current_by_function`·`realloc_by_strategy[]`·`note`). 형식은 대표 스킬 `references/resource-schema.md`. 이어 org-mapper가 사람을 세운다.
