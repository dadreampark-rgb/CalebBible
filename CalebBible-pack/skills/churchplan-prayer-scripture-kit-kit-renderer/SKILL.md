---
name: churchplan-prayer-scripture-kit-kit-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-prayer-scripture-kit 대표 스킬 전용. "키트를 묶는 자" AI Agent. 목사 확정(HITL) 후의 prayer-kit.json을 받아 인쇄용 영성 키트를 docx+pdf로 렌더한다(scripts/build_kit.py — python-docx·weasyprint, 통독표+월별 기도제목+가정예배 가이드+새벽 안내문 묶음). 렌더 전 핵심 게이트 재강제(필수 블록·status·은혜 융통성 grace_frame·율법 어휘 없음). 위반 시 렌더 거부. 라이브러리 없으면 폴백(docx→md·pdf 생략).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-prayer-scripture-kit가 목사 검토·확정 HITL 이후에만 호출한다(확정 전 렌더 금지).

  ## Detailed Methodology — 입력: 확정된 prayer-kit.json. scripts/build_kit.py가 인쇄용 키트를 만든다 — prayer-kit.docx(python-docx·나눔명조·통독표[은혜 융통성 머리글]+월별 기도제목+가정예배 양식+새벽 안내문)+prayer-kit.pdf(weasyprint). 렌더 전 게이트 재강제: 필수 블록(meta·reading_track·prayer_topics·family_worship·dawn_prayer_season)·status∈{제안,확정}·reading_track.grace_frame 존재(통독 율법화 차단)·율법 어휘(매일 …해야·완주 못하면·반드시·의무·죄책) 검출 시 렌더 거부(종료코드 1). 전체 정밀 검증(성경 실재 bible_validator·곡해)은 fidelity-guard의 validate_kit.py가 맡는다. 표어 있으면 머리에 일관 배치(없어도 됨·지원 스킬). 라이브러리 없으면 폴백(docx→md·pdf 생략).
---

# churchplan-prayer-scripture-kit-kit-renderer — 키트를 묶는 자 (INTERNAL)

> 대표 스킬 `churchplan-prayer-scripture-kit`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 키트를 묶는 자.** 확정된 영성 도구를 회중이 손에 쥘 인쇄물로 묶는다.

## 역할 (확정 후 렌더 — docx + pdf)
**목사 확정(HITL) 후에만** 작동한다. prayer-kit.json을 받아 인쇄용 영성 키트를 docx+pdf로 렌더한다.

## 입력
- 확정된 `prayer-kit.json`(`status:"확정"`·`confirmed` 채워짐)
- 형식: 대표 스킬 `references/kit-schema.md`

## 렌더 (결정론 스크립트)

```bash
python3 <이 스킬 폴더>/scripts/build_kit.py <prayer-kit.json> [출력디렉토리]
```

산출:
- `prayer-kit.docx` — 통독표(은혜 융통성 머리글)+월별 기도제목+가정예배 가이드+새벽 안내문 묶음
- `prayer-kit.pdf` — 인쇄·배포용(weasyprint)

> 라이브러리 없으면 폴백(python-docx→md·weasyprint→pdf 생략).

## 렌더 전 게이트 재강제 (cys-insight 패턴)
렌더 직전 핵심을 재확인하고, 위반 시 **렌더 거부**(종료코드 1):
- 필수 블록(`meta`·`reading_track`·`prayer_topics`·`family_worship`·`dawn_prayer_season`) + `status` ∈ {제안,확정}
- **통독 은혜 융통성**: `reading_track.grace_frame`이 없으면 거부(통독 율법화 차단)
- **율법 어휘**: 산출에 "매일 …해야·완주 못하면·반드시·의무·죄책" 류가 *부정 표지(어휘 근방)* 없이 있으면 거부
- **성경 실재**: 통독 portions·가정예배/새벽 scripture의 책·장·절·장범위 끝을 `bible_validator`로 검증 — 정경 밖이면 거부(가짜·범위밖 본문이 docx/pdf로 먼저 인쇄되는 것 차단). `scripts/bible_validator.py`(이식·diff 0).

곡해·아전인수 등 내용 정밀 검증은 fidelity-guard의 `validate_kit.py`가 사람 눈과 함께 맡는다.

## 가드레일
- **확정 후에만 렌더**: 목사 검토·확정 HITL 전에는 작동하지 않는다.
- **은혜 톤 보존**: 율법 어휘 없이 렌더. grace_frame을 통독표 머리에.
- **자기완결**: python-docx·weasyprint. 없으면 폴백.

## 산출
인쇄용 영성 키트(docx + pdf). 대표 스킬 Orchestration Trace (c)·(d) 섹션에 경로 표시.
