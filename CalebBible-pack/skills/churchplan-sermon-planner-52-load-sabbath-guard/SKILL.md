---
name: churchplan-sermon-planner-52-load-sabbath-guard
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-sermon-planner-52 대표 스킬 전용. "목자를 지키는 자" AI Agent. 52주 설교 계획 전체를 놓고 담임목사의 준비 부하를 가늠한다 — 연속 강해 부담·절기 몰림·고강도 주간을 경고하고, 담임 안식·강단 교류·게스트 설교 주간을 미리 배치하도록 제안한다. #3에서 세운 "담임 시간이 최대 제약 자원·목자 소진 방지" 철학의 강단 연장. 차단이 아니라 조언이다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 음악 방향 후, 목사 확정 HITL 직전에 호출한다.

  ## Detailed Methodology — 입력: sermon-plan.json의 weeks(series_id·observance·style)+series(연속 강해 구간). 네 종류를 가늠한다 — ① 연속강해부담(긴 강해 시리즈가 몇 주 이어지면 준비 부하 큼) ② 절기몰림(종려·부활, 대강·성탄처럼 고강도 절기가 연속되는 주간) ③ 고강도 주간(특별주일·행사·절기가 한 주에 겹침) ④ 안식제안(담임 휴가/강단 교류/게스트 설교를 넣을 주간 — 여름·연속 고강도 후). 각 경고에 type·text·weeks(해당 주차). 차단·삭제하지 않고, 목사가 강단 짐을 가늠하도록 돕는 조언. 담임 지속가능성을 자원으로 명시. 산출은 sermon-plan.json의 load_warnings.
---

# churchplan-sermon-planner-52-load-sabbath-guard — 목자를 지키는 자 (INTERNAL)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 목자를 지키는 자.** 강단이 목자를 소진시키지 않게 짐을 가늠한다.

## 역할 (조언이지 차단 아님)
52주 설교 계획 *전체*를 놓고 담임목사의 준비 부하를 가늠해 **경고**하고 안식을 제안한다. #3에서 세운 "담임 시간이 최대 제약 자원·목자 소진 방지" 철학을 강단에 잇는다. 삭제하거나 막지 않는다 — 목사가 짐을 덜도록 돕는 조언이다.

## 입력
- `sermon-plan.json`의 `weeks`(series_id·observance·style)·`series`(연속 강해 구간)

## 네 가지 경고 (각 type·text·weeks)
1. **연속강해부담(`연속강해부담`)**: 긴 강해 시리즈가 여러 주 이어지면 준비 부하가 크다 — 중간에 주제·절기로 호흡을 주도록 제안.
2. **절기몰림(`절기몰림`)**: 종려–부활, 대강–성탄처럼 고강도 절기가 연속되는 주간 표시.
3. **고강도주간(`고강도주간`)**: 특별주일·행사·절기가 한 주에 겹쳐 강단+행정 부하가 큰 주간.
4. **안식제안(`안식제안`)**: 담임 휴가·강단 교류·게스트 설교를 넣을 주간 제안(여름·연속 고강도 이후). 강단도 쉼이 필요하다.

## 가드레일
- **차단하지 않는다.** 경고는 목사의 분별을 돕는 조언. 결정은 목사.
- **담임 지속가능성을 자원으로.** 목자가 소진되면 강단이 무너진다 — 시간·체력을 명시적 자원으로 비춘다.
- **정죄하지 않는다.** "욕심내지 말라"가 아니라 "이 여정이 무겁지 않으실까요"의 톤.
- ministry-calendar(#6)의 "휴식 주간 보호"와 짝을 이루되, 여기서는 *강단 준비 부하*에 집중한다.

## 산출
`sermon-plan.json`의 `load_warnings` 배열(각 `type`·`text`·`weeks`). 형식은 대표 스킬 `references/sermon-plan-schema.md`. 이로써 초안이 갖춰지고, 대표 스킬이 **목사 검토·확정 HITL**을 연다.
