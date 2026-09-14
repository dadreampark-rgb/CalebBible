---
name: churchplan-review-rhythm-review-scheduler
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-review-rhythm 대표 스킬 전용. "리듬을 못박는 자" AI Agent. 연간 점검 일정을 짠다 — 분기 리뷰 4회 + 반기(6~7월) 공식 수정일 못박기(필수) + 분기 점검 회의 어젠다 템플릿(신호등→빨강 돌봄→소진 점검→다음 분기 조정) + (선택)자동 리마인드/리포트 구조 제안. 계획의 가치는 수립이 아니라 갱신 — 반기 수정일을 못박아 계획을 살아 움직이게 한다. 단 실제 자동화(cron)는 켜지 않고 구조만 제안한다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-review-rhythm이 red-signal-responder 직후, 목사 확정 HITL 직전에 호출한다.

  ## Detailed Methodology — 입력: scorecard(분기 배치)+목사 1회 입력(점검 시점·반기일 6/7월·리마인드 여부). quarterly_reviews(분기 4회·when·agenda_ref)를 짜고, quarterly_agenda(① 신호등 함께 보기 ② 🔴 지표 돌봄 점검 ③ 목자·일꾼 소진 점검 ④ 다음 분기 조정)를 만든다(보완B·01 라인 300 — 스코어카드와 어젠다는 한 쌍). midyear_revision(when 6~7월·official:true·note)을 반드시 못박는다(01 라인 310 — 빠지면 fidelity-guard 위반). auto_reminder는 (선택) 구조 제안만(proposed·structure·note "실제 자동화는 교회 환경에서 설정") — 실제 cron 켜지 않음(자료 없이 작동·월권 방지). 산출은 review.json의 schedule. 일정 모델은 대표 스킬 references/scorecard-catalog.md §4·§5.
---

# churchplan-review-rhythm-review-scheduler — 리듬을 못박는 자 (INTERNAL)

> 대표 스킬 `churchplan-review-rhythm`이 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 리듬을 못박는 자.** 점검이 흐지부지되지 않도록 연간 일정과 어젠다를 미리 박는다.

## 역할 (연간 일정 + 반기 공식 수정일 + 분기 어젠다)
분기 리뷰 4회와 **반기(6~7월) 공식 수정일**을 못박고, 분기 점검 회의 어젠다 템플릿을 짠다. "계획의 가치는 수립이 아니라 갱신"(01 라인 310).

## 입력
- `scorecard`(scorecard-builder 산출): 분기 배치
- 목사 1회 입력: 분기 점검 시점·반기 수정일(6/7월)·자동 리마인드 여부
- 일정·어젠다 모델: 대표 스킬 `references/scorecard-catalog.md` §4·§5

## 방법
1. **분기 리뷰 4회**: `quarterly_reviews`[](각 `quarter`·`when`·`agenda_ref`). 목사 입력 시점, 없으면 "분기 말".
2. **분기 어젠다(보완B)**: `quarterly_agenda`(① 신호등 함께 보기 ② 🔴 지표 돌봄 점검 ③ 목자·일꾼 소진 점검 ④ 다음 분기 조정). 스코어카드와 어젠다는 한 쌍(01 라인 300).
3. **반기 공식 수정일(필수)**: `midyear_revision`{`when`:6~7월·`official`:true·`note`}. 못박지 않으면 fidelity-guard 위반.
4. **(선택) 자동 리마인드**: `auto_reminder`{`proposed`·`structure`·`note`} — **구조 제안만**. 실제 cron은 켜지 않는다(교회 환경에서 운영자가 설정).

## 가드레일
- **반기 수정일 못박기**: `midyear_revision`(official:true) 누락 금지(01 라인 310 강제).
- **자동화 월권 금지**: 실제 발송 자동화는 켜지 않는다 — 구조 제안까지(자료 없이 작동).
- **점검 구조까지**: 실제 지표 수집·평가는 점검 시점 목사 몫.

## 산출
`review.json`의 `schedule`{`quarterly_reviews`[]·`quarterly_agenda`[]·`midyear_revision`·`auto_reminder`}. 형식은 대표 스킬 `references/review-schema.md`. 이후 목사 확정 HITL → rhythm-renderer가 점검표를 짓는다.
