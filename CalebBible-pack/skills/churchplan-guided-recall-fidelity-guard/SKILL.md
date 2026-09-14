---
name: churchplan-guided-recall-fidelity-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-guided-recall 대표 스킬 전용. "신뢰 지킴이" AI Agent. 목사를 심문하는 것이 아니라, 다음 스킬들로 거짓이 흘러가지 않도록 회상 데이터셋의 토대를 지킨다. 추정과 실측을 구분하고, 신뢰 '하' 항목을 가정으로 표시하며, 회상에 없던 임의 수치·이름·본문이 끼어들었는지 결정론 스크립트로 검사한다(garbage-in 차단).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-guided-recall이 dataset-builder 산출 직후 최종 검증 단계에서 호출한다.

  ## Detailed Methodology — ABSOLUTE ANCHOR #2 강제 전담 검증 sub-skill. scripts/validate_recall_dataset.py로 (1)스키마 적합 (2)모든 수치의 confidence 동반 여부 (3)단정 스칼라(범위·신뢰 없는 수치) 적발 (4)미회상 항목의 정직한 null 처리 (5)신뢰 '하'의 assumption 플래그 (6)교차 일관성(추이↔근거)을 결정론적으로 검사. 통과 시 integrity 블록을 채우고 verify-after-workshop 목록을 생성. 실패 시 위반 항목을 대표 스킬에 반환해 보완 질문 유도. 과장·거짓 확신·근거 없는 수치 산출을 구조적으로 차단.
---

# churchplan-guided-recall-fidelity-guard — 신뢰 지킴이 (INTERNAL)

> 대표 스킬 `churchplan-guided-recall`이 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 신뢰 지킴이.** dataset-builder 산출 직후 호출되는 최종 게이트.

## 역할 (오해 금지)
이 스킬은 **목사를 검증하지 않는다.** 목사의 기억은 존중받는다. 이 지킴이가 막는 것은 *AI가 회상에 없던 것을 만들어 끼워 넣는 것* — 즉 데이터 토대의 오염이다.

> ABSOLUTE ANCHOR #2: "토대가 오염되면 아무리 다듬어도 거짓이 정교해질 뿐이다. Garbage-in 차단." 추정으로 세운 80% 계획은 정직하면 강력하지만, 거짓 확신으로 부풀린 100% 계획은 위험하다. 이 게이트가 그 경계를 지킨다.

## 결정론 검증 (프롬프트 + 스크립트 이중화)

LLM의 자기 검증은 미끄러진다. 그래서 **스크립트로 못 박는다.** dataset-builder가 만든 `recall-dataset.json`을 다음으로 검사한다:

```bash
python3 <이 스킬 폴더>/scripts/validate_recall_dataset.py <recall-dataset.json 경로>
```

스크립트가 검사하는 것:
1. **스키마 적합** — 필수 블록(meta·calendar_timeline·people·scale·heart·health_8areas)이 모두 있는가
2. **신뢰수준 동반** — 모든 수치 항목에 `confidence`(상/중/하)가 있는가
3. **단정 스칼라·점값위장 적발** — 메트릭 자리에 박힌 맨숫자뿐 아니라 `value` 필드 *안*의 정밀 단일 숫자(예 `{"value": 131}`)도 잡아 범위(`range:[lo,hi]`)로 되돌린다. `range`는 [lo,hi] 숫자 2원소·lo≤hi·음수 금지 구조까지 검증
4. **정직한 누락** — 미회상 항목이 추측으로 메워지지 않고 `null`+`"status":"미회상"`인가
5. **가정 플래그** — 신뢰 '하' 항목에 `"assumption": true`가 달렸는가
6. **교차 일관성** — `trend`가 있으면 `basis`(근거)가 있는가, 8영역 score는 1~5 **정수**인가(bool·실수 차단)
7. **최신 편향 차단** — `calendar_timeline`에 month 1~12 항목이 *물리적으로 모두 존재*하는가(내용은 비워도 항목 누락은 위반)
8. **본문 창작 차단** — `heart.gripping_scriptures`의 장·절 인용을 공유 결정론 자산 `bible_validator.validate_reference`로 검증해 **정경 범위 밖 인용(지어낸 책·장·절)을 위반으로 차단**하고, 절 단위 정밀 인용은 '미확정' 표기 권고 경고
9. **무결성 일관성** — `integrity` 블록이 있으면 `confidence_summary` 카운트·`assumptions_flagged` 집합이 실제 데이터와 일치하는지 교차검증
10. **헌금 절대 금액 차단** — `scale.offering`의 `value`·`basis`·`ratio_sense` 텍스트에 '숫자 선행' 절대 금액(₩·원·만원·억·달러 등)이 끼었는지 결정론으로 적발해 **위반으로 차단**. 헌금은 결산 없이 비율(%)·증감 방향만 받는다(scale-recall 원칙). 회상 단계에서 지어낸 절대 금액이 resource-aligner(#8 '절대 금액 금지' 최우선 규칙)로 새지 않게 상류에서 막는다. 비율·증감·범위는 정상(통화 토큰만 차단)

## 검증 후 처리

### 통과 시
- `integrity` 블록을 채운다:
  - `confidence_summary`: {상: n, 중: n, 하: n}
  - `assumptions_flagged`: 신뢰 '하' 항목 목록
  - `verify_after_workshop`: 워크샵 후 실측으로 교체할 1순위 목록(plan-reinforce #12가 소비)
  - `fabrication_check`: "passed"
- 대표 스킬에 "검증 통과 — 데이터셋 완료"를 반환.

### 실패 시
- 위반 항목을 **구체적으로** 대표 스킬에 반환한다(예: "scale.offering에 confidence 없음", "heart.gripping_scriptures에 회상에 없던 장·절 추정 의심").
- 대표 스킬은 이를 받아 **보완 질문으로 되돌아간다**(임의로 메우지 않는다). 누락은 비난이 아니라 다음 질문의 출발점이다.

## 추가 인간적 가드레일 (스크립트 밖)
스크립트가 못 잡는 것을 사람의 눈으로 본다:
- **과장·거짓 확신**: "올해 폭발적 부흥"처럼 회상 근거 없이 부푼 서술이 끼었는가 → 톤을 회상 수준으로 되돌린다.
- **본문 창작**: heart의 `gripping_scriptures`에 목사가 말하지 않은 장·절이 *단정*되었는가 → 목사가 말한 표현으로 되돌리거나 "본문 미확정"으로 표시.
- **이름 창작**: `names_recalled`에 회상에 없던 이름이 생겼는가 → 제거.

## 출력
검증 리포트(통과/실패 + 항목별 결과) + 채워진 `integrity` 블록. 이 리포트는 대표 스킬의 Orchestration Trace (c) 섹션에 그대로 표시된다.
