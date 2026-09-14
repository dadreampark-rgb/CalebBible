# 자원 정렬 결과 스키마 (resource.json) — 단일 진실

> demand-estimator가 자원 수요 vs 가용 갭과 빼기 후보를, budget-allocator가 예산 재배분(비율·증감)을, org-mapper가 리더 공백·양성·배치를, pastor-time-guard가 담임 주간 시간을 채운다. aligner-renderer가 예산·조직·시간표를 렌더하고, fidelity-guard의 `validate_resource.py`가 검사한다. review-rhythm(#9)·plan-compiler(#10)가 입력으로 읽는다. **스키마 변경 시 두 스크립트(`validate_resource.py`·`build_resource.py`)도 함께 변경.**

## 공통 규칙 (더하기 전 빼기 · 비율만 · 목자도 자원)
- **절대 금액을 지어내지 않는다**: 예산은 **비율(%)과 증감 방향**만 다룬다(자료 없이 작동·01 라인 278). "원·만원·억" 같은 절대 금액은 금지 — 실제 금액은 재정 담당과 워크샵 후 확정.
- **더하기 전 빼기**: 새 자원 수요(증액·증원·시간 추가)가 있으면 반드시 `subtractions`(무엇을 멈출지)를 제시한다. 비면 위반 — "목표는 늘었는데 예산·사람은 그대로면 계획은 종이"(01 라인 291).
- **목자도 자원이다**: 담임 주간 시간에 **기도·쉼을 보호(protected) 자원**으로 명시한다(가드레일 ④ — 목자가 소진되면 계획도 무너진다). 100% 사역으로 채우지 않는다.
- **갭은 드러낸다**: 자원 수요 대비 가용이 모자라면 정직하게 `gap`으로 비춘다(메우는 척 금지).
- **상속 충실**: `org_plan.leader_gaps`는 #7 `gaps`(담당미정)에서, `placements.load`는 #7 `warnings`(중복배정)에서, 담임 시간은 #6 `rest_plan`에서 이어진다. 상속되지 않은 일꾼·부서·갭을 지어내지 않는다.
- action·calendar에 없던 부서·행사·목표를 새로 만들지 않는다(상속·전사).

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-resource-aligner","schema_version":"1.0",
    "source":["action.json","calendar.json"],
    "church_context":{ /* 상속 */ },
    "year":2027,
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",   // 상속 — 필수(없으면 위반)
    "status":"제안"                                        // 제안(기본) | 확정(목사 HITL 후)
  },

  "inputs_echo": {                                        // provenance
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "from_action":{                                       // #7
      "departments":["예배","교육","전도","선교","양육","행정"],
      "action_count":8,
      "gaps":[{"action_id":"A2","type":"담당미정","text":"A2 담당자 미정"}],   // 보완2 — 리더 공백의 출처
      "warnings":[{"type":"중복배정","text":"'김집사' 4개 담당"}]
    },
    "from_calendar":{                                     // #6
      "rest_plan":[{"weeks":[31,32],"type":"담임휴가"}],
      "inherited_warnings":{"from_events":[{"type":"인력한계","text":"환영팀 중복 동원"}]}
    },
    "workers_input":[                                     // 목사 기억(일꾼·은사·여력)
      {"name":"김집사","gifts":["환영","행정"],"capacity":"지침"},
      {"name":"이권사","gifts":["기도","심방"],"capacity":"여유"}
    ],
    "budget_input":{                                     // 목사 기억(비율·증감만, 절대금액 불요)
      "basis":"비율","by_function":{"인건비":40,"운영":20,"사역":30,"선교":10},
      "changes":{"선교":"10→15"}
    },
    "org_input":["예배부 운영","교육부 이름만","양육부 리더 부족"]   // 머릿속 조직도
  },

  "demand_gaps": [                                        // demand-estimator: 수요 vs 가용 갭 + 빼기 후보
    {
      "area":"전도",                                      // 3축 또는 부서
      "need":{"people":"환영팀 5명","budget":"증액","time":"담임 주 2h"},
      "available":{"people":"3명(workers_input)","budget":"현행","time":"포화"},
      "gap":"인력 2명 부족·예산 증액 필요",
      "subtract_candidate":"효과 약한 대형 전도집회 중단(#3 stop_list)"   // 더하기 전 빼기
    }
  ],

  "budget_plan": {                                        // budget-allocator (보완1 — 2층 구조)
    "basis":"비율(%)·증감 방향 (절대 금액 아님)",
    "current_by_function":{"인건비":40,"운영":20,"사역":30,"선교":10},   // 현황(목사 기억)
    "realloc_by_strategy":[                                              // 3축/부서별 재배분·증감·근거
      {"dimension":"3축","item":"전도","last":"%감각","this":"▲","change":"증액","rationale":"표어·전도 목표·정착 병목"},
      {"dimension":"부서","item":"선교","last":"10%","this":"15%","change":"▲5","rationale":"선교 결연 목표"}
    ],
    "note":"절대 금액은 재정 담당과 확정(자료 없이 비율·증감만)"
  },

  "org_plan": {                                           // org-mapper
    "leader_gaps":[                                       // #7 gaps(담당미정)에서 — 보완2
      {"ministry":"양육 소그룹","from_action_gap":"A2 담당미정","need":"리더 1명"}
    ],
    "develop_needed":[{"role":"소그룹 리더","count":"2명","note":"양성 트랙 필요"}],
    "placements":[                                        // #7 warnings(중복배정) 반영
      {"name":"김집사","role":"환영팀장","load":"과중","basis":"4개 action·capacity 지침"}
    ]
  },

  "pastor_time": {                                        // pastor-time-guard: 주간 시간 예산
    "basis":"주간 시간 예산(상대 비중)",
    "blocks":[
      {"area":"설교 준비","hours":"15","note":"#4 52주 강단"},
      {"area":"심방·돌봄","hours":"8"},
      {"area":"행정","hours":"6"},
      {"area":"기도·영성","hours":"7","protected":true},     // 보호 자원(소진 방지)
      {"area":"쉼·안식","hours":"방어","protected":true}      // #6 rest_plan 연계
    ],
    "warning":"설교+행사 부하기엔 심방 시간 압박 — 위임/축소 검토"
  },

  "subtractions":[                                         // 더하기 전 빼기(#3 stop_list 상속+신규)
    "효과 약했던 대형 전도집회 중단","이름만 있는 교육부 모임 정리"
  ],

  "warnings":[                                            // 자원 부족·과중 경고(조언)
    {"type":"인력부족","text":"새 목표 대비 일꾼 부족","basis":"demand_gaps 전도"},
    {"type":"담임과부하","text":"설교+심방+행정 합산이 주간 가용 초과 우려","basis":"pastor_time"}
  ],

  "confirmed": null                                       // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":["선교 비율 12%로","대형집회 중단 확정"],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`chosen_theme` 채워짐·`status`∈{제안,확정}) · `inputs_echo` · `budget_plan` · `pastor_time`.
