# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시한다. inline 시뮬레이션 단독 금지 — 어떤 하위 스킬이 언제·왜 호출됐는지 사용자가 검증 가능해야 한다(기준 #10).

## 출력 골격

```
## (a) 발동·분류
- 발동 마스터: churchplan-guided-recall
- 자동 분류 cycle: C1 전체 회상 (또는 부분: 예 "사람만")
- 교회 컨텍스트: 장로교(통합) · 중형 · 수도권 · 담임 단독

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | calendar-walk | 시간의 안내자 | 1→12월 순회 | 12개월 원자료 |
| 2 | people-recall | 사람의 안내자 | 깔때기 회상 | 병목 방향 |
| 3 | scale-recall | 규모의 안내자 | 범위+신뢰 | 추이 |
| 4 | heart-recall | 마음의 동행자 | 기쁨·아픔·기도 | 분별 재료 |
| 5 | health-map | 건강의 정리자 | 8영역 채점 | 레이더 |
| 6 | dataset-builder | 회상 정리자 | 정규화 | recall-dataset.json |
| 7 | fidelity-guard | 신뢰 지킴이 | 결정론 검증 | 검증 리포트 |
| (전 과정) | interview | 회상 대화 동행자 | 대화 구동·편향 완화 | — |

## (c) 하위 산출물 (각 별도 섹션)
### 📅 12개월 회상 타임라인
( calendar-walk + dataset-builder 결과 )
### 👥 사람 깔때기
( people-recall 결과 )
### 📊 규모 추정
( scale-recall 결과 )
### 💗 마음의 기록
( heart-recall 결과 )
### 🩺 건강 8영역
( health-map 결과 )
### 🗂️ 표준 데이터셋
( dataset-builder 결과 — recall-dataset.json )
### 🛡️ 신뢰 검증 리포트
( fidelity-guard 결과 — 통과/실패 + 가정 항목 )

## (d) 마스터 통합 Synthesis (별도 섹션)
### ✅ Top 3 강점
### ⚠️ Top 3 시급 과제
### 📌 워크샵 후 확인할 항목 (신뢰 '하' 모음)
### ➡️ 다음 단계: church-diagnostics(#1)로 전달
```

## 원칙
- 부분 사이클이면 호출하지 않은 하위 스킬은 trace에서 생략(억지로 채우지 않는다).
- 검증(fidelity-guard) 실패 시 (c)의 검증 리포트에 위반 항목을 그대로 노출하고, (d) 대신 "보완 질문" 섹션으로 되돌아간다.
