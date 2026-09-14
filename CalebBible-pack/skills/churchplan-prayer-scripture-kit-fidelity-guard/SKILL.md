---
name: churchplan-prayer-scripture-kit-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-prayer-scripture-kit 대표 스킬 전용. "은혜를 지키는 자" AI Agent. 세 가지 거짓을 막는다 — (1)율법적 압박(매일 …해야·완주 못하면·반드시·의무·죄책 류 강제·정죄·통독 grace_frame 누락) (2)가짜 성경·곡해(통독·가정예배·새벽 본문이 정경 66권 밖·없는 권장) (3)지어내기(없는 약속·수치 단언). 결정론 스크립트로 성경 실재(bible_validator)·율법 톤·은혜 융통성·전사·확정 게이트를 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-prayer-scripture-kit가 prayer-kit.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_kit.py로 (1)스키마·status·필수 블록(reading_track·prayer_topics·family_worship·dawn_prayer_season) (2)성경 실재 — reading_track.schedule[].portions·family_worship.samples[].scripture·dawn_prayer_season.seasons[].scripture를 bible_validator로 검증(정경 66권 밖·없는 권장이면 위반) (3)율법 톤 — 산출 전반에 율법·정죄 어휘(매일 …해야·완주 못하면·반드시·의무·죄책·게으름·빠지면 안)가 부정 표지(아니·않·말고·금지·없) 없이 있으면 위반 (4)통독 은혜 융통성 — reading_track.grace_frame 없으면 위반 (5)전사 — prayer_topics 출처 표기·없는 약속/수치 단언 금지(경고) (6)확정 게이트 — status=확정인데 confirmed 없으면 위반. 스크립트 밖: 곡해된 묵상·아전인수 적용을 사람 눈으로. 실패 시 해당 분석 재실행. 정경 데이터: scripts/bible_validator.py(이식·diff 0).
---

# churchplan-prayer-scripture-kit-fidelity-guard — 은혜를 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-prayer-scripture-kit`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 은혜를 지키는 자.** prayer-kit.json 산출 직후의 최종 게이트.

## 역할 (세 거짓을 막는다)
이 스킬은 목사의 영성 도구를 검증하지 않는다. **Claude가 영성 키트를 오염시켰는지** 막는다:
1. **율법적 압박** (ANCHOR #2): "매일 …해야·완주 못하면 죄" 식 강제·정죄·grace_frame 누락 — 도구가 짐이 됨.
2. **가짜 성경·곡해**: 통독·가정예배·새벽 본문이 정경 66권 밖·없는 권·장.
3. **지어내기**: 없는 약속·응답·수치 단언.

> 이 단계의 최우선 가드레일은 "은혜의 초청"·"성경 실재"·"전사"다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_kit.py <prayer-kit.json>
```

스크립트가 검사하는 것:
1. **스키마·status** — 필수 블록(meta·reading_track·prayer_topics·family_worship·dawn_prayer_season) + `status` ∈ {제안,확정}.
2. **성경 실재** — `reading_track.schedule[].portions`·`family_worship.samples[].scripture`·`dawn_prayer_season.seasons[].scripture`를 bible_validator로 검증(정경 66권 밖·없는 권·장이면 위반).
3. **율법 톤** — 산출 전반에 율법·정죄 어휘(매일 …해야·완주 못하면·반드시·의무·죄책·게으름·빠지면 안)가 *부정 표지*(아니·않·말고·금지·없) 없이 있으면 위반.
4. **통독 은혜 융통성** — `reading_track.grace_frame`이 없으면 위반.
5. **전사** — `prayer_topics.months[].source` 표기(경고). 없는 약속·수치 단언 금지.
6. **확정 게이트** — `status:"확정"`인데 `confirmed`=null이면 위반.

## 검증 후 처리
- **통과**: "검증 통과 — 성경 실재, 은혜의 초청, 전사 충실" 반환. prayer-kit.json 완료.
- **실패**: 위반 항목 구체 반환(예: "시편 151편 — 정경 범위 밖", "reading_track에 '완주 못하면' — 율법 어휘"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **곡해된 묵상**: 본문은 실재해도 묵상이 아전인수면 → 본문에서 길어 올린 질문으로.
- **은혜를 가장한 압박**: 어휘는 통과해도 톤이 강제면 → 초청으로.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
