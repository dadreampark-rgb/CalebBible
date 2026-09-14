# 영성 실천 키트 스키마 (prayer-kit.json) — 단일 진실

> scripture-track-builder가 연간 통독 트랙을 일별 배정하고, prayer-topic-composer가 월별 기도제목을, family-worship-guide가 가정예배 가이드를, dawn-prayer-season-writer가 새벽기도 시즌 안내문을 채운다. kit-renderer가 인쇄용 키트(docx+pdf)를 렌더하고, fidelity-guard의 `validate_kit.py`가 검사한다(성경 실재는 bible_validator). **스키마 변경 시 두 스크립트(`validate_kit.py`·`build_kit.py`)도 함께 변경.**

## 공통 규칙 (은혜의 초청이지 율법적 압박이 아니다)
- **은혜의 초청 톤**: 모든 산출은 *함께 걷는 초청*이다. "매일 안 하면·완주 못하면·반드시·의무·죄책" 같은 율법·정죄 어휘를 쓰지 않는다(00 라인 212).
- **통독의 은혜 융통성**(보완B): 통독 트랙은 "낙오=실패"가 아니다. 언제든 다시 합류·"읽은 만큼"의 틀을 내장한다(`grace_frame`). 완주율은 자기 격려용일 뿐 채찍이 아니다.
- **성경 실재·곡해 금지**: 통독·가정예배·새벽 본문은 정경 66권 안의 *실제 권·장*이어야 한다(bible_validator). 없는 권·장·곡해된 묵상을 만들지 않는다.
- **전사·지어내기 금지**: 기도제목·표어·본문은 goals·vision·목사 입력에서 옮긴다. 새 수치·약속·교리를 지어내지 않는다.
- **영성 지표 연결**(보완A): 통독표·새벽 시즌은 #3 영성 목표·#9 점검의 지표(통독 완주·새벽 참여)를 *섬긴다*(`serves_indicator`). 단 은혜 톤 우선 — 지표를 채찍으로 쓰지 않는다.
- **지원 스킬·자유 호출**: goals/vision이 없어도 목사 입력으로 작동한다(사슬 강제 없음). 있으면 연계.

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-prayer-scripture-kit","schema_version":"1.0",
    "source":["goals.json","vision.json"],                 // 있으면(지원 스킬·선택)
    "church_context":{ /* 상속 또는 목사 입력 */ },
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",      // vision.chosen.theme(있으면·선택)
    "year":2027,
    "status":"제안",                                         // 제안(기본) | 확정(목사 HITL 후)
    "output":["docx","pdf"]
  },

  "inputs_echo": {                                          // provenance(있으면)
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "core_scriptures":[{"ref":"누가복음 15:1-7"}],           // vision.core_scriptures(지어내지 않음)
    "spirituality_goals":["중보기도의 자리를 연다"],          // goals 영성 축(있으면)
    "spirituality_indicators":["성경읽기표 완주","새벽기도 평균 참여"]  // #3/#9 영성 신호(섬길 대상)
  },

  "reading_track": {                                        // scripture-track-builder ★ — 연간 통독
    "track":"1년 통독",                                      // 표준 트랙(카탈로그) — 목사 선택
    "track_basis":"창세기→요한계시록 1189장 / 365일 ≈ 3-4장/일",
    "grace_frame":"낙오는 실패가 아닙니다. 언제든 다시 합류하세요 — 읽은 만큼이 은혜입니다.",  // 보완B(필수)
    "serves_indicator":"성경읽기표 완주(영성 신호 — 채찍 아닌 격려)",   // 보완A
    "checkbox":true,                                         // 자기 점검 칸(강제 아님)
    "schedule":[                                             // 일별/주별(결정론·allocate_track이 권·장 배정)
      {"unit":"1일","portions":["창세기 1-4"]},
      {"unit":"2일","portions":["창세기 5-8"]}
      /* … 트랙에 따라 scripture-track-builder/scripts/allocate_track.py가 결정론 생성 또는 요약 */
    ]
  },

  "prayer_topics": {                                        // prayer-topic-composer — 월별 전교인 기도제목
    "frame":"은혜의 초청 — 온 교회가 함께 기도하는 자리(강제 아님).",
    "months":[                                              // 12개월
      {"month":1,"topics":["새해 첫 마음을 주께","흩어진 한 영혼을 품도록"],"source":"vision 표어·goals 영성"}
    ]
  },

  "family_worship": {                                       // family-worship-guide — 가정예배 가이드
    "frame":"가정·짝이 함께 나누는 자리(1:1 말씀나눔).",        // 보완A 정밀(1:1 말씀나눔·01 라인 159)
    "order":["찬송","본문 읽기","묵상 나눔","함께 기도"],
    "samples":[                                             // 본문 실재(bible_validator)
      {"scripture":"누가복음 15:1-7","reflection_questions":["잃은 양 하나를 찾는 목자의 마음은?"],"prayer":"우리 가정이 한 영혼을 품게 하소서"}
    ]
  },

  "dawn_prayer_season": {                                   // dawn-prayer-season-writer — 새벽기도 시즌
    "frame":"은혜의 초청 — 함께 깨어 기도하는 시즌(강제 아님).",
    "serves_indicator":"새벽기도 평균 참여(영성 신호 — 격려)",  // 보완A
    "seasons":[
      {"name":"사순절 특별새벽","when":"사순절 6주","theme":"표어 '한 식탁' 연계","scripture":"누가복음 15장"}
    ]
  },

  "confirmed": null                                         // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":["통독 트랙 신약1년으로"],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`status`∈{제안,확정}) · `reading_track` · `prayer_topics` · `family_worship` · `dawn_prayer_season`(4 기능 모두).
