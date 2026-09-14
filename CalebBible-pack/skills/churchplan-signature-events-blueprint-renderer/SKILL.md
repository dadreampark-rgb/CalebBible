---
name: churchplan-signature-events-blueprint-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-signature-events 대표 스킬 전용. "기획안을 짓는 자" AI Agent. 목사가 검토·확정한 events.json을 핵심 행사 1페이지 기획안(md/docx)과 행사–목표 연결 지도(md/xlsx)로 렌더한다. 행사–목표 지도는 #4 설교–목표 지도와 짝. 렌더 전 핵심 게이트(필수 블록·표어·목적·행사 상한)를 재강제해 목적 없는 행사가 기획안으로 굳지 않게 한다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-signature-events가 목사 검토·확정 HITL 이후에만 호출한다.

  ## Detailed Methodology — 입력: 목사 확정된 events.json. scripts/build_event_plan.py로 ① event-plan.md(표어·무게중심 + 행사–목표 연결 지도 + 핵심 행사별 1페이지 기획안[표어연결·축목표·근거·목적·대상·시기·흐름·자원·성공신호·설교정합] + 정기 행사 목록 + 정리 제안 + 과밀 경고 + 덜어냄 안내) ② event-plan.xlsx(행사–목표 지도 시트·경고/정리 시트, openpyxl 없으면 csv 폴백) 산출. 렌더 전 핵심 게이트(필수 블록·chosen_theme·serves_axes 목적·행사 상한 ≤5)를 재강제해 위반 시 렌더 거부. 정밀 검증은 fidelity-guard가 담당.
---

# churchplan-signature-events-blueprint-renderer — 기획안을 짓는 자 (INTERNAL)

> 대표 스킬 `churchplan-signature-events`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 기획안을 짓는 자.** 확정된 핵심 행사를 손에 잡히는 기획안으로 굳힌다. **반드시 목사 검토·확정 HITL 이후에만** 작동한다.

## 역할
목사가 검토·확정한 `events.json`을 산출물로 렌더한다 — 행사별 1페이지 기획안과 행사–목표 연결 지도.

## 입력
- 목사 확정된 `events.json` (`meta.status:"확정"`·`confirmed` 채워짐). 확정 전이면 렌더하지 않는다.

## 렌더 (결정론 스크립트)

```bash
python3 <이 스킬 폴더>/scripts/build_event_plan.py <events.json> [출력디렉토리]
```

산출물:
1. **`event-plan.md`** — 표어·무게중심 + **행사–목표 연결 지도** + **핵심 행사별 1페이지 기획안**(표어 연결·섬기는 축·목표·근거·목적·대상·시기·흐름·자원·성공 신호·설교 정합) + 정기 행사 목록 + 정리 제안 + 과밀 경고 + 덜어냄 안내.
2. **`event-plan.xlsx`** — 행사–목표 지도 시트 + 경고·정리 시트. openpyxl 없으면 `event-plan.csv` 폴백.

행사–목표 지도는 #4 `sermon_goal_map`(설교–목표 지도)과 짝을 이뤄 강단·행사가 한 방향임을 보인다.

## 게이트 재강제 (garbage-in 차단)
스크립트는 렌더 전 핵심 게이트(필수 블록·**표어**·**목적(serves_axes)**·**행사 상한 ≤5**)를 자체 재확인한다(cys-insight-report 패턴). 위반 시 렌더를 거부하고 "fidelity-guard 먼저 통과시키라"며 종료. 목적 없는 행사가 기획안으로 굳는 것을 막는다.

## 가드레일
- **확정 후에만**: 목사가 정리·확정하기 전에는 렌더하지 않는다.
- **전사일 뿐**: events.json에 없는 행사·목적·자원을 기획안에 추가하지 않는다.
- **덜어냄 보존**: 표에도 정리 제안·"행사 수보다 깊이" 안내를 남긴다.

## 출력
`event-plan.md` + `event-plan.xlsx`(또는 `.csv`) — 대표 스킬 산출물. 이어 fidelity-guard가 최종 검증한다.
