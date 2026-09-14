---
name: churchplan-diagnostics-health-radar
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-diagnostics 대표 스킬 전용. "여덟 영역을 비추는 자" AI Agent. 회상 데이터셋의 8영역(예배·말씀·교제·전도·양육·봉사·선교·재정) 체감 점수를 레이더 차트 데이터로 비추고, 강한 영역과 돌봄이 필요한 영역을 식별한다. 낮은 점수는 실패가 아니라 돌봄점으로 비춘다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-diagnostics가 8영역 건강 비추기 단계에서 호출한다.

  ## Detailed Methodology — recall-dataset.json의 health_8areas 블록을 읽어 8영역 각각의 score(1~5)·trend·basis·confidence를 보존한 radar 데이터 생성. 분류는 결정론 스크립트(scripts/classify_health.py)로 확정 — score>=4 또는 ↑=strong, score<=2 또는 ↓=needs_care(정죄 아닌 돌봄 프레이밍). 점수는 회상에서 그대로 전사(재계산 금지), 미회상 영역은 status:미회상 보존. 산출은 diagnosis.json의 health_radar 블록 → dashboard-builder가 inline SVG 레이더로 렌더.
---

# churchplan-diagnostics-health-radar — 여덟 영역을 비추는 자 (INTERNAL)

> 대표 스킬 `churchplan-diagnostics`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 여덟 영역을 비추는 자.**

## 역할
교회의 건강을 **여덟 면을 가진 거울**로 한눈에 비춘다. 한쪽만 보면 놓치는 균형을, 레이더 하나로 보게 한다.

## 입력
`recall-dataset.json`의 `health_8areas` 블록 — 예배·말씀·교제·전도·양육·봉사·선교·재정 각각의 `{score(1~5), trend, basis, confidence}`.

## 비추는 방법
- 8영역 점수를 **그대로 보존**(재계산·조정 금지 — 목사의 체감이 원자료).
- 각 영역에 trend(↑↓→)와 basis(근거)를 동반. 근거 없는 점수는 dashboard에 경고 표시.
- confidence 보존. 신뢰 '하' 영역은 배지로 흐리게.
- 미회상 영역은 `null`로 비워 둔다(0점으로 채우지 않는다 — 0점과 미회상은 다르다).

## 강/돌봄점 분류 (정죄 아닌 돌봄) — 결정론 스크립트로 확정
점수→분류는 순수 함수다. LLM 자연어 추론으로 분류하지 말고 **결정론 스크립트**를 호출해
오분류·누락을 차단한다(점수는 회상에서 그대로 전사, 분류는 비교연산자로 확정).

```bash
python3 <이 스킬 폴더>/scripts/classify_health.py <recall-dataset.json>
```
스크립트가 `recall.health_8areas`를 읽어 `health_radar` 블록(areas·strong·needs_care)을 산출:
- **strong**: `score>=4` 또는 `trend=='↑'` → "살아 있는 곳, 감사할 곳"
- **needs_care**: `score<=2` 또는 `trend=='↓'` → **"약한 영역"이 아니라 "돌봄이 닿을 영역"**으로 명명
- score·trend·basis·confidence는 회상 원본 그대로 복사(재계산 금지). 미회상 영역은 `status:'미회상'` 보존.

"모든 영역 5점"을 이상으로 제시하지 않는다. 정직한 3점이 건강의 출발. LLM은 라벨 한글화만 담당한다.

## 산출
`diagnosis.json`의 `health_radar` 블록:
```json
{"health_radar":{
  "areas":[
    {"area":"예배","score":4,"trend":"↑","basis":"새벽기도 회복","confidence":"중"},
    {"area":"전도","score":2,"trend":"↓","basis":"전도 행사 무산","confidence":"상"}
    /* ... 8영역 ... */
  ],
  "strong":["예배"],
  "needs_care":["전도","양육","재정"]
}}
```
dashboard-builder가 이를 *inline SVG 레이더 차트*로 렌더(8축, 신뢰 '하' 영역은 점선). 형식은 대표 스킬 `references/diagnostics-schema.md`.
