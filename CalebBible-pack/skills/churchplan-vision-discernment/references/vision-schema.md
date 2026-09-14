# 분별 결과 스키마 (vision.json) — 단일 진실

> theme-generator·scripture-pairing·coherence-check가 candidates를 채우고, comparison-table이 표를 만들며, declaration-writer가 (목사 선택 후) 선언문을 쓰고, fidelity-guard의 `validate_vision.py`가 검사한다. goal-architect(#3)가 입력으로 읽는다. **스키마 변경 시 스크립트도 함께 변경.**

## 공통 규칙
- 본문 `ref`: "책 장:절"(실재 66권 한글 책이름). 확신 없으면 `"본문 미확정"`.
- **`direction_declaration`은 `chosen`이 채워진 뒤에만** 값을 가진다(선택 전엔 null).
- 후보에 우열/추천 표기 금지. `comparison_note`는 "우열 아님".

## 전체 구조

```json
{
  "meta": {
    "generated_by":"churchplan-vision-discernment","schema_version":"1.0",
    "mode":"option1",                         // option1(미정·펼치기) | option2(기정·다듬기)
    "source":["diagnosis.json","recall-dataset.json"],
    "church_context":{ /* 상속 */ }
  },

  "inputs_echo": {                            // 분별의 입력을 비춰 둠(투명성)
    "prayer_keywords":["회복","다음세대","정직"],
    "gripping_scriptures":["이사야 43장 새 일"],
    "church_situation":["예배당 이전 논의","세대교체"],
    "bottleneck_headline":"유입은 있으나 정착에서 샌다",
    "one_wish":"흩어진 양들이 한 식탁에 다시 앉는 교회"
  },

  "original_theme": null,                     // option2일 때만: {"text":"...","scripture_hint":"...","note":"목사 원안"}

  "candidates": [
    {
      "id":"A",
      "family":"영성형",                      // 영성형|전도형|공동체형 (option1) / 원안|변주 (option2)
      "theme":"한 영혼을 품고 한 식탁에 앉는 교회",
      "rationale":"기도 키워드 '회복' + 병목 '정착에서 샘'에서",
      "core_scriptures":[
        {"ref":"누가복음 15:1-7","exegesis":"잃은 양 한 마리를 찾아 나서시는 목자의 마음.","application":"한 사람을 끝까지 품는 교회"}
      ],
      "axis_mapping":{"영성":"개인을 향한 중보·돌봄 기도","전도":"한 영혼 전도","양육":"식탁 공동체·소그룹 정착"},
      "abstraction":{"level":"구체","warning":null},
      "criteria_check":{"성경적":true,"상황구체":true,"행동번역":true},
      "sermon_seed":"1Q 잃은 양 → 2Q 환대 → 3Q 식탁 공동체 → 4Q 함께 감사",
      "blindspot":null                        // option2에서 주로 채움: "전도 축이 약할 수 있음"
    }
  ],

  "comparison_table":"| 표어 | 핵심 본문 | 영성 | 전도 | 양육 | 추상도 | 3요건 | 연계 설교 |\n|...|",
  "comparison_note":"우열 아님 — 기도 가운데 분별하라",

  "chosen": null,                            // 목사 선택 후: {"theme":"...","by":"목사 선택(HITL)","synthesized_from":["A","B"]}
  "direction_declaration": null              // chosen 후에만: "한 단락 방향 선언문..."
}
```

## 필수 블록 (fidelity-guard 검사 — 누락 시 위반 EXIT 1)
`meta`(+mode) · `candidates`(각 theme·core_scriptures·axis_mapping·abstraction·criteria_check). option2면 `original_theme` + family="원안" 후보. `chosen`=null이면 `direction_declaration`=null이어야 함. 본문 `ref`는 `bible_validator`로 장·절 실재성까지 완전 검증. 결정 월권 어휘("표어는 …입니다"·"하나님의 뜻은"·"최선·추천")는 위반.

## 완료 게이트 (`--final`)
중간 산출물(선택 전)은 `validate_vision.py <vision.json>`로 정직성만 검증(통과=정직). 목사 HITL 선택 후 최종 완료는 `validate_vision.py <vision.json> --final` — `chosen`·`direction_declaration` 채워짐을 강제한다. "완료"는 `--final` 통과를 의미한다.

## 다음 스킬이 읽는 곳
| 다음 스킬 | 주로 읽는 블록 |
|---|---|
| goal-architect (#3) | chosen(확정 표어)·direction_declaration·chosen 후보의 axis_mapping·core_scriptures |
| sermon-planner-52 (#4) | chosen·core_scriptures·candidates[].sermon_seed |
| plan-compiler (#10) | chosen.theme(표어)·direction_declaration(방향 선언문)·core_scriptures(비전 한 장 본문) |
| prayer-scripture-kit (#11) | chosen.theme(표어)·core_scriptures(통독·가정예배·새벽 본문 연계·지원·선택) |
