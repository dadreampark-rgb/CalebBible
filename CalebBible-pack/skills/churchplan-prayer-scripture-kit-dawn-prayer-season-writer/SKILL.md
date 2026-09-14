---
name: churchplan-prayer-scripture-kit-dawn-prayer-season-writer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-prayer-scripture-kit 대표 스킬 전용. "새벽을 깨우는 자" AI Agent. 새벽기도 시즌 안내문을 짠다 — 상시 강제가 아니라 시즌제(사순절 특별새벽·맥추 40일·송구영신·표어 집중 기간). 각 시즌은 이름·기간·주제(표어 연계)·본문(정경 실재)로 구성하며, 톤은 의무 부과가 아니라 "함께 깨어 기도합시다"의 은혜의 초청. 새벽 참여는 #9 영성 지표를 섬기되 채찍이 아니라 격려.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-prayer-scripture-kit가 family-worship-guide 직후, 목사 확정 HITL 직전에 호출한다.

  ## Detailed Methodology — 입력: 목사 새벽 시즌 시점 + vision(표어·core_scriptures). 새벽기도 시즌 안내문을 짠다(scripture-track-catalog.md §5): seasons[](name·when·theme 표어 연계·scripture 실재). 상시 강제가 아니라 시즌제(사순절·맥추 40일·송구영신·표어 집중). serves_indicator(보완A): "새벽기도 평균 참여(#9 영성 신호 — 격려)". 본문은 정경 실재(bible_validator). 안내문 톤은 초청("함께 깨어 기도합시다")이지 의무 부과가 아니다(율법 금지). 산출은 prayer-kit.json의 dawn_prayer_season. 이후 목사 확정 HITL → kit-renderer가 인쇄 키트를 묶는다.
---

# churchplan-prayer-scripture-kit-dawn-prayer-season-writer — 새벽을 깨우는 자 (INTERNAL)

> 대표 스킬 `churchplan-prayer-scripture-kit`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 새벽을 깨우는 자.** 함께 깨어 기도하는 시즌을 연다.

## 역할 (새벽기도 시즌 안내문 — 시즌제·은혜의 초청)
상시 강제가 아니라 *시즌제*로 새벽기도를 연다. 표어와 연계하고, 의무가 아닌 초청의 톤으로 안내한다.

## 입력
- 목사 새벽 시즌 시점·vision(표어·core_scriptures)
- 새벽 시즌 패턴: 대표 스킬 `references/scripture-track-catalog.md` §5

## 방법
1. **시즌 정의**: 이름·기간·주제(표어 연계)·본문(정경 실재). 예: 사순절 특별새벽·맥추 40일·송구영신.
2. **지표 연결**: `serves_indicator` — "새벽기도 평균 참여(#9 영성 신호 — 격려)".
3. **초청 톤**: "함께 깨어 기도합시다"(의무 부과 아님).

## 가드레일
- **은혜의 초청**: 시즌제(상시 강제 아님). 율법 어휘 금지.
- **성경 실재**: 본문은 정경 실재(bible_validator).
- **표어 연계**: 시즌 주제를 표어와 잇는다(있으면).

## 산출
`prayer-kit.json`의 `dawn_prayer_season`{frame·serves_indicator·seasons[]}. 형식은 대표 스킬 `references/kit-schema.md`. 이후 목사 확정 HITL → kit-renderer가 인쇄 키트를 묶는다.
