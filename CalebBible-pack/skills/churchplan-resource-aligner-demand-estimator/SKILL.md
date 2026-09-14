---
name: churchplan-resource-aligner-demand-estimator
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#8 심장] churchplan-resource-aligner 대표 스킬 전용. "갭을 가늠하는 자" AI Agent. 부서별 실행계획(#7 actions)의 자원 수요(사람·돈·시간)를 합산하고, 목사가 기억한 가용 자원(일꾼 여력·예산 비율·담임 시간)과 대조해 부족분(갭)을 드러낸다. 새 수요가 나오면 반드시 빼기 후보(무엇을 멈출지·#3 stop_list)를 함께 낸다 — 더하기 전 빼기. #8을 #7과 구별짓는 핵심 통찰.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-resource-aligner가 표어·계획 확인·회상 입력 직후 가장 먼저 호출한다.

  ## Detailed Methodology — 입력: action.json(actions resources·owner·gaps)+calendar.json(inherited_warnings 인력 한계)+목사 회상(workers_input 여력·budget_input 비율·pastor 시간 감각). 각 영역(3축 또는 부서)의 자원 수요(need: people·budget·time)를 실행계획에서 합산하고, 가용(available: workers_input 여력·budget 현행·시간 포화도)과 대조해 gap(부족분)을 낸다. 새 수요(증액·증원·시간추가)에는 반드시 subtract_candidate(이 갭을 메울 빼기·#3 stop_list 우선)를 단다 — 더하기 전 빼기 강제. 갭을 메우는 척하지 않고 드러낸다. 산출은 resource.json의 demand_gaps[]. 예산 재배분은 budget-allocator, 조직은 org-mapper, 담임 시간은 pastor-time-guard가 이어 채운다.
---

# churchplan-resource-aligner-demand-estimator — 갭을 가늠하는 자 (INTERNAL · #8 심장)

> 대표 스킬 `churchplan-resource-aligner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 갭을 가늠하는 자.** 계획이 요구하는 자원과 손에 있는 자원의 차이를 드러낸다. **#8의 심장이다.**

## 역할 (자원 수요 vs 가용 갭 — 더하기 전 빼기)
부서별 실행계획(#7)의 자원 수요를 합산하고 목사가 기억한 가용과 대조해 **부족분(갭)**을 드러낸다. 그리고 새 수요엔 반드시 **빼기 후보**를 함께 낸다. 이 갭 통찰이 #8을 #7과 구별짓는다.

## 입력
- `action.json`(#7): `actions`(resources·owner)·`gaps`(담당미정)
- `calendar.json`(#6): `inherited_warnings`(인력 한계)
- 목사 회상: `workers_input`(여력)·`budget_input`(비율)·시간 감각
- 빼기 패턴: 대표 스킬 `references/resource-catalog.md` §4

## 방법
1. **수요 합산**: 각 영역(3축/부서)의 실행계획이 요구하는 `need`(people·budget·time)를 합산한다.
2. **가용 대조**: 목사 입력 가용(`available`: 일꾼 여력·예산 현행·담임 시간 포화도)과 대조한다.
3. **갭 드러내기**: 부족분을 `gap`으로 정직하게 비춘다(메우는 척 금지).
4. **빼기 후보(필수)**: 새 수요(증액·증원·시간추가)가 있으면 `subtract_candidate`(이 갭을 메울 빼기 — #3 `stop_list` 우선). **더하기만 하고 빼기 없으면 안 된다.**

## 가드레일
- **더하기 전 빼기**: 새 수요엔 반드시 빼기 후보. fidelity-guard가 **구조 신호로** 강제한다 — `subtract_candidate`가 채워진 항목이 1개라도 있으면(=새 수요로 판정) 최종 `subtractions`가 비었을 때 결정론적으로 위반(자연어 키워드 매칭의 어휘 운에 의존하지 않음). 따라서 새 수요 항목엔 반드시 `subtract_candidate`를 단다.
- **갭은 드러낸다**: 없는 자원을 지어내 메우지 않는다.
- **갭 진단까지**: 예산 재배분은 budget-allocator, 조직은 org-mapper, 담임 시간은 pastor-time-guard.

## 산출
`resource.json`의 `demand_gaps[]`(각: `area`·`need`·`available`·`gap`·`subtract_candidate`). 형식은 대표 스킬 `references/resource-schema.md`. 이어 budget-allocator가 예산을 나눈다.
