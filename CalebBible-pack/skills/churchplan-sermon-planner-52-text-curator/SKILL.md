---
name: churchplan-sermon-planner-52-text-curator
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-sermon-planner-52 대표 스킬 전용. "본문을 살피는 자" AI Agent. 52주 본문이 ① 정경 66권에 실재하는지(없는 장·절·가짜 책 차단) ② 한 해 동안 중복되지 않는지 ③ 구약/신약·장르가 균형 있는지 ④ 핵심 복음·교리에 공백이 없는지 점검한다. 본문 실재 검증은 bible_validator.py로 결정론 수행 — sermon-planner-52week에서 이식한 자기완결 자산.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 52주 초안 직후 호출한다.

  ## Detailed Methodology — 입력: sermon-plan.json의 weeks(primary_text·parallel_texts). scripts/bible_validator.py의 validate_reference로 각 본문의 정경 실재성(책 약어 정규화·장 수·절 수 범위) 결정론 검증 — 없는 장·절·가짜 책 적발. 이어 ① 본문 중복(같은 본문이 한 해 여러 주) ② 구약/신약 비율·장르(내러티브/서신/시가/예언/복음서) 균형 ③ 핵심 복음·교리 주제 공백(십자가·부활·성령·은혜 등 한 해 동안 안 다룬 큰 주제) 점검. 균형·공백은 경고(조언), 본문 실재는 위반(차단). 산출은 sermon-plan.json의 coverage(ot_nt_balance·genre_balance·duplicates·doctrine_gaps).
---

# churchplan-sermon-planner-52-text-curator — 본문을 살피는 자 (INTERNAL)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 본문을 살피는 자.** 강단에 오를 본문이 실재하고 고른지 살핀다.

## 역할
52주 본문을 *전체*로 살핀다 — 실재하는가, 중복되지 않는가, 구약·신약과 장르가 고른가, 큰 교리에 공백이 없는가.

## 입력
- `sermon-plan.json`의 `weeks`(primary_text·parallel_texts)

## 결정론 본문 검증 (이식 자산)

```bash
python3 <이 스킬 폴더>/scripts/bible_validator.py <본문>   # 예: 누가복음 15:1-7
```

`bible_validator.py`는 **`sermon-planner-52week`에서 이식한 자기완결 결정론 자산**(개역개정 정경 66권 장·절 수 테이블 임베드, 원본과 동일·무결성 보존). `validate_reference(ref)`가 책 약어 정규화 후 장 수·절 수 범위를 검사해 **없는 장·절·가짜 책이름을 적발**한다(본문 할루시네이션 차단).

## 네 가지 점검
1. **본문 실재(위반)**: 각 `primary_text`·`parallel_texts`를 validate_reference로 검사. 없는 장·절·가짜 책은 위반(차단) — week-composer로 되돌려 교체.
2. **중복(경고)**: 같은 본문이 한 해 여러 주에 등장하면 표시(`duplicates`).
3. **균형(경고)**: 구약/신약 비율(`ot_nt_balance`)·장르 분포(`genre_balance`: 내러티브/서신/시가/예언/복음서). 한쪽 치우침 표시.
4. **교리 공백(경고)**: 한 해 동안 안 다룬 큰 복음·교리 주제(십자가·부활·성령·은혜·종말 등) 표시(`doctrine_gaps`).

## 가드레일
- **실재는 차단, 균형은 조언**: 본문 실재성은 위반으로 막되, 균형·공백은 경고(목사 의도·표어 흐름 존중).
- **지어내지 않음**: 본문을 모르면 "본문 미정"으로 두게 하고, 없는 본문을 그럴듯하게 만들지 않는다.
- **장르 분류는 보편적으로**: 학파 논쟁적 분류를 단정하지 않는다.

## 산출
`sermon-plan.json`의 `coverage`(`ot_nt_balance`·`genre_balance`·`duplicates`·`doctrine_gaps`). 형식은 대표 스킬 `references/sermon-plan-schema.md`. 이어 narrative-mapper가 여정을 잇는다.
