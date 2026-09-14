# 자료 보강 결과 스키마 (reinforce.json) — 단일 진실

> data-extractor가 업로드 자료에서 데이터를 추출하고, estimate-actual-reconciler가 신뢰'하' 우선 추정 vs 실측을 대조해 "추정→실측" 이력을 남기며, plan-updater가 진단·목표·예산을 갱신하고(어긋남→새 병목), carryover-tracker가 미확인 항목과 갱신 baseline을 #9로 넘긴다. reinforce-renderer가 보정 대시보드(xlsx)+계획서 v2(docx)를 렌더하고, fidelity-guard의 `validate_reinforce.py`가 검사한다. **스키마 변경 시 두 스크립트(`validate_reinforce.py`·`build_reinforce.py`)도 함께 변경.**

## 공통 규칙 (있는 만큼만 보정 · 실측을 날조하지 않는다)
- **있는 만큼만 보정**: 자료는 *있는 것만·순서 무관*. 자료가 부족해도 괜찮다 — 확인된 만큼만 확정하고 나머지는 #9 분기 점검으로 이월한다(02 라인 261). 부족을 비난하지 않는다.
- **실측을 날조하지 않는다**: `status:"실측교체"`는 반드시 `actual_source`(어느 자료에서 읽었는지)가 있어야 한다. 자료에 없는 값을 실측인 척하지 않는다(#12 고유 위험·할루시네이션 차단).
- **추정을 지우지 않는다**: 실측으로 교체해도 `estimate`(원래 추정·신뢰)를 보존한다 — "추정→실측" 이력(투명성). 추정 옆에 실측을 놓는다.
- **신뢰'하' 우선**: assumption·confidence='하' 항목부터 실측 교체(가장 흐린 곳부터 또렷이).
- **어긋남을 강조한다**: 추정과 실측이 유의하게 다르면 `mismatch:true` — 단순 교체가 아니라 *새 병목* 신호로 plan-updater 조정에 연결(02 라인 253).
- **닫힌 고리**: #12는 일회성 숙제가 아니라 **#9 분기 점검의 첫 사이클**이다. 실측 baseline과 이월 항목을 `to_review`로 #9에 넘긴다(02 라인 259·"살아 있는 리듬의 시작").

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-plan-reinforce","schema_version":"1.0",
    "source":["diagnosis.json","goals.json","resource.json","review.json","sermon-plan.json","plan-package.json"],  // 옵션1 산출물(있는 것·6스키마 #12 종자)
    "church_context":{ /* 상속 */ },
    "year":2027,
    "status":"제안",                                       // 제안(기본) | 확정(목사 HITL 후)
    "uploaded_materials":["2026 12월 주보(4주)","2026 결산서","교적부 일부"]  // 업로드된 자료(있는 만큼)
  },

  "verify_targets": [                                      // #10 reinforce_guide + 6스키마 종자(귀가 후 실측 대상)
    {"item":"헌금","from_skill":"diagnosis","original":{"estimate":"약간 감소","confidence":"하","basis":"미자립 헌금 감소"},"priority":1},
    {"item":"중보기도 모임 참여","from_skill":"review","original":{"estimate":"어림 20명","confidence":"하"},"priority":2}
  ],

  "extracted_data": [                                      // data-extractor — 자료에서 추출(있는 것만·출처 명시)
    {"source_material":"2026 12월 주보","data_type":"출석","value":"131명","source_detail":"4주 평균"},
    {"source_material":"2026 결산서","data_type":"헌금","value":"전년 대비 -7%","source_detail":"총수입 비교"}
  ],

  "reconciliations": [                                     // estimate-actual-reconciler ★ — 추정 vs 실측 이력
    {
      "item":"주일 출석",
      "estimate":"120~140명(신뢰 중)",                      // 원래 추정 보존(이력)
      "actual":"131명",                                     // 실측
      "actual_source":"2026 12월 주보 4주 평균",             // 자료 근거(실측교체 시 필수)
      "delta":"범위 내(중앙값 근접)",
      "mismatch":false,                                     // 추정-실측 유의차면 true(새 병목 신호)
      "status":"실측교체",                                   // 실측교체 | 추정유지 | 이월
      "new_confidence":"상"                                 // 실측 후 신뢰 갱신
    },
    {
      "item":"정착",
      "estimate":"5~7가정(신뢰 중)",
      "actual":"2가정",
      "actual_source":"교적부 신규 등록 추적",
      "delta":"추정보다 크게 낮음",
      "mismatch":true,                                      // 어긋남 강조 → 새 병목
      "status":"실측교체",
      "new_confidence":"상"
    }
  ],

  "plan_updates": [                                        // plan-updater — 갱신·새 병목 조정(mismatch 근거)
    {"target":"goals 양육 정착 목표","before":"3분기 2/3 수준","after":"정착 동선 재설계 우선","reason":"실측 정착 2가정(mismatch) — 새 병목","trigger":"reconciliations 정착 mismatch"}
  ],

  "carryovers": [                                          // carryover-tracker — 미확인 → #9 이월
    {"item":"새가족 6개월 정착률","reason":"교적부에 6개월 추적 자료 없음","to":"#9 review-rhythm 분기 추적"}
  ],

  "to_review": {                                           // 보완A — #9 분기 점검 첫 사이클로(닫힌 고리)
    "updated_baselines":[                                  // 실측 baseline → #9 다음 사이클(신뢰 상)
      {"indicator":"주일 출석","new_baseline":"131명","confidence":"상","from":"reinforce 실측교체"}
    ],
    "carryovers_ref":["새가족 6개월 정착률"],                // 위 carryovers를 #9로
    "note":"확인된 만큼 확정, 나머지는 #9 분기 점검에서 — 살아 있는 리듬의 시작"
  },

  "confirmed": null                                        // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":["정착 목표 재설계","출석 baseline 131명"],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`status`∈{제안,확정}) · `verify_targets` · `reconciliations`.
