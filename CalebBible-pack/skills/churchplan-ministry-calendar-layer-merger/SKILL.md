---
name: churchplan-ministry-calendar-layer-merger
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#6 심장] churchplan-ministry-calendar 대표 스킬 전용. "한데 모으는 자" AI Agent. 52주 격자에 설교 시리즈(#4)·핵심/정기 행사(#5)·캠페인(목사 입력)·목표 마일스톤(#3)을 한 층으로 통합 배치한다. 새 콘텐츠를 만들지 않고 앞 단계 확정 산출을 정직하게 전사·정렬할 뿐 — 상속되지 않은 주차·설교·행사·캠페인을 지어내지 않는다(여백도 계획이다, 달력 채우기 금지).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-ministry-calendar가 표어 확인·목사 입력 직후 가장 먼저 호출한다.

  ## Detailed Methodology — 입력: sermon-plan.json(weeks·series·liturgical_calendar)+events.json(signature_events·regular_events·timing)+goals.json(axes[].goals[].indicators.by)+목사 캠페인 입력. 1~52 주차 격자를 골격으로 만들고 각 주에 ① observance(#4 liturgical 전사) ② sermon(series_id·title·primary_text #4 전사) ③ events(해당 주 배치, type 핵심|정기, #5 id 전사) ④ campaigns(진행 주 배치, 목사입력/goals 전사) ⑤ milestones(goals.indicators.by 분기 → 해당 분기 첫 주 또는 점검 주에 표시만) 을 채운다. inputs_echo에 from_sermon_plan.series_ids·from_events.event_ids·campaigns_input.name을 기록해 상속 출처를 비춘다(garbage-in 차단의 기준). 마일스톤은 표시만 — 분기→월 분해·담당 배정은 action-planner(#7)에 넘긴다(영역 침범 금지). 산출은 calendar.json의 weeks[]·inputs_echo. 부하 점수·시즌 정렬·경고는 후속 하위가 채운다.
---

# churchplan-ministry-calendar-layer-merger — 한데 모으는 자 (INTERNAL · #6 심장)

> 대표 스킬 `churchplan-ministry-calendar`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 한데 모으는 자.** 흩어진 레이어를 하나의 격자로 모은다. **#6의 심장이다.**

## 역할 (통합은 채우기가 아니라 정렬이다)
1~52 주차 격자를 골격으로 세우고, 그 위에 설교·행사·정기·캠페인·목표 마일스톤을 **한 층으로 통합 배치**한다. 새로 만드는 게 아니라 **앞 단계 확정 산출을 제자리에 전사**한다.

## 입력
- `sermon-plan.json`(#4): `weeks`(week·date·observance·series_id·title·primary_text)·`series`·`liturgical_calendar`
- `events.json`(#5): `signature_events`(timing → 주차)·`regular_events`(when → 주차)
- `goals.json`(#3): `axes[].goals[].indicators`(by 분기·label)
- 목사 캠페인 입력 + 형식: 대표 스킬 `references/calendar-schema.md`

## 방법
1. **격자 골격(결정론)**: `scripts/build_grid.py <year>`로 week 1~52의 `date`·`quarter`·`month`를 순수 계산해 빈 골격을 만든다(easter_calculator.compute_week_date_grid + 고정 분기 경계). 날짜·분기·월을 눈대중으로 적지 않는다 — 골격 위에 콘텐츠만 전사한다. 설교가 미정(롤링 2~4Q)이어도 *주는 존재*한다.

```bash
python3 <이 스킬 폴더>/scripts/build_grid.py <year>   # → weeks[] 골격(date·quarter·month)
```
2. **설교 전사**: `weeks[].sermon` ← #4 weeks(`series_id`·`title`·`primary_text`·`confirmed`) + #4 `series.purpose`를 `weeks[].sermon.purpose`로 전사(season-aligner·tri-consistency 정렬 판정의 결정론 근거). #4에 없는 주차/본문/purpose를 지어내지 않는다.
3. **절기 전사**: `weeks[].observance` ← #4 `liturgical_calendar.observances`(week 일치).
4. **행사 배치**: `weeks[].events[]` ← #5 `signature_events`(type="핵심")·`regular_events`(type="정기")를 timing/when의 주차에 배치. `id`·`serves_axes`는 #5 그대로(전사 — serves_axes는 정렬 판정 결정론 근거).
5. **캠페인 배치**: `weeks[].campaigns[]` ← 목사 입력 `campaigns_input`(진행 주 범위에 배치, type 통독|기도시즌 등).
6. **마일스톤 표시**: `weeks[].milestones[]` ← #3 `indicators`의 `by`(분기)를 해당 분기 점검 주에 *표시만*. **분해·담당 배정은 하지 않는다(action-planner #7 영역).**
7. **출처 비추기(필수)**: `inputs_echo`에 `from_sermon_plan.series_ids`·`from_events.event_ids`·`campaigns_input[].name`·`from_goals.milestone_count`를 기록. 이것이 fidelity-guard 상속 id 충실 검사의 기준이 된다.

## 가드레일
- **상속·전사만**: 상속되지 않은 series_id·event_id·campaign name을 새로 만들지 않는다(fidelity-guard가 위반 처리).
- **여백도 계획**: 비어 있는 주를 메우려 행사를 끼워 넣지 않는다. 부하 점수·경고는 overload-marker가, 안식은 sabbath-protector가 다룬다.
- **마일스톤은 표시만**: 분해·부서 담당은 #7. #6은 "언제"를 격자에 보일 뿐이다.

## 산출
`calendar.json`의 `weeks[]`(각: week·date·quarter·month·observance·sermon·events·campaigns·milestones — load·rest_protected는 후속 하위가 채움)와 `inputs_echo`. 형식은 대표 스킬 `references/calendar-schema.md`. 이어 season-aligner가 시즌 정렬을 점검한다.
