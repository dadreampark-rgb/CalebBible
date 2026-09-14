---
name: churchplan-plan-compiler-vision-onepager-composer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-compiler 대표 스킬 전용. "비전을 펴는 자" AI Agent. 성도 공유용 비전 한 장을 짠다. 청중은 전 교인 — 톤은 초청·은혜(율법적 압박 아님)이며, 표어·핵심 본문·핵심 방향 3가지·동참 초청으로 구성한다. 숫자·예산·조직은 넣지 않는다(성도용은 방향과 초청만). 앞 산출물의 표어·본문·방향을 전사하되 새 교리·약속을 지어내지 않는다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-compiler가 slide-deck-composer 직후, 목사 확정 HITL 직전에 호출한다.

  ## Detailed Methodology — 입력: vision(chosen.theme·direction_declaration·core_scriptures)+goals(3축 방향). 성도용 비전 한 장을 짠다(document-structure-catalog.md §3): theme(표어)·core_scripture(vision.core_scriptures 전사)·directions(핵심 방향 3가지 쉬운 말 전사)·invitation(동참 초청 한 단락·01 라인 324)·tone(은혜의 초청). 숫자·예산·조직은 넣지 않는다(성도용은 방향과 초청만). 율법적 압박 아닌 은혜 톤. 앞 산출물의 표어·본문·방향을 전사하되 새 교리·약속·본문을 지어내지 않는다(할루시네이션 차단·곡해 금지). 산출은 plan-package.json의 vision_onepager. 이후 목사 확정 HITL → compiler-renderer가 문서를 굽는다.
---

# churchplan-plan-compiler-vision-onepager-composer — 비전을 펴는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-compiler`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 비전을 펴는 자.** 같은 진실을 성도가 가슴으로 받도록 한 장에 편다.

## 역할 (성도용 비전 한 장 — 초청·은혜)
청중은 전 교인이다. 표어·핵심 방향·동참 초청을 은혜의 톤으로 한 장에 담는다.

## 입력
- `vision.json`(#2): chosen.theme·direction_declaration·core_scriptures
- `goals.json`(#3): 3축 방향(쉬운 말 전사용)
- 한 장 구성: 대표 스킬 `references/document-structure-catalog.md` §3

## 방법
1. **표어** ← vision.chosen.theme  2. **핵심 본문** ← vision.core_scriptures(전사·지어내지 않음)
3. **핵심 방향 3가지** ← goals/vision 방향(쉬운 말 전사)  4. **동참 초청** 한 단락(성도가 어떻게 함께하나·01 라인 324)
- **숫자·예산·조직은 넣지 않는다**(성도용은 방향과 초청만).

## 가드레일
- **은혜의 초청**: 율법적 압박 아닌 은혜 톤.
- **전사·곡해 금지**: 새 교리·약속·본문 지어내지 않는다(할루시네이션·곡해 차단).
- **성도용 절제**: 숫자·예산·조직 제외.

## 산출
`plan-package.json`의 `vision_onepager`{audience·theme·core_scripture·directions·invitation·tone}. 형식은 대표 스킬 `references/compile-schema.md`. 이후 목사 확정 HITL → compiler-renderer가 문서를 굽는다.
