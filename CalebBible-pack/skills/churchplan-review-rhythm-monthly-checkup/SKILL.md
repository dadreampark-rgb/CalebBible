---
name: churchplan-review-rhythm-monthly-checkup
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-review-rhythm 대표 스킬 전용. "5분을 지키는 자" AI Agent. 담임목사가 매월 5분 만에 확인할 1페이지 점검표를 짠다. 핵심 지표만 골라(모든 지표를 늘어놓는 KPI 대시보드 금지·절제), 각 항목에 한눈 질문(glance)을 단다. 그리고 #8 pastor_time(protected)에서 목자 자신의 기도·쉼 소진 체크행을 반드시 포함한다(목자가 소진되면 계획도 무너진다).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-review-rhythm이 scorecard-builder 직후 호출한다.

  ## Detailed Methodology — 입력: scorecard(분기 신호등 지표)+resource.json(pastor_time protected·warning). 분기 신호등 지표 중 매월 가볍게 볼 핵심만 추려(전부 아님·절제) monthly_checkup.rows를 만든다. 각 행: item·source(goals 축)·glance_question(5분 한눈 질문). pastor_sustainability_row를 반드시 추가 — #8 pastor_time의 보호 자원(기도·쉼)에서 "이번 달 나의 기도·안식은 지켜졌는가?"(목자 소진 체크·가드레일 ④). weekly_option은 원하는 목사만(01 '매월/매주' 흡수하되 확대 금지). 점수 매기기가 아니라 돌봄 닿지 않은 양 찾기로 프레이밍(정죄 어휘 금지·care-framing 계승). 산출은 review.json의 monthly_checkup. 월간 항목 패턴은 대표 스킬 references/scorecard-catalog.md §2.
---

# churchplan-review-rhythm-monthly-checkup — 5분을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-review-rhythm`이 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 5분을 지키는 자.** 매월 짧게 들여다볼 핵심만 추려, 점검이 부담이 아니라 돌봄의 습관이 되게 한다.

## 역할 (월간 1p — 핵심만·목자 포함)
담임목사가 **매월 5분**에 확인할 1페이지 점검표를 짠다. 핵심 지표만 추리고(절제), 목자 자신의 소진도 점검 대상에 넣는다.

## 입력
- `scorecard`(scorecard-builder 산출): 분기 신호등 지표
- `resource.json`(#8): `pastor_time`(protected 기도·쉼·warning)
- 월간 항목 패턴: 대표 스킬 `references/scorecard-catalog.md` §2

## 방법
1. **핵심만 추리기**: 분기 신호등 지표 중 매월 가볍게 볼 *핵심만* 고른다. 모든 지표를 끌어오지 않는다(KPI 대시보드 금지·5분 절제).
2. **한눈 질문**: 각 행에 `item`·`source`(goals 축)·`glance_question`(5분에 답할 한 줄).
3. **목자 소진 체크(필수)**: `pastor_sustainability_row`를 #8 `pastor_time`(protected)에서 만든다 — "이번 달 나의 기도·안식은 지켜졌는가?"
4. **주간 옵션**: `weekly_option`은 *원하는 목사만*(01 "매월/매주" 흡수, 확대 아님).
5. **돌봄 프레이밍**: `frame`을 "점수 매기기가 아니라 돌봄 닿지 않은 양 찾기"로.

## 가드레일
- **절제**: 핵심 지표만. KPI 대시보드화 금지.
- **목자도 점검 대상**: `pastor_sustainability_row` 누락 금지(가드레일 ④).
- **돌봄 신호**: 정죄·성과 어휘 금지(care-framing 계승).

## 산출
`review.json`의 `monthly_checkup`{`frame`·`rows`[]·`pastor_sustainability_row`·`weekly_option`}. 형식은 대표 스킬 `references/review-schema.md`. 이어 red-signal-responder가 빨강 대응을 짠다.
