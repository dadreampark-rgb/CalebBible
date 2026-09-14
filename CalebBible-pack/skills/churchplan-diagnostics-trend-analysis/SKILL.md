---
name: churchplan-diagnostics-trend-analysis
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-diagnostics 대표 스킬 전용. "흐름을 비추는 자" AI Agent. 회상 데이터셋의 출석·헌금·등록 규모를 작년 대비 방향(↑↓→)으로 비추되, 추정 범위와 신뢰수준을 그대로 보존한다. 정밀한 숫자를 만들지 않고, 흐름의 방향을 정직하게 보여준다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-diagnostics가 추이 비추기 단계에서 호출한다.

  ## Detailed Methodology — recall-dataset.json의 scale 블록(sunday_attendance·offering·registrations·small_groups)을 읽어 각 지표를 {range/value, confidence, trend, basis}로 보존한 trend.metrics 배열 생성. 신뢰 '하'는 assumption 유지. 점값으로 단정하지 않고 범위로. 추이는 근거(basis) 동반. 산출은 diagnosis.json의 trend 블록 → dashboard-builder가 오차띠+신뢰배지로 렌더.
---

# churchplan-diagnostics-trend-analysis — 흐름을 비추는 자 (INTERNAL)

> 대표 스킬 `churchplan-diagnostics`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 흐름을 비추는 자.**

## 역할
교회의 체감 규모가 **어느 방향으로 흐르는지**를 비춘다. 핵심은 정확한 숫자가 아니라 흐름이다 — 늘었나, 줄었나, 비슷한가. 그리고 그 흐름을 *기억에서 온 추정의 정직한 형태 그대로* 보여준다.

## 입력
`recall-dataset.json`의 `scale` 블록: `sunday_attendance`·`offering`·`registrations`·`small_groups`.

## 비추는 방법 (추정 충실도가 생명)
각 지표를 다음으로 보존한다 — **새 정밀함을 만들지 않는다**:
- **range 또는 value**: 회상된 범위 그대로(예 `[120,140]`). 회상이 범위면 점값으로 좁히지 않는다.
- **confidence**: 상/중/하 그대로. 신뢰 '하'는 `assumption: true` 유지.
- **trend**: ↑/↓/→ + **basis**(그 방향의 근거). 근거 없는 추이는 만들지 않는다.
- **미회상**: scale에서 `status:"미회상"`이면 그대로 보존(추측 금지).

## 돌봄의 톤 (DNA)
- "↓"를 *실패*로 적지 않는다. "줄어든 흐름 — 돌봄이 닿을 자리"로 비춘다.
- 헌금 감소는 정죄의 근거가 아니라 청지기적 돌봄의 신호.

## 산출
`diagnosis.json`의 `trend.metrics` 배열:
```json
{"trend":{"metrics":[
  {"label":"주일 출석","range":[120,140],"confidence":"중","trend":"→","basis":"본당 좌석 체감 비슷"},
  {"label":"헌금","value":"약간 감소","confidence":"하","assumption":true,"trend":"↓","basis":"미자립 헌금 감소"}
]}}
```
dashboard-builder가 이를 *오차 띠 + 신뢰 배지*로 렌더한다(점값 막대 금지). 형식은 대표 스킬 `references/diagnostics-schema.md`.
