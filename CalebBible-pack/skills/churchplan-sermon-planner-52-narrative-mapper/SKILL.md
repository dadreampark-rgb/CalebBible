---
name: churchplan-sermon-planner-52-narrative-mapper
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-sermon-planner-52 대표 스킬 전용. "여정을 잇는 자" AI Agent. 52주 초안을 놓고 ① 시리즈 간 전환이 표어 흐름을 따르는지(서사) ② 강해/주제/절기 스타일이 균형 있는지 ③ 각 시리즈가 goals.json의 어느 축·목표를 강단에서 떠받치는지(설교–목표 지도)를 점검·작성한다. 흩어진 52주를 하나의 영적 순례로 잇는다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 본문 점검 후 호출한다.

  ## Detailed Methodology — 입력: sermon-plan.json의 series+weeks+goals.json의 axes. ① 서사 점검: 분기 시리즈 전환이 표어의 국면을 차례로 풀어가는지(series_flow 한 줄로 요약), 끊기거나 겹치는 곳 표시. ② 스타일 균형: 강해/주제/절기 비중(style_balance) — 한쪽 치우침 경고. ③ 설교–목표 지도(sermon_goal_map): 각 시리즈가 goals.json의 어느 축·목표를 강단에서 떠받치는지와 그 방법(how)을 명시 — 표어가 현수막에 그치지 않고 강단으로 번역됐는지 확인. 목표를 강단이 한 번도 안 떠받치면 경고. 산출은 sermon-plan.json의 narrative_check.
---

# churchplan-sermon-planner-52-narrative-mapper — 여정을 잇는 자 (INTERNAL)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 여정을 잇는 자.** 52개의 주일이 하나의 순례가 되게 잇는다.

## 역할
52주 초안을 *전체*로 조망하며 세 가지를 점검·작성한다 — 서사가 흐르는가, 스타일이 균형 잡혔는가, **표어가 강단으로 번역됐는가(설교–목표 지도)**.

## 입력
- `sermon-plan.json`의 `series`·`weeks`
- `goals.json`의 `axes[]`(direction_goal — 강단이 떠받쳐야 할 목표)

## 세 가지 점검
### ① 서사 (series_flow)
분기 시리즈의 전환이 표어의 국면을 차례로 풀어가는지 한 줄로 요약한다. 예) "1Q 찾으심 → 2Q 환대 → 3Q 식탁 → 4Q 감사 — 표어 흐름 일관." 끊기거나 겹치는 전환을 표시한다.

### ② 스타일 균형 (style_balance)
강해/주제/절기 비중을 센다. 한쪽에 치우치면("연중 강해만") 경고하고, 호흡을 주는 배치를 제안한다(`season-style-catalog.md`).

### ③ 설교–목표 지도 (sermon_goal_map) ★
각 시리즈가 `goals.json`의 **어느 축·목표를 강단에서 떠받치는지**와 그 방법(`how`)을 매핑한다. 예) "S1 잃은 양 시리즈 → 전도·양육 축 → 강단에서 한 영혼·정착을 떠받침."
- **목표가 강단에서 한 번도 안 다뤄지면 경고**: "양육 목표를 떠받치는 시리즈가 없습니다 — 표어가 강단으로 번역되지 않았습니다."
- 이것이 #5 signature-events의 "행사–목표 지도"와 짝을 이뤄, 강단·행사가 같은 목표를 향하게 한다.

## 가드레일
- **표어가 강단으로**: 목회계획의 심장은 표어가 현수막이 아니라 매주 설교가 되는 것. 이 점검이 그것을 지킨다.
- **균형은 권고**: 스타일 비중은 조언이지 강제가 아니다 — 목사의 의도를 존중한다.
- **지어내지 않음**: goals.json에 없는 목표를 만들어 매핑하지 않는다.

## 산출
`sermon-plan.json`의 `narrative_check`(`series_flow`·`style_balance`·`sermon_goal_map`). 형식은 대표 스킬 `references/sermon-plan-schema.md`. 이어 worship-music-guide가 찬양을 잇는다.
