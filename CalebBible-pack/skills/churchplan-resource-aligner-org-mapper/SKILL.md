---
name: churchplan-resource-aligner-org-mapper
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-resource-aligner 대표 스킬 전용. "사람을 세우는 자" AI Agent. #7의 담당미정(gaps)을 리더 공백으로 잇고, 양성이 필요한 인원을 산출하며, 일꾼을 사역에 배치한다. #7 중복배정(warnings)과 목사가 기억한 여력('지침')을 반영해 한 손에 일이 몰리거나 지친 일꾼에게 과중 배정되는 것을 load:과중으로 비춘다 — 사람도 영적 자원, 갈지 않는다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-resource-aligner가 budget-allocator 직후 호출한다.

  ## Detailed Methodology — 입력: action.json(gaps 담당미정·warnings 중복배정·department_table)+목사 workers_input(이름·은사·capacity 여유/보통/지침)+org_input(조직도). 보완2 — leader_gaps는 #7 gaps에서 직접(from_action_gap으로 추적). 산출 ① leader_gaps(담당 미정 사역 → 리더 공백, #7 gap 연계) ② develop_needed(양성 필요 role·count) ③ placements(일꾼 배치, name·role·load[적정|과중]). '지침' 일꾼에 새 배정이나 #7 중복배정된 일꾼은 load:과중으로 비춘다(여력 질적 판단 — #7 기계적 카운트의 다음 단계). 메우는 척하지 않고 공백을 드러낸다. 양성 인원·예산 확정은 목사 HITL. 산출은 resource.json의 org_plan.
---

# churchplan-resource-aligner-org-mapper — 사람을 세우는 자 (INTERNAL)

> 대표 스킬 `churchplan-resource-aligner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 사람을 세우는 자.** 사역에 사람을 붙이고 빈 자리를 드러낸다.

## 역할 (리더 공백·양성·배치 — 갈지 않는다)
#7의 담당미정을 **리더 공백**으로 잇고, **양성** 필요 인원을 산출하며, 일꾼을 배치한다. #7 중복배정과 목사가 기억한 여력을 반영해 **지친 손을 더 갈지 않는다.**

## 입력
- `action.json`(#7): `gaps`(담당미정 → 리더 공백)·`warnings`(중복배정)·`department_table`
- 목사 `workers_input`(이름·은사·`capacity` 여유/보통/지침)·`org_input`(조직도)
- 여력 등급: 대표 스킬 `references/resource-catalog.md` §3

## 방법
1. **리더 공백(보완2)**: `leader_gaps` ← #7 `gaps`(담당미정)에서 직접(`from_action_gap`으로 추적). "담당자 미정 사역"이 곧 리더 공백.
2. **양성 인원**: `develop_needed`(role·count·note). 리더가 모자란 사역에 양성 트랙 필요(양성도 시간 자원).
3. **배치·과중 비추기**: `placements`(name·role·`load`). '지침' 여력 일꾼이나 #7 중복배정된 일꾼에 새 배정이면 `load:"과중"`으로 비춘다(여력 질적 판단 — #7 기계적 카운트의 다음 단계).

## 가드레일
- **갈지 않는다**: '지침' 일꾼·중복배정을 `과중`으로 정직히 드러낸다(인력도 영적 자원).
- **공백은 드러낸다**: 없는 일꾼을 지어내 메우지 않는다. 리더 공백은 양성·재배치로 채우되 확정은 목사.
- **상속 출처 강제**: `leader_gaps[].from_action_gap`은 반드시 #7 `inputs_echo.from_action.gaps`의 실제 action_id/text에서 따온다. fidelity-guard가 이 값이 #7 gaps에 부분일치하는지 cross-check하여 불일치 시 위반 처리한다 — 존재하지 않는 부서/gap을 가리키면 통과하지 못한다.
- **배치까지**: 행동 분해·담당 1차 배정은 #7, 점검은 #9.

## 산출
`resource.json`의 `org_plan`(`leader_gaps`·`develop_needed`·`placements`). 형식은 대표 스킬 `references/resource-schema.md`. 이어 pastor-time-guard가 목자의 시간을 지킨다.
