# Orchestration Trace 양식 (응답 강제 구조)

> 대표 스킬이 사용자 명령에 응답할 때 반드시 이 4부 구조로 표시(기준 #10). inline 시뮬레이션 단독 금지.

```
## (a) 발동·분류
- 발동 마스터: churchplan-plan-compiler
- 상속: 앞 9개 산출물(vision·goals·sermon-plan·events·calendar·action·resource·review [+diagnosis 선택])
- 목사 1회 입력: 교회명 / 로고(선택) / 디자인 톤

## (b) 호출 Trace
| 순서 | 하위 스킬 | AI Agent | 한 일 | 산출 |
|------|-----------|----------|-------|------|
| 1 | source-collector | 산출물을 모으는 자 | 다 모였나·다 확정됐나 검증 + 보강 종자 수집 | sources·reinforce_seeds |
| 2 | plan-document-composer ★ | 계획서를 엮는 자 | 본문 9요소 전사(설교·행사 핵심 장) | plan_document |
| 3 | slide-deck-composer | 발표를 짓는 자 | 당회/제직회 슬라이드 10장 | slide_deck |
| 4 | vision-onepager-composer | 비전을 펴는 자 | 성도용 비전 한 장(은혜 톤) | vision_onepager |
| (확정 후) 5 | compiler-renderer | 문서를 굽는 자 | docx+pdf+pptx+html + 번들 + 보강 안내 | 문서 패키지 |
| 6 | fidelity-guard | 통합을 지키는 자 | 전사 충실·확정 게이트·할루시네이션 검증 | 검증 리포트 |

## (c) 하위 산출물 (각 별도 섹션)
### 📦 산출물 수집·확정 점검 (source-collector — 미확정이면 멈춤)
### 📖 목회계획서 본문 9요소 (plan-document-composer — 전사·설교/행사 핵심 장)
### 🖥️ 당회/제직회 요약 슬라이드 10장 (slide-deck-composer)
### 📄 성도용 비전 한 장 (vision-onepager-composer — 은혜 톤)
### 🌱 옵션2 보강 안내 (살아 움직이는 마무리 — #12·#9로 가는 다리)
### 📚 최종 문서 패키지 (compiler-renderer — 목사 확정 후에만)
### 🛡️ 통합 검증 (fidelity-guard)

## (d) 마스터 통합 + 최종 확정 초대 (별도 섹션)
### 📦 무엇이 모였나 (9개 산출물 확정 상태 — 미확정은 앞 단계로)
### 📖 계획서 본문 한눈 (표어 → 점검까지 9요소)
### 🖥️ 청중별 산출물 (당회 슬라이드 / 성도 비전 한 장)
### 🌱 끝이 아니라 시작 (귀가 후 보강 다리)
### 🙏 "이제 한 해 계획이 한 권으로 묶입니다. 교회명·날짜·문장을 확정해 주시겠습니까?"
   — [목사 검토·확정 HITL 대기. 교회명/세부 확정 전에는 최종 문서를 굽지 않는다.]
### (확정 완료 후) 📚 계획서(docx/pdf) + 슬라이드(pptx) + 비전 한 장 + 번들 + 보강 안내
### ➡️ 다음 단계: 귀가 후 #12 plan-reinforce·#9 분기 점검으로
```

## 원칙
- **(d)에서 반드시 확정을 기다린다.** 통합 제시와 최종 문서 굽기 사이에 목사의 교회명/날짜/문장 확정 HITL이 있다.
- **전사하되 재생산하지 않는다** — 앞 산출물에 없는 내용을 만들지 않는다(전 섹션).
- **다 확정돼야 묶는다** — 미확정 산출물은 멈추고 앞 단계로(garbage-in 차단).
- **청중별로 번역한다** — 당회=요약·결정 / 성도=초청·은혜.
- **끝이 아니라 시작** — 보강 안내로 #12·#9에 잇는다.
- fidelity-guard 실패 시 (c)에 위반 노출, 해당 분석 재실행(임의 보정 금지).
```
