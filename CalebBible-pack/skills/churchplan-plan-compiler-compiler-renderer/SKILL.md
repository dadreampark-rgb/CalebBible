---
name: churchplan-plan-compiler-compiler-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-compiler 대표 스킬 전용. "문서를 굽는 자" AI Agent. 목사 확정(HITL) 후의 plan-package.json을 받아 계획서 본문(docx+pdf)·당회/제직회 슬라이드(pptx)·성도용 비전 한 장(html+pdf)·옵션2 보강 안내를 자기완결 렌더한다(scripts/build_package.py — python-docx·python-pptx·weasyprint, 코어 출력 스킬 비의존). 앞 산출물(52주표·행사·캘린더·스코어카드·실행표·예산)은 재생산하지 않고 bundle로 참조 묶음. 렌더 전 핵심 게이트 재강제(필수 블록·표어·확정 게이트·9요소). 위반 시 렌더 거부.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-compiler가 목사 검토·확정 HITL 이후에만 호출한다(확정 전 렌더 금지).

  ## Detailed Methodology — 입력: 확정된 plan-package.json. scripts/build_package.py가 ① plan-document.docx(python-docx·9요소·나눔명조·표어 머리)+plan-document.pdf(weasyprint) ② slide-deck.pptx(python-pptx·10장) ③ vision-onepager.html+pdf(은혜 톤) ④ reinforce-guide(보강 안내·#12·#9 다리) ⑤ bundle 목록(앞 산출물 참조·재생산 안 함)을 만든다. 렌더 전 게이트 재강제: 필수 블록(meta·sources·plan_document·slide_deck·vision_onepager)·meta.chosen_theme·status∈{제안,확정}·sources.missing/unconfirmed 비어야(미확정 산출물 거부·#10 고유 게이트)·plan_document.chapters 9요소 위반 시 렌더 거부(종료코드 1). 전체 정밀 검증(전사 충실·할루시네이션)은 fidelity-guard의 validate_package.py가 맡는다. 코어 출력 스킬(docx·pptx·pdf) 비의존·자기완결. 라이브러리 없으면 가능한 포맷으로 폴백(pptx 없으면 md 개요·pdf 없으면 html).
---

# churchplan-plan-compiler-compiler-renderer — 문서를 굽는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-compiler`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 문서를 굽는 자.** 확정된 통합 패키지를 손에 잡히는 문서로 굽는다.

## 역할 (확정 후 렌더 — 자기완결)
**목사 확정(HITL) 후에만** 작동한다. plan-package.json을 받아 계획서·슬라이드·비전 한 장·보강 안내를 자기완결로 렌더하고, 앞 산출물을 bundle로 묶는다.

## 입력
- 확정된 `plan-package.json`(`status:"확정"`·`confirmed` 채워짐)
- 형식: 대표 스킬 `references/compile-schema.md`

## 렌더 (결정론 스크립트 · 자기완결)

```bash
python3 <이 스킬 폴더>/scripts/build_package.py <plan-package.json> [출력디렉토리]
```

산출:
- `plan-document.docx` + `plan-document.pdf` — 계획서 본문 9요소(나눔명조·표어 머리·설교/행사 핵심 장)
- `slide-deck.pptx` — 당회/제직회 슬라이드 10장
- `vision-onepager.html` + `vision-onepager.pdf` — 성도용 비전 한 장(은혜 톤)
- `reinforce-guide.md` — 옵션2 보강 안내(#12·#9 다리)
- `bundle.md` — 앞 산출물 참조 목록(재생산 아님)

> 코어 출력 스킬(docx·pptx·pdf)에 의존하지 않는다 — python-docx·python-pptx·weasyprint 자기완결. 라이브러리 없으면 폴백(pptx→md 개요·pdf→html).

## 렌더 전 게이트 재강제 (cys-insight 패턴)
렌더 직전 핵심만 재확인하고, 위반 시 **렌더 거부**(종료코드 1):
- 필수 블록(`meta`·`sources`·`plan_document`·`slide_deck`·`vision_onepager`) + `meta.chosen_theme` + `status` ∈ {제안,확정}
- **확정 게이트**: `sources.missing`/`sources.unconfirmed`가 비어 있지 않으면 거부(미확정 산출물 문서화 금지)
- **9요소**: `plan_document.chapters`가 9요소가 아니면 거부

전체 정밀 검증(전사 충실·할루시네이션)은 fidelity-guard의 `validate_package.py`가 맡는다.

## 가드레일
- **확정 후에만 렌더**: 목사 검토·확정 HITL 전에는 작동하지 않는다.
- **재생산 금지**: bundle은 앞 산출물 참조만(다시 만들지 않는다).
- **자기완결**: 코어 출력 스킬 비의존. 라이브러리 없으면 폴백.

## 산출
계획서(docx/pdf)·슬라이드(pptx)·비전 한장(html/pdf)·보강 안내·번들. 대표 스킬 Orchestration Trace (c)·(d) 섹션에 경로 표시.
