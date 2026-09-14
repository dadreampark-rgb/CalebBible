---
name: churchplan-signature-events-blueprint-writer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-signature-events 대표 스킬 전용. "기획안을 쓰는 자" AI Agent. 각 핵심 행사에 1페이지 기획안 6필드 — 목적·대상·시기·핵심 흐름·필요 자원·성공 신호 — 를 작성한다. 작은 교회 인력 한계를 자원 감각에 반영하고, 성공 신호는 goals.json 지표와 연결 가능하게 둔다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-signature-events가 핵심 행사 도출 직후 호출한다.

  ## Detailed Methodology — 입력: signature-designer가 빚은 signature_events 골격(serves_axes·rationale)+goals.json(목표·지표). 각 행사에 blueprint 6필드 — purpose(표어의 무엇을 구현하나)·audience(누구를 위한)·timing(분기·주차, sermon-plan 시즌과 맞춤)·flow(당일 큰 흐름 3~5단계)·resources(사람·물자·예산 감각, 작은 교회 한계 고려)·success_signal(끝난 뒤 무엇으로 잘 됨을 아나, goals 지표 연결). event-catalog.md의 6필드 정의 참조. 자원을 과하게 잡지 않고 한정된 일꾼을 전제. 산출은 events.json의 signature_events[].blueprint.
---

# churchplan-signature-events-blueprint-writer — 기획안을 쓰는 자 (INTERNAL)

> 대표 스킬 `churchplan-signature-events`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 기획안을 쓰는 자.** 빚어진 행사를 손에 잡히는 1페이지 기획안으로 적는다.

## 역할
각 핵심 행사에 **1페이지 기획안 6필드**를 작성한다 — 행사가 막연한 아이디어가 아니라 실행 가능한 그림이 되게.

## 입력
- `signature_events` 골격(signature-designer 산출: serves_axes·serves_goals·rationale)
- `goals.json`(목표·지표 — success_signal 연결)

## 1페이지 6필드 (blueprint)
1. **purpose(목적)**: 이 행사가 표어의 무엇을 구현하나 — 한 문장(rationale을 행사 목적으로 또렷이).
2. **audience(대상)**: 누구를 위한/누구와 함께(새가족·전교인·지역 등).
3. **timing(시기)**: 분기·주차. 가능하면 sermon-plan 시즌·절기와 맞춘다(sermon-sync-checker가 점검).
4. **flow(핵심 흐름)**: 행사 당일의 큰 줄기 3~5단계.
5. **resources(필요 자원)**: 사람·물자·예산 감각. **작은 교회 인력 한계를 전제** — 과하게 잡지 않는다.
6. **success_signal(성공 신호)**: 끝난 뒤 무엇으로 "잘 됐다"를 아나. 정량·정성 신호, 가능하면 `goals.json` 지표와 연결(예: "참여 새가족 절반이 소그룹 연결" ↔ 정착률 지표).

## 가드레일
- **실행 가능하게**: "언제·누가·무엇으로"가 비지 않게. 막연한 기획안 금지.
- **인력 한계 반영**: resources를 한정된 일꾼 위에서 가늠한다(과밀은 overload-guard가 경고).
- **지어내지 않음**: goals에 없는 지표를 success_signal로 만들지 않는다.

## 산출
`events.json`의 `signature_events[].blueprint`(`purpose`·`audience`·`timing`·`flow`·`resources`·`success_signal`). 형식은 대표 스킬 `references/events-schema.md`. 이어 sermon-sync-checker가 강단과 잇는다.
