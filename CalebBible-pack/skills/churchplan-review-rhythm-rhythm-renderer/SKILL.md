---
name: churchplan-review-rhythm-rhythm-renderer
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-review-rhythm 대표 스킬 전용. "점검표를 짓는 자" AI Agent. 목사 확정(HITL) 후의 review.json을 받아 점검 스코어카드·월간 점검표를 html + xlsx로 렌더한다(scripts/build_review.py). 렌더 전 핵심 게이트를 재강제한다(cys-insight 패턴) — 필수 블록·표어·미래값 둔갑 금지·반기 수정일·status. 위반 시 렌더 거부. xlsx는 openpyxl 있으면 쓰고 없으면 csv 폴백.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-review-rhythm이 목사 검토·확정 HITL 이후에만 호출한다(확정 전 렌더 금지).

  ## Detailed Methodology — 입력: 확정된 review.json. scripts/build_review.py가 ① review-scorecard.html(분기 신호등 카드 4분기 — 색은 점검 시점 빈칸·돌봄 frame·월간 5분 점검·빨강 대응·연간 일정·반기 수정일 강조) ② review-rhythm.xlsx(분기 스코어카드 시트·월간 점검표 시트·점검 일정 시트, openpyxl 없으면 csv)를 만든다. 렌더 전 게이트 재강제: 필수 블록(meta·scorecard·schedule)·meta.chosen_theme·status∈{제안,확정}·미래값 둔갑(점검 전 status 채워짐)·반기 수정일(midyear_revision official) 위반 시 렌더 거부(종료코드 1). 전체 정밀 검증(돌봄 프레이밍·상속 충실)은 fidelity-guard의 validate_review.py가 맡는다. xlsx 헤더 세피아 #594B3B. 표준 라이브러리만(xlsx는 openpyxl 있을 때만).
---

# churchplan-review-rhythm-rhythm-renderer — 점검표를 짓는 자 (INTERNAL)

> 대표 스킬 `churchplan-review-rhythm`이 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 점검표를 짓는 자.** 확정된 점검 리듬을 손에 잡히는 스코어카드·월간표로 만든다.

## 역할 (확정 후 렌더 — html + xlsx)
**목사 확정(HITL) 후에만** 작동한다. review.json을 받아 점검 스코어카드·월간 점검표를 html + xlsx로 렌더한다.

## 입력
- 확정된 `review.json`(`status:"확정"`·`confirmed` 채워짐)
- 형식: 대표 스킬 `references/review-schema.md`

## 렌더 (결정론 스크립트)

```bash
python3 <이 스킬 폴더>/scripts/build_review.py <review.json> [출력디렉토리]
```

산출:
- `review-scorecard.html` — 분기 신호등 카드(1Q~4Q, 색은 점검 시점에 채울 빈칸)·돌봄 frame·월간 5분 점검·빨강 대응·연간 일정(반기 수정일 강조)
- `review-rhythm.xlsx` — 분기 스코어카드 시트·월간 점검표 시트·점검 일정 시트(openpyxl 없으면 `.csv` 폴백)

## 렌더 전 게이트 재강제 (cys-insight 패턴)
렌더 직전 핵심만 재확인하고, 위반 시 **렌더 거부**(종료코드 1):
- 필수 블록(`meta`·`scorecard`·`schedule`) + `meta.chosen_theme` + `status` ∈ {제안,확정}
- **미래값 둔갑 금지**: 확정(`confirmed`) 전인데 분기 점검행 `status`가 채워져 있으면 거부
- **반기 수정일**: `schedule.midyear_revision`(official) 누락 시 거부

전체 정밀 검증(돌봄 프레이밍·상속 충실·signal_only)은 fidelity-guard의 `validate_review.py`가 맡는다.

## 가드레일
- **확정 후에만 렌더**: 목사 검토·확정 HITL 전에는 작동하지 않는다.
- **미래값 비움 보존**: 신호등 색·진행값은 빈칸으로 렌더(점검 시점에 채움).
- **자기완결**: 표준 라이브러리만. xlsx는 openpyxl 있을 때만, 없으면 csv.

## 산출
점검 스코어카드·월간 점검표 파일(html + xlsx/csv). 대표 스킬 Orchestration Trace (c)·(d) 섹션에 경로 표시.
