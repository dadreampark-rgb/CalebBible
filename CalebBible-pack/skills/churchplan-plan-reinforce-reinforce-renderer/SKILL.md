---
name: churchplan-plan-reinforce-reinforce-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-reinforce 대표 스킬 전용. "보정본을 굽는 자" AI Agent. 목사 확정(HITL) 후의 reinforce.json을 받아 보정 진단 대시보드(추정 vs 실측 비교·xlsx)와 신년 목회계획서 v2(보정 델타 문서·docx)를 자기완결 렌더한다(scripts/build_reinforce.py — openpyxl·python-docx). 렌더 전 핵심 게이트 재강제(필수 블록·status·실측 날조[actual_source]·추정 보존[estimate]). 위반 시 렌더 거부. 라이브러리 없으면 폴백(xlsx→csv·docx→md).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-reinforce가 목사 검토·확정 HITL 이후에만 호출한다(확정 전 렌더 금지).

  ## Detailed Methodology — 입력: 확정된 reinforce.json. scripts/build_reinforce.py가 ① reinforce-dashboard.xlsx(추정 vs 실측 비교 시트[항목·추정·실측·출처·delta·mismatch·status]+이월/갱신 시트, openpyxl 없으면 csv) ② plan-v2.docx(보정 델타 문서·python-docx·추정→실측 이력 + 갱신된 진단/목표/예산 + 새 병목 + #9 이월)를 만든다. 렌더 전 게이트 재강제: 필수 블록(meta·reconciliations)·status∈{제안,확정}·실측 날조(status=실측교체인데 actual_source 없으면 거부)·추정 보존(estimate 없으면 거부) 위반 시 렌더 거부(종료코드 1). 전체 정밀 검증(부족 비난·mismatch 조정 연결)은 fidelity-guard의 validate_reinforce.py가 맡는다. 전체 계획서 재조립은 #10(plan-compiler)·#12 v2는 보정 델타까지. 라이브러리 없으면 폴백.
---

# churchplan-plan-reinforce-reinforce-renderer — 보정본을 굽는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-reinforce`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 보정본을 굽는 자.** 추정과 실측을 나란히 담은 보정본을 손에 잡히게 만든다.

## 역할 (확정 후 렌더 — xlsx + docx)
**목사 확정(HITL) 후에만** 작동한다. reinforce.json을 받아 보정 대시보드(xlsx)와 계획서 v2(docx)를 자기완결로 렌더한다.

## 입력
- 확정된 `reinforce.json`(`status:"확정"`·`confirmed` 채워짐)
- 형식: 대표 스킬 `references/reinforce-schema.md`

## 렌더 (결정론 스크립트)

```bash
python3 <이 스킬 폴더>/scripts/build_reinforce.py <reinforce.json> [출력디렉토리]
```

산출:
- `reinforce-dashboard.xlsx` — 추정 vs 실측 비교(항목·추정·실측·출처·delta·mismatch·status) + 이월/갱신 시트(openpyxl 없으면 `.csv`)
- `plan-v2.docx` — 보정 델타 문서(추정→실측 이력 + 갱신된 진단/목표/예산 + 새 병목 + #9 이월)

## 렌더 전 게이트 재강제 (cys-insight 패턴)
렌더 직전 핵심만 재확인하고, 위반 시 **렌더 거부**(종료코드 1):
- 필수 블록(`meta`·`reconciliations`) + `status` ∈ {제안,확정}
- **실측 날조**: `reconciliations[].status:"실측교체"`인데 `actual_source`가 없으면 거부
- **추정 보존**: `reconciliations[].estimate`가 없으면 거부(이력 상실)

전체 정밀 검증(부족 비난·mismatch 조정)은 fidelity-guard의 `validate_reinforce.py`가 맡는다.

## 가드레일
- **확정 후에만 렌더**: 목사 검토·확정 HITL 전에는 작동하지 않는다.
- **추정·실측 시각 구분**: 대시보드에 추정과 실측을 나란히(투명성).
- **델타까지**: 전체 계획서 재조립은 #10. v2는 보정 델타 문서.

## 산출
보정 대시보드(xlsx) + 계획서 v2(docx). 대표 스킬 Orchestration Trace (c)·(d) 섹션에 경로 표시.
