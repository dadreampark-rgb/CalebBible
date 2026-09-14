---
name: churchplan-action-planner-action-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-action-planner 대표 스킬 전용. "실행표를 짓는 자" AI Agent. 목사 검토·확정(HITL) 후에만 작동해, action.json을 부서별 실행계획표로 렌더한다 — md(부서별 행동: 목적·시기·담당·자원·월별 step + 공백 목록 + 경고)와 xlsx(부서별 시트 + 공백·경고 시트, openpyxl 없으면 csv 폴백). 렌더 전 핵심 게이트(필수 블록·표어·부서·근거 추적·status)를 재강제한다(cys-insight 패턴).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-action-planner가 목사 검토·확정 HITL 이후에만 호출한다(확정 전 렌더 금지).

  ## Detailed Methodology — scripts/build_action.py 실행(표준 라이브러리만, xlsx는 openpyxl 있을 때만·없으면 csv). 입력 action.json → ① action-plan.md: 부서별 실행계획표(부서→action: 목적·시기·담당[TBD 강조]·자원·월별 step) + "언제·누가·무엇으로" 공백 목록 + 과잉·중복 경고 ② action-plan.xlsx: 부서별 실행 시트(부서·행동·목적·시기·담당·자원·마일스톤) + 공백·경고 시트, 세피아 헤더(#594B3B)·TBD 강조. 렌더 전 gate()로 핵심 게이트 재강제 — 필수 블록·meta.chosen_theme·departments·각 action source_goal·purpose 존재·status. 위반 시 렌더 거부(종료코드 1). 전체 정밀 검증(근거 추적·공백 정직·캘린더 정합)은 fidelity-guard.
---

# churchplan-action-planner-action-renderer — 실행표를 짓는 자 (INTERNAL)

> 대표 스킬 `churchplan-action-planner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 실행표를 짓는 자.** 확정된 행동을 부서별 실행계획표로 짓는다.

## 역할 (확정 후에만 짓는다)
**목사 검토·확정(HITL) 이후에만** action.json을 부서별 실행계획표로 렌더한다. 담당·자원 공백 채움, 과잉 행동 정리 전에는 최종 표를 짓지 않는다.

## 결정론 렌더

```bash
python3 <이 스킬 폴더>/scripts/build_action.py <action.json> [출력디렉토리]
```

산출:
- **`action-plan.md`** — 부서별 실행계획표(부서마다 행동: 목적·시기·담당[TBD 강조]·자원·월별 step) + "언제·누가·무엇으로" 공백 목록 + 과잉·중복 경고.
- **`action-plan.xlsx`** — 부서별 실행 시트(부서·행동·목적·시기·담당·자원·마일스톤) + 공백·경고 시트. 세피아 헤더(#594B3B). **openpyxl 없으면 `.csv` 폴백.**

## 렌더 전 게이트 재강제 (cys-insight 패턴)
`build_action.py`의 `gate()`가 렌더 전 핵심을 재검사한다 — 필수 블록(meta·actions)·`meta.chosen_theme`·`meta.departments`·**각 action의 `source_goal`·`purpose` 존재**·`status`. 위반 시 **렌더 거부**(종료코드 1)하고 fidelity-guard로 되돌린다. 근거 없는 행동·빈 표를 그려 확정처럼 보이게 하지 않는다.

## 가드레일
- **확정 후에만.** HITL 이전 렌더 금지.
- **공백을 숨기지 않는다.** TBD 담당·미정 자원을 표에 그대로(강조) 드러낸다 — 채워진 척 그리지 않는다.
- **고아 action을 숨기지 않는다.** `department`가 `meta.departments`에 없어 부서별 표에서 누락되는 action은 "⚠️ 부서 미배치 action" 섹션으로 가시화한다(조용히 사라지지 않게 — fidelity-guard로 되돌릴 신호).
- **전체 검증은 fidelity-guard.** 게이트는 렌더 최소 안전선일 뿐, 근거 추적·공백 정직·캘린더 정합 정밀 검증은 `validate_action.py`.

## 산출
`action-plan.md` + `action-plan.xlsx`(또는 `.csv`). 대표 스킬 Orchestration Trace (c)/(d)의 실행계획표 섹션에 표시. 이로써 부서별 실행계획표가 완성되어 resource-aligner(#8)·plan-compiler(#10)로 넘어간다.
