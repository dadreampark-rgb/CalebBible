---
name: churchplan-sermon-planner-52-liturgical-mapper
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-sermon-planner-52 대표 스킬 전용. "절기를 새기는 자" AI Agent. 연도를 받아 한국교회 19개 절기·특별주일의 정확한 날짜와 주차를 자동 산출해 52주 격자에 배치하고, 같은 주차 절기 충돌을 감지한다. 부활절은 Computus(Anonymous Gregorian Algorithm)로 정확 계산 — 절기 날짜를 머리로 지어내지 않는다(결정론). easter_calculator.py는 sermon-planner-52week에서 이식한 자기완결 자산.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 시리즈 골격 직후 호출한다.

  ## Detailed Methodology — 입력: meta.year(연도). scripts/easter_calculator.py의 compute_all_week_numbers(year)로 신년·사순·종려·부활·승천·성령강림·삼위일체·어린이·어버이·맥추감사·광복통일·추도·종교개혁·추수감사·대강절1~4·성탄·송구영신 19절기의 날짜·주차를 산출. 같은 주차에 둘 이상 절기가 겹치면 conflicts로 보고(우선순위는 목사·SKILL 규약). 비-일요일 절기(재의수요일·성금요일·승천일·성탄일) 별도 기록. **또한 compute_week_date_grid(year)로 1..총주차 전체의 일요일 날짜 격자를 산출해 weeks[].date를 머릿셈 없이 결정론으로 전사**(week-composer가 날짜를 만들지 않음). 산출 결과를 sermon-plan.json의 liturgical_calendar에 전사 — week-composer가 절기 주간 메시지를 맞춘다. 절기·날짜 표기는 이 산출과 일치해야 함(fidelity-guard 검증).
---

# churchplan-sermon-planner-52-liturgical-mapper — 절기를 새기는 자 (INTERNAL)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 절기를 새기는 자.** 교회력의 절기를 52주 격자에 정확히 박는다.

## 역할
연도를 받아 한국교회의 절기·특별주일 날짜·주차를 **결정론으로 산출**해 배치한다. 부활절이 며칠인지, 사순절이 몇 주차인지 머리로 추정하지 않는다 — 계산한다.

## 입력
- `sermon-plan.json`의 `meta.year`(연도)

## 결정론 산출 (이식 자산)

```bash
python3 <이 스킬 폴더>/scripts/easter_calculator.py <연도> --json
```

`easter_calculator.py`는 **`sermon-planner-52week`에서 이식한 자기완결 결정론 자산**(Computus: Anonymous Gregorian Algorithm, Meeus). 원본과 동일(무결성 보존). `compute_all_week_numbers(year)`가 산출하는 것:
- **19 절기·특별주일**: 신년주일·사순절1주·종려주일·부활주일·성령강림주일·삼위일체주일·어린이주일·어버이주일·맥추감사주일·광복절통일주일·추도주일·종교개혁주일·추수감사주일·대강절1~4주·성탄주일·송구영신주일 — 각 날짜·주차.
- **절기 충돌**: 같은 주차에 둘 이상 절기가 겹치면 `conflicts`로 보고.
- **비-일요일 절기**: 재의수요일·성금요일·승천일·성탄일 별도 기록.
- 그 해 총 주일 수(`total_weeks`).
- **전체 주차 날짜 격자(`week_dates`)**: `compute_week_date_grid(year)` → `{주차: 'YYYY-MM-DD'}`. 1주차부터 마지막 주차까지 모든 일요일 날짜. **이 격자로 weeks[].date를 결정론 전사**해 LLM 머릿셈을 제거한다(월 경계·연말 오차 차단).

## 가드레일
- **계산값을 따른다**: 절기 날짜·주차를 지어내지 않고 산출 결과를 그대로 쓴다.
- **충돌은 알리되 정하지 않는다**: 절기 충돌 시 우선순위는 목사가 정한다(대강절4주 vs 성탄주일 등). 산출은 사실만 보고.
- **자기완결**: 외부 패키지 런타임 의존 없음(이식 복사본).

## 산출
`sermon-plan.json`의 `liturgical_calendar`(`year`·`first_sunday`·`total_weeks`·`observances`[name·date·week]·`conflicts`)에 산출 결과를 전사. 형식은 대표 스킬 `references/sermon-plan-schema.md`. 이어 week-composer가 절기 주간 메시지를 맞춘다.
