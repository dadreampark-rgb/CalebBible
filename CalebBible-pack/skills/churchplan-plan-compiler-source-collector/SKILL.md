---
name: churchplan-plan-compiler-source-collector
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-compiler 대표 스킬 전용. "산출물을 모으는 자" AI Agent. 앞 9개 산출물(vision·goals·sermon-plan·events·calendar·action·resource·review [+diagnosis 선택])을 모아, 다 모였는지(missing)·다 확정됐는지(unconfirmed status=확정) 검증한다. 미확정·누락이 있으면 멈추고 앞 단계로 돌린다(garbage-in 차단·#10 고유 게이트). 동시에 review.verify_at_review + goals 신뢰'하' 항목을 보강 종자로 모아 reinforce_guide의 씨앗을 만든다(살아 움직이는 마무리).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-compiler가 교회명·톤 1회 입력 직후 가장 먼저 호출한다.

  ## Detailed Methodology — 입력: 앞 9개 산출물 + diagnosis(선택). 각 산출물의 존재(present)와 status를 점검해 sources{loaded·missing·unconfirmed·diagnosis_present}를 만든다. 필수 8개(vision·goals·sermon-plan·events·calendar·action·resource·review) 중 빠진 것은 missing, status≠확정은 unconfirmed — 하나라도 있으면 대표가 멈추고 앞 단계로 안내(미확정 산출물로 최종 문서 금지). 동시에 보강 종자 수집: review.json의 scorecard 지표 중 verify_at_review:true + goals 신뢰'하'/assumption 항목을 모아 reinforce_seeds로 담는다(#12 plan-reinforce·#9로 가는 다리). 앞 산출물에 없는 것을 지어내지 않는다(상속·전사). 산출은 plan-package.json의 sources + reinforce_guide.verify_seeds 씨앗. 이어 plan-document-composer가 본문을 엮는다.
---

# churchplan-plan-compiler-source-collector — 산출물을 모으는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-compiler`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 산출물을 모으는 자.** 묶기 전에 *다 모였나·다 확정됐나*를 먼저 본다.

## 역할 (수집 + 확정 검증 + 보강 종자)
앞 9개 산출물을 모아 존재·확정을 검증하고, 미확정·누락이면 멈춘다. 동시에 귀가 후 보강 종자를 모은다.

## 입력
- 앞 9개 산출물: vision·goals·sermon-plan·events·calendar·action·resource·review (+ diagnosis 선택)
- 스키마: 대표 스킬 `references/compile-schema.md`

## 방법
1. **수집**: 각 산출물의 존재(`present`)와 `meta.status`를 읽어 `loaded`에 담는다.
2. **누락 점검**: 필수 8개 중 빠진 것은 `missing`에.
3. **확정 점검**: status≠"확정"인 것은 `unconfirmed`에. **하나라도 있으면** 대표가 멈추고 앞 단계로 안내(garbage-in 차단).
4. **보강 종자**: review.json scorecard 지표 중 `verify_at_review:true` + goals 신뢰 '하'/assumption 항목을 모아 `reinforce_seeds`로(귀가 후 실측 대상).
5. **선택 처리**: diagnosis 있으면 `diagnosis_present:true`(도입 '지난해 돌아봄' 가능).

## 가드레일
- **다 확정돼야 묶는다**: missing/unconfirmed가 있으면 멈춘다(미확정 문서화 금지).
- **지어내지 않는다**: 없는 산출물·항목을 만들지 않는다(상속·전사).
- **수집·검증까지**: 본문 엮기는 plan-document-composer, 렌더는 compiler-renderer.
- **자기보고는 결정론으로 뒷받침된다**: 여기서 채운 `sources.missing`/`unconfirmed`는 LLM 보고이므로, 최종 게이트(fidelity-guard `validate_package.py <패키지> <앞-산출물-디렉토리>`)가 **실제 파일 status를 다시 열어** missing/unconfirmed를 재계산하고 보고 불일치(garbage-in 은폐)를 적발한다. 산출물이 디렉토리로 있으면 source-dir를 반드시 넘긴다.

## 산출
`plan-package.json`의 `sources`{loaded·missing·unconfirmed·diagnosis_present} + `reinforce_guide.verify_seeds` 씨앗. 형식은 대표 스킬 `references/compile-schema.md`. 이어 plan-document-composer가 본문을 엮는다.
