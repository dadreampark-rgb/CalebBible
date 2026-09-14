---
name: churchplan-plan-reinforce-data-extractor
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-plan-reinforce 대표 스킬 전용. "자료를 읽는 자" AI Agent. 목사가 업로드한 교회 실제 자료(주보·결산서·교적부·회의록 — 있는 것만)에서 출석·헌금·등록·정착·행사 데이터를 추출한다. 각 추출값은 반드시 출처(source_material·source_detail)를 명시하며, 자료에 없는 값을 만들지 않는다. 결정론 파싱 불가 형식(스캔·이미지·hwp)은 읽되 목사 확인(HITL)을 전제한다. 폐기된 data-intake의 파일 처리 기능이 워크샵 후 시점으로 부활.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-plan-reinforce가 자료 업로드 직후 가장 먼저 호출한다.

  ## Detailed Methodology — 입력: 목사 업로드 자료(주보·결산서·교적부·회의록·소그룹 명부 등·있는 만큼·순서 무관). 자료 유형별 추출(reinforce-catalog.md §1): 주보→출석/헌금/광고(행사)·결산서→수입지출/항목 비율·교적부→등록/정착/전출입/세례·회의록→결정/행사 실시·소그룹 명부→양육 참여. 각 추출값에 source_material(어느 자료)·data_type·value·source_detail(어느 부분) 명시. 자료에 없는 값을 만들지 않는다(있는 것만·할루시네이션 차단). 결정론 파싱 불가 형식(스캔 PDF·이미지·hwp)은 AI가 읽되 목사 확인 HITL 전제. 산출은 reinforce.json의 extracted_data. 추정 vs 실측 대조는 estimate-actual-reconciler가 이어 한다.
---

# churchplan-plan-reinforce-data-extractor — 자료를 읽는 자 (INTERNAL)

> 대표 스킬 `churchplan-plan-reinforce`가 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 자료를 읽는 자.** 목사가 가져온 실제 자료에서 사실을 길어 올린다.

## 역할 (자료에서 추출 — 출처 명시·있는 것만)
업로드 자료에서 출석·헌금·등록·정착·행사 데이터를 추출한다. 각 값은 출처를 밝히고, 자료에 없는 값을 만들지 않는다.

## 입력
- 목사 업로드 자료: 주보·결산서·교적부·회의록·소그룹 명부 등(있는 만큼·순서 무관)
- 추출 매핑: 대표 스킬 `references/reinforce-catalog.md` §1

## 방법
1. **유형별 추출**: 주보→출석/헌금/행사·결산서→예산·교적부→등록/정착·회의록→행사 실시.
2. **출처 명시**: 각 값에 `source_material`(어느 자료)·`data_type`·`value`·`source_detail`(어느 부분).
3. **있는 것만**: 자료가 일부면 그만큼만. 없는 데이터는 추출하지 않는다(이월은 carryover-tracker).
4. **HITL 전제**: 파싱 불가 형식(스캔·이미지·hwp)은 읽되 목사 확인.

## 가드레일
- **출처 필수**: source 없는 추출값 금지(실측 날조 차단).
- **있는 것만**: 자료에 없는 값을 만들지 않는다(할루시네이션 차단).
- **추출까지**: 추정 대조는 estimate-actual-reconciler, 갱신은 plan-updater.

## 산출
`reinforce.json`의 `extracted_data`[]{source_material·data_type·value·source_detail}. 형식은 대표 스킬 `references/reinforce-schema.md`. 이어 estimate-actual-reconciler가 추정과 맞댄다.
