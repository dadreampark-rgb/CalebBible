---
name: churchplan-action-planner-department-router
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-action-planner 대표 스킬 전용. "부서로 보내는 자" AI Agent. milestone-decomposer가 푼 행동을 교회 사역 부서(예배·교육·전도·선교·양육·행정)에 배치하고, 각 행동에 목적·시기·담당·자원을 단다. 담당이 미정이면 가짜 이름을 지어내지 않고 TBD로 둔다. 부서당 행동이 5개를 넘으면 과잉분해 경고를 단다(작은 교회 감당).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-action-planner가 milestone-decomposer의 행동 분해 직후 호출한다.

  ## Detailed Methodology — 입력: action.json actions[](source_goal·milestone·purpose·timing)+meta.departments(목사 입력 부서)+events.json blueprint.resources. 각 action을 어느 부서의 일인가로 배치(department, departments에 실재). 각 action에 purpose(목적)·timing(시기)·owner(담당, 미정이면 TBD·가짜 이름 금지)·resources(자원, blueprint.resources 단서)를 채운다. department_table(부서→action id 묶음, 렌더용) 생성. 부서당 action 5개 초과 시 warnings에 과잉분해(작은 교회 감당 점검). 없는 부서를 위해 행동을 지어내지 않는다. 여력 판단·예산은 resource-aligner(#8) — 여기서는 배치만. 산출은 actions[].department·purpose·timing·owner·resources + department_table + 과잉 warnings.
---

# churchplan-action-planner-department-router — 부서로 보내는 자 (INTERNAL)

> 대표 스킬 `churchplan-action-planner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 부서로 보내는 자.** 행동을 맡을 자리로 보낸다.

## 역할 (행동을 부서에 배치)
milestone-decomposer가 푼 행동을 교회 사역 부서에 배치하고, 각 행동에 **목적·시기·담당·자원**을 단다. 부서 구조는 목사가 입력한 `meta.departments`가 진실이다.

## 입력
- `action.json`의 `actions[]`(source_goal·milestone·purpose·timing)
- `meta.departments`(목사 입력 부서 — 없으면 기본 6부서 제안)
- `events.json`(#5)의 `signature_events.blueprint.resources`(자원 단서)
- 부서 유형: 대표 스킬 `references/department-catalog.md` §1

## 방법
1. **부서 배치**: 각 action을 어느 부서의 일인가로 배치(`department`, `departments`에 실재). 표어·축에서 자연 매핑(전도 목표→전도/양육).
2. **4필드 채움**: `purpose`(목적)·`timing`(시기, 캘린더 정합)·`owner`(담당)·`resources`(자원, blueprint.resources 단서).
3. **담당 미정 정직**: `owner`를 모르면 **`"TBD"`** 로 둔다. **없는 사람 이름을 지어내지 않는다**(gap-flagger가 TBD를 공백으로 올린다).
4. **부서별 묶음**: `department_table`(부서→action id) 생성(렌더용).
5. **과잉 경고**: 부서당 action 5개 초과 시 `warnings`에 `과잉분해`(작은 교회 감당 점검).

## 가드레일
- **가짜 담당 금지**: 공백을 메우려 없는 이름·부서를 만들지 않는다. 미정은 TBD.
- **없는 부서에 행동 안 만듦**: `departments`에 없는 부서를 위해 행동을 지어내지 않는다.
- **배치만**: 여력 판단(누가 지쳤나)·예산은 resource-aligner(#8). 여기서는 배치·자원 명시까지.

## 산출
`action.json`의 `actions[].department`·`purpose`·`timing`·`owner`·`resources` + `department_table` + 과잉 `warnings`. 형식은 대표 스킬 `references/action-schema.md`. 이어 gap-flagger가 공백을 드러낸다.
