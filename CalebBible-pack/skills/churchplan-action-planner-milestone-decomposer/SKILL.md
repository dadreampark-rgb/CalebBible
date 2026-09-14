---
name: churchplan-action-planner-milestone-decomposer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#7 심장] churchplan-action-planner 대표 스킬 전용. "행동으로 푸는 자" AI Agent. 3축 목표(goals.json indicators)를 분기 마일스톤으로, 다시 임박/핵심 행동의 월별 단계로 분해한다. 각 행동에 source_goal(어느 목표에서 왔나)을 달아 근거를 추적한다 — 목표에서 추적되지 않는 행동은 만들지 않는다. 월별 분해는 임박/핵심 action에만(과잉 절제).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-action-planner가 표어·목표 확인·부서 입력 직후 가장 먼저 호출한다.

  ## Detailed Methodology — 입력: goals.json(axes[].goals.direction_goal·indicators[].label·target·by)+calendar.json(weeks milestones·event_weeks·season_frame, 시기 정합)+events.json(signature_events.blueprint.flow). 각 목표를 ① 분기 마일스톤(indicators.by → milestone.by·from_indicator 전사) ② 핵심 행동(action) ③ 월별 단계(monthly_steps — 임박/핵심 action에만, 모든 목표에 12개월 강제 금지) 로 푼다. 각 action에 source_goal(근거 추적·필수)·milestone·timing(캘린더 정합·linked_event)을 단다. 부서 배치(department)는 department-router가, 공백 플래그는 gap-flagger가 채운다. 과잉 절제 — #4 롤링 정신(분기 마일스톤이 골격·월별은 필요한 만큼). 산출은 action.json의 actions[] 골격(department·owner 전 단계).
---

# churchplan-action-planner-milestone-decomposer — 행동으로 푸는 자 (INTERNAL · #7 심장)

> 대표 스킬 `churchplan-action-planner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 행동으로 푸는 자.** 목표를 실행 가능한 행동으로 푼다. **#7의 심장이다.**

## 역할 (목표에서 행동을 끌어낸다)
3축 목표(#3)를 **분기 마일스톤 → 핵심 행동 → (임박/핵심만) 월별 단계**로 분해한다. 행동을 먼저 짓고 목표를 붙이는 게 아니라, **목표(indicators)에서 행동을 끌어낸다.**

## 입력
- `goals.json`(#3): `axes[].goals.direction_goal`·`indicators`(label·target·`by`)
- `calendar.json`(#6): `weeks`(milestones·event_weeks)·`season_frame`(시기 정합)
- `events.json`(#5): `signature_events.blueprint.flow`(행사 실행 단서)
- 분해 패턴: 대표 스킬 `references/department-catalog.md` §2

## 방법
1. **분기 마일스톤**: 각 `indicators[].by`(분기)를 `milestone`으로 전사(`by`·`label`·`from_indicator`). 목표치(target)를 분기 마일스톤으로.
2. **핵심 행동 도출**: 마일스톤을 이룰 행동(action)을 끌어낸다. 각 action에 **`source_goal`(근거 추적·필수)** + `milestone` + `purpose` + `timing`(캘린더 정합, 행사 있으면 `linked_event`).
3. **월별 단계(절제)**: 임박/핵심 action에만 `monthly_steps`(month·step). **모든 목표에 12개월을 강제하지 않는다** — 분기 마일스톤이 골격, 월별은 필요한 만큼(#4 롤링 정신).

## 결정론 골격 생성 (LLM 평탄화·전사 금지)
goals.json의 중첩 `axes[].goals[]`를 평탄 `from_goals`와 action 골격으로 옮기는 일은 **LLM 자연어 추론에 맡기지 않는다**(키 오전사·목표 누락 방지). 다음 스크립트가 결정론적으로 생성한다:

```bash
python3 <이 스킬 폴더>/scripts/build_milestones.py <goals.json> "예배,교육,전도,선교,양육,행정" <action.json 출력경로>
```

- `inputs_echo.from_goals` ← `axes[].goals[]` 평탄 전사(axis·direction_goal·indicators)
- `actions[]` 골격 ← 각 indicator마다 한 action. **`source_goal`을 `"<axis>: <direction_goal>"` 키로 발급**해 fidelity-guard `validate_action.py`의 근거추적이 토큰 정확 매칭으로 통과되게 한다(garbage-in 차단).
- `milestone`(label·by·from_indicator·target) ← `indicators[].by`/`label`/`target` 전사
- `department`·`owner`·`resources`·`flags`는 빈 골격(department-router·gap-flagger가 채움)

LLM은 이 골격 위에서 `purpose`·`monthly_steps`(임박/핵심만)·`timing` 서술만 더한다. 평탄화·source_goal 발급은 파이썬이 확정.

## 가드레일
- **근거 우선**: `source_goal` 없는 행동은 만들지 않는다(fidelity-guard가 근거 누락·지어낸 목표를 위반 처리).
- **과잉 절제**: 목표를 잘게 쪼개지 않는다. 핵심 행동에 집중(작은 교회 감당).
- **골격만**: 여기서는 분해·마일스톤·시기까지. 부서 배치(`department`)는 department-router, 담당·자원 공백 플래그는 gap-flagger가 채운다.

## 산출
`action.json`의 `actions[]` 골격(각: `id`·`source_goal`·`milestone`·`purpose`·`timing`·`monthly_steps`·`linked_event` — `department`·`owner`·`resources`·`flags`는 후속 하위가). 형식은 대표 스킬 `references/action-schema.md`. 이어 department-router가 부서로 보낸다.
