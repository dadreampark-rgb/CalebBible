---
name: churchplan-diagnostics-findings-synthesis
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-diagnostics 대표 스킬 전용. "강점과 돌봄점을 모으는 자" AI Agent. 4개 분석(흐름·깔때기·8영역·지난마음)을 한데 모아, 병목의 방향을 진단의 첫 문장으로 세우고 Top3 강점·Top3 돌봄점(시급 과제)·귀가 후 확인 목록을 도출한다. 거울이 보여준 것을 목사가 붙들 세 가지로 압축한다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-diagnostics가 분석 4종 완료 후 종합 단계에서 호출한다.

  ## Detailed Methodology — diagnosis.json의 trend·funnel·health_radar·resolution_review를 통합. (1)funnel.bottleneck_direction을 bottleneck_headline 첫 문장으로 (4)신뢰 '하'·assumption·미회상 항목 전부를 verify_after_workshop로 모음 — (1)·(4)는 결정론 스크립트(scripts/collect_verify.py)로 자동 확정(누락 차단). (2)strong 영역+살아있는 흐름에서 strengths_top3 (3)needs_care 영역+병목+↓흐름에서 needs_care_top3(시급 과제를 돌봄점으로)는 회상 근거 내 LLM 압축. 과장·거짓 확신 금지(회상 근거 내에서만). 산출은 diagnosis.json의 findings 블록 → dashboard 상단·#2·#3 입력.
---

# churchplan-diagnostics-findings-synthesis — 강점과 돌봄점을 모으는 자 (INTERNAL)

> 대표 스킬 `churchplan-diagnostics`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 강점과 돌봄점을 모으는 자.** 분석 4종이 끝난 뒤 호출된다.

## 역할
거울이 비춘 네 면(흐름·깔때기·8영역·지난마음)을, 목사가 손에 쥘 **세 가지**로 모은다. 진단의 가치는 데이터의 양이 아니라 *붙들 것의 선명함*이다.

## 입력
`diagnosis.json`의 `trend`·`funnel`·`health_radar`·`resolution_review` (S1~S4 산출).

## 종합 방법

### 0) 결정론 환원 — bottleneck_headline + verify_after_workshop 자동 생성
1)·4)는 순수 복사·필터링이므로 LLM 추론 대신 **결정론 스크립트**로 확정한다(누락 차단).

```bash
python3 <이 스킬 폴더>/scripts/collect_verify.py <diagnosis.json>
```
산출 `{bottleneck_headline, verify_after_workshop}`을 findings에 그대로 옮긴다:
- `bottleneck_headline` = `funnel.bottleneck_direction` 직접 복사.
- `verify_after_workshop` = trend·funnel·health_radar·resolution_review 전 항목 중 `confidence=='하'`·`assumption==true`·`status=='미회상'`을 **전부** 수집.

LLM은 아래 2)·3)(Top3 강점·돌봄점 서사 압축)만 회상 근거 안에서 담당한다.

### 1) 진단의 첫 문장 = 병목 방향
`funnel.bottleneck_direction`을 그대로 **bottleneck_headline**으로 올린다(위 스크립트가 자동 복사). 이것이 진단 전체를 여는 한 문장이다(문서 01: 병목의 방향이 진단의 핵심).
> 예: "올해 우리 교회 진단의 첫 문장 — *유입은 있으나 정착에서 샌다.*"

### 2) Top 3 강점 (감사할 곳)
`health_radar.strong` + 살아 있는 흐름(↑) + 자란 다짐에서 셋. 회상 근거를 한 줄씩 단다(근거 없는 칭찬 금지).

### 3) Top 3 돌봄점 (= 시급 과제, 돌봄의 언어로)
`health_radar.needs_care` + `funnel.bottleneck` + ↓ 흐름에서 가장 시급한 셋. **"시급 과제"를 "가장 먼저 돌봄이 필요한 곳"으로** 명명한다(정죄 아닌 돌봄).

### 4) 귀가 후 확인 목록
모든 블록에서 신뢰 '하'·`assumption:true`·`status:미회상`을 모아 **verify_after_workshop**로 — 위 0) 스크립트가 결정론적으로 수집한다. 거울의 겸손 — 흐린 곳을 정직히 표시(plan-reinforce #12로 이월).

## 할루시네이션 가드레일 (ANCHOR #2)
- 회상 근거 안에서만 종합한다. "폭발적 부흥" 같은 부푼 서술 금지.
- 강점/돌봄점 각 항목은 어느 분석 블록에서 왔는지 추적 가능해야 한다.

## 산출
`diagnosis.json`의 `findings` 블록:
```json
{"findings":{
  "bottleneck_headline":"유입은 있으나 정착에서 샌다 (6개월 내 이탈)",
  "strengths_top3":[{"text":"예배·기도 회복세","basis":"health.예배 4↑·새벽기도"}],
  "needs_care_top3":[{"text":"정착 깔때기 누수","basis":"funnel.정착 샘"}],
  "verify_after_workshop":["이탈자 정확 수(교적부)","헌금 실제 증감(결산서)","재정 영역 실측"]
}}
```
형식은 대표 스킬 `references/diagnostics-schema.md`.
