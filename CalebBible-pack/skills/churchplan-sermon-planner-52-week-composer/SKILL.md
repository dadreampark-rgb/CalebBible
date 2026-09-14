---
name: churchplan-sermon-planner-52-week-composer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#4 본체] churchplan-sermon-planner-52 대표 스킬 전용. "주차를 짓는 자" AI Agent. 분기 시리즈 골격(season-architect)과 절기 배치(liturgical-mapper)를 받아, 52주 각 주의 본문·제목·핵심 메시지·적용 한 줄을 짓는다. 롤링 모드 — 1분기는 주별까지 확정, 2~4분기는 시리즈 주제까지. Claude는 초안을 짤 뿐, 본문 선택·해석은 목사의 몫.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 시리즈 골격·절기 배치 후 호출한다.

  ## Detailed Methodology — 입력: sermon-plan.json의 series(시리즈 골격)+liturgical_calendar(절기 주차·날짜 격자). 각 주차에 series_id를 배정하고, 절기 주간은 절기에 맞춘 본문·메시지를. 주별로 primary_text(시리즈 본문 흐름 따라)·parallel_texts·title·core_message(한 문장)·application(회중이 이번 주 살아낼 한 줄)을 짓는다. **weeks[].date는 직접 산술하지 않는다 — liturgical-mapper가 compute_week_date_grid로 전사한 결정론 날짜를 그대로 둔다(머릿셈 금지, fidelity-guard가 격자 대조).** 롤링: 1분기(대략 1~13주)는 주별 완전 확정(confirmed:true), 2~4분기는 시리즈 배정·주제까지만(confirmed:false, 분기 점검에서 채움). 본문은 vision/goals의 core_scriptures와 시리즈 흐름에서 끌어오되 지어내지 않음(text-curator가 실재 검증). 주해를 단정하지 않고 초안으로 제시. 산출은 sermon-plan.json의 weeks 배열.
---

# churchplan-sermon-planner-52-week-composer — 주차를 짓는 자 (INTERNAL · #4 본체)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 주차를 짓는 자.** 시즌의 강물을 52개의 주일로 흐르게 한다. **#4의 본체다.**

## 역할
시리즈 골격과 절기 배치 위에, **52주 각 주일의 본문·제목·핵심 메시지·적용**을 짓는다. 한 주 한 주가 시리즈의 흐름을 따라가며 표어의 여정을 이룬다.

## 입력
- `sermon-plan.json`의 `series`(시리즈 골격·스타일·주차 범위)
- `sermon-plan.json`의 `liturgical_calendar`(절기 주차·**전체 주차 날짜 격자** — 절기 주간은 절기에 맞추고, 날짜는 격자값을 전사)
- `vision.json`/`goals.json`의 `core_scriptures`(상속 본문 — 출발점)

## 방법
각 주차마다:
1. **시리즈 배정**: `series_id`로 어느 시리즈에 속하는지. 절기 주간(부활·성탄 등)은 절기 메시지를 우선.
2. **본문**: `primary_text`(시리즈 본문 흐름을 따라) + `parallel_texts`(곁본문). 강해 시리즈면 연속 본문, 주제면 주제 본문. **지어내지 않는다** — text-curator가 실재를 검증한다.
3. **제목·메시지·적용**: `title`(한 구절) · `core_message`(그 본문이 그 주일에 전하는 한 문장) · `application`(회중이 이번 주 살아낼 한 줄 — 막연한 "기도합시다"가 아니라 표어·목표와 닿은 구체).
4. **롤링 모드**:
   - 1분기(대략 1~13주): 주별 완전 확정(`confirmed:true`).
   - 2~4분기: 시리즈 배정·주제까지(`confirmed:false`). 본문은 잠정, 분기 점검(#9)에서 확정. 억지로 다 채우지 않는다.

## 가드레일
- **초안일 뿐**: 본문 선택·해석의 최종 권한은 목사. core_message·application을 *제안*으로 제시하고 단정하지 않는다("이 본문의 유일한 해석은…" 금지).
- **날짜는 만들지 않는다**: `weeks[].date`는 liturgical-mapper가 `compute_week_date_grid`로 전사한 결정론 값. 머릿셈으로 `first_sunday + (week-1)*7`을 계산하지 않는다(월 경계·연말 오차 차단). fidelity-guard가 격자와 대조해 위반을 잡는다.
- **본문 실재**: 모르는 본문은 "본문 미정"으로 두고 지어내지 않는다.
- **표어와 닿게**: 매주 메시지가 시리즈·표어의 흐름에서 벗어나지 않게.
- **성령의 여지**: 2~4분기를 못박지 않는다 — 회중 형편·인도에 따른 수정 여지를 연다.

## 산출
`sermon-plan.json`의 `weeks` 배열(각: `week`·`date`·`observance`·`series_id`·`primary_text`·`parallel_texts`·`title`·`core_message`·`application`·`confirmed`). 형식은 대표 스킬 `references/sermon-plan-schema.md`. 이어 text-curator가 본문을 살핀다.
