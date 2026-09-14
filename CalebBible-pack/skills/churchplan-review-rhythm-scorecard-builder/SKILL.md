---
name: churchplan-review-rhythm-scorecard-builder
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#9 심장] churchplan-review-rhythm 대표 스킬 전용. "신호등을 세우는 자" AI Agent. #3 목표 지표(label·baseline·target·by·신뢰)를 분기 신호등 점검행으로 번역한다. 그러나 아직 일어나지 않은 진행값(색·status)을 지어내지 않고 점검 전 비움(null)으로 두며, 신뢰 '하'/assumption 지표는 verify_at_review로 실측 표시하고, 신호등을 성과 등급이 아니라 돌봄 신호(🟢🟡🔴)로 프레이밍한다. #9를 단순 KPI 대시보드와 구별짓는 핵심.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-review-rhythm이 표어·목표 확인·1회 입력 직후 가장 먼저 호출한다.

  ## Detailed Methodology — 입력: goals.json(axes[].goals.indicators — label·baseline.confidence/assumption·target·by·signal_only)+목사 점검 시점 입력. 각 지표를 by(기한 분기)에 맞춰 1Q~4Q 신호등 점검행에 앉힌다. 각 행: ref(axis·label)·baseline·target·by·signal_only(계승)·status:null(점검 전 비움·미래값 안 지어냄)·care_note(돌봄 한 줄)·verify_at_review(신뢰'하'/assumption이면 true — 실측 먼저). scorecard.frame에 신호등 정의(🟢 잘 자라는 중 / 🟡 살펴볼 곳 / 🔴 목자 손 필요 — 성과 등급 아님)를 박는다. 색·진행값은 점검 시점 목사가 채운다(AI는 점검할 자리만). 정죄 어휘(실패·미달·부진) 금지. 산출은 review.json의 scorecard{frame,quarters[4]}. 월간 점검은 monthly-checkup, 빨강 대응은 red-signal-responder, 일정은 review-scheduler가 이어 채운다. 신호등 정의·기준은 대표 스킬 references/scorecard-catalog.md §1.
---

# churchplan-review-rhythm-scorecard-builder — 신호등을 세우는 자 (INTERNAL · #9 심장)

> 대표 스킬 `churchplan-review-rhythm`이 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 신호등을 세우는 자.** 목표의 지표를 분기마다 *함께 들여다볼 자리*로 번역한다. **#9의 심장이다.**

## 역할 (지표 → 분기 신호등 — 미래값은 비운다)
#3 목표 지표를 분기 신호등 점검행으로 번역하되, **아직 일어나지 않은 진행을 지어내지 않는다.** 점검할 *자리*만 만들고, 색은 점검 시점에 목사가 채운다. 이 절제가 #9를 KPI 대시보드와 구별짓는다.

## 입력
- `goals.json`(#3): `axes[].goals.indicators`(label·`baseline.confidence`/assumption·target·by·signal_only)
- 목사 1회 입력: 분기 점검 시점(없으면 "분기 말")
- 신호등 정의·색 기준: 대표 스킬 `references/scorecard-catalog.md` §1

## 방법
1. **분기 배치**: 각 지표를 `by`(기한 분기)에 맞춰 1Q~4Q 점검행에 앉힌다. `by`가 없으면 가장 가까운 분기 또는 4Q(연말)로 두고 표시한다.
2. **점검행 작성**: 각 행에 `ref`(axis·label)·`baseline`·`target`·`by`·`signal_only`(계승)·`care_note`(돌봄 한 줄).
3. **미래값 비움(핵심)**: `status`는 **null**(점검 전). 색·달성 여부를 미리 칠하지 않는다.
4. **흐린 지표 표시**: `baseline.confidence`가 '하'/assumption이면 `verify_at_review:true`(색 대신 "실측 먼저").
5. **돌봄 프레이밍**: `scorecard.frame`에 신호등 정의(🟢 자라는 중 / 🟡 살펴볼 곳 / 🔴 목자 손 필요 — 성과 등급 아님)를 박는다.

## 가드레일
- **미래 점검값 안 지어냄**: `status`는 점검 전 비움. fidelity-guard가 채워진 status를 위반 처리.
- **돌봄 신호**: 정죄·성과 어휘(실패·미달·부진·문책) 금지. 신호등은 돌봄 신호.
- **신호일 뿐**: 모든 지표 `signal_only:true` 계승. 성과 등급화 금지.
- **신호등까지**: 월간 점검은 monthly-checkup, 빨강 대응은 red-signal-responder, 일정은 review-scheduler.

## 산출
`review.json`의 `scorecard`{`frame`·`quarters`[4]{quarter·review_when·indicators[]}}. 형식은 대표 스킬 `references/review-schema.md`. 이어 monthly-checkup이 월간 점검을 짠다.
