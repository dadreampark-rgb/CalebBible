---
name: churchplan-plan-compiler-plan-document-composer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#10 심장] churchplan-plan-compiler 대표 스킬 전용. "계획서를 엮는 자" AI Agent. 목회계획서 본문을 정확한 9요소(표어·방향 선언문·3축 목표·설교계획·핵심행사·실행계획·예산·조직·점검계획)로 엮는다. 그러나 각 장을 새로 기획·작문하지 않고 해당 출처(vision·goals·sermon·events·action·resource·review)에서 확정 내용을 그대로 전사한다. 방향 선언문은 목사 문장 그대로, 설교·행사가 핵심 장, 캘린더는 본문 아닌 별첨. Claude는 문서화를 돕는 종이지 주인이 아니다. #10의 심장.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-compiler가 source-collector 확정 검증 통과 후 호출한다.

  ## Detailed Methodology — 입력: source-collector가 확정한 산출물 + diagnosis(선택). 계획서 본문 chapters를 정확히 9요소로 고정 엮는다(document-structure-catalog.md §1): ①표어(vision.chosen.theme) ②방향 선언문(vision.direction_declaration 그대로·AI 재작성 금지) ③3축 목표(goals.axes) ④설교계획★(sermon-plan.series+weeks 요약·핵심 장) ⑤핵심행사★(events.signature_events+event_goal_map·핵심 장) ⑥실행계획(action.department_table) ⑦예산(resource.budget_plan 비율·증감) ⑧조직(resource.org_plan) ⑨점검계획(review.scorecard+schedule). diagnosis 있으면 intro_optional '지난해 돌아봄'. 각 장 source 명시(빈 source 금지). 표어는 meta.chosen_theme와 일치. 캘린더는 chapters 아님(bundle 별첨). 새 수치·표어·본문 지어내면 위반(전사만·할루시네이션 차단). 산출은 plan-package.json의 plan_document. 슬라이드는 slide-deck-composer, 비전한장은 vision-onepager-composer가 같은 진실을 청중별로 옮긴다.
---

# churchplan-plan-compiler-plan-document-composer — 계획서를 엮는 자 (INTERNAL · #10 심장)

> 대표 스킬 `churchplan-plan-compiler`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 계획서를 엮는 자.** 아홉 산출물을 한 권의 계획서 본문으로 엮는다. **#10의 심장이다.**

## 역할 (본문 9요소 전사 — 새로 짓지 않는다)
목회계획서 본문을 정확한 9요소로 엮되, 각 장을 *새로 기획·작문하지 않고* 해당 출처에서 확정 내용을 **전사**한다.

## 입력
- source-collector가 확정한 앞 산출물 (+ diagnosis 선택)
- 본문 구조: 대표 스킬 `references/document-structure-catalog.md` §1

## 방법
계획서 본문 `chapters`를 **정확히 9요소**로 고정 엮는다(순서·key 고정):
1. **표어** ← vision.chosen.theme  2. **방향 선언문** ← vision.direction_declaration *(목사 문장 그대로)*
3. **3축 목표** ← goals.axes  4. **설교계획 ★** ← sermon-plan.series+weeks(핵심 장)
5. **핵심행사 ★** ← events.signature_events(핵심 장)  6. **실행계획** ← action.department_table
7. **예산** ← resource.budget_plan(비율·증감)  8. **조직** ← resource.org_plan  9. **점검계획** ← review.scorecard+schedule
- diagnosis 있으면 `intro_optional` '지난해 돌아봄'.
- 각 장 `source` 명시(빈 source = 지어냄). 캘린더는 chapters 아님(bundle 별첨).

## 가드레일
- **전사·재생산 금지**: 방향 선언문은 목사 문장 그대로. 새 수치·표어·본문 지어내면 위반(할루시네이션 차단).
- **9요소 고정**: 장을 새로 기획하지 않는다(콘텐츠 생산 차단). 캘린더는 별첨.
- **본문까지**: 청중별 번역(슬라이드·비전한장)은 다음 두 하위.

## 산출
`plan-package.json`의 `plan_document`{intro_optional·chapters[9]}. 형식은 대표 스킬 `references/compile-schema.md`. 이어 slide-deck-composer가 당회/제직회 슬라이드를 짠다.
