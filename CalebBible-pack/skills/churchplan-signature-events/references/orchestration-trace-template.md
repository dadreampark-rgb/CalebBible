# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시(기준 #10). inline 시뮬레이션 단독 금지.

```
## (a) 발동·분류
- 발동 마스터: churchplan-signature-events
- 무게중심: (영성/전도/양육 — 목사 답)
- 표어·목표·교회 컨텍스트: (vision/goals/sermon-plan에서 상속)

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | event-sifter | 행사를 가려내는 자 | 정기/핵심 구분·정리 제안 | regular_events·pruned_events |
| 2 | signature-designer | 핵심 행사를 빚는 자 ★ | 핵심 행사 3~5개·목표 연결 | signature_events |
| 3 | blueprint-writer | 기획안을 쓰는 자 | 1p 기획안 6필드 | signature_events[].blueprint |
| 4 | sermon-sync-checker | 강단과 잇는 자 | sermon-plan 정합 | signature_events[].sermon_sync |
| 5 | overload-guard | 과밀을 가늠하는 자 | 과밀·자원·인력 경고 | warnings |
| (확정 후) 6 | blueprint-renderer | 기획안을 짓는 자 | 기획안·행사–목표 지도 | 기획안 파일·event_goal_map |
| 7 | fidelity-guard | 행사를 지키는 자 | 목적·상한·정합 검증 | 검증 리포트 |

## (c) 하위 산출물 (각 별도 섹션)
### 🔎 정기/핵심 구분 · 정리 제안 (event-sifter)
### ✨ 핵심 행사 · 행사–목표 연결 (signature-designer)
### 📄 행사별 1페이지 기획안 (blueprint-writer)
### 🔗 설교 정합 (sermon-sync-checker)
### ⚖️ 과밀·자원·인력 경고 (overload-guard)
### 🗺️ 행사–목표 연결 지도 (blueprint-renderer — 목사 확정 후에만)
### 🛡️ 행사 검증 (fidelity-guard)

## (d) 마스터 통합 + 정리·확정 초대 (별도 섹션)
### ✨ 핵심 행사 3~5개 (한눈에) + 행사–목표 지도
### ⚖️ 과밀·인력 경고 요약 (감당할 행사 수인가)
### ➖ 정리 제안 (목적 약한 행사)
### 🙏 "목적이 약한 행사는 덜어내고, 핵심 3~5개로 압축하시겠습니까?"
   — [목사 검토·확정 HITL 대기. 확정 전에는 최종 기획안을 렌더하지 않는다.]
### (확정 완료 후) 📄 핵심 행사 기획안 + 행사–목표 연결 지도
### ➡️ 다음 단계: ministry-calendar(#6)·plan-compiler(#10)로 전달
```

## 원칙
- **(d)에서 반드시 확정을 기다린다.** 핵심 행사 제시와 최종 기획안 렌더 사이에 목사의 정리·확정 HITL이 있다.
- 목적 없는 행사를 만들거나 "작년에 했으니"로 정당화하지 않는다(전 섹션).
- fidelity-guard 실패 시 (c)에 위반 노출, 해당 분석 재실행(임의 보정 금지).
- 행사–목표 지도는 #4 설교–목표 지도와 짝 — 강단·행사가 한 방향임을 보인다.
