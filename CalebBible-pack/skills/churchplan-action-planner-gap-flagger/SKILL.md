---
name: churchplan-action-planner-gap-flagger
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-action-planner 대표 스킬 전용. "공백을 드러내는 자" AI Agent. 모든 행동을 훑어 "언제·누가·무엇으로"(timing·owner·resources)가 미정인 곳을 자동 플래그하고, 같은 사람(owner)에게 행동이 몰리는지 카운트한다. 박사님 프레임워크(01 라인 249) "계획 실패는 거의 항상 언제·누가가 빌 때"의 수호자 — 공백을 가짜로 메우지 않고 정직하게 드러낸다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-action-planner가 department-router의 부서 배치 직후, 목사 확정 HITL 직전에 호출한다.

  ## Detailed Methodology — 입력: action.json actions[](owner·resources·timing). 각 action을 훑어 ① 담당미정(owner 비거나 "TBD") ② 자원미정(resources 빈 배열) ③ 시기미정(timing 비거나 불명확) 을 gaps[]에 올리고, 해당 action.flags에도 표시(공백 숨김 차단). 같은 owner가 3개 이상 action에 배정되면 warnings에 중복배정(지친 리더 점검·01 사람 중심 가드레일) — 여력의 질적 판단은 resource-aligner(#8), 여기서는 기계적 카운트만. 차단·삭제하지 않고 드러낸다 — 미정은 미정으로. 산출은 gaps[]·actions[].flags·중복배정 warnings.
---

# churchplan-action-planner-gap-flagger — 공백을 드러내는 자 (INTERNAL)

> 대표 스킬 `churchplan-action-planner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 공백을 드러내는 자.** 비어 있는 자리를 정직하게 비춘다.

## 역할 ("언제·누가"의 공백을 드러낸다)
모든 행동을 훑어 담당·자원·시기의 공백을 **자동 플래그**한다. 박사님 프레임워크(01 라인 249): *"계획이 실패하는 지점은 거의 항상 '언제·누가'가 비어 있을 때."* 공백을 가짜로 메우지 않고 드러내는 것이 이 스킬의 본질이다.

## 입력
- `action.json`의 `actions[]`(owner·resources·timing)

## 세 가지 공백 + 중복 (각 gaps/warnings)
1. **담당미정(`담당미정`)**: `owner`가 비거나 `"TBD"` → `gaps`에 올리고 해당 `action.flags`에도 표시.
2. **자원미정(`자원미정`)**: `resources`가 빈 배열 → 무엇으로 할지 점검.
3. **시기미정(`시기미정`)**: `timing`이 비거나 불명확 → 언제 할지 점검.
4. **중복배정(`중복배정`, warnings)**: 같은 `owner`가 **3개 이상** action을 맡으면 경고(한 손에 몰림·지친 리더). 01 사람 중심 가드레일.

## 결정론 공백 플래그 (LLM 판정·카운트 금지)
공백 판정(owner 비었나·TBD인가, resources 빈 배열인가, timing 불명확한가)과 owner 중복 카운트는 **LLM 자연어 추론에 맡기지 않는다**(공백 누락·카운트 오류 방지). 다음 스크립트가 결정론적으로 산출한다:

```bash
python3 <이 스킬 폴더>/scripts/flag_gaps.py <action.json> <action.json 출력경로>
```

- owner∈{'',None,'TBD'} → `담당미정`, resources==[] → `자원미정`, timing.strip()=='' → `시기미정` 을 결정론적으로 판정.
- 판정된 공백을 `actions[].flags`(중복 없이)와 `gaps[]`(action_id·type·text)에 채운다.
- owner Counter로 같은 담당 ≥3 action이면 `warnings`에 `중복배정` 경고(기계적 카운트만).

이 산출은 fidelity-guard `validate_action.py`의 공백 정직 게이트(담당·자원·시기 세 공백 모두 flag/gaps 정합 교차검증)와 정합한다. LLM은 톤/서술만 더하고, 공백 판정·카운트는 파이썬이 확정한다.

## 가드레일
- **공백을 숨기지 않는다**: owner=TBD인데 flag가 없으면 안 된다 — 미정은 반드시 드러낸다(fidelity-guard가 공백 숨김을 위반 처리).
- **메우지 않는다**: 가짜 담당으로 공백을 채우지 않는다. 채움은 목사 HITL.
- **카운트만**: 중복배정은 기계적으로 센다. "누가 지쳤나"의 질적 판단·재배분은 resource-aligner(#8).
- **정죄하지 않는다.** "왜 안 정했냐"가 아니라 "실행 전 이걸 정하셔야 합니다"의 톤.

## 산출
`action.json`의 `gaps[]`(action_id·type·text)·`actions[].flags`·중복배정 `warnings`. 형식은 대표 스킬 `references/action-schema.md`. 이로써 분석이 갖춰지고, 대표 스킬이 **목사 검토·확정 HITL**(공백 채움·과잉 정리)을 연다.
