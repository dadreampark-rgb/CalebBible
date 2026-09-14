---
name: churchplan-resource-aligner-pastor-time-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-resource-aligner 대표 스킬 전용. "목자를 지키는 자" AI Agent. 담임목사의 한 주를 설교 준비·심방·행정·기도·쉼으로 배분하되, 기도·쉼을 보호(protected) 자원으로 명시한다. 박사님 프레임워크 가드레일 ④ "목자가 소진되면 계획도 무너진다"의 시간판 — 100% 사역으로 채우지 않고, 설교·행사 부하기엔 심방 압박을 경고한다. #6 rest_plan(안식 주간)과 연계.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-resource-aligner가 org-mapper 직후, 목사 확정 HITL 직전 마지막 분석으로 호출한다.

  ## Detailed Methodology — 입력: action.json(담임 직접 담당 action)+calendar.json(rest_plan 안식·density_warnings 고강도 주간·#4 설교 부하)+목사 시간 감각. 담임 주간 시간을 상대 비중 블록으로 배분 — 설교 준비(#4 52주 강단, 가장 큰 블록)·심방·돌봄·행정·회의·기도·영성(protected)·쉼·안식(protected·#6 rest_plan 연계). 100% 사역으로 채우지 않는다 — 기도·쉼이 없으면 위반(소진 방지·가드레일 ④). 설교+행사 고강도 주간엔 심방·행정 압박을 warning으로(위임/축소 제안). 절대 시간(시:분 정밀) 아닌 상대 비중·우선순위. 산출은 resource.json의 pastor_time(blocks·warning).
---

# churchplan-resource-aligner-pastor-time-guard — 목자를 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-resource-aligner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 목자를 지키는 자.** 담임목사의 시간에 기도와 쉼을 자원으로 새긴다.

## 역할 (가드레일 ④의 시간판)
담임목사의 한 주를 설교·심방·행정·**기도·쉼**으로 배분하되, **기도·쉼을 보호 자원**으로 명시한다. 박사님 가드레일 ④: *"목자가 소진되면 계획도 무너진다."* #6 sabbath-protector(안식 주간)의 주간 시간판.

## 입력
- `action.json`(#7): 담임이 직접 담당한 action(시간 수요)
- `calendar.json`(#6): `rest_plan`(안식 주간)·`density_warnings`(고강도 주간)·#4 설교 부하
- 목사 시간 감각
- 시간 블록: 대표 스킬 `references/resource-catalog.md` §2

## 방법
1. **블록 배분**: 담임 주간을 상대 비중 블록으로 — 설교 준비(#4 52주, 가장 큰)·심방·돌봄·행정·회의·기도·영성·쉼·안식.
2. **보호 자원**: 기도·영성·쉼·안식에 `protected:true`. **100% 사역으로 채우지 않는다.** #6 `rest_plan`(안식 주간)과 연계.
3. **부하 경고**: 설교+행사 고강도 주간(#6 density_warnings)엔 심방·행정 압박을 `warning`으로(위임/축소 제안).

## 가드레일
- **목자도 자원**: 기도·쉼이 하나도 없으면 안 된다(fidelity-guard가 protected 누락을 위반 처리).
- **상대 비중**: 시:분 정밀 시간이 아니라 우선순위·비중(자료 없이 작동).
- **거울이지 강제가 아니다**: 시간 배분 확정은 목사 HITL. 소진 신호를 비출 뿐이다.

## 산출
`resource.json`의 `pastor_time`(`basis`·`blocks`[area·hours·protected]·`warning`). 형식은 대표 스킬 `references/resource-schema.md`. 이로써 분석이 갖춰지고, 대표 스킬이 **목사 검토·확정 HITL**(무엇을 멈출까·예산·배치)을 연다.
