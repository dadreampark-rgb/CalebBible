# 목표 결과 스키마 (goals.json) — 단일 진실

> axis-prioritizer가 축별 목표를 세우고, smart-refiner가 기준선·목표치·기한을 다듬고, indicator-designer가 정량 신호 지표를 한 쌍으로 붙이며, stop-start-curator가 유지/중단을 채우고, overreach-guard가 warnings를 달고, checklist-builder가 표를 렌더하며, fidelity-guard의 `validate_goals.py`가 검사한다. sermon-planner-52(#4)·signature-events(#5)·action-planner(#7)·review-rhythm(#9)가 입력으로 읽는다. **스키마 변경 시 두 스크립트(`validate_goals.py`·`build_checklist.py`)도 함께 변경.**

## 공통 규칙 (번역하되 환원하지 않음)
- **정성+정량 한 쌍 강제**: 각 목표는 `direction_goal`(정성 방향) **그리고** `indicators`(정량 신호 ≥1)를 둘 다 가진다. 하나라도 없으면 위반 — 방향 없는 숫자도, 숫자 없는 영성 목표도 둘 다 환원이다.
- **근거 추적 강제**: 각 목표 `rationale`은 표어(vision)·병목(diagnosis)·마음 중 무엇에서 왔는지 밝힌다. 비면 위반(진단/표어에 추적 안 되는 목표 = garbage-in).
- **추정 충실도 계승**: 기준선 신뢰가 '하'(assumption)면 목표치를 점값으로 단정하지 않는다(범위·방향으로). → 허위 정밀 차단.
- **신호일 뿐**: 모든 지표는 `signal_only:true`(돌봄의 신호지 성과 채찍 아님)를 표기한다.
- **측정 가능성**: 지표는 실제로 셀 수 있어야 한다(`measure_real`). "성령충만 80%"처럼 측정 불가의 허위 정량 금지.
- vision·diagnosis·recall에 없던 수치·이름을 새로 만들지 않는다.

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-goal-architect","schema_version":"1.0",
    "source":["vision.json","diagnosis.json"],
    "church_context":{ /* vision.meta.church_context 상속 */ },
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",   // vision.chosen.theme — 필수(null이면 위반: 표어 먼저)
    "status":"제안"                                        // 제안(목사 확정 전·기본) | 확정(목사 HITL 후)
  },

  "inputs_echo": {                              // 번역의 입력을 비춰 둠(투명성·추적)
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "direction_declaration":"…방향 선언문 1단락…",        // vision.direction_declaration
    "axis_mapping":{"영성":"개인 중보·돌봄 기도","전도":"한 영혼 전도","양육":"식탁 공동체·소그룹 정착"},  // vision chosen 후보
    "core_scriptures":[{"ref":"누가복음 15:1-7"}],         // vision chosen 후보 본문(지어내지 않음)
    "bottleneck":"정착",                                   // diagnosis.funnel.bottleneck
    "bottleneck_headline":"유입은 있으나 정착에서 샌다",      // diagnosis.findings.bottleneck_headline
    "needs_care":["전도","양육","재정"],                    // diagnosis.health_radar.needs_care
    "pastor_focus_axis":"양육"                              // 목사 1회 입력(없으면 null → 병목 따라감)
  },

  "axes": [                                     // 정확히 3개 엔트리(영성·전도·양육). 목표 없는 축은 goals:[]
    {
      "axis":"양육",                            // 영성 | 전도 | 양육 (이 셋만)
      "axis_full":"양육·소그룹·공동체",
      "goals":[                                 // 0~2개 (과욕 상한: 축당 ≤2)
        {
          "direction_goal":"흩어진 양이 한 식탁에 앉도록 정착 동선을 연다",   // 정성(필수)
          "rationale":"표어 '한 식탁' + 병목 '정착에서 샘' + 돌봄점 양육2↓에서",  // 추적 근거(필수)
          "scripture_link":"누가복음 15장 잃은 양",          // 표어 본문 연결(선택)
          "priority":1,                                     // 축 내 우선순위
          "indicators":[                                    // 정량 신호 ≥1 (비면 환원 위반)
            {
              "label":"새가족 6개월 정착률",
              "baseline":{"value":"체감 절반","confidence":"중","from":"diagnosis.funnel 정착 샘"},
              // baseline은 value(서술) 또는 range:[lo,hi](띠)로 둔다 — diagnosis에서 상속(smart-refiner). 신뢰'하'면 assumption:true 권장
              "target":"3분기까지 2/3 수준",                 // 신뢰'하' 기준선이면 점값 금지(범위·방향)
              "by":"3Q",
              "signal_only":true,                            // 돌봄 신호 표기(누락 시 경고)
              "measure_real":true                            // 실제 측정 가능(false면 허위 정량 의심)
            }
          ],
          "smart":{"specific":true,"measurable":true,"achievable":true,"relevant":true,"timebound":true},
          "achievable_note":null                            // 무리하면 경고 텍스트(smart-refiner)
        }
      ]
    },
    { "axis":"영성","axis_full":"영성·기도·말씀","goals":[ /* … */ ] },
    { "axis":"전도","axis_full":"전도·선교·성장","goals":[] }   // 올해는 '유지'만 → keep_list로
  ],

  "keep_list":["주일·새벽 예배 현행 유지","단기선교 연 1회 유지"],     // 올해 유지(빼기의 반대편)
  "stop_list":["효과 약했던 대형 전도행사 중단","이름만 있는 부서 모임 정리"],  // 올해는 하지 않을 것(빼기)

  "warnings":[                                  // overreach-guard 산출(경고지 차단 아님)
    {"type":"과욕","text":"세 축 모두 신규 목표면 담임 시간 초과 우려","basis":"핵심 목표 수·담임 단독"},
    {"type":"자원충돌","text":"전도축제·양육개강이 2분기 집중","basis":"두 목표 모두 2Q 기한"},
    {"type":"시간한계","text":"설교 준비 시간과 충돌 가능","basis":"담임목사 주간 시간 제약"}
  ],

  "summary_table":"| 축 | 방향 목표 | 신호 지표 | 기준선 | 올해 목표치 | 기한 |\n|...|",

  "confirmed": null                             // 목사 확정 HITL 후에만: {"by":"목사 확정(HITL)","adjusted":["목표치 하향"],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`chosen_theme` 채워짐·`status`∈{제안,확정}) · `inputs_echo` · `axes`(3축 엔트리).
