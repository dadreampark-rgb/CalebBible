# 핵심 행사 결과 스키마 (events.json) — 단일 진실

> event-sifter가 정기/핵심을 가르고 정리 후보를, signature-designer가 핵심 행사·행사–목표 연결을, blueprint-writer가 1페이지 기획안을, sermon-sync-checker가 설교 정합을, overload-guard가 경고를 채운다. blueprint-renderer가 기획안·지도를 렌더하고, fidelity-guard의 `validate_events.py`가 검사한다. ministry-calendar(#6)·plan-compiler(#10)가 입력으로 읽는다. **스키마 변경 시 두 스크립트(`validate_events.py`·`build_event_plan.py`)도 함께 변경.**

## 공통 규칙 (목적 없는 행사를 막는다)
- **모든 핵심 행사는 목적을 가진다**: 각 `signature_events[]`는 `serves_axes`(섬기는 축)와 `rationale`(왜 이 행사인가)을 반드시 가진다. 비면 위반 — "이 행사가 표어의 무엇을 구현하나?"에 답 없는 행사는 만들지 않는다.
- **행사 수보다 깊이**: 핵심 행사는 3~5개 집중. 5개 초과는 위반(집중이 깨진다). 0개도 위반.
- **"작년에 했으니" 경계**: 작년 효과·목적을 따져 정리 후보를 `pruned_events`로 제안.
- **정기 행사는 배치만**: 절기·연례 행사는 `sermon-plan.liturgical_calendar`를 상속해 배치만 하고, 기획 에너지는 핵심 행사에 집중.
- vision·goals·sermon-plan에 없던 표어·목표·절기를 지어내지 않는다.

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-signature-events","schema_version":"1.0",
    "source":["vision.json","goals.json","sermon-plan.json"],
    "church_context":{ /* 상속 */ },
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",   // vision.chosen — 필수(없으면 위반)
    "focus":"전도",                                       // 올해 무게중심(자유 주제어) — 목사 입력. serves_axes(영성|전도|양육 3축)과 별개의 넓은 무게중심이며 AXES 대조 검증을 받지 않는다.
    "status":"제안"                                       // 제안(기본) | 확정(목사 HITL 후)
  },

  "inputs_echo": {
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "direction_declaration":"…vision 방향 선언문…",
    "axis_goals":{"영성":"말씀·기도 뿌리내림","전도":"한 영혼 정착","양육":"식탁 공동체"},  // goals
    "season_frame":{"1Q":"영성","2Q":"전도","3Q":"양육","4Q":"감사"},                      // sermon-plan/목사
    "last_year_events":[{"name":"전도 축제","effect":"효과 약함"}],                          // diagnosis/recall
    "focus":"전도"
  },

  "regular_events": [                           // event-sifter: 정기(절기·연례) — 배치만
    {"name":"부활절","when":"13주(2027-03-28)","type":"절기","note":"sermon-plan.liturgical_calendar 상속·배치만"},
    {"name":"추수감사주일","when":"47주","type":"절기","note":"배치만"}
  ],

  "signature_events": [                         // signature-designer + blueprint-writer: 핵심 3~5개
    {
      "id":"E1","title":"한 영혼 환영 페스티벌",
      "serves_axes":["전도","양육"],            // 필수 — 목적 없는 행사 차단
      "serves_goals":["새가족 6개월 정착"],      // goals 목표 연결
      "theme_link":"표어 '한 영혼을 품고'",
      "rationale":"표어 + 병목 '정착에서 샘' + 작년 전도행사 무산에서",   // 필수(근거 추적)
      "blueprint":{                             // 1페이지 6필드
        "purpose":"새가족이 공동체에 첫 발을 떼는 자리",
        "audience":"새가족·초청 대상",
        "timing":"2분기 (20주 전후)",
        "flow":["환영 예배","식탁 교제","소그룹 배치"],
        "resources":["환영팀","식사 준비","소그룹 리더"],
        "success_signal":"참여 새가족 중 절반이 소그룹 연결"
      },
      "sermon_sync":{                           // sermon-sync-checker
        "linked_weeks":[20],
        "supports":"성령강림주일 설교가 환대를 떠받침",
        "aligned":true
      },
      "priority":1
    }
  ],

  "pruned_events":[                             // event-sifter: 정리 제안("작년에 했으니" 경계)
    {"name":"대형 전도집회","reason":"작년 효과 약함·목적이 표어와 불명확"}
  ],

  "event_goal_map":"| 행사 | 섬기는 축 | 목표 | 시기 |\n|...|",   // 행사–목표 연결 지도(#4 sermon_goal_map과 짝). blueprint-renderer의 build_event_plan.py가 signature_events에서 100% 결정론으로 계산해 기록(LLM 자유텍스트 금지). 행 수 = 핵심 행사 수.

  "warnings":[                                  // overload-guard
    {"type":"과밀","text":"2분기에 핵심 행사 3개 집중","basis":"E1·E2·E3 모두 2Q"},
    {"type":"인력한계","text":"환영팀·소그룹 리더 중복 동원 우려","basis":"작은 교회 일꾼 한정"}
  ],

  "confirmed": null                             // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":[...],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`chosen_theme` 채워짐·`status`∈{제안,확정}) · `inputs_echo` · `signature_events`.
- **`meta.chosen_theme` 비면 위반** — 표어 미확정으로 행사 기획 불가(vision-discernment #2로).
- `signature_events` 0개 위반(핵심 행사 없음), **5개 초과 위반**(행사 수보다 깊이).
- 각 핵심 행사: **`serves_axes`(≥1)** + **`rationale`** 필수(목적·근거 없는 행사 차단).
- `status:"확정"`인데 `confirmed`=null이면 위반.

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| ministry-calendar (#6) | regular_events·signature_events(timing)·warnings(과밀 회피) |
| action-planner (#7) | signature_events.blueprint(resources·flow → 부서 실행) |
| resource-aligner (#8) | warnings(인력 한계)·blueprint.resources |
| plan-compiler (#10) | signature_events(기획안)·event_goal_map |
