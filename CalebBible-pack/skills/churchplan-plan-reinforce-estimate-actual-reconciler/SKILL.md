---
name: churchplan-plan-reinforce-estimate-actual-reconciler
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#12 심장] churchplan-plan-reinforce 대표 스킬 전용. "추정과 실측을 맞대는 자" AI Agent. 워크샵에서 기억으로 표시한 추정값(특히 신뢰'하'/assumption 항목)을 자료에서 추출한 실측값과 맞대 "추정→실측" 이력을 남긴다. 추정을 지우지 않고 옆에 실측을 놓으며(estimate 보존·delta 차이), 실측은 자료 근거(actual_source) 있을 때만 교체하고, 추정과 실측이 유의하게 다르면 mismatch로 강조해 새 병목 신호로 연결한다. #12의 심장이자 "계획이 스스로 자란다"의 핵심.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-reinforce가 data-extractor 직후 호출한다.

  ## Detailed Methodology — 입력: verify_targets(#10 verify_seeds + 6스키마 신뢰'하' 종자)+extracted_data(자료 추출값). 신뢰'하'/assumption 항목 우선으로 추정 vs 실측을 대조(reinforce-catalog.md §2~3): 각 reconciliation에 estimate(원래 추정·보존)·actual(실측)·actual_source(자료 근거·실측교체 시 필수)·delta(차이)·mismatch(추정-실측 유의차)·status(실측교체|추정유지|이월)·new_confidence(실측 후 신뢰 갱신). 추정을 지우지 않는다(이력·투명성). 자료 없는 항목은 status=추정유지 또는 이월(실측 날조 금지). 어긋남(mismatch:true)은 강조 — 단순 교체가 아니라 새 병목 신호(02 라인253)로 plan-updater 조정에 연결. 산출은 reinforce.json의 reconciliations. 갱신은 plan-updater, 이월은 carryover-tracker가 이어 한다.
---

# churchplan-plan-reinforce-estimate-actual-reconciler — 추정과 실측을 맞대는 자 (INTERNAL · #12 심장)

> 대표 스킬 `churchplan-plan-reinforce`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 추정과 실측을 맞대는 자.** 기억의 추정과 자료의 실측을 나란히 놓아 계획을 또렷이 한다. **#12의 심장이다.**

## 역할 (추정 vs 실측 대조 — 이력 보존·어긋남 강조)
신뢰'하' 항목 우선으로 추정과 실측을 맞대고, 추정을 지우지 않고 "추정→실측" 이력을 남긴다. 어긋남은 새 병목 신호로 강조한다.

## 입력
- `verify_targets`(#10 verify_seeds + 6스키마 신뢰'하' 종자)
- `extracted_data`(data-extractor 산출)
- 이력·어긋남 양식: 대표 스킬 `references/reinforce-catalog.md` §2~3

## 방법
1. **신뢰'하' 우선**: assumption·confidence='하' 항목부터 대조(가장 흐린 곳부터).
2. **추정 보존**: 각 reconciliation에 `estimate`(원래 추정) 보존 + `actual`(실측) + `delta`(차이).
3. **실측 근거**: `status:"실측교체"`는 `actual_source`(자료 근거) 필수. 자료 없으면 `추정유지`/`이월`.
4. **어긋남 강조**: 추정-실측 유의차면 `mismatch:true`(새 병목 신호 → plan-updater).
5. **신뢰 갱신**: 실측 후 `new_confidence`(보통 '상').

## 가드레일
- **추정 삭제 금지**: estimate 보존(이력·투명성).
- **실측 날조 금지**: actual_source 없는 실측교체 금지.
- **대조까지**: 갱신은 plan-updater, 이월은 carryover-tracker.

## 산출
`reinforce.json`의 `reconciliations`[]{item·estimate·actual·actual_source·delta·mismatch·status·new_confidence}. 형식은 대표 스킬 `references/reinforce-schema.md`. 이어 plan-updater가 갱신한다.
