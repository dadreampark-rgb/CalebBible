# 점검 리듬 결과 스키마 (review.json) — 단일 진실

> scorecard-builder가 지표를 분기 신호등 점검행으로 번역하고, monthly-checkup이 월간 1p 점검표를, red-signal-responder가 빨강 대응 시나리오를, review-scheduler가 연간 일정·반기 공식 수정일·분기 어젠다를 채운다. rhythm-renderer가 스코어카드·월간표를 렌더하고, fidelity-guard의 `validate_review.py`가 검사한다. plan-compiler(#10)가 입력으로 읽는다. **스키마 변경 시 두 스크립트(`validate_review.py`·`build_review.py`)도 함께 변경.**

## 공통 규칙 (점검은 돌봄이지 채찍이 아니다)
- **숫자는 목자의 눈이지 채찍이 아니다**(01 라인 331): 모든 지표·신호등은 *돌봄 신호*다. `실패·미달·부진·문책·추궁·징계·낙제·질책`(금칙어 단일 진실원 — 8개) 같은 성과·정죄 어휘를 산출에 쓰지 않는다(care-framing 계승).
- **미래 점검값을 지어내지 않는다**(#9 추정 충실도): 분기 점검행의 `status`는 **점검 전 비움(null)** 이다. 아직 일어나지 않은 진행("1Q 녹색 달성")을 미리 채우면 위반.
- **신호일 뿐**: 모든 점검 지표는 `signal_only:true`를 계승한다(#3 indicator). 성과 등급이 아니다.
- **흐린 지표는 분기에 또렷이**: #3 기준선 신뢰가 '하'/assumption인 지표는 `verify_at_review:true`로 표시한다(분기 점검 시 실측 확인 대상 — #1 "귀가 후 확인 목록"·#12 plan-reinforce 이월의 착지점).
- **살아 움직이게**: 반기(6~7월) **공식 수정일**을 못박는다(01 라인 310). 빠지면 위반.
- **절제**: 월간 점검은 핵심 지표만(5분 점검). 모든 지표를 늘어놓아 KPI 대시보드로 만들지 않는다.
- goals·resource에 없던 지표·경고·이름을 새로 만들지 않는다(상속·전사).

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-review-rhythm","schema_version":"1.0",
    "source":["goals.json","resource.json"],
    "church_context":{ /* 상속 */ },
    "year":2027,
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",   // 상속 — 필수(없으면 위반)
    "status":"제안"                                        // 제안(기본) | 확정(목사 HITL 후)
  },

  "inputs_echo": {                                        // provenance
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "indicators_from_goals":[                             // #3 axes[].goals.indicators (지어내지 않음)
      {"axis":"양육","label":"새가족 6개월 정착률","baseline":{"value":"체감 절반","confidence":"중"},
       "target":"3분기까지 2/3 수준","by":"3Q","signal_only":true}
    ],
    "sustainability_from_resource":{                      // #8 (지속가능성 점검 항목)
      "warnings":[{"type":"담임과부하","text":"설교+심방+행정 합산 초과 우려"}],
      "demand_gaps":[{"area":"전도","gap":"인력 2명 부족"}],
      "pastor_time":{"protected":["기도·영성","쉼·안식"],"warning":"심방 시간 압박"}
    }
  },

  "scorecard": {                                          // scorecard-builder ★ — 분기 신호등
    "frame":"신호등은 돌봄 신호다 — 🟢 잘 자라는 중 / 🟡 살펴볼 곳 / 🔴 목자의 손이 필요한 곳. 성과 등급이 아니다(숫자는 목자의 눈이지 채찍 아님).",
    "quarters":[                                          // 정확히 4분기(1Q~4Q)
      {
        "quarter":"1Q",
        "review_when":"3월 말 주일 오후(목사 입력 — 없으면 '분기 말')",
        "indicators":[                                    // 이 분기에 점검할 지표(by 정합)
          {
            "ref":"양육 · 새가족 6개월 정착률",            // axis · label (상속)
            "baseline":"체감 절반(신뢰 중)",
            "target":"3분기까지 2/3 수준",
            "by":"3Q",
            "signal_only":true,
            "verify_at_review":false,                     // 기준선 신뢰 '하'/assumption면 true(실측 확인 대상)
            "status":null,                                // 점검 전 비움 — 미래 진행값 지어내지 않음
            "care_note":"숫자가 낮으면 추궁이 아니라 '머물 자리를 못 찾은 양'을 함께 찾는다"
          }
        ]
      },
      { "quarter":"2Q","review_when":"…","indicators":[] },
      { "quarter":"3Q","review_when":"…","indicators":[] },
      { "quarter":"4Q","review_when":"…","indicators":[] }
    ]
  },

  "monthly_checkup": {                                     // monthly-checkup — 월간 1p(5분)
    "frame":"매월 5분 — 점수 매기기가 아니라 돌봄이 닿지 않은 양을 찾는 시간.",
    "rows":[                                               // 핵심 지표만(절제 — KPI 대시보드 금지)
      {"item":"새가족 정착","source":"goals.양육","glance_question":"이번 달 새로 온 분이 자리를 찾았는가?"}
    ],
    "pastor_sustainability_row":{                          // #8 pastor_time — 목자 소진 체크(필수)
      "item":"목자의 기도·쉼",
      "source":"resource.pastor_time(protected)",
      "glance_question":"이번 달 나의 기도·안식 시간은 지켜졌는가?"
    },
    "weekly_option":"주간 5분 — 강단·심방 한 줄 메모(원하는 목사만, 선택)"  // 01 '매월/매주' 흡수(확대 아님)
  },

  "red_signal_scenarios":[                                 // red-signal-responder — 빨강 대응(정죄 아님)
    {
      "indicator_ref":"양육 · 새가족 6개월 정착률",
      "if_red":"이 지표가 🔴이면 — 실패가 아니라, 머물 자리를 찾지 못한 양이 있다는 표지다.",
      "response":["정착이 끊긴 지점을 함께 본다(환영→소그룹 동선)","흔들리는 한 사람의 이름을 떠올린다","무리한 목표치였는지 반기 수정일에 다시 본다"],
      "not":"성과 추궁·담당자 문책 금지(돌봄 점검이지 인사 평가 아님)"
    }
  ],

  "schedule": {                                            // review-scheduler
    "quarterly_reviews":[                                  // 분기 리뷰 4회
      {"quarter":"1Q","when":"3월 말","agenda_ref":"quarterly_agenda"}
    ],
    "quarterly_agenda":[                                   // 분기 점검 회의 어젠다 템플릿(보완B·01 라인 300)
      "① 신호등 함께 보기(돌봄 신호로)",
      "② 🔴 지표 돌봄 점검(대응 시나리오)",
      "③ 목자·일꾼 소진 점검(#8 지속가능성)",
      "④ 다음 분기 조정(무리한 목표치 손보기)"
    ],
    "midyear_revision":{                                   // 반기 공식 수정일 — 못박기(필수)
      "when":"6~7월","official":true,
      "note":"현실과 동떨어진 계획을 1년 내내 붙들지 않도록 공식적으로 수정하는 날(01 라인 310)"
    },
    "auto_reminder":{                                      // (선택) 구조 제안만 — 실제 발송 아님
      "proposed":true,
      "structure":"분기 말 자동 리마인드 + 지표 수집 양식 발송(목사/운영자가 켜는 구조 제안)",
      "note":"실제 자동화는 교회 환경에서 설정. 여기서는 구조만 제안(자료 없이 작동)."
    }
  },

  "confirmed": null                                        // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":["반기 수정일 7월 첫 주로","리마인드 사용"],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`chosen_theme` 채워짐·`status`∈{제안,확정}) · `inputs_echo` · `scorecard` · `schedule`.
- **`meta.chosen_theme` 비면 위반** — 표어·목표 미확정으로 점검 리듬 불가(앞 단계로).
- **미래값 둔갑 금지**: `scorecard.quarters[].indicators[].status`가 점검 전(`confirmed`=null)에 채워져 있으면 위반.
- **signal_only 계승**: 점검 지표에 `signal_only`가 빠지면 경고(성과 등급화 의심).
- **돌봄 프레이밍**: `scorecard`·`monthly_checkup`·`red_signal_scenarios`·`schedule`의 모든 AI 자유텍스트 leaf(`frame`·`care_note`·`glance_question`·`quarterly_agenda`·시나리오)에 성과·정죄 금칙어(실패·미달·부진·문책·추궁·징계·낙제·질책 — 8개)가 절 단위 부정 표지 없이 있으면 위반(재귀 순회로 검사 표면 자동 망라, 수치/상속 필드 제외).
- **반기 수정일 못박기**: `schedule.midyear_revision`이 없거나 `official`≠true면 위반(01 라인 310 강제).
- **상속 충실**: `inputs_echo.indicators_from_goals`/`sustainability_from_resource` 없이 지표·경고를 지어내면 위반.
- **추정 이월**: 기준선 신뢰 '하'/assumption 지표인데 `verify_at_review`가 true가 아니면 위반(흐린 지표 또렷한 척 금지 — #3→점검 매핑은 결정론).
- `status:"확정"`인데 `confirmed`=null이면 위반.
- 분기 무결성: `scorecard.quarters`는 정확히 4개(1Q~4Q)여야 하며, 어긋나면 위반. 지표 `by`와 배치 분기가 어긋나도 위반(by→분기 결정론 배치).

## 신뢰 표기 (goals에서 계승)
점검 지표의 기준선 신뢰는 #3 `indicators[].baseline.confidence`(상/중/하)를 잇는다. '하'/assumption이면 `verify_at_review:true`로 표시하고, 점검 시점에 추정을 실측으로 좁힌다(#12 plan-reinforce 이월의 착지점). 점값으로 단정하지 않는다.

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| plan-compiler (#10) | scorecard(분기 스코어카드)·schedule(연간 점검 일정·반기 수정일)·monthly_checkup(월간 점검표) |
| plan-reinforce (#12) | scorecard.quarters[].indicators[].verify_at_review=true → 귀가 후 실측 교체 대상 이월 |
