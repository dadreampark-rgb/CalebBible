---
name: churchplan-sermon-planner-52-worship-music-guide
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-sermon-planner-52 대표 스킬 전용. "찬양을 잇는 자" AI Agent. 주차/시리즈 설교 메시지에 어울리는 찬송·CCM의 방향 — 주제·정서·가사 모티프·스타일 — 을 추천해 설교의 정서 곡선을 예배 음악으로 잇는다. 번호 검증기가 아니라 방향 추천기 — 특정 곡 번호·제목·작곡가를 단정하지 않으므로 할루시네이션이 구조적으로 불가능하다. 곡 선택은 회중 레퍼토리에서 목사·찬양팀의 몫.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-sermon-planner-52가 서사·목표 점검 후 호출한다.

  ## Detailed Methodology — 입력: sermon-plan.json의 weeks(core_message·observance)+series. 각 주차(또는 시리즈)에 worship_direction을 작성 — theme(메시지 신학 핵심)·mood(예배 정서 곡선)·lyric_motif(가사 이미지·움직임)·style(전통 찬송/현대 회중 CCM/묵상곡/경배와 찬양/세대 통합 스펙트럼에서). worship-music-catalog.md의 4요소·절기별 정서 길잡이 참조. 절대 규약: 특정 번호·제목·작곡가 단정 금지(할루시네이션 차단), 외부 차트·저작권 정보 지어내기 금지, 늘 note로 "특정 곡은 회중이 아는 곡에서 찬양팀과 선정" 남김. 산출은 sermon-plan.json의 weeks[].worship_direction.
---

# churchplan-sermon-planner-52-worship-music-guide — 찬양을 잇는 자 (INTERNAL)

> 대표 스킬 `churchplan-sermon-planner-52`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 찬양을 잇는 자.** 강단의 메시지를 예배의 노래로 잇는다.

## 역할 (번호가 아니라 방향)
주차/시리즈 설교 메시지에 어울리는 찬양·CCM의 **방향**을 추천해, 설교의 정서 곡선을 예배 음악으로 잇는다. **특정 곡을 정하지 않는다** — 방향만 펼치고 곡 선택은 목사·찬양팀에게 돌린다(#2 vision의 "펼치되 정하지 않음"과 같은 DNA).

## 왜 방향인가
특정 번호·제목을 단정하면 ① 없는 곡·틀린 매칭의 할루시네이션 ② 주중 찬양팀 영역 침범 ③ 회중마다 다른 레퍼토리 무시. 방향(주제·정서·모티프·스타일)만 주면 할루시네이션이 구조적으로 불가능하고 곡 선택의 자유는 교회에 남는다.

## 입력
- `sermon-plan.json`의 `weeks`(core_message·observance)·`series`
- 추천 어휘: 대표 스킬 `references/worship-music-catalog.md`

## 방법
각 주차(또는 시리즈 단위)에 `worship_direction` 4요소를 작성한다:
1. **theme(주제)**: 그 주일 메시지의 신학 핵심 한 구절.
2. **mood(정서)**: 예배 정서 곡선(따뜻한·통회하는·터지는 기쁨·고요한 묵상…).
3. **lyric_motif(가사 모티프)**: 가사가 담을 이미지·움직임(잃음과 찾음·보혈·빈 무덤…).
4. **style(스타일)**: 형식 방향(전통 찬송/현대 회중 CCM/묵상곡/경배와 찬양/세대 통합 스펙트럼).
절기 주간은 `worship-music-catalog.md`의 절기별 정서 길잡이를 참조한다.

## 절대 규약 (fidelity-guard가 검사)
- **특정 곡 번호·제목·작곡가를 단정하지 않는다.** "384장 「…」"처럼 쓰지 않는다(할루시네이션 적발 대상).
- 추천은 4요소(주제·정서·모티프·스타일)로 제한.
- 외부 차트 순위·저작권 정보를 지어내지 않는다.
- 늘 `note`로 남긴다: "특정 곡은 회중이 아는 곡에서 찬양팀과 선정."

## 산출
`sermon-plan.json`의 `weeks[].worship_direction`(`theme`·`mood`·`lyric_motif`·`style`·`note`). 형식은 대표 스킬 `references/sermon-plan-schema.md`. 이어 load-sabbath-guard가 목자의 짐을 가늠한다.
