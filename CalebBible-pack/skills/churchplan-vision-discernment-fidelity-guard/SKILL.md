---
name: churchplan-vision-discernment-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-vision-discernment 대표 스킬 전용. "분별을 지키는 자" AI Agent. 두 가지 거짓을 막는다 — (1)본문 할루시네이션(없는 구절·가짜 책이름·곡해 주해) (2)결정 월권(Claude가 표어를 정하거나 "하나님의 뜻"을 단정). 결정론 스크립트로 본문 형식·결정 월권 어휘·선택 전 선언문을 적발한다(ABSOLUTE ANCHOR #2).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-vision-discernment가 vision.json 산출 후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증. scripts/validate_vision.py로 (1)스키마·mode(option1/2) (2)본문 ref 실재 66권 한글 책이름+장:절 형식(가짜 책 적발) (3)결정 월권 어휘("표어는 X입니다"·"하나님의 뜻은"·"최선/추천") 적발 (4)선택 전 선언문 차단(chosen=null인데 direction_declaration 존재=위반) (5)option2 original_theme 존재 (6)candidates 3요건·axis_mapping·추상도 플래그 구비. 스크립트 밖: 주해 정통성(가짜 어원·풍유 곡해)을 인간 눈으로 점검. 실패 시 해당 분석 재실행.
---

# churchplan-vision-discernment-fidelity-guard — 분별을 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-vision-discernment`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 분별을 지키는 자.** vision.json 산출 직후의 최종 게이트.

## 역할 (두 거짓을 막는다)
이 스킬은 목사의 분별을 검증하지 않는다. **Claude가 분별을 오염시켰는지** 막는다:
1. **본문 할루시네이션** (ANCHOR #2): 없는 장·절, 가짜 책이름, 근거 없는 어원, 풍유적 곡해.
2. **결정 월권**: Claude가 표어를 *정하거나*("올해 표어는 X입니다"), "하나님의 뜻은 …"이라 *단정*하거나, 후보에 우열("최선·추천")을 매기는 것.

> 이 단계의 최우선 가드레일은 "방향 단정 금지"다. 분별의 주인은 하나님과 목자이며, 이 게이트가 그 경계를 지킨다.

## 결정론 검증

```bash
python3 <이 스킬 폴더>/scripts/validate_vision.py <vision.json>
```

스크립트가 검사하는 것:
1. **스키마·mode** — 필수 블록(meta·candidates) + `meta.mode` ∈ {option1, option2}
2. **본문 실재성** — 각 `core_scriptures[].ref`를 공유 결정론 자산 `bible_validator.validate_reference`로 검사: **실재 66권 한글 책이름 + 장 수 상한 + 절 수 상한 + 범위·쉼표 불연속절**까지 완전 검증(실재 책 + 가짜 장·절 할루시네이션 적발). `"본문 미확정"`은 통과. *(공유 자산 import — 같은 scripts/ 폴더에 `bible_validator.py` canonical 복사본.)*
3. **결정 월권 어휘(위반)** — `direction_declaration`·`comparison_note`·`comparison_table`·candidates에서 "표어는 …입니다(단정)"·"하나님의 뜻은"·"최선·가장 좋은·추천·선택하세요" 패턴 적발 → **위반(EXIT 1)**. discernment-guardrails.md의 "절대 금지"는 경고가 아닌 위반이다.
4. **선택 전 선언문 차단** — `chosen`이 null인데 `direction_declaration`이 채워졌으면 위반(목사 선택 전 월권).
5. **option2 무결성** — mode=option2면 `original_theme` 존재 + candidates에 family="원안" 포함(둘 다 위반 처리).
6. **분별 재료 구비(필수)** — 각 candidate에 `axis_mapping`·`abstraction`·`criteria_check` 존재(누락 시 위반).
7. **최종 완료 게이트(`--final`)** — `--final` 인자 시 `chosen`(표어 선택)·`direction_declaration`(선언문) 채워짐을 강제. 선택 전 중간 산출물은 `--final` 없이 정직성만 검증.
8. **적대적 입력 방어** — 최상위 JSON이 객체 아니면 EXIT 2, `candidates`·`core_scriptures`가 배열 아니면 위반(traceback 없이 깔끔한 종료).

## 검증 후 처리
- **통과**: "검증 통과 — 본문 정직, 결정 월권 없음" 반환. vision.json 완료.
- **실패**: 위반 항목 구체 반환(예: "core_scriptures.ref '바울서 3:5' 실재하지 않는 책", "chosen 없는데 선언문 존재 — 월권"). 해당 분석으로 되돌아간다(임의 보정 금지).

## 스크립트 밖 인간 가드레일 (주해 정통성)
스크립트가 못 잡는 *내용*을 사람의 눈으로:
- **가짜 어원**: "이 히브리어는 원래 …" 류 근거 없는 주장 → 제거.
- **풍유적 곡해**: 본문에 없는 알레고리로 표어에 끼워 맞춤 → 본문 의미로 되돌림.
- **아전인수 적용**: 문맥 무시한 적용 → 문맥으로 교정.

## 출력
검증 리포트(통과/실패 + 항목별) — 대표 스킬 Orchestration Trace (c) 섹션에 표시.