- **`meta.chosen_theme`가 비면 위반** — 표어 미확정 상태로 목표를 세울 수 없다(vision-discernment #2로 돌아간다).
- 전체 `goals` 합이 0이면 위반(아무 목표도 없음). axis당 `goals` ≤2, 전체 ≤6 초과 시 위반(과욕 하드 상한).
- 각 목표: `direction_goal`+`indicators`(≥1) 둘 다 + `rationale` 필수.
- `status:"확정"`인데 `confirmed`=null이면 위반(목사 확정 전 확정 표기 금지).

## 신뢰 표기 (diagnosis에서 계승)
기준선 `confidence`는 diagnosis의 신뢰수준(상/중/하)을 잇는다. '하'면 `baseline`에 `assumption:true`를 권장하고, 그 위의 `target`은 점값(예 "131명")이 아니라 범위·방향("약간 증가","2/3 수준")으로 둔다. 기준선 값은 서술형 `value` 또는 diagnosis에서 상속한 `range:[lo,hi]`(오차 띠) 중 하나로 둔다 — 점검표 렌더(build_checklist)는 둘 다 읽는다.

## 다음 스킬이 읽는 곳

**주 소비자 (SKILL.md 명시 — #4·#5·#7·#9):**
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| sermon-planner-52 (#4) | meta.chosen_theme·axes[].direction_goal·inputs_echo.core_scriptures |
| signature-events (#5) | axes[].goals(어느 축·목표를 섬길 행사인가)·warnings(과밀 회피) |
| action-planner (#7) | axes[].goals.indicators(목표치·기한 → 분기 마일스톤) |
| review-rhythm (#9) | axes[].goals.indicators(baseline·confidence/assumption·target·by·signal_only) → 분기 스코어카드(신뢰 '하'/추정은 verify_at_review 실측 표시) |

**참조 소비자 (계획서·캘린더·키트·보강 단계에서 부수적으로 읽음):**
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| ministry-calendar (#6) | axes[].goals[].indicators(by·target → 분기 마일스톤 캘린더 표시점) |
| plan-compiler (#10) | axes(3축 목표·지표 → 계획서 본문 '3축 목표' 장)·신뢰 '하' 항목(보강 종자) |
| prayer-scripture-kit (#11) | axes[영성].goals·indicators(통독 완주·새벽 참여 신호 → 영성 키트 연계·지원·선택) |
| plan-reinforce (#12) | indicators[].baseline 중 confidence='하'/assumption → 실측 교체 대상 |
