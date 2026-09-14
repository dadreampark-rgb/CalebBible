# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시(기준 #10). inline 시뮬레이션 단독 금지.

```
## (a) 발동·분류
- 발동 마스터: churchplan-sermon-planner-52
- 목사 입력: 연도 / 시즌제 골격 / 설교 스타일 / 작년 본문
- 표어·목표·교회 컨텍스트: (vision/goals에서 상속)

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | season-architect | 시즌을 세우는 자 | 표어+목표 → 분기 시리즈 골격 | series |
| 2 | liturgical-mapper | 절기를 새기는 자 | easter_calculator 절기 배치 | liturgical_calendar |
| 3 | week-composer | 주차를 짓는 자 ★ | 52주 본문·제목·메시지·적용 | weeks |
| 4 | text-curator | 본문을 살피는 자 | bible_validator + 중복·장르·공백 | coverage |
| 5 | narrative-mapper | 여정을 잇는 자 | 서사·균형 + 설교–목표 지도 | narrative_check |
| 6 | worship-music-guide | 찬양을 잇는 자 | 음악 주제·정서·모티프·스타일 | weeks[].worship_direction |
| 7 | load-sabbath-guard | 목자를 지키는 자 | 부하·절기 몰림·안식 경고 | load_warnings |
| (확정 후) 8 | plan-renderer | 계획표를 짓는 자 | 52주 표·시리즈 개요 | 계획표 파일 |
| 9 | fidelity-guard | 강단을 지키는 자 | 본문·절기·정합·곡 단정·월권 검증 | 검증 리포트 |

## (c) 하위 산출물 (각 별도 섹션)
### 📐 분기 시리즈 골격 (season-architect)
### 📅 절기 자동 배치 (liturgical-mapper)
### 📖 52주 설교 초안 (week-composer)
### 🔍 본문 점검·커버리지 (text-curator)
### 🧭 서사·균형·설교–목표 지도 (narrative-mapper)
### 🎵 음악 방향 (worship-music-guide — 곡 단정 없이)
### 🛌 부하·안식 경고 (load-sabbath-guard)
### 📋 52주 계획표 (plan-renderer — 목사 확정 후에만)
### 🛡️ 강단 검증 (fidelity-guard)

## (d) 마스터 통합 + 확정 초대 (별도 섹션)
### 🗺️ 52주 강단 여정 (한눈에 — 분기 시리즈 흐름)
### 🛌 부하·안식 경고 요약 (목자가 감당할 여정인가)
### 🙏 "이 강단 여정이 마음에 맞으십니까? 어색한 본문은 바꾸시고, 확정 범위(1Q 주별/2~4Q 시리즈)를 정하십시오."
   — [목사 검토·확정 HITL 대기. 확정 전에는 최종 계획표를 렌더하지 않는다.]
### (확정 완료 후) 📋 2027 52주 설교 계획표 + 분기 시리즈 개요 + 설교–목표 지도
### ➡️ 다음 단계: signature-events(#5)·ministry-calendar(#6)로 전달
```

## 원칙
- **(d)에서 반드시 확정을 기다린다.** 52주 초안 제시와 최종 계획표 렌더 사이에 목사의 검토·확정 HITL이 있다.
- 본문 해석을 단정하거나 특정 찬송 곡을 못박지 않는다(전 섹션).
- fidelity-guard 실패 시 (c)에 위반 노출, 해당 분석 재실행(임의 보정 금지).
- 절기·본문은 계산·검증 결과를 따르고 머리로 지어내지 않는다.
