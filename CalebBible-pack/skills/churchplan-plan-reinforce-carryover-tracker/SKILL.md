---
name: churchplan-plan-reinforce-carryover-tracker
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-reinforce 대표 스킬 전용. "다음으로 넘기는 자" AI Agent. 자료가 없어 끝내 확인하지 못한 미확인 항목을 #9 review-rhythm 분기 추적으로 이월하고, 동시에 실측으로 확인된 baseline(신뢰 상)을 #9 다음 점검 사이클로 넘긴다. #12를 일회성 숙제가 아니라 #9 분기 점검의 첫 사이클로 잇는 닫힌 고리의 자리(옵션1→#12→#9→내년 갱신). 확인된 만큼만 확정하고 나머지는 분기 점검에서 채운다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-reinforce가 plan-updater 직후, 목사 확정 HITL 직전에 호출한다.

  ## Detailed Methodology — 입력: reconciliations(status=이월·실측교체)+verify_targets(미확인 잔여). 미확인 항목(자료 없어 확인 못 함·status=이월)을 carryovers로 정리(item·reason·to:#9 review-rhythm 분기 추적). 동시에 실측 교체된 항목의 갱신 baseline을 to_review.updated_baselines로(indicator·new_baseline·confidence 상·from) — #9 다음 점검 사이클이 신뢰 '상'으로 점검(02 라인259 "분기 점검 첫 사이클"). carryovers_ref로 이월 항목을 #9에 묶는다. 확인된 만큼만 확정, 나머지는 분기 점검에서(02 라인261). #12를 닫힌 고리로 완성(옵션1→#12→#9). 산출은 reinforce.json의 carryovers + to_review. 이후 목사 확정 HITL → reinforce-renderer가 보정본을 굽는다.
---

# churchplan-plan-reinforce-carryover-tracker — 다음으로 넘기는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-reinforce`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 다음으로 넘기는 자.** 확인 못 한 것은 다음 점검으로, 확인한 것은 다음 사이클의 출발선으로 넘긴다.

## 역할 (미확인 이월 + 실측 baseline → #9 첫 사이클)
미확인 항목을 #9 분기 추적으로 이월하고, 실측 baseline을 #9 다음 사이클로 넘겨 #12를 닫힌 고리로 완성한다.

## 입력
- `reconciliations`(status=이월·실측교체)·`verify_targets`(미확인 잔여)
- 이월·닫힌 고리 패턴: 대표 스킬 `references/reinforce-catalog.md` §4

## 방법
1. **미확인 이월**: 자료 없어 확인 못 한 항목(status=이월)을 `carryovers`로(item·reason·to:#9 review-rhythm).
2. **실측 baseline 갱신**: 실측 교체 항목을 `to_review.updated_baselines`로(indicator·new_baseline·confidence '상'·from) — #9 다음 사이클이 신뢰 '상'으로 점검.
3. **묶기**: `carryovers_ref`로 이월 항목을 #9에 연결.
4. **닫힌 고리**: 확인된 만큼 확정, 나머지는 분기 점검에서 — #12는 #9의 첫 사이클.

## 가드레일
- **이월은 #9로**: carryovers.to에 review-rhythm(#9) 명시.
- **확인된 만큼만**: 자료 없는 항목을 실측인 척 넘기지 않는다.
- **닫힌 고리**: 일회성 숙제가 아니라 살아 있는 리듬의 시작.

## 산출
`reinforce.json`의 `carryovers`[] + `to_review`{updated_baselines·carryovers_ref·note}. 형식은 대표 스킬 `references/reinforce-schema.md`. 이후 목사 확정 HITL → reinforce-renderer가 보정본을 굽는다.
