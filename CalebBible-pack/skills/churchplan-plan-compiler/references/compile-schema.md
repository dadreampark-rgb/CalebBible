# 통합 패키지 스키마 (plan-package.json) — 단일 진실

> source-collector가 앞 9개 산출물을 모아 확정 여부를 검증하고, plan-document-composer가 계획서 본문 9요소를 전사하며, slide-deck-composer가 당회/제직회 슬라이드를, vision-onepager-composer가 성도용 비전 한 장을 짠다. compiler-renderer가 docx·pdf·pptx·html을 렌더하고 앞 산출물을 번들한다. fidelity-guard의 `validate_package.py`가 검사한다. **스키마 변경 시 두 스크립트(`validate_package.py`·`build_package.py`)도 함께 변경.**

## 공통 규칙 (전사하되 재생산하지 않는다 — Claude는 문서화를 돕는 종)
- **전사만, 재생산 금지**: 표어·방향 선언문·목표·설교·행사·예산은 앞 산출물의 *확정 내용을 그대로 옮긴다*. 매끈한 AI 문장으로 다시 쓰지 않는다(01 라인 330 "Claude는 정리·비교·문서화를 돕는 종이지 방향을 정하는 주인이 아니다").
- **앞 산출물에 없는 내용을 만들지 않는다**: 새 수치·표어·본문·행사를 지어내면 위반(할루시네이션 차단·ANCHOR#2).
- **다 확정돼야 묶는다**: 모든 필수 산출물이 `status:"확정"`이어야 한다. 미확정(제안) 산출물로 최종 문서를 만들지 않는다(garbage-in 차단 — #10 고유 게이트).
- **재생산 금지·번들**: 52주표·행사·캘린더·스코어카드·실행표·예산은 앞 스킬이 만든 파일을 *참조·번들*한다. #10이 다시 만들지 않는다.
- **청중별 번역**: 같은 진실을 당회/제직회(요약·결정)와 성도(초청·은혜 톤)로 다르게 옮긴다.
- **살아 움직이는 마무리**: 패키지는 끝이 아니라 #12 plan-reinforce·#9 분기 점검으로 이어지는 다리(`reinforce_guide`)를 담는다(설계원칙3·02 라인 241).

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-plan-compiler","schema_version":"1.0",
    "source":["vision.json","goals.json","sermon-plan.json","events.json","calendar.json","action.json","resource.json","review.json"],
    "church_context":{ /* 상속 */ },
    "church_name":"○○교회",          // 목사 1회 입력(없으면 경고)
    "logo":null,                      // 목사 1회 입력(선택)
    "tone":"표어 기반 따뜻한 톤",       // 목사 1회 입력(디자인 톤 일관성)
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",   // vision.chosen.theme 상속 — 필수
    "year":2027,
    "status":"제안"                    // 제안(기본) | 확정(목사 HITL 후)
  },

  "sources": {                         // source-collector — 무엇이 모였나·다 확정됐나
    "loaded":[
      {"skill":"vision-discernment","file":"vision.json","status":"확정","present":true},
      {"skill":"goal-architect","file":"goals.json","status":"확정","present":true}
      /* … 8개 필수 + diagnosis(선택) */
    ],
    "missing":[],                      // 빠진 필수 산출물(있으면 위반 — 앞 단계로)
    "unconfirmed":[],                  // status≠확정 산출물(있으면 위반 — 확정 먼저)
    "diagnosis_present":false          // 선택 입력
  },

  "plan_document": {                   // plan-document-composer ★ — 계획서 본문 = 정확한 9요소(전사)
    "intro_optional":{"source":"diagnosis.json","content":"지난해 돌아봄(diagnosis 있을 때만·선택)"},
    "chapters":[                       // 정확히 이 9요소(01 라인 316) — 순서·키 고정
      {"key":"표어","source":"vision.chosen.theme","content":"한 영혼을 품고 한 식탁에 앉는 교회"},
      {"key":"방향 선언문","source":"vision.direction_declaration","content":"…목사의 방향 선언문 그대로 전사…"},
      {"key":"3축 목표","source":"goals.axes","content":"…영성·전도·양육 목표·지표 전사…"},
      {"key":"설교계획","source":"sermon-plan.series","content":"…분기 시리즈 개요 + 52주 요약(핵심 장)…"},
      {"key":"핵심행사","source":"events.signature_events","content":"…핵심 행사 기획안 요약 + 행사–목표 지도(핵심 장)…"},
      {"key":"실행계획","source":"action.department_table","content":"…부서별 실행계획 요약…"},
      {"key":"예산","source":"resource.budget_plan","content":"…예산 배분(비율·증감)…"},
      {"key":"조직","source":"resource.org_plan","content":"…조직 배치·리더 양성…"},
      {"key":"점검계획","source":"review.scorecard+schedule","content":"…분기 점검 리듬·반기 수정일…"}
    ]
    /* 캘린더는 본문 9요소가 아님 — bundle로 별첨 */
  },

  "slide_deck": {                      // slide-deck-composer — 당회/제직회 요약(10장 내외)
    "audience":"당회/제직회",
    "slides":[                         // 표어·설교 흐름·핵심 행사 중심(02 라인 225)
      {"n":1,"title":"2027 표어","bullets":["한 영혼을 품고 한 식탁에 앉는 교회"],"source":"vision"},
      {"n":2,"title":"지난해 돌아봄","bullets":["…"],"source":"diagnosis(선택)"}
      /* … 약 10장: 표어·현황·3축목표·설교 흐름·핵심행사·캘린더 한눈·예산·조직·점검·동참 */
    ]
  },

  "vision_onepager": {                 // vision-onepager-composer — 성도용 1장(은혜 톤)
    "audience":"성도",
    "theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "core_scripture":"누가복음 15:1-7",    // vision.core_scriptures 전사(지어내지 않음)
    "directions":["…핵심 방향 3가지(전사)…"],
    "invitation":"…올 한 해 함께 하자는 동참 초청…",   // 01 라인 324
    "tone":"은혜의 초청(율법적 압박 아님)"
  },

  "reinforce_guide": {                 // 보완A — 살아 움직이는 마무리(끝이 아니라 시작)
    "verify_seeds":[                   // 귀가 후 실측 대상 — review verify_at_review + goals 신뢰'하'에서
      {"indicator":"중보기도 모임 참여","reason":"기준선 신뢰 '하'(추정)","from":"review.verify_at_review"}
    ],
    "auto_review_note":"…분기 자동 점검 설정 안내(review.schedule.auto_reminder 전사·원하는 목사만)…",
    "next":"#12 plan-reinforce — 주보·결산서·교적부를 있는 만큼 올리면 추정이 실측으로, 계획서 v2로 자란다"
  },

  "bundle":[                           // 재생산 금지 — 앞 산출물 파일 참조 번들
    {"name":"2027 52주 설교 계획표","from":"sermon-planner-52","files":["sermon-plan.xlsx"]},
    {"name":"연간 핵심 행사 기획안","from":"signature-events","files":["event-plan.md","event-plan.xlsx"]},
    {"name":"연간 사역 캘린더","from":"ministry-calendar","files":["calendar.html","calendar.xlsx"]},
    {"name":"3축 목표·지표 스코어카드","from":"review-rhythm","files":["review-scorecard.html","review-rhythm.xlsx"]},
    {"name":"부서별 실행계획표","from":"action-planner","files":["action.xlsx"]},
    {"name":"예산 배분안","from":"resource-aligner","files":["resource-plan.xlsx"]}
  ],

  "confirmed": null                    // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":["교회명·날짜 확정","문장 다듬기"],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`chosen_theme` 채워짐·`status`∈{제안,확정}) · `sources` · `plan_document` · `slide_deck` · `vision_onepager`.
- **`meta.chosen_theme` 비면 위반** — 표어 없이 계획서 불가(앞 단계로).
- **확정 게이트(garbage-in)**: `sources.missing`가 비어 있지 않으면 위반(필수 산출물 빠짐). `sources.unconfirmed`가 비어 있지 않으면 위반(미확정 산출물로 문서화 금지).
- **9요소 고정**: `plan_document.chapters`의 key가 정확히 [표어·방향 선언문·3축 목표·설교계획·핵심행사·실행계획·예산·조직·점검계획]이어야 한다(빠지면 위반). 캘린더가 chapters에 있으면 경고(본문 아님·bundle로).
- **전사 충실**: `plan_document.chapters[].source`가 비면 위반(출처 없는 본문 = 지어냄). `chapters[표어].content`가 `meta.chosen_theme`와 다르면 위반.
- **재생산 금지**: `bundle[]`은 앞 산출물 파일 참조만. 새 데이터 삽입 금지.
- **살아있는 마무리**: `reinforce_guide`가 없거나 `next`에 plan-reinforce 언급이 없으면 경고(끝이 아니라 시작).
- **슬라이드 분량**: `slide_deck.slides`가 7~12장 범위를 벗어나면 경고(10장 내외).
- `status:"확정"`인데 `confirmed`=null이면 위반.

## 입력 출처 (앞 스킬 → #10)
| 출처 | 읽는 내용 | 비고 |
|---|---|---|
| vision.json (#2) | chosen.theme·direction_declaration·core_scriptures | 표어·방향·비전한장 |
| goals.json (#3) | axes(3축 목표·지표)·신뢰'하' 항목 | 3축 목표·보강 종자 |
| sermon-plan.json (#4) | series·weeks·sermon_goal_map | 설교계획(핵심 장) |
| events.json (#5) | signature_events·event_goal_map | 핵심행사(핵심 장) |
| calendar.json (#6) | weeks·season_alignment | bundle 별첨 |
| action.json (#7) | department_table·actions·gaps | 실행계획 |
| resource.json (#8) | budget_plan·org_plan·pastor_time·subtractions | 예산·조직 |
| review.json (#9) | scorecard·schedule·verify_at_review·auto_reminder | 점검계획·보강 종자 |
| diagnosis.json (#1) | findings(선택) | 도입 '지난해 돌아봄'(선택) |

## 다음 단계 (패키지는 끝이 아니라 시작)
plan-package + 최종 문서(계획서 docx/pdf·슬라이드 pptx·비전 한장)를 손에 들고 귀가 → `reinforce_guide`를 따라 **#12 plan-reinforce**(귀가 후 자료 보강)·**#9 review-rhythm**(분기 점검)으로 이어진다.
