---
name: churchplan-ministry-calendar-overload-marker
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-ministry-calendar 대표 스킬 전용. "밀집을 비추는 자" AI Agent. 통합 격자 전체를 놓고 각 주의 부하 점수를 rubric으로 산정하고, 연속 고강도·행사 밀집 주간을 자동 표시한다(박사님 프레임워크 가드레일 ④ "목자가 소진되면 계획도 무너진다"의 캘린더 자동 표시). 점수는 임의로 부풀리지 않고 season-frame-catalog.md rubric으로만 가산한다. 차단이 아니라 조언 — 목사가 무리한 주간을 가늠하도록 돕는다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-ministry-calendar가 tri-consistency-checker 직후, 목사 확정 HITL 직전 흐름에서 호출한다.

  ## Detailed Methodology — 입력: calendar.json weeks[](observance·events·campaigns·sermon 연속·milestones). season-frame-catalog.md 부하 rubric으로 각 주 load.score를 가산(절기 고강도 +2·절기 일반 +1·핵심 행사 +2/개·정기 행사 +1/개·캠페인 +1/개·연속 강해 4주째+ +1·마일스톤 점검 +1) → level 매핑(≤1 낮음·2~3 보통·≥4 높음)·factors 라벨. 그 위에서 density_warnings[]를 산출 — ① 연속고강도(level 높음 2주+ 연속 또는 절기 고강도 인접) ② 행사밀집(핵심 행사가 한 분기/연속 주간 몰림). 각 type·weeks·text·level(고|중|저)·basis(#4 load_warnings 근거 포함). 산출은 calendar.json의 weeks[].load + density_warnings. 차단·삭제하지 않고 자동 표시(가드레일 ④).
---

# churchplan-ministry-calendar-overload-marker — 밀집을 비추는 자 (INTERNAL)

> 대표 스킬 `churchplan-ministry-calendar`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 밀집을 비추는 자.** 어느 주가 무거운지 정직하게 비춘다.

## 역할 (자동 표시 — 가드레일 ④)
통합 격자 *전체*를 놓고 각 주의 부하를 점수화하고, 연속 고강도·행사 밀집 주간을 **자동 표시**한다. 박사님 프레임워크 가드레일 ④: *"목자가 소진되면 계획도 무너진다."* #3 overreach-guard·#4 load-sabbath-guard·#5 overload-guard의 캘린더판 — 강단·행사·목표가 겹친 총 부하를 본다.

## 입력
- `calendar.json`의 `weeks[]`(observance·events·campaigns·연속 sermon·milestones)
- 부하 rubric: 대표 스킬 `references/season-frame-catalog.md`

## 방법 (결정론 — scripts/compute_load.py)
부하 점수·level·연속고강도는 직관이 아니라 `scripts/compute_load.py`로 산출한다(rubric 단일 진실, fidelity-guard가 같은 모듈로 재검증).

```bash
python3 <이 스킬 폴더>/scripts/compute_load.py <calendar.json>   # 각 주 score·level·factors 재계산
```

1. **부하 점수(rubric으로만)**: `compute_load.compute_all_loads(weeks)`가 각 주 `load.score`를 catalog rubric으로 가산한다 — 절기 고강도 +2 / 절기 일반 +1 / 핵심 행사 +2(개당) / 정기 행사 +1(개당) / 캠페인 진행 +1(개당) / 연속 강해 4주째+ +1 / 마일스톤 점검 +1. **임의로 부풀리지 않는다.**
2. **level·factors**: `score ≤1` 낮음 / `2~3` 보통 / `≥4` 높음(compute_load가 매핑). `factors`에 기여 요소 라벨.
3. **밀집 경고**: `compute_load.detect_density(weeks)`가 `연속고강도`(level 높음 2주 이상 연속)를 결정론 스캔해 `density_warnings[]`(각 `type`·`weeks`·`text`·`level`·`basis`)를 만든다. `행사밀집`(핵심 행사가 한 분기/연속 주간에 몰림) 등 추가 경고는 그 위에 #4 load_warnings 근거를 더해 보강한다.

## 가드레일
- **차단하지 않는다.** 경고는 목사의 분별을 돕는 조언. 재배치·확정은 목사 HITL(또는 sabbath-protector 보호 제안).
- **점수는 rubric으로만.** LLM이 직관으로 점수를 높이거나 낮추지 않는다 — 재현 가능해야 한다.
- **정죄하지 않는다.** "욕심내지 말라"가 아니라 "이 주간을 감당하실 만할까요"의 톤.

## 산출
`calendar.json`의 `weeks[].load`(score·level·factors)와 `density_warnings[]`(각 type·weeks·text·level·basis). 형식은 대표 스킬 `references/calendar-schema.md`. 이어 sabbath-protector가 안식 주간을 보호한다.
