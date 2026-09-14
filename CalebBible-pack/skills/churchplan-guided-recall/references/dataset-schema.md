# 표준 회상 데이터셋 스키마 (recall-dataset.json) — 단일 진실

> dataset-builder가 이 스키마대로 작성하고, fidelity-guard의 `validate_recall_dataset.py`가 이 스키마로 검사한다. 다음 스킬(church-diagnostics #1·vision-discernment #2·goal-architect #3)이 이 규격을 입력으로 읽는다. **스키마를 바꾸면 검증 스크립트도 함께 바꾼다.**

## 공통 규칙
- 모든 수치 항목은 **객체**로: `{"range": [lo,hi]` 또는 `"value": ...`, `"confidence": "상|중|하"`, `"trend": "↑|↓|→"(선택)`, `"basis": "근거"(trend 있으면 필수)}`. **맨숫자(단정 스칼라) 금지.**
- 회상 못 한 항목: `{"value": null, "status": "미회상"}` — 추측으로 메우지 않는다.
- 신뢰 `"하"` 항목: 반드시 `"assumption": true`.
- 회상된 이름: `"names_recalled": [...]` 원문 보존. 창작 금지.

## 전체 구조

```json
{
  "meta": {
    "generated_by": "churchplan-guided-recall",
    "schema_version": "1.0",
    "recall_year": 2026,
    "church_context": {
      "denomination": "장로교(통합)",
      "size_band": "중형(150~300)",
      "region": "수도권 도시",
      "ministry_mode": "담임 단독"
    }
  },

  "calendar_timeline": [
    {
      "month": 1,
      "events": ["신년 특별새벽기도", "송구영신 여운"],
      "season": "신년주일",
      "tone": "기쁨",                
      "scene": "새벽기도 첫 주 가득 찬 본당",
      "confidence": "중"
    }
    /* ... 1~12월. 회상 못 한 달도 month는 두되 events 비울 수 있음 ... */
  ],

  "people": {
    "new_families":  {"value": "8~12가정", "confidence": "중", "names_recalled": ["김OO가정","이OO"]},
    "settled":       {"value": "5~7가정", "confidence": "중", "names_recalled": []},
    "left":          {"value": "3~5명", "confidence": "하", "assumption": true, "names_recalled": []},
    "new_leaders":   {"value": "2명", "confidence": "상", "names_recalled": ["박OO 구역장"]},
    "funnel_bottleneck": "유입은 있으나 정착에서 샌다 (6개월 내 이탈)"
  },

  "scale": {
    "sunday_attendance": {"range": [120,140], "confidence": "중", "trend": "→", "basis": "본당 좌석 체감 비슷"},
    "offering":          {"value": "약간 감소 느낌", "confidence": "하", "assumption": true, "trend": "↓", "basis": "연말 미자립 헌금 줄어듦", "ratio_sense": {"인건비":"40%대","운영":"20%대","사역":"20%대","선교":"10%대"}},
    "registrations":     {"value": null, "status": "미회상"},
    "small_groups":      {"value": "살아있음:이름만 = 6:4 느낌", "confidence": "중", "tired_leaders": "2개 구역 리더 소진"}
  },

  "heart": {
    "joys_top3": ["청년부 회복", "새벽기도 부흥", "장로 임직"],
    "pains_top3": ["핵심 집사 가정 이탈", "재정 압박", "다음세대 공백"],
    "sleepless_burden": "다음세대가 비어간다는 두려움",
    "prayer_keywords": ["회복", "다음세대", "정직"],
    "gripping_scriptures": ["이사야 43장 새 일"],   
    "church_situation": ["예배당 이전 논의", "세대교체"],
    "one_wish": "흩어진 양들이 한 식탁에 다시 앉는 교회"
  },

  "health_8areas": {
    "예배": {"score": 4, "trend": "↑", "basis": "새벽기도 회복", "confidence": "중"},
    "말씀": {"score": 3, "trend": "→", "basis": "주일설교 외 성경공부 약함", "confidence": "중"},
    "교제": {"score": 3, "trend": "→", "basis": "소그룹 절반만 활성", "confidence": "중"},
    "전도": {"score": 2, "trend": "↓", "basis": "전도 행사 무산", "confidence": "상"},
    "양육": {"score": 2, "trend": "↓", "basis": "양육 트랙 정체", "confidence": "중"},
    "봉사": {"score": 3, "trend": "→", "basis": "기존 봉사자 유지", "confidence": "중"},
    "선교": {"score": 3, "trend": "→", "basis": "단기선교 1회 시행", "confidence": "중"},
    "재정": {"score": 2, "trend": "↓", "basis": "미자립 헌금 감소", "confidence": "하", "assumption": true}
  },

  "integrity": {
    "confidence_summary": {"상": 2, "중": 9, "하": 3},
    "assumptions_flagged": ["people.left", "scale.offering", "health_8areas.재정"],
    "verify_after_workshop": [
      "이탈자 정확 수 (교적부)",
      "헌금 실제 증감 (결산서)",
      "재정 영역 실측 (예산 보고서)"
    ],
    "fabrication_check": "passed"
  },

  "top_findings": {
    "strengths_top3": ["예배·기도 회복세", "새 리더 배출", "선교 지속"],
    "urgent_top3": ["정착 깔때기 누수", "양육 트랙 정체", "다음세대 공백"]
  }
}
```

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| church-diagnostics (#1) | calendar_timeline·people(병목)·scale(추이)·health_8areas·top_findings·integrity |
| vision-discernment (#2) | **heart 전체**·church_context·top_findings |
| goal-architect (#3) | people(병목)·heart(one_wish·prayer_keywords)·health_8areas(약한 영역) |
| resource-aligner (#8) | scale.offering.ratio_sense·small_groups.tired_leaders |
| plan-reinforce (#12) | integrity.verify_after_workshop·assumptions_flagged |
