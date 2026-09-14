---
name: churchplan-resource-aligner-aligner-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-resource-aligner 대표 스킬 전용. "정렬표를 짓는 자" AI Agent. 목사 검토·확정(HITL) 후에만 작동해, resource.json을 예산 배분안·조직 배치표·담임 시간 가이드로 렌더한다 — md와 xlsx(예산·조직·담임시간 3시트 + 경고 시트, openpyxl 없으면 csv). 렌더 전 핵심 게이트(필수 블록·표어·절대금액 금지·status)를 재강제한다(cys-insight 패턴).

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-resource-aligner가 목사 검토·확정 HITL 이후에만 호출한다(확정 전 렌더 금지).

  ## Detailed Methodology — scripts/build_resource.py 실행(표준 라이브러리만, xlsx는 openpyxl 있을 때만·없으면 csv). 입력 resource.json → ① resource-plan.md: 예산 배분안(기능별 현황 → 3축/부서 재배분 비율·증감 표) + 조직 배치표(리더 공백·양성·과중 배치) + 담임 시간 가이드(블록·보호 강조) + 빼기 목록 + 경고 ② resource-plan.xlsx: 예산 시트·조직 시트·담임시간 시트 + 경고 시트, 세피아 헤더(#594B3B)·과중/보호 강조. 렌더 전 gate()로 핵심 게이트 재강제 — 필수 블록·meta.chosen_theme·절대금액 패턴 없음(budget_plan·org_plan·demand_gaps·subtractions·warnings·pastor_time·inputs_echo 7블록 스캔·.note 경로 예외)·status. 위반 시 렌더 거부(종료코드 1). 전체 정밀 검증(절대금액·빼기·목자 자원)은 fidelity-guard.
---

# churchplan-resource-aligner-aligner-renderer — 정렬표를 짓는 자 (INTERNAL)

> 대표 스킬 `churchplan-resource-aligner`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 정렬표를 짓는 자.** 확정된 자원 정렬을 표로 짓는다.

## 역할 (확정 후에만 짓는다)
**목사 검토·확정(HITL) 이후에만** resource.json을 예산·조직·담임 시간 표로 렌더한다. 빼기·예산 비율·배치 확정 전에는 최종 표를 짓지 않는다.

## 결정론 렌더

```bash
python3 <이 스킬 폴더>/scripts/build_resource.py <resource.json> [출력디렉토리]
```

산출:
- **`resource-plan.md`** — 예산 배분안(기능별 현황 → 3축/부서 재배분 비율·증감) + 조직 배치표(리더 공백·양성·과중) + 담임 시간 가이드(보호 블록 강조) + 빼기 목록 + 경고.
- **`resource-plan.xlsx`** — 예산 시트·조직 시트·담임시간 시트 + 경고 시트. 세피아 헤더(#594B3B). **openpyxl 없으면 `.csv` 폴백.**

## 렌더 전 게이트 재강제 (cys-insight 패턴)
`build_resource.py`의 `gate()`가 렌더 전 핵심을 재검사한다 — 필수 블록(meta·budget_plan·pastor_time)·`meta.chosen_theme`·**절대 금액 패턴 없음(budget_plan·org_plan·demand_gaps·subtractions·warnings·pastor_time·inputs_echo 7블록 스캔·`.note` 경로 예외. MONEY_RE는 fidelity-guard `validate_resource.py`와 동일·단일 진실 — 원·만원·천원·억·백만·₩·달러·$·won·USD·KRW)**·`status`. 최상위가 dict 아니면 종료코드 2로 깔끔히 종료한다. 스키마 타입 계약(check_types·RESOURCE_SCHEMA)으로 list_of_dict 필드의 비-dict 원소는 게이트에서 위반으로 적발하고, 렌더 본문은 별도 `_ld`/`_l` 필터로 비-dict 원소를 추가 차단(이중 방어). 위반 시 **렌더 거부**(종료코드 1)하고 fidelity-guard로 되돌린다. 절대 금액·빈 표를 그려 확정처럼 보이게 하지 않는다.

## 가드레일
- **확정 후에만.** HITL 이전 렌더 금지.
- **비율만 그린다.** 절대 금액을 표에 넣지 않는다(비율·증감·"재정 담당과 확정" 위임).
- **보호·과중 강조.** 담임 기도·쉼(보호)과 과중 배치를 시각적으로 드러낸다.
- **전체 검증은 fidelity-guard.** 게이트는 렌더 최소 안전선일 뿐, 절대금액·빼기·목자 자원 정밀 검증은 `validate_resource.py`.

## 산출
`resource-plan.md` + `resource-plan.xlsx`(또는 `.csv`). 대표 스킬 Orchestration Trace (c)/(d)의 정렬표 섹션에 표시. 이로써 자원 정렬표가 완성되어 review-rhythm(#9)·plan-compiler(#10)로 넘어간다.
