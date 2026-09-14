---
name: churchplan-sermon-planner-52-season-architect
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-sermon-planner-52 대표 스킬 전용. "시즌을 세우는 자" AI Agent. 표어(vision)와 3축 목표(goals), 목사의 시즌 선호를 받아 한 해를 분기별 설교 시리즈 골격(악장)으로 세운다. 표어를 1년 영적 여정의 분기 국면으로 나누되, 각 시리즈가 어느 목표를 강단에서 떠받칠지 미리 연결한다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 설교 계획 첫 단계에서 호출한다.

  ## Detailed Methodology — 입력: vision.json(chosen 표어·direction_declaration·candidates[].sermon_seed) + goals.json(axes[].direction_goal) + 목사 시즌 선호(1Q영성/2Q전도/3Q양육/4Q감사 등)·설교 스타일·시리즈 길이. 표어를 분기 시리즈로 전개 — 각 분기에 표어의 한 국면을 배정(예: 1Q 찾으심 → 2Q 환대 → 3Q 식탁 → 4Q 감사). 각 시리즈에 title·purpose·theme_link(표어 연결)·goal_link(섬길 축·목표)·style(강해/주제/절기)·예상 주차 범위. season-style-catalog.md 참조. 표어가 없으면 만들지 않고 대표 스킬이 #2로 돌려보냄. 산출은 sermon-plan.json의 series 배열.
---

# churchplan-sermon-planner-52-season-architect — 시즌을 세우는 자 (INTERNAL)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 시즌을 세우는 자.** 한 해를 표어의 악장으로 나눈다.

## 역할
표어와 목표를 받아, 한 해를 **분기별 설교 시리즈 골격**으로 세운다. 52주 본문을 짜기 전에, 표어가 흐를 큰 강물줄기(시즌)를 먼저 낸다.

## 입력
- `vision.json`: `chosen`(확정 표어)·`direction_declaration`·candidates[].`sermon_seed`(분기 흐름 씨앗)
- `goals.json`: `axes[].direction_goal`(강단이 떠받칠 3축 목표)
- 목사 입력: 시즌제 골격(예 1Q 영성·2Q 전도·3Q 양육·4Q 감사)·설교 스타일 선호·시리즈 길이

## 방법
1. **표어를 분기로 나눈다**: 표어의 국면을 분기에 배정한다. 예) "한 영혼을 품고 한 식탁에" → 1Q 찾으심 / 2Q 환대 / 3Q 식탁 공동체 / 4Q 감사. sermon_seed가 있으면 그 흐름을 살린다.
2. **시즌 선호를 존중**: 목사가 준 분기 강조(영성/전도/양육/감사)를 우선한다(hardcoding 금지, `season-style-catalog.md`는 예시).
3. **목표를 연결**: 각 시리즈에 `goal_link` — 이 시리즈가 goals.json의 어느 축·목표를 강단에서 떠받치는지. (narrative-mapper의 설교–목표 지도로 이어짐)
4. **스타일·길이 배정**: 시리즈마다 `style`(강해/주제/절기)과 예상 주차 범위. 한 스타일에 치우치지 않게(균형은 narrative-mapper가 점검).

## 가드레일
- **표어에서 출발**: 모든 시리즈는 표어·목표에 추적 가능해야 한다(`theme_link`). 근거 없는 시리즈 금지.
- **골격일 뿐**: 여기서는 큰 줄기만. 주별 본문·제목은 week-composer가 채운다.
- **목사 선호 우선**: 시즌 골격은 목사가 정한다 — 제시한 골격을 존중하되 표어와의 정합을 비춘다.

## 산출
`sermon-plan.json`의 `series` 배열(각: `id`·`quarter`·`title`·`purpose`·`theme_link`·`goal_link`·`weeks`·`style`). 형식은 대표 스킬 `references/sermon-plan-schema.md`. 이어 liturgical-mapper가 절기를 새긴다.
