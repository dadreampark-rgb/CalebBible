# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시(기준 #10). inline 시뮬레이션 단독 금지.

```
## (a) 발동·분류
- 발동 마스터: churchplan-vision-discernment
- 옵션: 1 표어 펼치기 (미정) / 2 표어 다듬기 (기정)
- 교회 컨텍스트: (diagnosis/recall에서 상속)

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | theme-generator | 표어를 펼치는 자 | 옵션1 3계열 / 옵션2 원안+변주 | candidates |
| 2 | scripture-pairing | 말씀을 잇는 자 | 본문·주해·적용 | core_scriptures |
| 3 | coherence-check | 분별을 돕는 자 | 3축·추상도·3요건 | axis/criteria |
| 4 | comparison-table | 나란히 놓는 자 | 비교표 | comparison_table |
| (선택 후) 5 | declaration-writer | 방향을 적는 자 | 방향 선언문 | direction_declaration |
| 6 | fidelity-guard | 분별을 지키는 자 | 본문·월권 검증 | 검증 리포트 |

## (c) 하위 산출물 (각 별도 섹션)
### 🌱 표어 후보 (theme-generator)
### 📖 핵심 본문·주해 (scripture-pairing)
### 🧭 3축 연결·추상도·3요건 (coherence-check)
### 📊 표어 후보 비교표 (comparison-table)
### ✍️ 방향 선언문 (declaration-writer — 목사 선택 후에만)
### 🛡️ 분별 검증 (fidelity-guard)

## (d) 마스터 통합 + 분별 초대 (별도 섹션)
### 📊 표어 후보 비교표 (다시 한 번 한눈에)
### 🙏 "이 중 어느 것이 마음에 와닿으십니까? 기도 가운데 택하시거나 합치십시오."
   — [목사 선택 HITL 대기. 선택 전에는 선언문을 쓰지 않는다.]
### (선택 완료 후) ✍️ 확정 표어 + 방향 선언문
### ➡️ 다음 단계: goal-architect(#3)로 전달
```

## 원칙
- **(d)에서 반드시 선택을 기다린다.** 비교표 제시와 선언문 작성 사이에 목사의 기도 선택 HITL이 있다.
- fidelity-guard 실패 시 (c)에 위반 노출, 해당 분석 재실행.
- 우열·추천 표기 금지(비교표·통합 모두).
