# 진단 결과 스키마 (diagnosis.json) — 단일 진실

> 분석 4종(trend·funnel·health_radar·resolution_review)이 채우고, findings-synthesis가 종합하며, dashboard-builder가 렌더하고, fidelity-guard의 `validate_diagnostics.py`가 검사한다. vision-discernment(#2)·goal-architect(#3)가 입력으로 읽는다. **스키마 변경 시 두 스크립트도 함께 변경.**

## 공통 규칙 (추정 충실도)
- 모든 수치 항목: `{range:[lo,hi]` 또는 `value:...`, `confidence:"상|중|하"`, `trend:"↑|↓|→"(선택)`, `basis:(trend 있으면 필수)`}.
- **신뢰 '하/중'은** 정밀 `point` 금지(range 또는 **서술** value만). 숫자를 문자열로 적어도(예 `"187"`·`"187명"`·`"4520만원"`) 점값 둔갑으로 차단 — 범위(`"8~12가정"`)·완곡(`"약 130명"`·`"130명 내외"`)·서술(`"약간 감소"`)만 허용. **신뢰 '하'는 추가로 `assumption:true`**. → 점값 둔갑 차단.
- 미회상: `{value:null,"status":"미회상"}`. 0으로 채우지 않음.
- 회상 데이터셋(recall-dataset.json)에 없던 수치·이름을 새로 만들지 않음.

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-diagnostics","schema_version":"1.0",
    "source_recall":"recall-dataset.json",
    "recall_year":2026,                              /* recall-dataset.meta.recall_year 복사 (헤더 회상연도) */
    "church_context":{ /* recall-dataset.meta.church_context 복사 */ }
  },

  "trend": {
    "metrics":[
      {"label":"주일 출석","range":[120,140],"confidence":"중","trend":"→","basis":"본당 좌석 체감"},
      {"label":"헌금","value":"약간 감소","confidence":"하","assumption":true,"trend":"↓","basis":"미자립 헌금 감소"},
      {"label":"등록","value":null,"status":"미회상"}
    ]
  },

  "funnel": {
    "stages":[
      {"name":"유입(전도)","sense":"있음","value":"8~12가정","confidence":"중"},
      {"name":"정착","sense":"샘","value":"5~7가정","confidence":"중"},
      {"name":"양육","sense":"정체","confidence":"중"},
      {"name":"리더","sense":"소수 배출","value":"2명","confidence":"상"}
    ],
    "bottleneck":"정착",
    "bottleneck_direction":"유입은 있으나 정착에서 샌다 (6개월 내 이탈)",
    "care_note":"들어온 양이 머물 자리를 못 찾는다 — 정착 동선 돌봄 필요"
  },

  "health_radar": {
    "areas":[
      {"area":"예배","score":4,"trend":"↑","basis":"새벽기도 회복","confidence":"중"},
      {"area":"말씀","score":3,"trend":"→","basis":"성경공부 약함","confidence":"중"},
      {"area":"교제","score":3,"trend":"→","basis":"소그룹 절반","confidence":"중"},
      {"area":"전도","score":2,"trend":"↓","basis":"전도 행사 무산","confidence":"상"},
      {"area":"양육","score":2,"trend":"↓","basis":"양육 트랙 정체","confidence":"중"},
      {"area":"봉사","score":3,"trend":"→","basis":"봉사자 유지","confidence":"중"},
      {"area":"선교","score":3,"trend":"→","basis":"단기선교 1회","confidence":"중"},
      {"area":"재정","score":2,"trend":"↓","basis":"미자립 헌금 감소","confidence":"하","assumption":true}
    ],
    "strong":["예배"],
    "needs_care":["전도","양육","재정"]
  },

  "resolution_review": {
    "status":"부분 수집",
    "items":[
      {"resolution":"전도 축제 분기 1회","grew":"멈춤","actual":"상반기 1회 후 무산",
       "grace_note":"여건이 따르지 않았을 뿐, 전도의 마음은 청년부 회복으로 다르게 열매 맺음"}
    ]
  },

  "findings": {
    "bottleneck_headline":"유입은 있으나 정착에서 샌다 (6개월 내 이탈)",
    "strengths_top3":[
      {"text":"예배·기도 회복세","basis":"health.예배 4↑·새벽기도"},
      {"text":"새 리더 배출","basis":"funnel.리더 2명 상"},
      {"text":"선교 지속","basis":"health.선교 3·단기선교 1회"}
    ],
    "needs_care_top3":[
      {"text":"정착 깔때기 누수","basis":"funnel.정착 샘"},
      {"text":"양육 트랙 정체","basis":"health.양육 2↓"},
      {"text":"재정 압박","basis":"trend.헌금 ↓·health.재정 2"}
    ],
    "verify_after_workshop":[
      "이탈자 정확 수 (교적부)","헌금 실제 증감 (결산서)","재정 영역 실측 (예산 보고서)"
    ]
  }
}
```

## 필수 블록 (fidelity-guard 검사)
`meta` · `trend` · `funnel` · `health_radar` · `findings`. (`resolution_review`는 status:미수집 허용.)
`findings.bottleneck_headline`은 반드시 채워져야 한다(진단의 심장).

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| vision-discernment (#2) | findings.bottleneck_headline·needs_care·strengths + (recall) heart |
| goal-architect (#3) | funnel.bottleneck·health_radar.needs_care·findings.needs_care_top3 |
| plan-reinforce (#12) | findings.verify_after_workshop + assumption:true 항목 |
