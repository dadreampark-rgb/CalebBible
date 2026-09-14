# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시(기준 #10). inline 시뮬레이션 단독 금지 — 호출 visibility를 사용자가 검증 가능하게.

```
## (a) 발동·분류
- 발동 마스터: churchplan-diagnostics
- 자동 분류 cycle: C1 전체 진단 (또는 부분: 예 "깔때기만")
- 교회 컨텍스트: (recall-dataset.meta.church_context에서) 장로교(통합)·중형·수도권

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | trend-analysis | 흐름을 비추는 자 | 추이 비추기 | trend |
| 2 | funnel-analysis | 어디서 새는지 함께 보는 자 | 병목 지목 | funnel(★) |
| 3 | health-radar | 여덟 영역을 비추는 자 | 8영역 | health_radar |
| 4 | resolution-review | 지난 마음을 함께 돌아보는 자 | 은혜의 대조 | resolution_review |
| 5 | findings-synthesis | 강점과 돌봄점을 모으는 자 | 종합 | findings |
| 6 | dashboard-builder | 한 장 거울을 닦는 자 | 렌더 | .html+.xlsx |
| 7 | fidelity-guard | 거울을 정직하게 지키는 자 | 검증 | 검증 리포트 |

## (c) 하위 산출물 (각 별도 섹션)
### 📈 흐름 (trend)
### 🕳️ 어디서 새는가 (funnel) ★진단의 첫 문장
### 🕸️ 여덟 영역 (health radar)
### 🌱 지난 마음 (resolution review)
### 🗂️ 한 장 거울 (dashboard.html + xlsx 경로)
### 🛡️ 정직 검증 (fidelity-guard 리포트)

## (d) 마스터 통합 + 교정 초대 (별도 섹션)
### 🔑 진단의 첫 문장 (병목 방향)
### ✅ Top 3 강점 (감사할 곳)
### 🤲 Top 3 돌봄점 (먼저 손이 필요한 곳)
### 📌 귀가 후 확인 목록 (신뢰 '하')
### 🪞 "보시기에 다른 곳이 있나요?" — 목사 교정 1회(HITL) 후 확정
### ➡️ 다음 단계: vision-discernment(#2)로 전달
```

## 원칙
- 부분 사이클이면 미호출 하위는 trace에서 생략.
- fidelity-guard 실패 시 (c)에 위반 항목 노출, (d) 대신 "보완" 섹션으로 해당 분석 재실행.
- 교정(HITL)은 거울의 본질 — 초안을 확정으로 들이밀지 않는다.
