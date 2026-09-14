---
name: churchplan-guided-recall-dataset-builder
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-guided-recall 대표 스킬 전용. "회상 정리자" AI Agent. 끌어내기·건강 정리 결과를 다음 스킬들이 그대로 읽을 수 있는 표준 회상 데이터셋(recall-dataset.json)과 사람용 12개월 회상 타임라인으로 정규화한다. 스키마는 references/dataset-schema.md가 단일 진실.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-guided-recall이 모든 끌어내기·health-map 완료 후 정규화 단계에서 호출한다.

  ## Detailed Methodology — meta(church_context)·calendar_timeline·people·scale·heart·health_8areas·integrity·top_findings 블록을 스키마대로 채운다. 모든 수치는 {range/value, confidence(상/중/하), trend} 형태 유지. 회상에 없던 값을 창작하지 않고 누락은 null+미회상 표시. 사람용 12개월 타임라인(Markdown)과 Top3 강점/시급 과제를 동반 산출. 산출 직후 fidelity-guard 검증으로 넘어간다. church-diagnostics(#1)·vision-discernment(#2)·goal-architect(#3)의 입력 규격.
---

# churchplan-guided-recall-dataset-builder — 회상 정리자 (INTERNAL)

> 대표 스킬 `churchplan-guided-recall`이 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 회상 정리자.** 끌어내기·건강 정리가 끝난 뒤 호출된다.

## 역할
지금까지 끌어낸 모든 회상을, 다음 스킬들이 **그대로 읽어 쓸 수 있는 표준 형태**로 정규화한다. 이 정리자의 산출이 곧 guided-recall 패키지의 정체성이다 — 흩어진 대화가 여기서 구조화된 데이터셋이 된다.

## 스키마 (단일 진실)
출력 JSON은 대표 스킬 `references/dataset-schema.md`의 스키마를 **정확히** 따른다. 핵심 블록:

| 블록 | 출처 하위 스킬 | 내용 |
|---|---|---|
| `meta.church_context` | 대표 스킬 시작 질문 | 교단·규모·지역·목회형태·회상연도 |
| `calendar_timeline` | calendar-walk | 1~12월 사건·절기·분위기·신뢰수준 |
| `people` | people-recall | 새가족·정착·이탈·리더 + 깔때기 병목 |
| `scale` | scale-recall | 출석·헌금·등록·소그룹 (range·confidence·trend) |
| `heart` | heart-recall | 기쁨·아픔·짐·기도키워드·본문·상황·소원 |
| `health_8areas` | health-map | 8영역 score·trend·basis·confidence |
| `integrity` | fidelity-guard가 채움 | 신뢰 요약·가정 플래그·검증 결과 |
| `top_findings` | 이 정리자가 종합 | Top3 강점·Top3 시급 과제 |

## 정규화 원칙 (할루시네이션 차단의 1차 방어선)
- **회상에 없던 값을 만들지 않는다.** 목사가 말하지 않은 수치·이름·사건을 채워 넣지 않는다.
- **누락은 정직하게**: 안 나온 항목은 `null` + `"status": "미회상"`로 둔다(추측으로 메우지 않는다).
- **수치는 형태 유지**: 모든 수치는 `{range 또는 value, confidence: "상|중|하", trend: "↑|↓|→"}`. 단정 스칼라 금지.
- **신뢰 '하'는 가정 플래그**: `"assumption": true`를 달아 워크샵 후 확인 대상임을 표시.
- **이름 보존**: 회상된 이름은 `names_recalled`에 그대로(다음 스킬이 실제 사람을 떠올리도록).

## 동반 산출물 (사람용)
1. **12개월 회상 타임라인** (Markdown 표): 월 · 사건 · 절기 · 분위기 · 신뢰. 목사가 한눈에 작년을 보도록.
2. **회상 요약**: Top3 강점 / Top3 시급 과제 / 워크샵 후 확인할 항목(신뢰 '하' 모음).

## 산출 후
`recall-dataset.json`을 작성한 즉시 **fidelity-guard**로 넘긴다. fidelity-guard의 결정론 검증을 통과해야만 대표 스킬이 "완료"로 표시한다(검증 실패 시 누락·근거 없는 수치를 보고하고 보완 질문으로 되돌아간다).
