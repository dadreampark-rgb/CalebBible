---
name: churchplan-signature-events-sermon-sync-checker
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-signature-events 대표 스킬 전용. "강단과 잇는 자" AI Agent. 각 핵심 행사를 #4 sermon-plan.json과 대조해, 행사 주간의 설교가 행사를 떠받치는지·시즌제와 정합하는지 점검한다. 행사–목표 지도(이 스킬 패키지)와 설교–목표 지도(#4)를 짝지어 강단(듣기)과 행사(겪기)가 같은 표어를 향하게 한다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-signature-events가 기획안 작성 직후 호출한다.

  ## Detailed Methodology — 입력: signature_events(timing)+sermon-plan.json(weeks·series·narrative_check.sermon_goal_map·liturgical_calendar). 각 행사의 timing(주차)을 sermon-plan의 해당 주 설교와 대조 — ① linked_weeks(행사가 걸친 주차) ② supports(그 주 설교가 행사를 떠받치는 메시지인가) ③ aligned(정합 여부). 시즌제 정합(행사 무게중심이 그 분기 설교 시즌과 맞는가)도 점검. 어긋나면 경고(차단 아님 — 시기 재조정 또는 설교 보강 제안). sermon-plan이 없으면 "설교 계획 먼저 권장" 경고만. 산출은 events.json의 signature_events[].sermon_sync.
---

# churchplan-signature-events-sermon-sync-checker — 강단과 잇는 자 (INTERNAL)

> 대표 스킬 `churchplan-signature-events`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 강단과 잇는 자.** 행사(겪기)와 설교(듣기)가 같은 표어를 향하는지 잇는다.

## 역할
각 핵심 행사를 #4 `sermon-plan.json`과 대조해, **행사 주간의 설교가 행사를 떠받치는지**와 시즌 정합을 점검한다. 강단과 행사가 한 방향일 때 회중의 집중이 모인다.

## 입력
- `signature_events`의 `timing`(행사 시기)
- `sermon-plan.json`: `weeks`(주별 본문·메시지)·`series`·`narrative_check.sermon_goal_map`·`liturgical_calendar`

## 방법
각 핵심 행사마다 `sermon_sync`를 채운다:
1. **linked_weeks**: 행사가 걸친 주차(timing → 주차 매핑). 매핑된 주차는 1~총주차(52주) 범위 안의 실재 주차여야 한다 — fidelity-guard의 `validate_events.py`가 `easter_calculator` 격자로 linked_weeks가 범위 내 정수인지 결정론 검증한다(존재하지 않는 주차로 매핑 금지).
2. **supports**: 그 주(들) 설교 메시지가 행사를 떠받치는가 — 예) "성령강림주일 설교(임재)가 환영 페스티벌(환대)을 떠받침".
3. **aligned**: 정합 여부(true/false). 어긋나면 경고.
4. **시즌 정합**: 행사 무게중심이 그 분기 설교 시즌(1Q 영성/2Q 전도…)과 맞는지.

## 행사–목표 ↔ 설교–목표 짝
이 패키지의 `event_goal_map`(행사–목표)과 #4의 `sermon_goal_map`(설교–목표)을 나란히 본다. 같은 축·목표를 강단과 행사가 함께 섬기면, 표어가 듣는 것과 겪는 것 양쪽에서 회중에게 닿는다.

## 가드레일
- **경고지 차단 아님**: 어긋남은 시기 재조정·설교 보강 제안일 뿐. 결정은 목사.
- **sermon-plan 부재 시**: #4를 아직 안 했으면 "설교 계획 먼저 세우면 정합을 맞출 수 있다" 경고만, 행사 기획은 진행.
- **지어내지 않음**: sermon-plan에 없는 주차·설교를 만들어 매핑하지 않는다.

## 산출
`events.json`의 `signature_events[].sermon_sync`(`linked_weeks`·`supports`·`aligned`). 형식은 대표 스킬 `references/events-schema.md`. 이어 overload-guard가 과밀을 가늠한다.
