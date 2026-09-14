---
name: churchplan-plan-compiler-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-compiler 대표 스킬 전용. "통합을 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)재생산(앞 산출물에 없는 표어·수치·본문을 지어냄·표어 불일치) (2)미확정 산출물 문서화(sources.missing/unconfirmed 있는데 묶음·garbage-in) (3)9요소 깨짐(계획서 본문이 정확한 9요소가 아님·콘텐츠 생산). 결정론 스크립트로 전사 충실·확정 게이트·9요소·살아있는 마무리·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-compiler가 plan-package.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_package.py로 (1)스키마·meta.chosen_theme·status·필수 블록(sources·plan_document·slide_deck·vision_onepager) (2)확정 게이트 — sources.missing 또는 unconfirmed 비어 있지 않으면 위반(미확정/누락 산출물 문서화 금지·#10 고유) (3)9요소 — plan_document.chapters key가 정확히 [표어·방향 선언문·3축 목표·설교계획·핵심행사·실행계획·예산·조직·점검계획]이어야 함(빠지면 위반·캘린더가 chapters에 있으면 경고) (4)전사 충실 — chapters[].source 비면 위반(출처 없는 본문=지어냄), chapters[표어].content≠meta.chosen_theme면 위반 (5)재생산 금지 — bundle은 앞 산출물 file 참조만(경고) (6)살아있는 마무리 — reinforce_guide 없거나 next에 plan-reinforce 없으면 경고 (7)슬라이드 분량 7~12 벗어나면 경고 (8)확정 게이트 — status=확정인데 confirmed 없으면 위반. 스크립트 밖: 매끈한 AI 재작성·청중 무시를 사람 눈으로. 실패 시 해당 분석 재실행.
---

# churchplan-plan-compiler-fidelity-guard — 통합을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-compiler`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 통합을 지키는 자.** plan-package.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 계획을 검증하지 않는다. **Claude가 통합을 오염시켰는지** 막는다:
1. **재생산** (ANCHOR #2): 앞 산출물에 없는 표어·수치·본문을 지어냄·표어 불일치 — 매끈한 AI 보고서가 목사 목소리를 덮음.
2. **미확정 산출물 문서화**: missing/unconfirmed가 있는데 묶음 — garbage-in.
3. **9요소 깨짐**: 계획서 본문이 정확한 9요소가 아님 — 장을 새로 기획(콘텐츠 생산).

> 이 단계의 최우선 가드레일은 "전사하되 재생산하지 않는다"·"다 확정돼야 묶는다"·"9요소 고정"이다.

## 결정론 검증

```bash
# 기본(자기일관성)
python3 <이 스킬 폴더>/scripts/validate_package.py <plan-package.json>
# 원본 산출물 폴더가 있으면 함께 — vision.json 등 원본을 열어 전사·확정을 결정론 대조(권장)
python3 <이 스킬 폴더>/scripts/validate_package.py <plan-package.json> <앞-산출물-디렉토리>
```

스크립트가 검사하는 것:
1. **스키마·표어·status** — 필수 블록(meta·sources·plan_document·slide_deck·vision_onepager) + `meta.chosen_theme` + `status` ∈ {제안,확정}. 최상위 JSON이 객체가 아니면 종료코드 2(깨진 입력), 장(chapter)이 객체가 아니면 위반.
2. **확정 게이트** — `sources.missing` 또는 `sources.unconfirmed`가 비어 있지 않으면 위반(미확정/누락 산출물 문서화 금지).
3. **9요소** — `plan_document.chapters` key가 정확히 [표어·방향 선언문·3축 목표·설교계획·핵심행사·실행계획·예산·조직·점검계획]이어야 함(빠지면 위반·캘린더가 chapters에 있으면 경고).
4. **전사 충실** — `chapters[].source`가 비면 위반(출처 없는 본문=지어냄). `chapters[표어].content`≠`meta.chosen_theme`면 위반.
5. **성경 본문 결정론 검증** — `vision_onepager.core_scripture`를 공유 자산 `bible_validator.validate_reference`로 검사. 존재하지 않는 장·절(예: 요한계시록 99:99)이면 위반(7차원 할루시네이션 1순위 차단).
6. **재생산 금지** — `bundle`은 앞 산출물 file 참조만(경고).
7. **살아있는 마무리** — `reinforce_guide`가 없거나 `next`에 plan-reinforce 언급이 없으면 경고.
8. **슬라이드 분량** — `slide_deck.slides`가 비었거나 7~12장 벗어나면 경고.
9. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.
10. **원본 대조(source-dir 주면)** — vision.json 등 실제 파일을 열어 ① `missing`/`unconfirmed`를 파일 status로 재계산(LLM 자기보고 불신·garbage-in 차단) ② `meta.chosen_theme`=`vision.chosen.theme`, `chapters[방향 선언문].content`에 `vision.direction_declaration` 원문 포함(AI 재작성 적발), `core_scripture`가 vision 원본 본문 집합의 멤버인지 결정론 대조.

## 검증 후 처리
- **통과**: "검증 통과 — 전사 충실, 다 확정됨, 9요소 고정" 반환. plan-package.json 완료.
- **실패**: 위반 항목 구체 반환(예: "sources.unconfirmed에 review.json — 확정 먼저", "chapters에 '설교계획' 없음 — 9요소"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **매끈한 AI 재작성**: source는 맞아도 문장이 목사 목소리를 덮으면 → 전사로 교정.
- **청중 무시**: 성도용 한 장에 숫자·예산이 들어가면 → 초청·은혜 톤으로.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