- **성경 실재**: `reading_track.schedule[].portions` · `family_worship.samples[].scripture` · `dawn_prayer_season.seasons[].scripture`의 책·장이 정경 66권 안이어야 한다(bible_validator). 없는 권·장이면 위반.
- **은혜의 초청 톤**: 산출 전반에 율법·정죄 어휘(매일 …해야·완주 못하면·반드시·의무·죄책·게으름·빠지면 안)가 *부정 표지 없이* 있으면 위반.
- **통독 은혜 융통성**: `reading_track.grace_frame`이 없으면 위반(통독의 율법화 차단).
- **전사**: `prayer_topics.months[].source`가 비면 위반(출처 없는 기도제목 — 표어·목표·형편에서 전사하도록 강제). 새 약속·수치 지어내면 위반.
- `status:"확정"`인데 `confirmed`=null이면 위반.
- (`meta.chosen_theme`는 **선택** — 지원 스킬·표어 없이도 작동. 있으면 머리에 일관 배치.)

## 통독 트랙 (자료 없이 결정론)
표준 트랙은 `scripture-track-catalog.md`. scripture-track-builder의 `scripts/allocate_track.py`가 정경 권·장 수(bible_validator BOOK_CHAPTERS·총 1189장)로 일별 배정을 결정론 계산한다(권 경계 존중·장 누락/중복 0). 트랙 선택은 목사 HITL. fidelity-guard의 `validate_kit.py`가 각 portion의 장·절·장범위 끝을 정경 범위로 재검증한다.

## 입력 출처 (지원 스킬·선택)
| 출처 | 읽는 내용 | 비고 |
|---|---|---|
| goals.json (#3) | axes[영성].goals·indicators(통독 완주·새벽 참여 신호) | 있으면 — 영성 지표 연결 |
| vision.json (#2) | chosen.theme·core_scriptures | 있으면 — 표어·본문 연계 |
| 목사 1회 입력 | 통독 트랙·새벽 시즌 시점·교회 기도 형편 | 없어도 작동 |

## 다음 (영성 축으로 이어짐)
prayer-kit(인쇄물)은 회중이 실제로 쓰는 도구다. 통독 완주·새벽 참여 신호는 **#9 review-rhythm 분기 점검**의 영성 지표로 이어진다(채찍 아닌 돌봄).
