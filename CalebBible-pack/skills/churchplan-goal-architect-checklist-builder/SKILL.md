---
name: churchplan-goal-architect-checklist-builder
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-goal-architect 대표 스킬 전용. "점검표를 짓는 자" AI Agent. 목사가 확정한 goals.json을 3축 목표·지표 요약표(md)와 분기 점검 칸을 가진 xlsx 점검표 씨앗으로 렌더한다. 이 점검표는 #9 review-rhythm이 이어받는 씨앗이다. 렌더 전 핵심 게이트(정성↔정량 짝·과욕 상한)를 재강제해 오염된 목표가 표로 굳지 않게 한다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-goal-architect가 목사 목표치 확정 HITL 이후에만 호출한다.

  ## Detailed Methodology — 입력: 목사 확정된 goals.json(meta.status='확정'·confirmed 채워짐). scripts/build_checklist.py로 ① goal-checklist.md(표어·상태·3축 목표 요약표[축·방향목표·신호지표·기준선·목표치·기한] + 유지/중단 + 짐 가늠 경고 + 신호 프레이밍 안내) ② goal-checklist.xlsx(분기 점검 칸 Q1~Q4 빈칸 포함·유지중단 시트·경고 시트, openpyxl 없으면 csv 폴백) 산출. 스크립트는 렌더 전 핵심 게이트(필수 블록·정성정량 짝·과욕 상한)를 재강제(cys-insight 패턴)해 위반 시 렌더 거부. xlsx 점검표는 #9 review-rhythm 분기 스코어카드의 씨앗.
---

# churchplan-goal-architect-checklist-builder — 점검표를 짓는 자 (INTERNAL)

> 대표 스킬 `churchplan-goal-architect`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 점검표를 짓는 자.** 확정된 목표를 1년 내내 따라갈 점검표로 굳힌다. **반드시 목사 확정 HITL 이후에만** 작동한다.

## 역할
목사가 확정한 `goals.json`을 손에 잡히는 산출물로 렌더한다 — 한눈에 보는 요약표(md)와 분기마다 따라갈 점검표 씨앗(xlsx).

## 입력
- 목사 확정된 `goals.json` (`meta.status:"확정"`·`confirmed` 채워짐). 확정 전이면 렌더하지 않는다.

## 렌더 (결정론 스크립트)

```bash
python3 <이 스킬 폴더>/scripts/build_checklist.py <goals.json> [출력디렉토리]
```

산출물:
1. **`goal-checklist.md`** — 표어·상태 + **3축 목표 요약표**(축·방향 목표·신호 지표·기준선·올해 목표치·기한) + 올해 유지/중단 + 짐 가늠 경고 + "지표는 채찍 아닌 목자의 눈" 안내.
2. **`goal-checklist.xlsx`** — 동일 표 + **분기 점검 칸(Q1~Q4 빈칸)** + 유지·중단 시트 + 경고 시트. openpyxl 없으면 `goal-checklist.csv` 폴백.

## 게이트 재강제 (garbage-in 차단)
스크립트는 렌더 전 핵심 게이트(필수 블록·**정성↔정량 짝**·**과욕 상한**)를 자체 재확인한다(cys-insight-report 패턴). 위반 시 렌더를 거부하고 "fidelity-guard 먼저 통과시키라"며 종료. 오염된 목표가 점검표로 굳는 것을 막는다.

## 분기 점검 씨앗
xlsx의 Q1~Q4 빈칸은 #9 `review-rhythm`이 이어받아 분기 스코어카드(신호등)로 키운다. 여기서는 *씨앗*만 — 목표·지표·기한이 점검 가능한 격자로 정렬되면 충분하다.

## 가드레일
- **확정 후에만**: 목사가 목표치를 확정하기 전에는 렌더하지 않는다("정해 주지 않음"의 #3 버전).
- **신호 프레이밍 보존**: 표에도 지표가 돌봄 신호임을 안내로 남긴다.
- **지어내지 않음**: goals.json에 없는 목표·수치를 표에 추가하지 않는다(렌더는 전사일 뿐).

## 출력
`goal-checklist.md` + `goal-checklist.xlsx`(또는 `.csv`) — 대표 스킬 산출물. 이어 fidelity-guard가 최종 검증한다.
