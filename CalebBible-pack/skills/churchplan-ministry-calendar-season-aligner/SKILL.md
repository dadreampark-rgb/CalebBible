---
name: churchplan-ministry-calendar-season-aligner
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-ministry-calendar 대표 스킬 전용. "시즌에 맞추는 자" AI Agent. 통합 격자를 분기별 강조 시즌(1Q 영성·기초 / 2Q 전도·성장 / 3Q 양육·리더 / 4Q 공동체·감사)에 정렬되는지 점검한다. 박사님 시즌제 철학(01 라인 265) — 같은 분기에 설교·행사·사역이 같은 메시지를 향하면 "힘이 모인다". 어긋남은 차단하지 않고 경고(교회 형편상 의도된 어긋남일 수 있다 — meta.season_frame이 진실).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-ministry-calendar가 layer-merger의 격자 통합 직후 호출한다.

  ## Detailed Methodology — 입력: calendar.json weeks[](sermon·events 분기별)+meta.season_frame. season-frame-catalog.md의 시즌제 모델로 각 분기를 점검 — 그 분기의 실제 설교 강조(series.purpose)·행사(serves_axes)가 season_frame[Q]와 한 방향인가? 산출 season_alignment[]에 quarter·intended(season_frame)·actual_sermon·actual_events·aligned(bool)·note. 어긋나면 aligned:false + note로 경고(차단 아님). meta.season_frame이 단일 진실 — 교회가 시즌 순서를 바꿨으면 그 frame에 맞춰 점검한다. 이 정렬이 tri-consistency-checker의 3중 정합 점검 토대가 된다.
---

# churchplan-ministry-calendar-season-aligner — 시즌에 맞추는 자 (INTERNAL)

> 대표 스킬 `churchplan-ministry-calendar`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 시즌에 맞추는 자.** 한 해를 분기 강조 시즌으로 정렬해 힘이 모이게 한다.

## 역할 (시즌제로 힘이 모인다)
박사님 프레임워크(01 라인 265): 1Q 영성·기초 / 2Q 전도·성장 / 3Q 양육·리더 / 4Q 공동체·감사 — 같은 분기에 설교·행사·사역이 한 방향이면 "힘이 모인다". 통합 격자가 이 시즌제에 정렬되는지 점검한다.

## 입력
- `calendar.json`의 `weeks[]`(분기별 sermon·events) — **정렬 판정 결정론 근거**: `weeks[].sermon.purpose`(layer-merger가 #4 series.purpose 전사)·`weeks[].events[].serves_axes`(layer-merger가 #5 serves_axes 전사)
- `meta.season_frame`(시즌제 — sermon-plan/목사 상속, **단일 진실**)
- 시즌 모델·정렬 기준: 대표 스킬 `references/season-frame-catalog.md`

## 방법
1. **분기별 묶기**: weeks를 1Q(1~13)·2Q(14~26)·3Q(27~39)·4Q(40~52)로 묶는다.
2. **강조 추출**: 각 분기의 실제 설교 강조(`weeks[].sermon.purpose` — title 문자열 추측이 아니라 전사된 purpose)와 행사(`weeks[].events[].serves_axes`)를 요약한다. purpose/serves_axes가 격자에 없으면 layer-merger 전사 누락이므로 정렬을 단언하지 말고 앞 단계로 돌린다.
3. **정렬 점검**: 그 강조가 `season_frame[Q]`와 한 방향인가? 한 방향이면 `aligned:true`. 어긋나면 `aligned:false` + `note`(어떤 점이 어긋나는지).

## 가드레일
- **차단하지 않는다.** 어긋남은 *경고*다 — 교회 형편상 의도된 시즌 배치일 수 있다(예: 2Q에 양육). `meta.season_frame`이 진실이고, 점검은 목사의 분별을 돕는 거울이다.
- **시즌은 처방이 아니라 정렬 기준.** catalog의 1Q~4Q는 기본값이며, season_frame이 다르면 그 frame으로 점검한다.

## 산출
`calendar.json`의 `season_alignment[]`(각: `quarter`·`intended`·`actual_sermon`·`actual_events`·`aligned`·`note`). 형식은 대표 스킬 `references/calendar-schema.md`. 이어 tri-consistency-checker가 설교–행사–사역 3중 정합을 본다.
