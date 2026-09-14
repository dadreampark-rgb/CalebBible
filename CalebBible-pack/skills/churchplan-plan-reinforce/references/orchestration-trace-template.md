# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시(기준 #10). inline 시뮬레이션 단독 금지.

```
## (a) 발동·분류
- 발동 마스터: churchplan-plan-reinforce
- 상속: 옵션1 산출물(diagnosis·goals·resource·review·plan-package) + #10 reinforce_guide.verify_seeds
- 목사 업로드: 교회 실제 자료(주보·결산서·교적부·회의록 — 있는 만큼·순서 무관)

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | data-extractor | 자료를 읽는 자 | 자료에서 출석·헌금·등록·행사 추출(출처 명시) | extracted_data |
| 2 | estimate-actual-reconciler ★ | 추정과 실측을 맞대는 자 | 신뢰'하' 우선 추정 vs 실측·이력·어긋남 강조 | reconciliations |
| 3 | plan-updater | 계획을 자라게 하는 자 | 진단·목표·예산 갱신 + 어긋남→새 병목 조정 | plan_updates |
| 4 | carryover-tracker | 다음으로 넘기는 자 | 미확인 이월 + 실측 baseline → #9 첫 사이클 | carryovers·to_review |
| (확정 후) 5 | reinforce-renderer | 보정본을 굽는 자 | 보정 대시보드 xlsx + 계획서 v2 docx | 보정 파일 |
| 6 | fidelity-guard | 정직을 지키는 자 | 실측 날조·추정 삭제·비난 검증 | 검증 리포트 |

## (c) 하위 산출물 (각 별도 섹션)
### 📥 자료에서 추출한 데이터 (data-extractor — 출처 명시·있는 것만)
### ⚖️ 추정 vs 실측 대조 (estimate-actual-reconciler — 이력·어긋남 강조)
### 🌱 진단·목표·예산 갱신 (plan-updater — 새 병목 조정)
### ➡️ #9 분기 점검으로 이월·갱신 (carryover-tracker — 닫힌 고리)
### 📊 보정 대시보드 + 계획서 v2 (reinforce-renderer — 목사 확정 후에만)
### 🛡️ 보강 정직성 검증 (fidelity-guard)

## (d) 마스터 통합 + 확정 초대 (별도 섹션)
### 📥 무엇을 자료로 확인했나 (있는 만큼)
### ⚖️ 추정→실측 이력 (어디가 또렷해졌나·어긋난 곳은)
### 🌱 새 병목·갱신 제안 (어긋남이 부른 조정)
### ➡️ #9 분기 점검 첫 사이클로 (확인된 만큼 확정·나머지는 점검에서)
### 🙏 "계획이 자료를 만나 또렷해졌습니다. 실측 교체와 갱신을 확정하시겠습니까?"
   — [목사 검토·확정 HITL 대기. 실측 교체·갱신 확정 전에는 보정본을 굽지 않는다.]
### (확정 완료 후) 📊 보정 진단 대시보드(xlsx) + 신년 목회계획서 v2(docx)
```

## 원칙
- **(d)에서 반드시 확정을 기다린다.** 추정→실측 제시와 보정본 굽기 사이에 목사의 확정 HITL이 있다.
- **있는 만큼만 보정한다** — 자료 부족해도 괜찮다(이월).
- **실측을 날조하지 않는다** — actual_source 없는 실측 금지(전 섹션).
- **추정을 지우지 않는다** — estimate 보존·이력.
- **부족을 비난하지 않는다** — "계획이 스스로 자란다".
- **#9 첫 사이클로** — 일회성 숙제가 아니라 살아 있는 리듬의 시작.
- fidelity-guard 실패 시 (c)에 위반 노출, 해당 분석 재실행(임의 보정 금지).
```
