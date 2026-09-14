---
name: churchplan-diagnostics-dashboard-builder
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-diagnostics 대표 스킬 전용. "한 장 거울을 닦는 자" AI Agent. 종합된 diagnosis.json을 담임목사가 한눈에 보는 한 장짜리 HTML 진단 대시보드와 xlsx 정리표로 결정론 스크립트가 렌더한다. 신뢰수준 배지·범위 오차띠·8영역 inline SVG 레이더·따뜻한 팔레트로, 추정이 사실로 둔갑하지 않게 그린다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-diagnostics가 종합 후 렌더링 단계에서 호출한다.

  ## Detailed Methodology — scripts/build_dashboard.py가 diagnosis.json(+recall-dataset.json)을 입력받아 diagnostics-dashboard.html과 diagnostics.xlsx 동시 산출. LLM이 차트를 그리지 않아(스크립트 결정론) 할루시네이션 차단. 렌더 규칙(references/dashboard-design.md): 모든 수치에 신뢰 배지, 범위는 오차 띠(점값 막대 금지), 신뢰 '하'는 흐리게/점선, 낮은 점수는 경보색 아닌 따뜻한 저채도. 상단에 병목 헤드라인, 8영역 SVG 레이더, 흐름 카드, 깔때기 그림, 강점/돌봄점, 귀가 후 확인 목록.
---

# churchplan-diagnostics-dashboard-builder — 한 장 거울을 닦는 자 (INTERNAL)

> 대표 스킬 `churchplan-diagnostics`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 한 장 거울을 닦는 자.** 종합(S5)이 끝난 뒤 호출된다.

## 역할
지금까지 비춘 모든 것을 **담임목사가 한눈에 들여다보는 한 장의 거울**로 닦아 낸다. 외부 컨설턴트가 며칠 걸려 만드는 진단표를, 신뢰수준이 정직하게 표기된 한 장으로.

## 결정론 렌더링 (할루시네이션 차단)
차트와 표는 **LLM이 그리지 않는다.** 스크립트가 `diagnosis.json`을 받아 결정론적으로 그린다 — 그래야 없던 숫자·없던 막대가 생기지 않는다.

```bash
python3 <이 스킬 폴더>/scripts/build_dashboard.py <diagnosis.json> [recall-dataset.json] --out <출력 디렉터리>
```
산출: `diagnostics-dashboard.html` + `diagnostics.xlsx`

**렌더 전 게이트 재강제(검증기-렌더러 parity).** 스크립트는 렌더 직전 핵심 정직성 게이트를
재강제한다 — 필수 블록 형식·점값 둔갑(신뢰 '하'에 정밀 point)·병목/헤드라인 누락·범위형/score
오류·근거 추적성. 위반이 하나라도 있으면 **렌더를 거부(종료코드 1)** 하여 거짓 정밀한 거울이
산출되지 않게 한다. 회상 대조 등 전체 정밀 검증은 아래 `fidelity-guard`가 맡는다(의도적 비대칭).

## 렌더 규칙 (추정 충실도 — 생명) — `references/dashboard-design.md` 준수
- **모든 수치에 신뢰 배지**(상/중/하). 배지 없는 수치 렌더 금지.
- **범위는 오차 띠로.** `range:[120,140]`을 점값 막대(131)로 그리지 않는다 — 거짓 정밀 금지.
- **신뢰 '하'는 흐리게**(저채도/점선) + "추정" 표시. 확정처럼 또렷하게 그리지 않는다.
- **미회상은 빈칸**(0 아님)으로, "—" + "워크샵 후 확인".
- **8영역 레이더**: inline SVG(외부 라이브러리 의존 없음, 인쇄 안정). 신뢰 '하' 축은 점선.

## 돌봄의 팔레트 (DNA)
- 낮은 점수·새는 깔때기를 **경보색(쨍한 빨강)으로 칠하지 않는다.** 따뜻한 저채도(흙빛·차분한 주황)로 "돌봄점"임을 표시.
- 상단 헤드라인은 `findings.bottleneck_headline`(병목 방향 한 문장).
- 톤: 성적표가 아니라 목양 거울. 색·여백·문구가 정죄가 아닌 돌봄을 전한다.

## 레이아웃 (한 장)
1. 헤더: 교회명·회상연도·"추정 기반 진단 — 신뢰수준 표기" 고지
2. 병목 헤드라인(큰 글씨)
3. 8영역 레이더(SVG) | 흐름 카드(오차 띠+배지)
4. 깔때기 그림(단계별 sense)
5. Top3 강점 | Top3 돌봄점
6. 귀가 후 확인 목록(신뢰 '하')
7. footer: 추정/실측 구분 범례

## 산출 후
`fidelity-guard`가 `diagnosis.json`을 검증한다(대시보드가 추정을 사실로 둔갑시켰는지 포함). 통과해야 대표 스킬이 "완료" 표시.
