# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시(기준 #10). inline 시뮬레이션 단독 금지.

```
## (a) 발동·분류
- 발동 마스터: churchplan-goal-architect
- 희망 축: (목사 답 / 없으면 "병목 따라감")
- 표어·교회 컨텍스트: (vision/diagnosis에서 상속)

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | axis-prioritizer | 길을 고르는 자 | 병목·마음 → 축별 우선목표 1~2 | axes[].goals(direction_goal·rationale) |
| 2 | smart-refiner | 또렷이 다듬는 자 | SMART·기준선·잠정 목표치·기한 | goals[].smart·target·by, achievable_note |
| 3 | indicator-designer | 신호를 짓는 자 ★ | 정성↔정량 한 쌍 | goals[].indicators |
| 4 | overreach-guard | 짐을 가늠하는 자 | 자원충돌·시간·과욕 경고 | warnings |
| 5 | stop-start-curator | 빼기를 돕는 자 | 유지/중단 | keep_list·stop_list |
| (확정 후) 6 | checklist-builder | 점검표를 짓는 자 | md 표 + xlsx 씨앗 | summary_table·점검표 파일 |
| 7 | fidelity-guard | 목표를 지키는 자 | 짝·근거·과욕·표어 검증 | 검증 리포트 |

## (c) 하위 산출물 (각 별도 섹션)
### 🧭 축별 우선목표 (axis-prioritizer)
### 🎯 또렷한 목표·기준선·목표치 (smart-refiner)
### 📊 신호 지표 — 정성↔정량 한 쌍 (indicator-designer)
### ⚖️ 과욕·자원 경고 (overreach-guard)
### ➖ 올해 유지 / 올해는 하지 않을 것 (stop-start-curator)
### ✅ 3축 목표 점검표 (checklist-builder — 목사 확정 후에만)
### 🛡️ 목표 검증 (fidelity-guard)

## (d) 마스터 통합 + 확정 초대 (별도 섹션)
### 📋 3축 목표·지표표 (한눈에)
### ⚖️ 과욕 경고 요약 (감당 가능한 짐인가)
### 🙏 "이 목표와 목표치, 그대로 감당하실 만한가요? 무리한 곳은 낮추시고, 뺄 것은 빼십시오."
   — [목사 목표치 확정 HITL 대기. 확정 전에는 점검표를 렌더하지 않는다.]
### (확정 완료 후) ✅ 확정 3축 목표표 + 점검표 + 유지/중단
### ➡️ 다음 단계: sermon-planner-52(#4)·signature-events(#5)로 전달
```

## 원칙
- **(d)에서 반드시 확정을 기다린다.** 목표 제안과 점검표 렌더 사이에 목사의 목표치 확정 HITL이 있다.
- 과욕 경고는 *차단이 아니라 조언*으로 제시한다 — 목사가 짐을 가늠하도록.
- fidelity-guard 실패 시 (c)에 위반 노출, 해당 분석 재실행(임의 보정 금지).
- 영적 목표를 숫자로 환원하거나 목표 미달을 정죄로 프레이밍하지 않는다(전 섹션).
