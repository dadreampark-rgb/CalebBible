# 통합 캘린더 결과 스키마 (calendar.json) — 단일 진실

> layer-merger가 52주 격자에 설교·행사·정기·캠페인·목표 마일스톤을 통합 배치하고, season-aligner가 시즌 정렬을, tri-consistency-checker가 설교–행사–사역 3중 정합을, overload-marker가 밀집 주간 경고를, sabbath-protector가 안식 주간 보호를 채운다. calendar-renderer가 캘린더(html+xlsx)를 렌더하고, fidelity-guard의 `validate_calendar.py`가 검사한다. action-planner(#7)·plan-compiler(#10)가 입력으로 읽는다. **스키마 변경 시 두 스크립트(`validate_calendar.py`·`build_calendar.py`)도 함께 변경.**

## 공통 규칙 (여백도 계획이다 — 채우기가 아니라 정렬하기)
- **통합은 채우기가 아니다**: #6은 새 콘텐츠를 만들지 않는다. #3·#4·#5(+목사 입력 캠페인)의 확정 산출을 **한 격자에 정렬·전사**할 뿐이다. 없던 주차·설교·행사·캠페인·마일스톤을 지어내지 않는다(상속·전사만).
- **52주 격자는 골격이다**: `weeks`는 1~52 주차를 격자로 가진다. 설교가 미정(롤링 2~4Q)이어도 *주는 존재*한다. 주차 중복 금지, 범위 1~52.
- **상속 id 충실(garbage-in 차단)**: `weeks[].sermon.series_id`는 `inputs_echo.from_sermon_plan.series_ids`에, `weeks[].events[].id`는 `inputs_echo.from_events.event_ids`에, `weeks[].campaigns[].name`은 `inputs_echo.campaigns_input[].name`에 존재해야 한다. 상속되지 않은 id를 캘린더가 새로 만들면 위반.
- **정렬 근거 전사(season-aligner·tri-consistency 결정론 근거)**: layer-merger는 `weeks[].sermon.purpose`(#4 `series.purpose` 전사)와 `weeks[].events[].serves_axes`(#5 `serves_axes` 전사)를 격자에 함께 전사한다. season-aligner·tri-consistency-checker의 `aligned` 판정은 title 문자열 추측이 아니라 이 결정론 필드를 근거로 한다(전사 출처 없이 정렬을 단언하지 않는다).
- **소진 방지는 척추다**(01 가드레일 ④): 연속 고강도 주간을 자동 표시(`density_warnings`)하고, 목자 휴식·안식 주간을 보호(`rest_plan`)한다. #4 `load_warnings`·#5 `warnings`를 `inherited_warnings`로 통합한다.
- **마일스톤은 표시만, 분해하지 않는다**: `weeks[].milestones`는 `goals.indicators.by`(분기)를 캘린더에 *전사 표시*만 한다. 분기→월 분해·부서 배정·담당 지정은 action-planner(#7)의 몫이지 #6이 아니다.
- **결정은 목사**: `density_warnings`·`rest_plan`은 조언이다. 무리한 주간 재배치·안식 주간 확정은 목사 HITL 후 `confirmed`에 기록한다. renderer는 확정 후에만 최종 캘린더를 렌더한다.

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-ministry-calendar","schema_version":"1.0",
    "source":["sermon-plan.json","events.json","goals.json"],
    "church_context":{ /* 상속 */ },
    "year":2027,                                       // 절기·날짜 정합 — 필수(정수)
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",   // 상속 — 필수(없으면 위반)
    "season_frame":{                                    // 시즌제(01 라인 265 모델, sermon-plan/목사 상속)
      "1Q":"영성·기초","2Q":"전도·성장","3Q":"양육·리더","4Q":"공동체·감사"
    },
    "status":"제안"                                     // 제안(기본) | 확정(목사 HITL 후)
  },

  "inputs_echo": {                                      // provenance — 상속의 출처를 비춰 둠
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "from_sermon_plan":{
      "total_weeks":52,"series_ids":["S1","S2","S3","S4"],
      "observances":[{"name":"부활주일","week":13}]      // #4 liturgical_calendar 상속
    },
    "from_events":{
      "event_ids":["E1","E2","E3"],"signature_count":3,"regular_count":4
    },
    "from_goals":{"milestone_count":4},                  // #3 axes[].goals[].indicators[].by
    "campaigns_input":[                                  // 보완1 — 출처: 목사입력 | goals 기간성 항목 | (미래)#11
      {"name":"40일 새벽기도","weeks":[6,7,8,9,10,11],"source":"목사입력"}
    ],
    "pastor_rest_input":[                                // 목사 1회 입력(휴가·안식·피할 지역/학사 일정)
      {"weeks":[31,32],"reason":"여름 휴가"}
    ]
  },

  "weeks": [                                            // layer-merger: 52주 통합 격자(1~52 골격)
    {
      "week":1,"date":"2027-01-03","quarter":1,"month":1,
      "observance":"신년주일",                            // #4 liturgical 상속
      "sermon":{"series_id":"S1","title":"한 마리를 찾아 나서는 목자","primary_text":"누가복음 15:1-7","purpose":"잃은 양을 찾으시는 목자의 마음(영성·회복)","confirmed":true},  // purpose: #4 series.purpose 전사(정렬 판정 결정론 근거)
      "events":[ {"id":"E1","title":"한 영혼 환영 페스티벌","type":"핵심","serves_axes":["전도"]} ],   // #5 상속(해당 주 배치). type: 핵심|정기. serves_axes: #5 serves_axes 전사(정렬 판정 근거)
      "campaigns":[ {"name":"40일 새벽기도","type":"기도시즌"} ],              // 보완1 — 진행 중 캠페인 배치
      "milestones":[ {"axis":"전도","label":"새가족 6개월 정착률","by":"1Q","note":"분기 점검 표시"} ],  // #3 표시만
      "load":{"score":2,"level":"보통","factors":["신년주일","캠페인 진행"]},   // overload-marker(rubric: season-frame-catalog)
      "rest_protected":false                            // sabbath-protector(true면 안식 보호 주간)
    }
    // … week 2 ~ 52 …
  ],

  "season_alignment": [                                 // season-aligner: 분기별 시즌 정렬 점검
    {
      "quarter":1,"intended":"영성·기초",
      "actual_sermon":"잃은 양 시리즈(영성/회복)","actual_events":["환영 페스티벌"],
      "aligned":true,"note":"강단·행사가 1Q 영성 강조와 한 방향"
    }
  ],

  "tri_consistency": [                                  // tri-consistency-checker: 설교–행사–사역 3중 정합
    {
      "quarter":1,
      "sermon_thrust":"찾으시는 목자의 마음",
      "event_thrust":"새가족 환영·정착",
      "ministry_thrust":"전도 정착률 1Q 점검 + 40일 새벽기도",   // 보완2 — 목표 마일스톤 + 캠페인
      "aligned":true,"gap":null                          // aligned=false면 gap에 간극 서술(경고)
    }
  ],

  "density_warnings":[                                  // overload-marker: 밀집·연속 고강도 주간 자동 표시
    {"type":"연속고강도","weeks":[12,13,14],"text":"종려·부활·행사 3주 연속 고강도","level":"고","basis":"#4 load_warnings 절기몰림 + E2"},
    {"type":"행사밀집","weeks":[20,21],"text":"2주 연속 핵심 행사","level":"중","basis":"E2·E3 모두 2Q"}
  ],

  "rest_plan":[                                         // sabbath-protector: 안식 주간 보호(가드레일 ④)
    {"weeks":[31,32],"type":"담임휴가","status":"보호","note":"강단 교류/게스트 설교 권장","basis":"pastor_rest_input 여름 휴가"},
    {"weeks":[33],"type":"안식제안","status":"권장","note":"고강도 절기 후 회복 주간","basis":"#4 load_warnings 안식제안 상속"}
  ],

  "inherited_warnings":{                               // #4 load_warnings + #5 warnings 통합(총 부하)
    "from_sermon":[ {"type":"연속강해부담","text":"3~7주 연속 강해","weeks":[3,4,5,6,7]} ],
    "from_events":[ {"type":"인력한계","text":"환영팀·소그룹 리더 중복 동원 우려"} ]
  },

  "confirmed": null                                    // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":["33주 안식 확정","21주 행사 이동"],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`year` 정수·`chosen_theme` 채워짐·`status`∈{제안,확정}) · `inputs_echo` · `weeks`.
- **`meta.chosen_theme` 비면 위반** — 표어 미확정이면 통합할 계획이 없다(앞 단계로).
- `weeks` 주차 번호는 1~52 범위, **중복 금지**(위반). 52개 미만이면 누락 경고(완전 격자 권장), 52 초과 위반.
- **상속 id 충실**: `weeks[].sermon.series_id`∈`from_sermon_plan.series_ids`, `weeks[].events[].id`∈`from_events.event_ids`, `weeks[].campaigns[].name`∈`campaigns_input[].name`. 위배 시 위반(지어냄 차단).
- `density_warnings`·`rest_plan` 키 존재. `rest_plan` 비면 경고("안식 계획 없음 — 목자 지속가능성 점검").
- `tri_consistency[].aligned=false`면 경고(간극 점검).
- `status:"확정"`인데 `confirmed`=null이면 위반.

## 부하 점수(load.score) 산정
`references/season-frame-catalog.md`의 rubric을 따른다(설교 부하 + 행사 가중 + 캠페인 + 마일스톤 점검의 단순 가산 → level 매핑). LLM이 점수를 임의로 부풀리지 않는다.

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| action-planner (#7) | weeks(milestones·events → 분기→월 분해·담당 배정)·season_frame |
| resource-aligner (#8) | density_warnings·inherited_warnings(인력 한계)·rest_plan(담임 시간) |
| review-rhythm (#9) | weeks[].milestones(분기 점검 표시점)·season_alignment |
| plan-compiler (#10) | weeks(통합 캘린더 표)·season_alignment·tri_consistency |
