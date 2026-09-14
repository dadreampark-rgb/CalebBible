---
name: churchplan-ministry-calendar-calendar-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-ministry-calendar 대표 스킬 전용. "달력을 짓는 자" AI Agent. 목사 검토·확정(HITL) 후에만 작동해, calendar.json을 2027 통합 연간 사역 캘린더로 렌더한다 — html(분기·월·주 보기 + 부하 히트맵 + 안식 주간 강조)과 xlsx(52주 통합 그리드 + 경고·안식 시트, openpyxl 없으면 csv 폴백). 렌더 전 핵심 게이트(필수 블록·표어·52주 무결성·상속 id)를 재강제한다(cys-insight 패턴).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-ministry-calendar가 목사 검토·확정 HITL 이후에만 호출한다(확정 전 렌더 금지).

  ## Detailed Methodology — scripts/build_calendar.py 실행(표준 라이브러리만, xlsx는 openpyxl 있을 때만·없으면 csv). 입력 calendar.json → ① calendar.html: 분기 섹션 + 각 주 셀(주차·날짜·절기·설교 제목·행사·캠페인·마일스톤)에 부하 level 히트맵 색상(낮음 연녹·보통 연황·높음 연적)·안식 보호 주간 파랑 강조·밀집 경고 배지, 분기/월/주 보기, inline CSS·세피아 팔레트(#594B3B) ② calendar.xlsx: 52주 그리드 시트(주차·날짜·분기·절기·설교·행사·캠페인·마일스톤·부하) + 경고·안식 시트. 렌더 전 gate()로 핵심 게이트 재강제 — 필수 블록·meta.chosen_theme·week 1~52 무결성(중복/범위)·status. 위반 시 렌더 거부(종료코드 1). 전체 정밀 검증은 fidelity-guard.
---

# churchplan-ministry-calendar-calendar-renderer — 달력을 짓는 자 (INTERNAL)

> 대표 스킬 `churchplan-ministry-calendar`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 달력을 짓는 자.** 통합된 한 해를 한눈에 보이는 달력으로 짓는다.

## 역할 (확정 후에만 짓는다)
**목사 검토·확정(HITL) 이후에만** calendar.json을 통합 연간 사역 캘린더로 렌더한다. 무리한 주간 재배치·안식 확정 전에는 최종 캘린더를 짓지 않는다.

## 결정론 렌더

```bash
python3 <이 스킬 폴더>/scripts/build_calendar.py <calendar.json> [출력디렉토리]
```

산출:
- **`calendar.html`** — 분기·월·주 보기. 각 주 셀에 주차·날짜·절기·설교 제목·행사·캠페인·마일스톤. **부하 히트맵**(낮음 연녹·보통 연황·높음 연적), **안식 보호 주간** 파랑 강조, **밀집 경고** 배지. inline CSS·세피아 팔레트(#594B3B, #5 일관).
- **`calendar.xlsx`** — 52주 통합 그리드 시트(주차·날짜·분기·절기·설교·행사·캠페인·마일스톤·부하) + 경고·안식 시트. **openpyxl 없으면 `.csv` 폴백.**

## 렌더 전 게이트 재강제 (cys-insight 패턴)
`build_calendar.py`의 `gate()`가 렌더 전 핵심을 재검사한다 — 필수 블록(meta·weeks)·`meta.chosen_theme`·**week 1~52 무결성**(범위·중복)·`status`. 위반 시 **렌더 거부**(종료코드 1)하고 fidelity-guard로 되돌린다. 렌더러가 garbage를 그려 확정처럼 보이게 하지 않는다.

## 가드레일
- **확정 후에만.** HITL 이전 렌더 금지.
- **여백을 지운다고 채우지 않는다.** 빈 주는 빈 채로 그린다(쉼의 시각화) — 부하 히트맵이 낮음/여백을 정직하게 보인다.
- **전체 검증은 fidelity-guard.** 게이트는 렌더 최소 안전선일 뿐, 상속 id 충실·밀집/안식 정밀 검증은 `validate_calendar.py`.

## 산출
`calendar.html` + `calendar.xlsx`(또는 `.csv`). 대표 스킬 Orchestration Trace (c)/(d)의 캘린더 섹션에 표시. 이로써 통합 캘린더가 완성되어 action-planner(#7)·plan-compiler(#10)로 넘어간다.
