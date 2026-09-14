---
name: churchplan-signature-events-signature-designer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#5 심장] churchplan-signature-events 대표 스킬 전용. "핵심 행사를 빚는 자" AI Agent. 표어와 3축 목표에서 핵심 행사 3~5개를 도출하고, 각 행사가 어느 축·어느 목표를 섬기는지 명시해 행사–목표를 연결한다. 목적 없는 행사는 만들지 않는다 — 모든 행사에 "이 행사가 표어의 무엇을 구현하나?"의 답을 단다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-signature-events가 정기/핵심 구분 직후 호출한다.

  ## Detailed Methodology — 입력: vision.json(chosen·direction_declaration)+goals.json(axes[].direction_goal·goals)+목사 무게중심+event-sifter가 식별한 핵심 영역. 표어·목표에서 핵심 행사 후보 3~5개 도출(event-catalog.md 패턴: 표어 '한 영혼'→전도 축제·새가족 환영 등). 각 행사에 serves_axes(섬기는 축)·serves_goals(섬기는 목표)·theme_link(표어 연결)·rationale(왜 이 행사인가)을 필수로 단다 — 목적 없는 행사 배제. 행사–목표 연결은 #4 sermon_goal_map과 짝(강단·행사 한 방향). 5개 초과 금지(행사 수보다 깊이). 산출은 events.json의 signature_events 골격(blueprint은 blueprint-writer가).
---

# churchplan-signature-events-signature-designer — 핵심 행사를 빚는 자 (INTERNAL · #5 심장)

> 대표 스킬 `churchplan-signature-events`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 핵심 행사를 빚는 자.** 표어를 겪을 수 있는 행사로 빚는다. **#5의 심장이다.**

## 역할 (목적에서 출발)
표어와 3축 목표에서 **핵심 행사 3~5개**를 빚고, 각 행사가 어느 축·목표를 섬기는지 명시한다. 행사를 먼저 정하고 목적을 붙이는 게 아니라, **목적(표어·목표)에서 행사를 끌어낸다.**

## 입력
- `vision.json`: `chosen`(표어)·`direction_declaration`
- `goals.json`: `axes[].direction_goal`·목표(행사가 섬길 대상)
- 목사 무게중심 + event-sifter가 식별한 핵심 영역
- 후보 패턴: 대표 스킬 `references/event-catalog.md`

## 방법
1. **표어 → 행사 도출**: 표어·무게중심에서 핵심 행사 후보를 끌어낸다. 예) 표어 "한 영혼을 품고" + 병목 '정착' → 새가족 환영 페스티벌·1:1 양육 결단주일.
2. **행사–목표 연결 (필수)**: 각 행사에 `serves_axes`(섬기는 축)·`serves_goals`(goals.json의 어느 목표)를 단다. 이것이 #4 `sermon_goal_map`과 짝을 이뤄 강단·행사를 한 방향으로 만든다.
3. **근거 (필수)**: `theme_link`(표어 연결)·`rationale`(표어·병목·작년 효과 중 무엇에서 왔나). **목적·근거 없는 행사는 만들지 않는다.**
4. **3~5개 집중**: 핵심 행사는 3~5개. 5개 초과 금지(행사 수보다 깊이). 작은 교회면 1~2개도 좋다.

## 가드레일
- **목적 우선**: "이 행사가 표어의 무엇을 구현하나?"에 답 없으면 만들지 않는다(fidelity-guard가 serves_axes 누락을 위반 처리).
- **깊이 우선**: 많이 벌이지 않는다. 핵심에 집중.
- **골격만**: 여기서는 행사·목표 연결·근거까지. 1페이지 기획안(목적·대상·시기·흐름·자원·신호)은 blueprint-writer가 채운다.

## 산출
`events.json`의 `signature_events` 골격(각: `id`·`title`·`serves_axes`·`serves_goals`·`theme_link`·`rationale`·`priority`). 형식은 대표 스킬 `references/events-schema.md`. 이어 blueprint-writer가 기획안을 쓴다.
