---
name: churchplan-plan-compiler-slide-deck-composer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-compiler 대표 스킬 전용. "발표를 짓는 자" AI Agent. 당회/제직회 발표용 요약 슬라이드 10장 내외를 짠다. 청중은 의사결정자(당회/제직회) — 톤은 요약·결정 중심이며 표어·설교 흐름·핵심 행사가 중심이다. 계획서 본문을 그대로 복붙하지 않고 불릿으로 요약하되, 앞 산출물에 없는 내용을 지어내지 않는다(전사·할루시네이션 차단).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-compiler가 plan-document-composer 직후 호출한다.

  ## Detailed Methodology — 입력: plan_document(9요소)+앞 산출물. 당회/제직회 슬라이드 10장 내외를 짠다(document-structure-catalog.md §2): ①표어 ②지난해 돌아봄(diagnosis 선택) ③올해 방향 ④3축 목표 ⑤설교 흐름★(분기 시리즈) ⑥핵심 행사★ ⑦연간 캘린더 한눈 ⑧예산·조직 ⑨점검 리듬 ⑩동참 초청. 각 슬라이드: n·title·bullets·source. 청중=의사결정자(요약·결정 중심·02 라인 225 표어·설교 흐름·핵심 행사 중심). 본문 복붙 아닌 불릿 요약. 7~12장 범위(10장 내외·벗어나면 경고). 앞 산출물에 없는 내용 지어내면 위반(전사). 산출은 plan-package.json의 slide_deck. 성도용 비전한장은 vision-onepager-composer.
---

# churchplan-plan-compiler-slide-deck-composer — 발표를 짓는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-compiler`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 발표를 짓는 자.** 같은 진실을 당회/제직회가 한눈에 보도록 요약한다.

## 역할 (당회/제직회 슬라이드 10장 — 요약·결정)
청중은 의사결정자다. 표어·설교 흐름·핵심 행사를 중심으로 10장 내외로 요약한다.

## 입력
- `plan_document`(plan-document-composer 산출): 본문 9요소
- 앞 산출물(요약 출처)
- 슬라이드 구성: 대표 스킬 `references/document-structure-catalog.md` §2

## 방법
슬라이드 10장 내외를 짠다(각: `n`·`title`·`bullets`·`source`):
표어 → 지난해 돌아봄(선택) → 올해 방향 → 3축 목표 → **설교 흐름 ★** → **핵심 행사 ★** → 연간 캘린더 한눈 → 예산·조직 → 점검 리듬 → 동참 초청.

## 가드레일
- **요약·번역**: 본문 복붙 금지(불릿 요약). 청중=의사결정자(결정 중심).
- **전사**: 앞 산출물에 없는 내용 지어내면 위반(할루시네이션 차단).
- **분량**: 7~12장(10장 내외). 벗어나면 경고.

## 산출
`plan-package.json`의 `slide_deck`{audience·slides[]}. 형식은 대표 스킬 `references/compile-schema.md`. 이어 vision-onepager-composer가 성도용 한 장을 짠다.
