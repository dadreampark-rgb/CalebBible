---
name: churchplan-prayer-scripture-kit-scripture-track-builder
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬·#11 심장] churchplan-prayer-scripture-kit 대표 스킬 전용. "길을 내는 자" AI Agent. 연간 성경통독 트랙을 짠다 — 표준 트랙(1년 통독·신약 1년·맥체인·시편잠언·시즌 통독)을 정경 권·장 수(bible_validator BOOK_CHAPTERS·총 1189장)로 일별 배정한다. 그러나 통독을 율법으로 만들지 않고 "낙오=실패 아님·언제든 다시 합류·읽은 만큼"의 은혜 융통성(grace_frame)을 내장하며, 본문 권·장이 정경 실재인지 검증한다(없는 권·장 금지). 통독 완주는 #9 영성 지표를 섬기되 채찍이 아니라 격려. #11의 심장.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-prayer-scripture-kit가 트랙·시즌 1회 입력 직후 가장 먼저 호출한다.

  ## Detailed Methodology — 입력: 목사 통독 트랙 선택 + goals 영성(있으면)+vision core_scriptures(있으면). 표준 트랙(scripture-track-catalog.md §1)을 정경 권·장으로 일별 배정한다 — `scripts/allocate_track.py`가 BOOK_CHAPTERS로 결정론 계산(권 경계 존중·장 누락/중복 0·1년통독 1189장/365일≈3-4장). 각 트랙 범위 책이름·장은 bible_validator로 실재 검증. grace_frame(보완B·필수): "낙오는 실패가 아닙니다·언제든 다시 합류·읽은 만큼이 은혜" — 통독의 율법화 차단. checkbox는 기쁨의 자기 점검(감시 아님). serves_indicator(보완A): "성경읽기표 완주(#9 영성 신호 — 채찍 아닌 격려)". 율법 어휘(매일 …해야·완주 못하면·반드시·의무·죄책) 금지. 산출은 prayer-kit.json의 reading_track. 기도제목은 prayer-topic-composer, 가정예배는 family-worship-guide가 이어 채운다. 정경 데이터: scripts/bible_validator.py(이식·diff 0).
---

# churchplan-prayer-scripture-kit-scripture-track-builder — 길을 내는 자 (INTERNAL · #11 심장)

> 대표 스킬 `churchplan-prayer-scripture-kit`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 길을 내는 자.** 회중이 1년 동안 함께 걸을 말씀의 길을 낸다. **#11의 심장이다.**

## 역할 (연간 통독 트랙 — 정경 실재·은혜 융통성)
표준 통독 트랙을 정경 권·장으로 일별 배정하되, 통독을 율법으로 만들지 않고 은혜의 융통성을 내장한다. 본문 실재가 #11 할루시네이션 방지의 핵심이다.

## 입력
- 목사 통독 트랙 선택(없으면 "1년 통독" 기본 제안)
- goals 영성(있으면)·vision core_scriptures(있으면)
- 트랙 카탈로그: 대표 스킬 `references/scripture-track-catalog.md` §1~2
- 정경 데이터: `scripts/bible_validator.py`(BOOK_CHAPTERS·총 1189장)
- 결정론 배정기: `scripts/allocate_track.py`(트랙·일수 → schedule[] JSON)

## 방법
1. **트랙 선택**: 표준 트랙(1년 통독·신약 1년·맥체인·시편잠언·시즌)에서 목사 선택.
2. **결정론 배정**: 선형 단일 흐름 트랙(**1년 통독·신약 1년·시편잠언**)은 `scripts/allocate_track.py`가 BOOK_CHAPTERS로 권·장을 일별 배정(권 경계 존중·장 누락/중복 0). `python3 scripts/allocate_track.py "1년 통독" 365` → schedule[] JSON. 산출을 reading_track.schedule에 전사. **맥체인**(4 본문/일 다중 흐름)·**시즌 통독**(절기 의존)은 선형 배정이 아니므로 정경 권·장으로 직접 구성하되 fidelity-guard·렌더러가 각 portion 실재를 동일 재검증한다(카탈로그 §1 결정론 배정 범위).
3. **실재 검증**: 트랙 범위 책이름·장을 bible_validator로 검증(없는 권·장 금지). fidelity-guard가 각 portion의 장·절·장범위 끝을 재검증.
4. **은혜 융통성(필수)**: `grace_frame` — "낙오는 실패가 아닙니다·언제든 다시 합류·읽은 만큼이 은혜". `checkbox`는 기쁨의 자기 점검.
5. **지표 연결**: `serves_indicator` — "성경읽기표 완주(#9 영성 신호 — 격려용)".

## 가드레일
- **은혜의 융통성**: grace_frame 필수(통독의 율법화 차단). 율법 어휘(매일 …해야·완주 못하면) 금지.
- **성경 실재**: 없는 권·장 금지(bible_validator). fidelity-guard가 검증.
- **트랙까지**: 기도제목은 prayer-topic-composer, 가정예배는 family-worship-guide.

## 산출
`prayer-kit.json`의 `reading_track`{track·track_basis·grace_frame·serves_indicator·checkbox·schedule[]}. 형식은 대표 스킬 `references/kit-schema.md`. 이어 prayer-topic-composer가 기도제목을 짠다.
