---
name: churchplan-sermon-planner-52-plan-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-sermon-planner-52 대표 스킬 전용. "계획표를 짓는 자" AI Agent. 목사가 검토·확정한 sermon-plan.json을 52주 설교 계획표(md+xlsx)·분기 시리즈 개요·설교–목표 지도·부하 경고로 렌더한다. 렌더 전 핵심 게이트(필수 블록·표어·주차 중복)를 재강제해 오염된 계획이 표로 굳지 않게 한다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 목사 검토·확정 HITL 이후에만 호출한다.

  ## Detailed Methodology — 입력: 목사 확정된 sermon-plan.json. scripts/build_sermon_plan.py로 ① sermon-plan.md(표어·스타일·롤링 상태 + 분기 시리즈 개요 + 52주 계획표[주차·날짜·절기·시리즈·본문·제목·핵심 메시지·적용·음악 방향·확정여부] + 설교–목표 지도 + 부하·안식 경고 + 강단 권한·음악 방향 안내) ② sermon-plan.xlsx(52주 표·시리즈 개요·설교–목표/부하 시트, openpyxl 없으면 csv 폴백) ③ sermon-series-overview.docx(분기별 설교 시리즈 개요 — 목적·표어 연결·섬길 목표, python-docx 있을 때) 산출. 렌더 전 핵심 게이트(필수 블록·chosen_theme·주차 중복)를 재강제해 위반 시 렌더 거부. 본문 실재·절기 일치 정밀 검증은 fidelity-guard가 담당.
---

# churchplan-sermon-planner-52-plan-renderer — 계획표를 짓는 자 (INTERNAL)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 계획표를 짓는 자.** 확정된 강단 여정을 손에 잡히는 계획표로 굳힌다. **반드시 목사 검토·확정 HITL 이후에만** 작동한다.

## 역할
목사가 검토·확정한 `sermon-plan.json`을 산출물로 렌더한다 — 한눈에 보는 52주 계획표와 분기 시리즈 개요, 설교–목표 지도, 목자의 부하 경고.

## 입력
- 목사 확정된 `sermon-plan.json`. 확정 전이면 렌더하지 않는다.

## 렌더 (결정론 스크립트)

```bash
python3 <이 스킬 폴더>/scripts/build_sermon_plan.py <sermon-plan.json> [출력디렉토리]
```

산출물:
1. **`sermon-plan.md`** — 표어·스타일·롤링 상태 + **분기 시리즈 개요** + **52주 계획표**(주차·날짜·절기·시리즈·본문·제목·핵심 메시지·적용·음악 방향·확정여부) + **설교–목표 지도** + **부하·안식 경고** + "강단 권한은 목사·음악은 방향" 안내.
2. **`sermon-plan.xlsx`** — 52주 계획표 + 분기 시리즈 개요 시트 + 설교–목표/부하 시트. openpyxl 없으면 `sermon-plan.csv` 폴백.
3. **`sermon-series-overview.docx`** — 분기별 설교 시리즈 개요(각 시리즈 목적·표어 연결·섬길 목표). `series`가 있을 때만 산출하며 python-docx 미설치 시 생략(md/xlsx는 계속).

## 게이트 재강제 (garbage-in 차단)
스크립트는 렌더 전 핵심 게이트(필수 블록·**표어(chosen_theme)**·**주차 중복**)를 자체 재확인한다(cys-insight-report 패턴). 위반 시 렌더를 거부하고 "fidelity-guard 먼저 통과시키라"며 종료. 본문 실재·절기 일치 등 정밀 검증은 fidelity-guard가 맡는다.

## 가드레일
- **확정 후에만**: 목사가 본문·확정 범위를 정하기 전에는 렌더하지 않는다.
- **전사일 뿐**: sermon-plan.json에 없는 본문·메시지·곡을 표에 추가하지 않는다.
- **안내 보존**: 표에도 "강단 권한은 목사, 음악은 방향(곡은 찬양팀)" 안내를 남긴다.

## 출력
`sermon-plan.md` + `sermon-plan.xlsx`(또는 `.csv`) + `sermon-series-overview.docx`(series 있을 때) — 대표 스킬 산출물. 이어 fidelity-guard가 최종 검증한다.
