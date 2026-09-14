#!/usr/bin/env python3
"""
validate_goals.py — churchplan-goal-architect 목표 결과(goals.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 목표 설계가 세 거짓을 흘리지 않게 지킨다.
  (1) 환원 — 영적 방향을 숫자로 바꿔치기(정성 없는 숫자) 또는 점검 불가의 영성(정량 없는 방향)
  (2) 근거 없음 — 진단·표어에 추적되지 않는 목표(garbage-in)
  (3) 허위 정밀 / 과욕 — 신뢰 낮은 기준선 위 점값 목표치, 담임 단독 역량을 넘는 목표 수
목사의 목표를 검증하는 것이 아니라, AI가 목표 설계를 오염시켰는지 검사한다.

사용:  python3 validate_goals.py <goals.json>
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bible_validator import validate_reference


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


AXES = {"영성", "전도", "양육"}
GOALS_PER_AXIS_MAX = 2          # 축당 핵심 목표 상한 (과욕 절제)
GOALS_TOTAL_MAX = 6             # 전체 핵심 목표 하드 상한 (3축 × 2)

# 점값 탐지: 숫자가 딱 박힌 단정값 (신뢰 '하' 기준선 위에서는 금지)
POINT_PAT = re.compile(r"\d")
# 완충어(범위·방향) — 하나라도 있으면 점값으로 보지 않음
SOFT_WORDS = ["수준", "약", "가량", "정도", "내외", "~", "±", "범위", "방향",
              "증가", "감소", "늘", "줄", "절반", "분의", "/", "→", "이상", "이하", "쯤", "안팎"]
# 측정 불가의 허위 정량 어휘 (셀 수 없는데 숫자를 붙인 것)
FAKE_QUANT_PAT = re.compile(r"(성령\s*충만|믿음|은혜|사랑|영성|거룩|헌신도)\s*\d+\s*(%|점|퍼센트)")


def is_point_value(target):
    """target이 점값(단정 숫자)인가 — 숫자가 있고 완충어가 없으면 점값."""
    if not target:
        return False
    t = str(target)
    if not POINT_PAT.search(t):
        return False
    return not any(w in t for w in SOFT_WORDS)


# 어절 토큰화 — 공백·구두점 제거 후 2자 이상 한글/영숫자 토큰 (bookwriting M6 어절 부분일치)
_TOKEN_PAT = re.compile(r"[가-힣A-Za-z0-9]{2,}")
# 구조 라벨 불용어 — 근거가 출처를 '인용'할 때 쓰는 범주명(표어·병목·마음 등).
# 내용이 아니라 라벨이므로 추적 대조에서 제외해야 지어낸 근거를 잡는다.
_LABEL_STOPWORDS = {"표어", "병목", "마음", "돌봄", "진단", "비전", "출처",
                    "근거", "에서", "나옴", "기반", "따라", "교회"}


def _tokens(text):
    return {t for t in _TOKEN_PAT.findall(str(text or "")) if t not in _LABEL_STOPWORDS}


def rationale_sources(inputs_echo):
    """inputs_echo의 실재 vision·diagnosis 값에서 추적 가능한 출처 토큰 집합."""
    inputs_echo = _d(inputs_echo)
    src_texts = []
    for key in ("chosen_theme", "bottleneck", "bottleneck_headline", "pastor_focus_axis"):
        v = inputs_echo.get(key)
        if v:
            src_texts.append(str(v))
    for n in _l(inputs_echo.get("needs_care")):
        if n:
            src_texts.append(str(n))
    toks = set()
    for t in src_texts:
        toks |= _tokens(t)
    return toks


def rationale_traced(rationale, src_tokens):
    """rationale이 실재 출처(src_tokens)에 추적되는가 — 한국어 조사·합성을 고려한 부분일치.

    bookwriting M6 어절 부분일치 패턴: 정확 토큰 일치가 아니라, rationale 토큰과
    출처 토큰이 서로를 부분 포함(2자 이상 공통 어간)하면 추적된 것으로 본다.
    예: 출처 '정착' ⊂ rationale '정착에서', 출처 '식탁에' ⊃ rationale '식탁'.
    """
    rat_toks = _tokens(rationale)
    if not rat_toks or not src_tokens:
        return False
    for rt in rat_toks:
        for st in src_tokens:
            # 2자 이상 어간이 한쪽이 다른 쪽에 포함되면 일치
            if len(rt) >= 2 and len(st) >= 2 and (rt in st or st in rt):
                return True
    return False


def validate(g):
    errors, warnings = [], []

    # 1. 스키마 필수 블록
    for blk in ("meta", "inputs_echo", "axes"):
        if blk not in g:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    # 1-b. 스키마-타입 필드가 비-dict/비-list로 오염되면 안전 환원 + 형식오류 등록(조용한 통과 금지).
    #      _d/_l이 런타임 crash는 막지만, 잘못된 컨테이너 타입은 schema 위반이므로 errors로도 1건 등록한다.
    for f in ("meta", "inputs_echo", "confirmed"):
        if f in g and g.get(f) is not None and not isinstance(g.get(f), dict):
            errors.append(f"[형식오류] 최상위 '{f}'가 객체(dict)가 아님 — 비-dict로 안전 환원")
    for f in ("axes", "keep_list", "stop_list", "warnings"):
        if f in g and not isinstance(g.get(f), list):
            errors.append(f"[형식오류] 최상위 '{f}'가 배열(list)이 아님 — 비-list로 안전 환원")
    # keep_list/stop_list 원소는 문자열, warnings 원소는 객체여야 함
    for f in ("keep_list", "stop_list"):
        for ei, el in enumerate(_l(g.get(f))):
            if isinstance(el, (dict, list)):
                errors.append(f"[형식오류] {f}[{ei}]가 문자열이 아님(dict/list) — 비-문자열 원소 제외")
    for ei, el in enumerate(_l(g.get("warnings"))):
        if not isinstance(el, dict):
            errors.append(f"[형식오류] warnings[{ei}]가 객체(dict)가 아님 — 비-dict 원소 제외")

    meta = _d(g.get("meta"))

    # 2. 표어 정합 — 표어 없이 목표 못 세운다
    chosen = meta.get("chosen_theme")
    if not chosen or not str(chosen).strip():
        errors.append("[표어미확정] meta.chosen_theme 비어 있음 — 표어를 먼저 확정하라(vision-discernment #2로)")

    # 3. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 4~7. 축·목표 수
    axes = _l(g.get("axes"))
    # 근거 추적 출처 토큰 (inputs_echo가 비면 추적 검사 skip)
    src_tokens = rationale_sources(g.get("inputs_echo"))
    seen_axes = []
    total_goals = 0
    for i, ax in enumerate(axes):
        if not isinstance(ax, dict):
            errors.append(f"[형식오류] axes[{i}]: 객체여야 함"); continue
        name = ax.get("axis")
        if name not in AXES:
            errors.append(f"[축오류] axes[{i}].axis '{name}' — 영성|전도|양육 여야 함")
        if name in seen_axes:
            errors.append(f"[축중복] '{name}' 축이 둘 이상")
        seen_axes.append(name)

        # goals는 schema상 배열 — truthy 비-list(문자열 등)면 [형식오류] 등록(조용한 축 소실 차단)
        if "goals" in ax and not isinstance(ax.get("goals"), list):
            errors.append(f"[형식오류] axes[{i}:{name}].goals가 배열(list)이 아님 — 비-list로 안전 환원")
        goals = _l(ax.get("goals"))
        if len(goals) > GOALS_PER_AXIS_MAX:
            errors.append(f"[과욕] '{name}' 축 목표 {len(goals)}개 — 축당 최대 {GOALS_PER_AXIS_MAX}개(더하기 전 빼기)")
        total_goals += len(goals)

        # 8. 각 목표 — 환원 차단의 핵심
        for j, goal in enumerate(goals):
            tag = f"axes[{i}:{name}].goals[{j}]"
            if not isinstance(goal, dict):
                errors.append(f"[형식오류] {tag}: 객체여야 함"); continue
            dg = goal.get("direction_goal")
            inds = _l(goal.get("indicators"))
            # 정성↔정량 한 쌍 강제
            if not dg or not str(dg).strip():
                errors.append(f"[환원-정성누락] {tag}: direction_goal 없음 — 숫자만 있는 목표 금지(방향이 머리다)")
            if not inds:
                errors.append(f"[환원-정량누락] {tag}: indicators 없음 — 정성 목표에 신호 지표 한 쌍 필수(점검 불가 방지)")
            # 근거 추적 — 비어있지 않음 + 실재 출처(표어·병목·돌봄점) 토큰 부분일치
            rat = goal.get("rationale")
            if not rat or not str(rat).strip():
                errors.append(f"[근거누락] {tag}: rationale 없음 — 표어·병목·마음 중 출처를 밝혀라(garbage-in 차단)")
            elif src_tokens and not rationale_traced(rat, src_tokens):
                errors.append(
                    f"[근거위장] {tag}: rationale가 실재 표어·병목·돌봄점 어느 것에도 추적되지 않음 "
                    f"(inputs_echo 키워드 미일치) — 지어낸 근거 금지(garbage-in 차단)")

            # 성경 본문 실재성 — scripture_link 정경 범위 결정론 검사
            sl = goal.get("scripture_link")
            if sl and str(sl).strip():
                ok, msg = validate_reference(str(sl))
                if not ok:
                    errors.append(f"[성경허위] {tag}.scripture_link '{sl}' — {msg}")

            # 지표별 검사
            for k, ind in enumerate(inds):
                itag = f"{tag}.indicators[{k}]"
                if not isinstance(ind, dict):
                    errors.append(f"[형식오류] {itag}: 객체여야 함"); continue
                if not ind.get("label"):
                    errors.append(f"[지표누락] {itag}.label 없음")
                # 허위 정량 (측정 불가)
                if ind.get("measure_real") is False:
                    warnings.append(f"[허위정량] {itag}: measure_real=false — 셀 수 있는 대리 신호로 교체 권장 ('{ind.get('label')}')")
                if FAKE_QUANT_PAT.search(str(ind.get("label", ""))):
                    warnings.append(f"[허위정량] {itag}: '{ind.get('label')}' — 측정 불가의 정량(성령충만/믿음 %류) 의심")
                # 신호 프레이밍
                if not ind.get("signal_only"):
                    warnings.append(f"[신호표기] {itag}: signal_only 누락 — 지표는 성과 채찍 아닌 돌봄 신호로 표기 권장")
                # 허위 정밀 — 신뢰 '하' 기준선 위 점값 목표치
                if "baseline" in ind and not isinstance(ind.get("baseline"), dict):
                    errors.append(f"[형식오류] {itag}.baseline이 객체(dict)가 아님 — 비-dict로 안전 환원")
                base = _d(ind.get("baseline"))
                low_conf = base.get("confidence") == "하" or base.get("assumption") is True
                if low_conf and is_point_value(ind.get("target")):
                    warnings.append(f"[허위정밀] {itag}: 신뢰'하' 기준선 위 점값 목표치 '{ind.get('target')}' — 범위·방향으로(예 '2/3 수준')")

    if total_goals == 0:
        errors.append("[목표없음] 전체 핵심 목표가 0개 — 적어도 한 축에 목표가 필요(유지만이라면 keep_list로)")
    if total_goals > GOALS_TOTAL_MAX:
        errors.append(f"[과욕] 전체 핵심 목표 {total_goals}개 — 최대 {GOALS_TOTAL_MAX}개(담임 단독 시간이 최대 제약 자원)")

    for ax_name in AXES:
        if ax_name not in seen_axes:
            warnings.append(f"[축누락] '{ax_name}' 축 엔트리 없음 — 목표 없어도 goals:[] 로 두면 keep_list와 짝이 맞음")

    # 9. 확정 게이트
    confirmed = g.get("confirmed")
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    # 10. 표어 echo 일치
    ie = _d(g.get("inputs_echo"))
    if chosen and ie.get("chosen_theme") and ie.get("chosen_theme") != chosen:
        warnings.append("[표어불일치] meta.chosen_theme ≠ inputs_echo.chosen_theme — vision.chosen 재확인")

    # 10-b. inputs_echo 하위 list-기대 필드 타입 검사(조용한 통과 금지)
    for f in ("core_scriptures", "needs_care"):
        if f in ie and not isinstance(ie.get(f), list):
            errors.append(f"[형식오류] inputs_echo.{f}가 배열(list)이 아님 — 비-list로 안전 환원")
    # needs_care 원소는 문자열(축/영역명)이어야 함 — dict/list 원소는 schema 위반
    for ei, el in enumerate(_l(ie.get("needs_care"))):
        if isinstance(el, (dict, list)):
            errors.append(f"[형식오류] inputs_echo.needs_care[{ei}]가 문자열이 아님(dict/list) — 비-문자열 원소 제외")

    # 11. core_scriptures 성경 본문 실재성 — #4 sermon-planner-52로 가짜 본문 전파 차단
    #     (최상위 비-list는 위 10-b에서 [형식오류]로 이미 차단 — 여기선 원소별 본문 실재만 검사)
    for ci, cs in enumerate(_l(ie.get("core_scriptures"))):
        if isinstance(cs, list):
            errors.append(f"[형식오류] inputs_echo.core_scriptures[{ci}]가 배열 — ref 문자열/객체여야 함")
            continue
        ref = cs.get("ref") if isinstance(cs, dict) else cs
        if not ref or not str(ref).strip():
            continue
        ok, msg = validate_reference(str(ref))
        if not ok:
            errors.append(f"[성경허위] inputs_echo.core_scriptures[{ci}].ref '{ref}' — {msg}")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_goals.py <goals.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            g = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}"); sys.exit(2)

    if not isinstance(g, dict):
        print("[오류] 최상위가 객체(dict)가 아님 — goals.json은 객체여야 함"); sys.exit(2)

    errors, warnings = validate(g)
    print("=" * 60)
    print("churchplan-goal-architect 목표 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for e in errors:
            print(f"  ✗ {e}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 숫자로 환원하거나 근거 없는 목표를 만들지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 정성↔정량 짝 맞음, 근거 추적됨, 과욕 상한 이내. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