- **`meta.chosen_theme` 비면 위반** — 표어·계획 미확정으로 자원 정렬 불가(앞 단계로).
- **절대 금액 금지**: `budget_plan`·`demand_gaps`·`subtractions`·`warnings`·`pastor_time`에 "원·만원·천원·억·백만·₩·달러·$·won·USD·KRW" 등 통화/절대금액 패턴이 있으면 위반(비율·증감만). `*.note` 경로만 경고로 완화. **두 스크립트(`validate_resource.py`·`build_resource.py`)의 MONEY_RE는 동일 패턴(단일 진실) — 변경 시 함께 변경.**
- **더하기 전 빼기**: `demand_gaps`에 증액·증원·강화·보강·부족 등 새 수요 키워드가 있거나 `subtract_candidate`가 채워진 항목이 있는데 `subtractions`가 비면 위반(구조 신호 병행).
- **목자 자원**: `pastor_time.blocks`에 기도/쉼(`protected:true`) 항목이 하나도 없으면 위반(소진 방지 누락).
- **상속 출처**: `org_plan.leader_gaps[].from_action_gap`이 `inputs_echo.from_action.gaps`의 action_id/text에서 상속됐는지 cross-check — 불일치 시 위반(지어낸 부서/gap 차단).
- `status:"확정"`인데 `confirmed`=null이면 위반.

## 비율·여력 표기 (자료 없이 작동)
- 예산은 `%` 또는 증감 방향(`▲`/`▼`/`증액`/`감액`)만. 절대 금액은 `note`로 "재정 담당과 확정" 위임.
- 일꾼 여력은 `capacity`: `여유`|`보통`|`지침`. '지침'인 일꾼에 새 배정은 `placements.load:"과중"`으로 비춘다(여력 질적 판단 — #7 중복 카운트의 다음 단계).

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| review-rhythm (#9) | warnings·demand_gaps(분기 점검 항목)·pastor_time(지속가능성 점검) |
| plan-compiler (#10) | budget_plan(예산 배분안)·org_plan(조직 배치표)·pastor_time(시간 가이드)·subtractions |
| plan-reinforce (#12) | budget_plan.current_by_function(비율 → 귀가 후 실제 결산으로 실측 교체) |
