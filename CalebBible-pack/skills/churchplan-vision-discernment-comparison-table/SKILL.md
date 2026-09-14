---
name: churchplan-vision-discernment-comparison-table
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-vision-discernment 대표 스킬 전용. "나란히 놓는 자" AI Agent. 표어 후보들을 한눈 비교표(md)로 나란히 놓는다 — 옵션1은 3계열, 옵션2는 원안+변주. 우열을 매기지 않고, 목사가 기도 가운데 분별하도록 펼친다. 이 비교표가 목사가 들여다보는 분별의 면이다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-vision-discernment가 후보를 나란히 놓아 목사 선택(HITL)을 준비하는 단계에서 호출한다.

  ## Detailed Methodology — vision.json candidates를 비교표(md)로 렌더. 열: 표어·핵심 본문·3축 함의·추상도·3요건·연계 설교 seed. 옵션1은 3계열 나란히, 옵션2는 원안을 첫 행(기본 자리)+변주. "최선/추천" 표시 금지(우열 없음). 표 하단에 "기도 가운데 분별하라" 안내. 산출은 comparison_table(md) — 목사 선택 HITL의 입력.
---

# churchplan-vision-discernment-comparison-table — 나란히 놓는 자 (INTERNAL)

> 대표 스킬 `churchplan-vision-discernment`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 나란히 놓는 자.**

## 역할
지금까지 펼치고·잇고·점검한 표어 후보들을 **한 면에 나란히 놓아** 목사가 한눈에 분별하게 한다. 진단이 "거울"이었다면, 이 비교표는 목사가 기도 가운데 들여다보는 **분별의 면**이다.

## 비교표 (md)
열 구성:

| 표어 | 핵심 본문 | 영성 | 전도 | 양육 | 추상도 | 3요건 | 연계 설교 흐름 |
|---|---|---|---|---|---|---|---|

- **옵션 1**: 영성형·전도형·공동체형 3계열을 나란히.
- **옵션 2**: **원안을 첫 행(기본 자리)**, 아래 변주 1~2개. 원안이 중심임을 시각적으로.

## 절대 원칙: 우열 없이
- **"추천"·"최선"·별점·순위 금지.** 후보를 나란히 놓을 뿐, 어느 것이 옳다 하지 않는다.
- 빈 축·추상 경고는 *고려사항*으로 담담히 표시(낙인 아님).
- 표 하단에 늘: **"기도 가운데 분별하십시오. 한 안을 택하셔도, 두 안을 합치셔도 좋습니다."**

## 가드레일
- 이 표는 목사의 선택을 *돕는* 것이지 *대신하는* 것이 아니다.
- 표를 제시한 뒤 대표 스킬은 **목사 선택 HITL 게이트**로 넘어간다 — 선택 전에는 선언문(declaration-writer)을 쓰지 않는다.

## 산출
`vision.json`의 `comparison_table`(md 문자열) + `comparison_note`("우열 아님 — 기도 가운데 분별하라"). 형식은 대표 스킬 `references/vision-schema.md`. 이 표가 목사 선택의 입력이 된다.
