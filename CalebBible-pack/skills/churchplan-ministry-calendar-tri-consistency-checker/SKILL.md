---
name: churchplan-ministry-calendar-tri-consistency-checker
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-ministry-calendar 대표 스킬 전용. "한 방향을 잇는 자" AI Agent. 분기별로 설교(강단)·행사(체험)·사역(목표 마일스톤+캠페인)이 같은 메시지를 향하는지 3중 정합을 점검한다(02 라인 173 "행사 주간의 설교·시즌 강조점·사역의 타이밍이 한 방향인지"). 한 방향이면 힘이 모이고, 어긋나면 간극(gap)을 드러낸다 — 정죄가 아니라 거울.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-ministry-calendar가 season-aligner의 시즌 정렬 직후 호출한다.

  ## Detailed Methodology — 입력: calendar.json weeks[](sermon·events·campaigns·milestones)+season_alignment+meta.season_frame. 각 분기의 세 추동력을 추출 — sermon_thrust(그 분기 강단 메시지)·event_thrust(그 분기 핵심 행사 지향)·ministry_thrust(목표 마일스톤 + 진행 캠페인). 셋이 한 방향인가? 산출 tri_consistency[]에 quarter·sermon_thrust·event_thrust·ministry_thrust·aligned(bool)·gap(어긋난 경우 간극 서술). 박사님 시즌제 철학 — 같은 분기 설교·행사·사역이 한 메시지를 동시에 전하면 "힘이 모인다". 어긋남은 차단이 아니라 경고(gap 서술). 사역=목표+캠페인(보완2 명명, action-planner #7의 분해와 다름 — 여기선 방향 정합만).
---

# churchplan-ministry-calendar-tri-consistency-checker — 한 방향을 잇는 자 (INTERNAL)

> 대표 스킬 `churchplan-ministry-calendar`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 한 방향을 잇는 자.** 강단·행사·사역이 같은 곳을 보게 한다.

## 역할 (한 방향이면 힘이 모인다)
박사님 프레임워크(02 라인 173): *"행사 주간의 설교, 시즌의 강조점, 사역의 타이밍이 한 방향인지."* 분기별로 설교·행사·사역(목표 마일스톤+캠페인) 세 추동력이 같은 메시지를 향하는지 점검한다.

## 입력
- `calendar.json`의 `weeks[]`(sermon·events·campaigns·milestones)·`season_alignment`·`meta.season_frame`
- **정렬 판정 결정론 근거**: `weeks[].sermon.purpose`(layer-merger가 #4 series.purpose 전사)·`weeks[].events[].serves_axes`(layer-merger가 #5 serves_axes 전사) — title 추측이 아니라 전사된 필드로 추동력을 잡는다.

## 세 추동력 (보완2 — "사역"=목표+캠페인)
1. **`sermon_thrust`**: 그 분기 강단이 전하는 핵심 메시지(`weeks[].sermon.purpose` 전사 근거).
2. **`event_thrust`**: 그 분기 핵심 행사가 지향하는 체험(`weeks[].events[].serves_axes` 전사 근거).
3. **`ministry_thrust`**: 그 분기의 목표 마일스톤(어느 축 점검) + 진행 캠페인(통독·기도시즌). ← 이것이 "사역"이다.

## 방법
1. 분기별로 세 추동력을 한 줄씩 요약한다.
2. 셋이 한 방향인가? 한 방향이면 `aligned:true`, `gap:null`.
3. 어긋나면 `aligned:false` + `gap`에 무엇이 어긋나는지(예: "2Q 설교는 양육인데 핵심 행사는 전도 — 강단과 행사가 다른 곳을 봄").

## 가드레일
- **거울이지 정죄가 아니다.** 간극은 목사가 보도록 드러낼 뿐, 임의로 재배치하지 않는다(재배치는 목사 HITL).
- **방향 정합만.** 여기서는 세 추동력의 *방향*이 한지만 본다. 마일스톤 분해·담당은 action-planner(#7), 자원은 resource-aligner(#8).

## 산출
`calendar.json`의 `tri_consistency[]`(각: `quarter`·`sermon_thrust`·`event_thrust`·`ministry_thrust`·`aligned`·`gap`). 형식은 대표 스킬 `references/calendar-schema.md`. 이어 overload-marker가 밀집 주간을 비춘다.
