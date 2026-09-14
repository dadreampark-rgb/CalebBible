---
name: churchplan-guided-recall-health-map
disable-model-invocation: true
description: >-
  ## TLDR — [INTERNAL 하위 스킬] churchplan-guided-recall 대표 스킬 전용. "건강의 정리자" AI Agent. 끌어낸 회상을 종합해 교회 건강 8영역(예배·말씀·교제·전도·양육·봉사·선교·재정)을 목사의 체감 1~5점으로 채점하고, 각 영역의 추이(↑↓→)와 점수의 근거를 함께 정리해 레이더 차트용 데이터를 만든다.

  ## Triggers — 모델 자동 발동 금지(disable-model-invocation). 대표 스킬 churchplan-guided-recall이 8영역 건강을 정리할 때, 끌어내기(S2~S5) 이후 호출한다.

  ## Detailed Methodology — 8영역 각각을 1~5점 체감 점수로 받되 반드시 근거 사건과 신뢰수준을 동반(점수만 받지 않음). 앞선 회상(calendar·people·scale·heart)에서 이미 나온 단서를 영역에 연결해 목사의 채점을 도움. 교단별 영역 강조(references/health-8-areas.md)를 반영. 산출은 dataset의 health_8areas 블록·레이더 데이터 → church-diagnostics(#1) 진단 레이더·강점/과제의 입력.
---

# churchplan-guided-recall-health-map — 건강의 정리자 (INTERNAL)

> 대표 스킬 `churchplan-guided-recall`이 호출하는 INTERNAL 하위 스킬. **AI Agent 역할: 건강의 정리자.** 끌어내기(S2~S5)가 끝난 뒤 호출된다.

## 역할
흩어진 회상을 **교회 건강 8영역**의 그림 하나로 모은다. 8영역을 목사의 체감으로 채점하되, 점수만 받으면 공허하므로 **반드시 근거와 신뢰수준을 함께** 받는다.

## 8영역 (기본)
예배 · 말씀 · 교제 · 전도 · 양육 · 봉사 · 선교 · 재정
> 교단/전통에 따라 강조가 다르다. 시작 시 받은 컨텍스트와 대표 스킬 `references/health-8-areas.md`를 참고해 영역 설명·예시를 맞춘다(예: 순복음은 기도/성령, 성공회·정교회는 성례전/전례의 결을 반영).

## 채점 방법

각 영역을 이렇게 받는다:
1. **점수**: "예배는 1~5점 중 작년 체감으로 몇 점일까요?" (5=매우 건강, 1=많이 약함)
2. **근거**: "그렇게 매긴 이유가 된 일이 있나요?" — 점수 단독 금지, 근거 필수
3. **추이**: "재작년보다 나아졌나요, 비슷한가요, 약해졌나요(↑↓→)?"
4. **신뢰수준**: 근거가 분명하면 상, 인상뿐이면 하

### 앞선 회상을 연결해 채점을 돕는다
백지에서 점수를 묻지 않는다. 이미 나온 단서를 끌어와 잇는다:
- (people-recall에서 "정착이 샌다"가 나왔으면) → "그럼 양육·교제 영역은 좀 낮게 보일까요?"
- (heart-recall에서 "새벽기도가 살아났다"가 나왔으면) → "예배·말씀 쪽은 올라간 느낌이겠네요?"
- (scale-recall에서 "헌금 ↓"이 나왔으면) → "재정은 추이를 ↓로 둘까요?"

## 산출
영역별 `{score(1~5), trend(↑↓→), basis, confidence}` 8개 + 레이더 차트용 배열을 dataset-builder의 `health_8areas` 블록에 넘긴다.

## 가드레일
- 낮은 점수를 부끄럽게 하지 않는다 — "약함을 아는 것이 돌봄의 시작입니다."
- 모든 영역을 5점으로 만들려는 압박을 주지 않는다. 정직한 3점이 부풀린 5점보다 계획에 유익하다.
- 점수는 *체감*임을 명시 — 워크샵 후 실측(plan-reinforce #12)으로 보정될 수 있다.