- **실측 날조 금지**: `reconciliations[].status:"실측교체"`인데 `actual_source`가 비면 위반(자료 근거 없는 실측).
- **추정 보존**: `reconciliations[].estimate`가 비면 위반(추정→실측 이력 상실).
- **있는 만큼만**: `extracted_data`에 근거가 없는데 `status:"실측교체"`면 의심(경고). 자료 없는 항목은 `status:"이월"`.
- **부족 비난 금지**: 산출 전반에 부족 비난 어휘(자료가 이것밖에·왜 없·부실·게을·성의)가 *부정 표지 없이* 있으면 위반.
- **어긋남→조정**: `reconciliations[].mismatch:true`인데 `plan_updates`에 연결된 조정이 하나도 없으면 경고(새 병목 누락).
- **이월**: `carryovers[].to`에 review-rhythm(#9) 언급이 없으면 경고.
- `status:"확정"`인데 `confirmed`=null이면 위반.

## 추정→실측 이력 (투명성)
실측 교체는 추정을 *지우는* 것이 아니라 추정 옆에 실측을 놓는 것이다. `estimate`(원래)·`actual`(실측)·`actual_source`(근거)·`delta`(차이)를 함께 남겨, 확정 범위가 어디까지 또렷해졌는지 투명하게 비춘다.

## 입력 출처 (옵션1 산출물 — 6스키마가 #12 종자 표시)
| 출처 | 읽는 종자 |
|---|---|
| diagnosis.json (#1) | findings.verify_after_workshop + assumption:true |
| goals.json (#3) | indicators[].baseline confidence='하'/assumption |
| resource.json (#8) | budget_plan.current_by_function(비율 → 실제 결산) |
| review.json (#9) | scorecard verify_at_review=true |
| sermon-plan.json (#4) | weeks confirmed=false(2~4Q) |
| plan-package.json (#10) | reinforce_guide.verify_seeds(1차 목록) |

## 다음 (닫힌 고리)
reinforce.json + 보정 대시보드 + 계획서 v2 → `to_review`를 따라 **#9 review-rhythm 분기 점검의 첫 사이클**로. 옵션1→#12→#9→내년 갱신의 닫힌 고리.
