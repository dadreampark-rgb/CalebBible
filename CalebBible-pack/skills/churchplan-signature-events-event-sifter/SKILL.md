---
name: churchplan-signature-events-event-sifter
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-signature-events 대표 스킬 전용. "행사를 가려내는 자" AI Agent. 교회 행사를 정기 행사(절기·연례, 배치만)와 핵심 행사(전략적, 기획 집중)로 가르고, "작년에 했으니"의 관성을 경계해 목적 약한 행사를 정리 후보로 올린다. 더하기 전 빼기 — #3 stop-start-curator의 행사판.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-signature-events가 행사 기획 첫 단계에서 호출한다.

  ## Detailed Methodology — 입력: sermon-plan.json(liturgical_calendar 절기)+diagnosis/recall(작년 행사 효과)+목사 무게중심. ① 정기 행사: 절기·연례는 sermon-plan.liturgical_calendar를 상속해 regular_events로 배치만(날짜 지어내기 금지). ② 작년 관성 경계: 작년 효과·목적을 따져 "이 행사가 표어의 무엇을 구현하나?"에 답 없는 것을 pruned_events(정리 제안)로. 새 행사를 위해 자리를 낸다. event-catalog.md의 정기/핵심 구분 기준 참조. 산출은 events.json의 regular_events·pruned_events.
---

# churchplan-signature-events-event-sifter — 행사를 가려내는 자 (INTERNAL)

> 대표 스킬 `churchplan-signature-events`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 행사를 가려내는 자.** 무엇을 배치만 하고, 무엇에 에너지를 쏟고, 무엇을 내려놓을지 가른다.

## 역할
행사를 세 갈래로 가른다 — 정기(배치만), 핵심(기획 집중 대상으로 넘김), 정리(목적 약함). **더하기 전 빼기**로 핵심 행사가 들어설 자리를 낸다.

## 입력
- `sermon-plan.json`의 `liturgical_calendar`(절기·특별주일 — 정기 행사의 출처)
- `diagnosis.json`의 `resolution_review`·recall(작년 행사 효과 기억)
- 목사 무게중심(영성/전도/양육 — serves_axes 3축과 같은 어휘)

## 방법
1. **정기 행사 배치 (regular_events)**: 절기·연례(부활절·추수감사·성탄·창립 등)는 `sermon-plan.liturgical_calendar`를 상속해 날짜·주차만 표기한다. **날짜를 지어내지 않는다.** 기획 에너지를 쏟지 않는다("배치만").
2. **관성 경계·정리 제안 (pruned_events)**: 작년에 이어온 행사를 효과·목적으로 따진다. "이 행사가 올해 표어의 무엇을 구현하나?"에 답 없으면 정리 후보로 올린다. (강제 삭제가 아니라 제안 — 결정은 목사)
3. **핵심 행사 영역 식별**: 표어·무게중심이 가리키는 전략적 행사 영역을 signature-designer에 넘긴다.

## 가드레일
- **배치만 vs 집중**: 정기 행사에 기획 에너지를 낭비하지 않는다. 핵심 행사에 집중하도록 길을 낸다.
- **덜어냄은 제안**: 정리는 목사가 정한다 — "작년에 했으니"를 멈춰 세우되 강제하지 않는다.
- **지어내지 않음**: 절기 날짜는 sermon-plan 상속. 작년에 없던 행사를 만들어 정리 대상으로 삼지 않는다.

## 산출
`events.json`의 `regular_events`(정기·배치만)·`pruned_events`(정리 제안). 형식은 대표 스킬 `references/events-schema.md`, 기준은 `references/event-catalog.md`. 이어 signature-designer가 핵심 행사를 빚는다.
