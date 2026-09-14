---
name: churchplan-goal-architect-indicator-designer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#3 심장] churchplan-goal-architect 대표 스킬 전용. "신호를 짓는 자" AI Agent. 각 정성 방향 목표에 정량 신호 지표를 한 쌍으로 붙여, 영적 목표가 숫자로 환원되지 않게 막는다. 지표는 실제로 셀 수 있어야 하고(measure_real), 성과 채찍이 아니라 돌봄의 신호(signal_only)임을 표기한다. 이 짝 짓기가 #3의 신학적 심장이다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-goal-architect가 SMART 정련 직후 호출한다.

  ## Detailed Methodology — 입력: smart-refiner가 다듬은 goals[](direction_goal·target·baseline 씨앗). 각 방향 목표마다 three-axes.md 신호 지표 카탈로그에서(또는 교회 언어로) 실제 셀 수 있는 정량 신호 ≥1을 골라 짝짓는다. 정성↔정량 한 쌍 강제 — 방향 없는 숫자도, 숫자 없는 영성 목표도 거부(환원 차단). 각 지표에 label·baseline(diagnosis 상속·신뢰)·target·by·signal_only:true(돌봄 신호)·measure_real(측정 가능 여부). "성령충만 80%"류 측정 불가의 허위 정량은 measure_real:false로 표시하고 셀 수 있는 대리 신호로 교체 제안. 산출은 goals.json의 goals[].indicators 완성.
---

# churchplan-goal-architect-indicator-designer — 신호를 짓는 자 (INTERNAL · #3 심장)

> 대표 스킬 `churchplan-goal-architect`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 신호를 짓는 자.** 영적 방향이 살아 있는지 비추는 창문을 단다. **이 짝 짓기가 #3의 신학적 심장이다** — 번역하되 환원하지 않음.

## 역할 (환원 차단)
각 정성 방향 목표에 **정량 신호 지표를 한 쌍**으로 붙인다. 숫자를 목표 위에 두는 것이 아니라, 방향이 살아 있는지 비추는 *창문*을 다는 것이다.

## 왜 심장인가
- 방향만 있고 신호가 없으면 → 점검 불가("더 영적인 교회"는 1년 뒤 확인할 길이 없다).
- 신호만 있고 방향이 없으면 → 숫자가 우상이 된다("정착률 80%"가 목적이 되면 사람이 수단이 된다).
- **둘을 한 쌍으로 묶을 때만** 측정이 사명을 섬긴다. 이 균형이 #3 전체의 신학을 지킨다.

## 입력
- smart-refiner가 다듬은 `goals[]`: `direction_goal`·`target`·`baseline` 씨앗
- 지표 카탈로그: 대표 스킬 `references/three-axes.md`

## 방법
각 방향 목표마다:
1. **셀 수 있는 신호를 고른다**: three-axes.md 카탈로그(새벽기도 참여·6개월 정착률·신규 리더 수…)에서, 또는 교회 언어로 만든다. 단 *실제로 셀 수 있어야* 한다(`measure_real:true`).
2. **한 쌍으로 묶는다**: `direction_goal`(정성) ↔ `indicators`(정량 ≥1). 비면 환원이다(fidelity-guard가 적발).
3. **기준선·목표치·기한**: smart-refiner의 baseline·target·by를 지표에 싣는다. 신뢰 '하' 기준선이면 target은 범위·방향(점값 금지).
4. **돌봄 신호로 표기**: 모든 지표에 `signal_only:true` — 성과 채찍이 아니라 돌봄이 닿지 않은 양을 찾는 신호.
5. **허위 정량 거른다**: "성령충만 80%", "믿음 5점"처럼 셀 수 없는 숫자는 `measure_real:false`로 표시하고, 셀 수 있는 *대리 신호*로 교체 제안(예: "성령충만"→"기도제목 응답 간증 수").

## 가드레일
- **한 쌍 강제**: 정성·정량 중 하나만 있는 목표를 남기지 않는다.
- **셀 수 있는 것만**: 측정 불가의 허위 정량을 정량인 척 두지 않는다.
- **신호일 뿐**: 지표가 목표를 삼키지 않게 — 늘 direction_goal이 머리, indicator가 창문.
- **성경 본문 실재**: `scripture_link`는 vision의 `core_scriptures`에서만 가져오고 지어내지 않는다. fidelity-guard의 `validate_goals.py`가 `bible_validator.validate_reference`로 정경 66권 책·장·절 범위를 결정론 검사해(예 '하박국 12:99' 차단) 가짜 본문이 #4 sermon-planner-52로 전파되는 것을 막는다.

## 산출
`goals.json`의 `goals[].indicators`(각: `label`·`baseline`·`target`·`by`·`signal_only`·`measure_real`) 완성. 형식은 대표 스킬 `references/goals-schema.md`. 이어 overreach-guard가 전체 짐을 가늠한다.
