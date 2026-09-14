---
name: churchplan-signature-events-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-signature-events 대표 스킬 전용. "행사를 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)목적 없는 행사(serves_axes/rationale 없는 "작년에 했으니"의 잔재) (2)행사 과다(핵심 5개 초과로 깊이가 깨짐) (3)표어 이탈(표어 미확정·정합 없음). 결정론 스크립트로 목적 추적·행사 상한·표어/설교 정합·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-signature-events가 events.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_events.py로 (1)스키마·meta.chosen_theme·status (2)목적 추적 — 각 signature_event의 serves_axes(섬기는 축)+rationale(근거) 필수, 없으면 위반(목적 없는 행사 차단) (3)행사 상한 — 0개 위반·5개 초과 위반(행사 수보다 깊이) (4)1페이지 기획안 핵심 필드(purpose·timing·success_signal) 점검 (5)표어 연결(theme_link)·설교 정합(sermon_sync.aligned=false) 경고 (6)확정 게이트(status=확정인데 confirmed 없으면 위반). 스크립트 밖: 표어와 무관한 끼워맞춤 목적을 인간 눈으로. 실패 시 해당 분석 재실행.
---

# churchplan-signature-events-fidelity-guard — 행사를 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-signature-events`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 행사를 지키는 자.** events.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 행사를 검증하지 않는다. **Claude가 행사 기획을 오염시켰는지** 막는다:
1. **목적 없는 행사** (ANCHOR #2): `serves_axes`·`rationale` 없는 행사 — "이 행사가 표어의 무엇을 구현하나?"에 답 없는 "작년에 했으니"의 잔재.
2. **행사 과다**: 핵심 행사 5개 초과 — 행사 수보다 깊이를 깨뜨림.
3. **표어 이탈**: 표어 미확정·표어와 정합 없는 행사.

> 이 단계의 최우선 가드레일은 "목적 없는 행사는 만들지 않는다"와 "행사 수보다 깊이"다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_events.py <events.json>
```

스크립트가 검사하는 것:
1. **스키마·표어·status** — 필수 블록(meta·inputs_echo·signature_events) + `meta.chosen_theme` 존재 + `status` ∈ {제안,확정}.
2. **목적 추적** — 각 행사 `serves_axes`(≥1) + `rationale` 필수. 없으면 위반(목적 없는 행사 차단).
3. **행사 상한** — 0개 위반, 5개 초과 위반.
4. **1페이지 기획안** — `blueprint.purpose`·`timing`·`success_signal` 점검(누락 경고).
5. **표어·설교 정합** — `theme_link` 누락 경고, `sermon_sync.aligned=false` 경고.
6. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.
7. **절기 날짜·주차 결정론 대조** — `easter_calculator`(같은 패키지의 결정론 절기 계산기, 같은 scripts/에 복사본)로 2027 절기 격자를 산출해 `regular_events[].when`의 주차/날짜(부활주일 13주 2027-03-28·성령강림 20주·추수감사 47주 등)와 대조. 불일치 시 위반(절기 날짜·주차 지어내기 차단). `signature_events[].sermon_sync.linked_weeks`가 1~총주차 범위 밖이면 위반(존재하지 않는 주차 매핑 금지). `serves_axes`·`serves_goals` 원소가 비-문자열이면 위반(렌더러 join 계약 일치).
8. **행사–목표 지도 결정론 대조** — `event_goal_map`이 있으면 `signature_events`에서 재계산한 정규 지도(blueprint-renderer의 `build_event_goal_map`과 byte-for-byte 동일 로직)와 1:1 대조. 다르면 위반(LLM 자유텍스트·지어낸 행/축/목표/시기 차단 — plan-compiler #10가 사실로 읽으므로). blueprint-renderer 재실행으로 재기록.

## 검증 후 처리
- **통과**: "검증 통과 — 모든 행사에 목적·근거 있음, 3~5개 이내, 표어 정합" 반환. events.json 완료.
- **실패**: 위반 항목 구체 반환(예: "signature_events[E3] serves_axes 없음 — 목적 없는 행사", "핵심 행사 6개 — 상한 초과"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **끼워맞춤 목적**: serves_axes·rationale은 있으나 표어와 실제 무관한 사후 정당화 → 진짜 목적으로 교정하거나 정리.
- **관성 행사 위장**: "작년에 했으니"를 그럴듯한 목적으로 포장한 것 → event-sifter 정리 후보로.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
