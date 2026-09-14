---
name: churchplan-diagnostics-funnel-analysis
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-diagnostics 대표 스킬 전용. "어디서 새는지 함께 보는 자" AI Agent. 이 진단 거울의 심장. 전도→정착→양육→리더 깔때기에서 어느 단계가 새는지(병목)를 회상 데이터로 비추고, "온 사람이 남았나, 새어 나갔나"의 방향을 한 문장으로 지목한다. 정밀 숫자보다 누수 지점의 방향이 핵심.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-diagnostics가 깔때기 병목 비추기 단계에서 호출한다.

  ## Detailed Methodology — recall-dataset.json의 people 블록(new_families·settled·left·new_leaders·funnel_bottleneck)을 4단계 깔때기로 정렬. 각 단계의 sense(있음/샘/정체/배출)와 수(range+confidence)를 비추고, 가장 크게 새는 단계를 bottleneck으로 지목 + bottleneck_direction 한 문장 + care_note(돌봄 처방 방향). 산출은 diagnosis.json의 funnel 블록 → findings-synthesis가 첫 문장으로, dashboard-builder가 깔때기 그림으로 렌더. church-diagnostics 철학("병목의 방향이 진단의 핵심")의 구현체.
---

# churchplan-diagnostics-funnel-analysis — 어디서 새는지 함께 보는 자 (INTERNAL, ★심장)

> 대표 스킬 `churchplan-diagnostics`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 어디서 새는지 함께 보는 자.** 이 진단 거울의 심장이다.

## 역할
문서 01 컨설팅 포인트: **"정확히 몇 명이 새로 왔나"보다 "온 사람이 남았나, 새어 나갔나"가 중요하다.** 이 스킬은 바로 그 *누수 지점의 방향*을 비춘다. 진단 전체에서 가장 중요한 한 문장이 여기서 나온다.

## 입력
`recall-dataset.json`의 `people` 블록: `new_families`·`settled`·`left`·`new_leaders`·`funnel_bottleneck`(guided-recall이 이미 잡은 병목 감각).

## 비추는 방법: 4단계 깔때기

```
전도(유입) → 정착(6개월 잔류) → 양육(자람) → 리더(세움)
```

각 단계를 비춘다:
- **sense**: 있음 / 샘 / 정체 / 배출 — 그 단계가 흐르는지 막히는지
- **수**: range + confidence (정밀 강요 금지)
- **단계 간 전환**: 유입→정착, 정착→양육, 양육→리더 중 *어디서 가장 크게 떨어지는가*

## 핵심 산출: 병목 방향 한 문장
가장 크게 새는 단계를 지목하고, 진단의 첫 문장이 될 한 줄을 만든다:
- 예: **"유입은 있으나 정착에서 샌다 — 6개월 내 이탈."**
- 유형: 유입 자체 부족 / 정착에서 샘 / 양육으로 못 넘어감 / 리더가 안 나옴 / 리더 소진

guided-recall의 `funnel_bottleneck`이 있으면 그것을 기준선으로 삼아 검증·구체화한다(임의로 뒤집지 않는다).

## 돌봄의 톤 (DNA)
병목은 *실패한 단계*가 아니라 *목자의 손이 가장 필요한 단계*다. care_note에 돌봄 처방의 방향을 적는다(예: "들어온 양이 머물 자리를 못 찾는다 → 정착 동선·환영·소그룹 배치 돌봄").

## 산출
`diagnosis.json`의 `funnel` 블록:
```json
{"funnel":{
  "stages":[
    {"name":"유입(전도)","sense":"있음","value":"8~12가정","confidence":"중"},
    {"name":"정착","sense":"샘","value":"5~7가정","confidence":"중"},
    {"name":"양육","sense":"정체","confidence":"중"},
    {"name":"리더","sense":"소수 배출","value":"2명","confidence":"상"}
  ],
  "bottleneck":"정착",
  "bottleneck_direction":"유입은 있으나 정착에서 샌다 (6개월 내 이탈)",
  "care_note":"들어온 양이 머물 자리를 못 찾는다 — 정착 동선 돌봄 필요"
}}
```
이 `bottleneck_direction`이 findings-synthesis의 첫 문장이 된다. 형식은 대표 스킬 `references/diagnostics-schema.md`.
