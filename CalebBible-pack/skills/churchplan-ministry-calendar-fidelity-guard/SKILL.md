---
name: churchplan-ministry-calendar-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-ministry-calendar 대표 스킬 전용. "통합을 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)지어낸 통합(상속되지 않은 주차·설교·행사·캠페인을 캘린더가 새로 만듦) (2)깨진 격자(52주 중복·범위 이탈) (3)소진 은폐(밀집 경고·안식 계획 누락). 결정론 스크립트로 52주 무결성·상속 id 충실·밀집/안식 존재·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-ministry-calendar가 calendar.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_calendar.py로 (1)스키마·meta.chosen_theme·year·status (2)52주 무결성 — week 1~52 범위·중복 금지·52 미만 누락 경고·52 초과 위반 (3)상속 id 충실 — weeks[].sermon.series_id∈inputs_echo.from_sermon_plan.series_ids·weeks[].events[].id∈from_events.event_ids·weeks[].campaigns[].name∈campaigns_input[].name, 위배 시 위반(지어낸 통합 차단) (4)소진 방지 — density_warnings·rest_plan 키 존재, rest_plan 비면 경고(목자 지속가능성) + detect_density 연속고강도 run이 density_warnings에 빠지면 밀집은폐 위반(소진 은폐 차단) (5)3중 정합 — tri_consistency[].aligned=false면 경고 (6)확정 게이트 — status=확정인데 confirmed 없으면 위반. 스크립트 밖: 끼워맞춘 정렬·시즌 위장을 사람 눈으로. 실패 시 해당 분석 재실행.
---

# churchplan-ministry-calendar-fidelity-guard — 통합을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-ministry-calendar`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 통합을 지키는 자.** calendar.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 계획을 검증하지 않는다. **Claude가 통합을 오염시켰는지** 막는다:
1. **지어낸 통합** (ANCHOR #2): 상속되지 않은 주차·설교(series_id)·행사(event id)·캠페인(name)을 캘린더가 새로 만듦 — "여백을 채우려" 없던 것을 끼워 넣은 잔재.
2. **깨진 격자**: 52주 중복·범위 이탈 — 통합 골격이 무너짐.
3. **소진 은폐**: 밀집 경고(`density_warnings`)·안식 계획(`rest_plan`) 누락 — 부하를 숨겨 꽉 찬 달력을 좋아 보이게 함.

> 이 단계의 최우선 가드레일은 "상속·전사만(지어내지 않음)"과 "소진을 숨기지 않는다"다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_calendar.py <calendar.json>
```

스크립트가 검사하는 것:
1. **스키마·표어·year·status** — 필수 블록(meta·inputs_echo·weeks) + `meta.chosen_theme` 존재 + `year` 정수 + `status` ∈ {제안,확정}.
2. **52주 무결성** — week 1~52 범위·중복 금지·유효 주차 0개면 위반·52 미만 누락 경고·52 초과 위반.
3. **상속 id 충실** — `weeks[].sermon.series_id`∈`from_sermon_plan.series_ids`, `weeks[].events[].id`∈`from_events.event_ids`, `weeks[].campaigns[].name`∈`campaigns_input[].name`. 위배 시 위반(지어낸 통합 차단). **중복 주차에 숨긴 항목도 검사**(survivor만 보지 않음). weeks에 콘텐츠가 있는데 대응 출처 집합이 비면 **출처없음 위반**(garbage-in 차단).
4. **부하 재계산 대조** — `compute_load.py`(season-frame-catalog rubric)로 `weeks[].load.score/level`을 재계산해 표기값과 불일치 시 **부하조작 위반**(LLM 임의 부풀림 차단).
5. **격자 날짜·분기·월 대조** — `build_grid.py`(easter_calculator)로 결정론 격자를 만들어 `weeks[].date/quarter/month`와 불일치 시 위반(날짜·분기·월 hallucination 차단).
6. **소진 방지** — `density_warnings`·`rest_plan` 키 존재. `rest_plan` 비면 경고(목자 지속가능성 점검). **밀집 은폐 대조** — `compute_load.detect_density`(결정론 연속 '높음' 구간)가 적발한 `연속고강도` run이 `density_warnings`에 표시 안 되면 **밀집은폐 위반**(부하 재계산처럼, 진짜 연속 고강도를 빼서 꽉 찬 달력을 좋아 보이게 하는 소진 은폐 차단·가드레일 ④).
7. **3중 정합** — `tri_consistency[].aligned=false`면 경고(간극 점검).
8. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.

## 검증 후 처리
- **통과**: "검증 통과 — 모든 통합이 상속에서 왔고, 52주 격자 온전, 밀집·안식 표시됨" 반환. calendar.json 완료.
- **실패**: 위반 항목 구체 반환(예: "weeks[21].events[E9] — from_events.event_ids에 없음(지어낸 행사)", "week 13 중복"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **끼워맞춘 정렬**: season_alignment·tri_consistency가 `aligned:true`이나 실제 메시지가 따로 노는 사후 정당화 → 진짜 간극으로 교정.
- **빈칸 메우기 위장**: 부하가 낮은 주를 그럴듯한 행사로 채워 "통합"으로 포장 → 여백으로 되돌린다(여백도 계획).

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
