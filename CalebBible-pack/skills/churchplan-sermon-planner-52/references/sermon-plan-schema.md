# 설교 계획 결과 스키마 (sermon-plan.json) — 단일 진실

> season-architect가 시리즈 골격을, liturgical-mapper가 절기 주차를, week-composer가 52주 본체를, text-curator가 본문 점검을, narrative-mapper가 서사·균형·설교–목표 지도를, worship-music-guide가 음악 방향을, load-sabbath-guard가 부하 경고를 채운다. plan-renderer가 표·개요를 렌더하고, fidelity-guard의 `validate_sermon_plan.py`가 검사한다. ministry-calendar(#6)·plan-compiler(#10)가 입력으로 읽는다. **스키마 변경 시 두 스크립트(`validate_sermon_plan.py`·`build_sermon_plan.py`)도 함께 변경.**

## 공통 규칙 (강단을 지킨다)
- **본문은 실재해야 한다**: `primary_text`·`parallel_texts`는 정경 66권 실재 장:절(`bible_validator.py`가 검사). 없는 장·절·가짜 책 금지.
- **절기는 계산값을 따른다**: `observance`의 주차는 `easter_calculator.py` 산출과 일치(LLM이 절기 날짜를 지어내지 않음).
- **음악은 방향만, 곡은 단정 금지**: `worship_direction`은 주제·정서·가사 모티프·스타일만. **특정 찬송 번호·제목·작곡가를 단정하지 않는다**(할루시네이션 차단 — 곡 선택은 목사·찬양팀).
- **주해는 초안일 뿐**: `core_message`·`application`에 "유일한 해석"·"이 본문은 반드시 …"처럼 해석을 단정하지 않는다. Claude는 초안 생성기, 강단의 권한은 목사.
- vision·goals에 없던 표어·본문을 지어내지 않는다(상속·전사).

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-sermon-planner-52","schema_version":"1.0",
    "source":["vision.json","goals.json"],
    "church_context":{ /* 상속 */ },
    "year":2027,                                // 절기 계산용 — 필수(정수)
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",  // vision.chosen — 필수(없으면 위반)
    "preaching_style":"강해 중심",               // 강해|주제|절기|혼합 (목사 선호)
    "rolling_mode":true,                         // true=1Q 주별 확정·2~4Q 시리즈까지(롤링)
    "status":"제안"                              // 제안(기본) | 확정(목사 HITL 후)
  },

  "inputs_echo": {
    "chosen_theme":"한 영혼을 품고 한 식탁에 앉는 교회",
    "direction_declaration":"…vision 방향 선언문…",
    "core_scriptures":[{"ref":"누가복음 15:1-7"}],   // vision/goals 상속, 지어내지 않음
    "axis_goals":{"영성":"말씀·기도 뿌리내림","전도":"한 영혼 정착","양육":"식탁 공동체"},  // goals axes[].direction_goal
    "season_frame":{"1Q":"영성·기초","2Q":"전도·성장","3Q":"양육·리더","4Q":"공동체·감사"},  // 목사 입력
    "last_year_texts":["요한복음 연속 강해"]          // 중복 회피(기억나는 대로)
  },

  "liturgical_calendar": {                        // liturgical-mapper: easter_calculator 산출 전사
    "year":2027,"first_sunday":"2027-01-03","total_weeks":52,
    "observances":[ {"name":"부활주일","date":"2027-03-28","week":13} ],
    "conflicts":{ }
  },

  "series": [                                     // season-architect: 분기 시리즈 골격
    {
      "id":"S1","quarter":1,"title":"잃은 양 한 마리",
      "purpose":"표어의 '한 영혼'을 강단에 — 찾으시는 목자의 마음",
      "theme_link":"표어 '한 영혼을 품고'",
      "goal_link":["전도: 한 영혼 정착","양육: 식탁 공동체"],   // 설교–목표 정합(narrative-mapper)
      "weeks":[1,2,3,4,5],
      "style":"강해"                              // 강해|주제|절기
    }
  ],

  "weeks": [                                      // week-composer: 52주 본체
    {
      "week":1,"date":"2027-01-03","observance":"신년주일","series_id":"S1",
      "primary_text":"누가복음 15:1-7",            // bible_validator 검사
      "parallel_texts":["에스겔 34:11-16"],
      "title":"한 마리를 찾아 나서는 목자",
      "core_message":"아흔아홉을 두고 하나를 찾으시는 하나님의 마음",
      "application":"올해 우리가 끝까지 품을 '한 사람'은 누구인가",
      "worship_direction":{                        // worship-music-guide(곡 단정 금지)
        "theme":"찾으시는 은혜·돌아옴","mood":"따뜻하고 부르는",
        "lyric_motif":"잃음과 찾음·돌아오라는 초청",
        "style":"전통 찬송 + 잔잔한 회중 CCM",
        "note":"특정 곡은 회중이 아는 곡에서 찬양팀과 선정"
      },
      "confirmed":true                             // 롤링: 1Q 주별 확정 / 2~4Q는 false(시리즈까지만)
    }
  ],

  "coverage": {                                   // text-curator
    "ot_nt_balance":{"구약":18,"신약":34},
    "genre_balance":{"내러티브":20,"서신":15,"시가":8,"예언":5,"복음서":4},
    "duplicates":[],                               // 본문 중복 경고
    "doctrine_gaps":["성령론 비중 점검 권장"]         // 핵심 교리 공백 경고
  },

  "narrative_check": {                            // narrative-mapper
    "style_balance":{"강해":30,"주제":15,"절기":7},
    "series_flow":"1Q 찾으심 → 2Q 환대 → 3Q 식탁 → 4Q 감사 — 표어 흐름 일관",
    "sermon_goal_map":[                            // 설교–목표 지도(추천①)
      {"series":"S1","serves_axes":["전도","양육"],"how":"강단에서 한 영혼·정착을 떠받침"}
    ]
  },

  "load_warnings":[                               // load-sabbath-guard(추천②)
    {"type":"연속강해부담","text":"3~7주 연속 강해 — 준비 부하 큼","weeks":[3,4,5,6,7]},
    {"type":"절기몰림","text":"종려·부활 2주 연속 고강도","weeks":[12,13]},
    {"type":"안식제안","text":"8월 셋째 주 강단 교류/게스트 설교 권장","weeks":[33]}
  ],

  "confirmed": null                               // 목사 확정 HITL 후: {"by":"목사 확정(HITL)","adjusted":[...],"note":"…"}
}
```

## 필수 블록 (fidelity-guard 검사)
`meta`(+`year` 정수·`chosen_theme` 채워짐·`status`∈{제안,확정}) · `inputs_echo` · `weeks`.
- **`meta.chosen_theme` 비면 위반** — 표어 미확정으로 설교계획 불가(vision-discernment #2로).
- `weeks` 주차 중복 금지. 롤링이면 1분기(대략 1~13주)는 `primary_text`·`title` 채워짐(주별 확정), 그 외는 시리즈 배정(`series_id`)까지 허용.
- 각 채워진 주: `primary_text` 실재(bible_validator) + `observance` 있으면 절기 주차 일치(easter_calculator) — **불일치 위반**.
- 각 채워진 주: `date`는 `compute_week_date_grid(year)` 격자값과 일치(유효 ISO·일요일·해당 주차) — **불일치 위반**(날짜 지어내기 금지).
- `weeks[].series_id`는 정의된 `series.id`를 가리켜야 한다 — **미정의 위반**.
- `worship_direction`에 특정 곡 번호/제목 단정 금지.
- `status:"확정"`인데 `confirmed`=null이면 위반.

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| ministry-calendar (#6) | weeks(week·date·observance·series_id)·series·liturgical_calendar·load_warnings |
| signature-events (#5) | series.goal_link·weeks.observance(행사 주간 설교 정합) |
| plan-compiler (#10) | series(분기 개요)·weeks(52주 표)·narrative_check.sermon_goal_map |
| plan-reinforce (#12) | weeks 중 confirmed=false(2~4Q) → 분기 점검에서 확정 |
