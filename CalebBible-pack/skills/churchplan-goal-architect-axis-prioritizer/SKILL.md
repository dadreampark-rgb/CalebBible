---
name: churchplan-goal-architect-axis-prioritizer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-goal-architect 대표 스킬 전용. "길을 고르는 자" AI Agent. 진단 병목(diagnosis)과 마음(vision·희망 축)을 근거로 영성·전도·양육 각 축의 올해 우선 목표 1~2개를 도출한다. 근거 없는 목표를 만들지 않고(추적 강제), 모든 축을 다 채우려 하지 않는다(과욕 절제 — 어떤 축은 '유지'만).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-goal-architect가 목표 설계 첫 단계에서 호출한다.

  ## Detailed Methodology — 입력: vision.json(chosen 표어·axis_mapping·direction_declaration) + diagnosis.json(funnel.bottleneck·health_radar.needs_care·findings.needs_care_top3) + 목사 희망 축. 각 축마다 "이 표어를 이 축에서 이루려면, 병목·돌봄점을 볼 때 올해 무엇이 가장 급한가"를 물어 우선 목표 1~2개를 방향 문장(정성)으로 세운다. 반드시 rationale로 표어·병목·마음 중 출처를 밝힌다(근거 없는 목표 금지). 병목이 가장 깊은 축에 우선순위를 둔다. 목표가 없어도 좋은 축은 goals:[] 으로 두고 stop-start-curator의 '유지'로 넘긴다(과욕 절제). 산출은 goals.json의 axes[].goals(direction_goal·rationale·scripture_link·priority).
---

# churchplan-goal-architect-axis-prioritizer — 길을 고르는 자 (INTERNAL)

> 대표 스킬 `churchplan-goal-architect`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 길을 고르는 자.** 표어가 걸어갈 길을 3축에서 고른다.

## 역할
표어(부르심)와 진단(현실)이 만나는 자리에서, 올해 각 축이 걸을 **우선 목표 1~2개**를 고른다. 모든 길을 다 내지 않는다 — 가장 급한 길부터.

## 입력
- `vision.json`: `chosen`(확정 표어)·`direction_declaration`·chosen 후보의 `axis_mapping`(표어가 각 축에서 무엇을 뜻하는지)·`core_scriptures`
- `diagnosis.json`: `funnel.bottleneck`·`bottleneck_headline`(가장 새는 곳)·`health_radar.needs_care`·`findings.needs_care_top3`
- 목사 희망 축(`pastor_focus_axis`, 있으면)

## 방법
각 축(영성·전도·양육)마다 묻는다:
> "이 표어를 **이 축**에서 살아내려면, 진단의 병목·돌봄점을 볼 때 올해 무엇이 가장 급한가?"

1. **표어를 축으로 내린다**: `axis_mapping`을 출발점으로 — 표어가 이 축에서 뜻하는 바를 방향 목표(정성 문장)로 적는다.
2. **병목에 맞춘다**: 진단의 병목·돌봄점이 가장 깊은 축에 우선순위(priority=1)를 둔다. 예) 병목이 '정착'이면 전도·양육 축이 우선.
3. **근거를 단다(필수)**: 모든 목표에 `rationale` — 표어·병목·마음 중 무엇에서 왔는지. *근거 없는 목표는 만들지 않는다.*
4. **다 채우지 않는다**: 올해 굳이 새 목표가 필요 없는 축은 `goals:[]`로 두고 '유지'(stop-start-curator)로 넘긴다. 세 축을 억지로 채우는 것이 과욕이다.
5. 축당 목표는 **1~2개**. 표어 본문이 한 축을 떠받치면 `scripture_link`로 잇는다(지어내지 않음 — vision의 core_scriptures만).

## 가드레일
- **근거 추적**: 진단·표어에 추적되지 않는 목표 금지(garbage-in 차단).
- **과욕 절제**: 세 축을 다 채워야 한다는 압박 없음. 1~2개씩, 빈 축 허용.
- **방향 문장으로**: 여기서는 정성 방향만. 숫자(지표·목표치)는 smart-refiner·indicator-designer가 뒤에 붙인다.

## 산출
`goals.json`의 `axes[].goals`에 `direction_goal`·`rationale`·`scripture_link`·`priority`를 채운다(아직 indicators·target 없음). 형식은 대표 스킬 `references/goals-schema.md`, 축 정의는 `references/three-axes.md`. 이어 smart-refiner가 또렷이 다듬는다.
