# 실행계획 결과 스키마 (action.json) — 단일 진실

> milestone-decomposer가 목표를 분기 마일스톤·월별 행동으로 풀고, department-router가 부서·목적·시기·담당·자원을 배치하며, gap-flagger가 "언제·누가·무엇으로" 공백을 플래그하고, action-renderer가 부서별 실행계획표를 렌더하며, fidelity-guard의 `validate_action.py`가 검사한다. resource-aligner(#8)·review-rhythm(#9)·plan-compiler(#10)가 입력으로 읽는다. **스키마 변경 시 두 스크립트(`validate_action.py`·`build_action.py`)도 함께 변경.**

## 공통 규칙 (빈칸을 지어내지 않는다)
- **근거 추적 강제**: 각 action의 `source_goal`은 `inputs_echo.from_goals`의 실재 목표에서 와야 한다. 비거나 상속되지 않은 목표를 지어내면 위반(garbage-in 차단) — "이 행동이 어느 목표를 이루나?"에 답 없는 행동은 만들지 않는다.
- **공백은 메우지 말고 드러낸다**: 담당(`owner`)·자원(`resources`)·시기(`timing`)가 미정이면 **`owner:"TBD"`** 등으로 두고 `flags`에 표시한다. **없는 사람·부서 이름을 지어내 공백을 메우지 않는다**(가짜 담당 금지). 미정은 미정으로 정직하게.
- **과잉을 절제한다**: 목표를 잘게 쪼개 작은 교회를 압도하지 않는다. `monthly_steps`는 **임박/핵심 action에만** 채운다(나머지는 분기 마일스톤까지). #3 "더하기 전 빼기"·#6 "여백도 계획"의 실행판.
- **사람을 갈지 않는다**: 같은 `owner`에게 여러 action이 반복 배정되면 `warnings`에 `중복배정`으로 비춘다(01 사람 중심 가드레일 — 지친 리더). 여력의 질적 판단은 resource-aligner(#8).
- **캘린더와 정합**: `linked_event`·`timing`은 #6 `calendar.json`(event_weeks·season_frame)과 어긋나지 않는다.
- goals·calendar·events에 없던 목표·행사·부서를 새로 만들지 않는다(상속·전사).

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-action-planner","schema_version":"1.0",
    "source":["goals.json","calendar.json","events.json"],
    "church_context":{ /* 상속 */ },
    "year":2027,
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",   // 상속 — 필수(없으면 위반)
    "departments":["예배","교육","전도","선교","양육","행정"],  // 목사 1회 입력(교회 부서 구조)
    "status":"제안"                                        // 제안(기본) | 확정(목사 HITL 후)
  },

  "inputs_echo": {                                        // provenance
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "from_goals":[                                        // #3 axes[].goals — 근거 추적 기준
      {"axis":"전도","direction_goal":"한 영혼 정착",
       "indicators":[{"label":"새가족 6개월 정착률","target":"3분기까지 2/3","by":"3Q"}]}
    ],
    "from_calendar":{                                     // #6
      "season_frame":{"1Q":"영성·기초","2Q":"전도·성장","3Q":"양육·리더","4Q":"공동체·감사"},
      "event_weeks":[{"id":"E1","week":13,"title":"한 영혼 환영 페스티벌"}]
    },
    "department_input":["예배","교육","전도","선교","양육","행정"]   // 목사 입력(없으면 기본 6부서 제안)
  },

  "actions": [                                            // milestone-decomposer + department-router
    {
      "id":"A1",
      "source_goal":"전도: 한 영혼 정착",                  // 근거 추적(필수) — from_goals에 실재
      "milestone":{                                       // 분기 마일스톤
        "label":"새가족 6개월 정착률 2/3","by":"3Q","from_indicator":"새가족 6개월 정착률"
      },
      "department":"전도",                                // 부서 배치(department_input에 실재)
      "purpose":"새가족이 소그룹에 연결되도록",            // 목적
      "timing":"2분기(20주 전후, E1 환영 페스티벌 연계)",   // 시기(캘린더 정합)
      "owner":"TBD",                                      // 담당 — 미정이면 TBD(가짜 이름 금지)
      "resources":["환영팀","소그룹 리더"],                // 필요 자원(미정이면 빈 배열 + flag)
      "monthly_steps":[                                   // 월별 행동 — 임박/핵심 action에만(과잉 절제)
        {"month":4,"step":"새가족 환영 동선 설계"},
        {"month":5,"step":"소그룹 배치 1차"}
      ],
      "linked_event":"E1",                                // 캘린더 행사 연계(선택, event_weeks에 실재)
      "flags":["담당미정"]                                // gap-flagger 산출(없으면 빈 배열)
    }
  ],

  "department_table": {                                   // department-router: 부서별 묶음(렌더용)
    "전도":["A1","A3"],"양육":["A2"],"예배":[],"교육":[],"선교":[],"행정":[]
  },

  "gaps":[                                                // gap-flagger: "언제·누가·무엇으로" 공백 강제 노출
    {"action_id":"A1","type":"담당미정","text":"A1 담당자 미정 — 누가 맡을지 정해야 실행됨"},
    {"action_id":"A4","type":"자원미정","text":"A4 필요 자원 불명확 — 무엇으로 할지 점검"}
  ],

  "warnings":[                                            // 과잉·중복 경고(조언, 차단 아님)
    {"type":"과잉분해","text":"전도 부서에 action 6개 집중 — 작은 교회 감당 점검","basis":"department_table 전도"},
    {"type":"중복배정","text":"'김집사'가 4개 action 담당 — 한 손에 몰림(지친 리더 점검)","basis":"owner 반복"}
  ],

  "confirmed": null                                       // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":["A1 담당 배정","A5 정리"],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`chosen_theme` 채워짐·`departments` 비어있지 않음·`status`∈{제안,확정}) · `inputs_echo` · `actions`.
- **`meta.chosen_theme` 비면 위반** — 표어·목표 미확정으로 실행계획 불가(앞 단계로).
- `actions` 0개 위반(분해할 목표가 없음).
- 각 action: **`source_goal`**(필수·from_goals에 추적) + **`department`**(departments에 실재) + `purpose` 필수.
- **공백 정직**: `owner`가 비거나 "TBD"인데 `flags`에 담당미정류가 없으면 위반(공백 숨김 차단). `linked_event`가 `from_calendar.event_weeks`에 없으면 위반(지어낸 행사 연계).
- `status:"확정"`인데 `confirmed`=null이면 위반.

## 월별 분해 절제 (과잉 방지)
`monthly_steps`는 **임박하거나 핵심인 action에만** 채운다. 모든 action에 12개월 단계를 강제하지 않는다 — #4 롤링 모드(1Q 주별·2~4Q 시리즈까지)와 같은 정신. 분기 마일스톤(`milestone.by`)이 골격, 월별은 필요한 만큼.

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| resource-aligner (#8) | actions(owner·resources)·gaps(담당미정 → 리더 공백)·warnings(중복배정·과잉)·department_table → 인력·예산·여력 정렬 |
| review-rhythm (#9) | actions[].milestone(by·label)·gaps → 분기 점검 항목 |
| plan-compiler (#10) | department_table·actions(부서별 실행계획표)·gaps |
