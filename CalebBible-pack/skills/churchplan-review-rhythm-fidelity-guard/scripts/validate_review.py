#!/usr/bin/env python3
"""
validate_review.py — churchplan-review-rhythm 점검 리듬(review.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 점검 리듬이 세 거짓을 흘리지 않게 지킨다.
  (1) 점검=성과 채찍 — 신호등 frame·빨강 시나리오에 정죄·문책 어휘
  (2) 미래 점검값 둔갑 — 점검 전(confirmed=null)인데 status가 채워짐(안 일어난 진행 지어냄)
  (3) 박제된 계획 — 반기 공식 수정일(midyear_revision)이 없음
목사의 점검을 검증하는 것이 아니라, AI가 점검 리듬을 오염시켰는지 검사한다.

사용:  python3 validate_review.py <review.json>
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import re
import sys


def _d(x):
    """truthy 비-dict(문자열·리스트·정수)도 {}로 안전 환원."""
    return x if isinstance(x, dict) else {}


def _l(x):
    """truthy 비-list도 []로 안전 환원."""
    return x if isinstance(x, list) else []


def _ld(x):
    """list-of-dict만 남긴다(비-dict 원소 제거)."""
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


# 정죄·성과 금칙어 (점검은 돌봄이지 채찍이 아니다) — care-framing 계승
CONDEMN = ["실패", "미달", "부진", "문책", "추궁", "징계", "낙제", "질책"]
# 부정·금지 표지 (금칙어가 '실패가 아니라'·'문책 금지'처럼 정당히 쓰인 경우 면제)
NEGATE_RE = re.compile(r"(아니|않|말고|금지|없)")


# 절 분리(문장 단위) — 부정 면제를 같은 문장 안으로 좁힌다(전역 면제 결함 차단).
# 문장 종결부호(.!?)와 줄바꿈만 경계로 본다. 가운뎃점(·)·쉼표는 한국어에서
# 한 문장 안의 나열 구분자이므로 쪼개지 않는다('추궁·문책 금지'의 금지를 잃지 않게).
CLAUSE_SPLIT_RE = re.compile(r"[.!?\n]+")


def condemn_hits(text):
    """텍스트에 정죄 어휘가 부정 표지 없이 쓰였으면 적발(돌봄 프레이밍 면제).

    면제 판정은 **같은 절(문장)** 안의 부정 표지로만 한다. 한 문자열의 다른 절에
    부정어가 있다고 채찍 절을 면제하던 전역 스코프 결함을 막는다.
    (예: '실패한 부서를 색출한다. 변명은 없다.' → '실패' 절에 부정어 없으므로 적발)
    """
    if not isinstance(text, str) or not text.strip():
        return []
    hits = []
    for clause in CLAUSE_SPLIT_RE.split(text):
        if not clause.strip():
            continue
        if NEGATE_RE.search(clause):
            continue
        for w in CONDEMN:
            if w in clause and w not in hits:
                hits.append(w)
    return hits


def walk_strings(node, path="", skip_keys=()):
    """JSON 트리를 재귀 순회하며 (경로, 문자열 leaf)를 yield.

    수치·상속 필드(baseline/target 등)는 skip_keys로 제외 — 정죄 검사 대상은
    AI 자유텍스트(frame·care_note·glance_question·agenda·시나리오)에 한정한다.
    """
    if isinstance(node, dict):
        for k, v in node.items():
            if k in skip_keys:
                continue
            walk_path = f"{path}.{k}" if path else str(k)
            yield from walk_strings(v, walk_path, skip_keys)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, f"{path}[{i}]", skip_keys)
    elif isinstance(node, str):
        yield path, node


def validate(r):
    errors, warnings = [], []

    # 1. 스키마 필수 블록 — 누락이거나 dict가 아니면(truthy 비-dict 포함) 위반 등록.
    #    안전 환원(_d)으로 raw traceback은 막되, [형식오류]를 등록해 조용한 통과를 금한다.
    for blk in ("meta", "inputs_echo", "scorecard", "schedule"):
        if blk not in r:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")
        elif not isinstance(r.get(blk), dict):
            errors.append(f"[형식오류] 최상위 '{blk}'가 객체(dict)가 아님: {type(r.get(blk)).__name__}")

    meta = _d(r.get("meta"))
    ie = _d(r.get("inputs_echo"))
    scorecard = _d(r.get("scorecard"))
    schedule = _d(r.get("schedule"))
    confirmed = r.get("confirmed")

    # 1-b. 구조 타입 검사 — 알려진 dict/list 하위 필드가 present-but-wrong-type면
    #      [형식오류] 등록(조용한 통과 금지). 안전 환원은 _d/_l/_ld가 맡아 raw traceback 차단.
    #      (truthy 비-dict subfield 결함 클래스의 결정론적 차단 — 검사 표면 자동 망라)
    def _need_dict(container, key, label):
        if isinstance(container, dict) and key in container and not isinstance(container[key], dict):
            errors.append(f"[형식오류] {label}가 객체(dict)가 아님: {type(container[key]).__name__}")

    def _need_list(container, key, label):
        if isinstance(container, dict) and key in container and not isinstance(container[key], list):
            errors.append(f"[형식오류] {label}가 배열(list)이 아님: {type(container[key]).__name__}")

    mc_blk = r.get("monthly_checkup")
    if "monthly_checkup" in r and not isinstance(mc_blk, dict):
        errors.append(f"[형식오류] monthly_checkup가 객체(dict)가 아님: {type(mc_blk).__name__}")
    if "red_signal_scenarios" in r and not isinstance(r.get("red_signal_scenarios"), list):
        errors.append(f"[형식오류] red_signal_scenarios가 배열(list)이 아님: {type(r.get('red_signal_scenarios')).__name__}")
    _need_list(ie, "indicators_from_goals", "inputs_echo.indicators_from_goals")
    _need_dict(_d(mc_blk), "pastor_sustainability_row", "monthly_checkup.pastor_sustainability_row")
    _need_list(_d(mc_blk), "rows", "monthly_checkup.rows")
    _need_dict(schedule, "midyear_revision", "schedule.midyear_revision")
    _need_dict(schedule, "auto_reminder", "schedule.auto_reminder")
    _need_list(schedule, "quarterly_reviews", "schedule.quarterly_reviews")
    _need_list(schedule, "quarterly_agenda", "schedule.quarterly_agenda")
    # 리스트 원소가 비-dict이면(섞임 포함) 형식오류 — 산출물 오염 차단
    for q in _ld(scorecard.get("quarters")):
        _need_list(q, "indicators", f"{q.get('quarter','?')}.indicators")
    for lst_key, lbl in (("indicators_from_goals", "inputs_echo.indicators_from_goals"),):
        for i, el in enumerate(_l(ie.get(lst_key))):
            if not isinstance(el, dict):
                errors.append(f"[형식오류] {lbl}[{i}] 항목이 객체(dict)가 아님: {type(el).__name__}")
    for i, el in enumerate(_l(r.get("red_signal_scenarios"))):
        if not isinstance(el, dict):
            errors.append(f"[형식오류] red_signal_scenarios[{i}] 항목이 객체(dict)가 아님: {type(el).__name__}")
    for i, el in enumerate(_l(_d(mc_blk).get("rows"))):
        if not isinstance(el, dict):
            errors.append(f"[형식오류] monthly_checkup.rows[{i}] 항목이 객체(dict)가 아님: {type(el).__name__}")
    for i, el in enumerate(_l(schedule.get("quarterly_reviews"))):
        if not isinstance(el, dict):
            errors.append(f"[형식오류] schedule.quarterly_reviews[{i}] 항목이 객체(dict)가 아님: {type(el).__name__}")

    # 2. 표어
    theme = meta.get("chosen_theme")
    if not theme or not str(theme).strip():
        errors.append("[표어미확정] meta.chosen_theme 비어 있음 — 표어·목표를 먼저 확정하라(앞 단계로)")

    # 3. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # quarters가 truthy 비-list(문자열·정수)면 _l이 []로 환원하고 아래에서 형식오류 등록.
    quarters_raw = scorecard.get("quarters")
    if "quarters" in scorecard and not isinstance(quarters_raw, list):
        errors.append(f"[형식오류] scorecard.quarters가 배열(list)이 아님: {type(quarters_raw).__name__}")
    quarters = _l(quarters_raw)
    all_inds = []
    for q in quarters:
        if not isinstance(q, dict):
            errors.append(f"[형식오류] scorecard.quarters 항목이 객체(dict)가 아님: {type(q).__name__}")
            continue
        for ind in _l(q.get("indicators")):
            if not isinstance(ind, dict):
                errors.append(f"[형식오류] {q.get('quarter','?')} indicators 항목이 객체(dict)가 아님: {type(ind).__name__}")
                continue
            all_inds.append((q.get("quarter", "?"), ind))

    # 4. 미래값 둔갑 — 점검 전(confirmed 없음)인데 status가 채워짐
    if not confirmed:
        filled = [(q, ind.get("ref", "?")) for q, ind in all_inds
                  if ind.get("status") not in (None, "", "null")]
        for q, ref in filled:
            errors.append(f"[미래값둔갑] {q} '{ref}'의 status가 점검 전에 채워짐 — 아직 일어나지 않은 진행은 지어내지 않는다(점검 전 비움)")

    # 5. 돌봄 프레이밍 — 정죄 금칙어(부정 표지 없이)를 모든 AI 자유텍스트 leaf에서 적발.
    #    수치·상속 필드(baseline/target/ref/by 등)와 provenance(inputs_echo)는 제외 —
    #    검사 표면은 사람이 손으로 고른 부분집합이 아니라 재귀 순회로 자동 망라한다.
    mc = _d(r.get("monthly_checkup"))
    SKIP_KEYS = ("baseline", "target", "ref", "by", "status", "quarter",
                 "signal_only", "verify_at_review", "inputs_echo", "meta", "confirmed")
    seen = set()
    for blk in ("scorecard", "monthly_checkup", "red_signal_scenarios", "schedule"):
        if blk not in r:
            continue
        for path, txt in walk_strings(r[blk], blk, SKIP_KEYS):
            for hit in condemn_hits(txt):
                key = (path, hit)
                if key in seen:
                    continue
                seen.add(key)
                errors.append(f"[정죄어휘] {path}에 '{hit}' — 점검은 돌봄이지 채찍이 아니다(care-framing)")

    # 6. 반기 공식 수정일 못박기 (01 라인 310)
    mid = _d(schedule.get("midyear_revision"))
    if not mid or mid.get("official") is not True:
        errors.append("[반기수정일누락] schedule.midyear_revision(official:true)이 없음 — 반기(6~7월) 공식 수정일을 못박아라(계획은 갱신으로 산다)")
    else:
        when = str(mid.get("when", ""))
        if not re.search(r"(6|7|반기|상반|하반)", when):
            warnings.append(f"[반기시점확인] midyear_revision.when '{when}' — 6~7월 권장")

    # 7. signal_only 계승
    for q, ind in all_inds:
        if "signal_only" not in ind:
            warnings.append(f"[신호표기누락] {q} '{ind.get('ref','?')}'에 signal_only 없음 — 지표는 신호지 성과 등급 아님(#3 계승)")

    # 8. 상속 충실 — scorecard 지표가 #3 지표에서 왔는가
    src_inds = _ld(ie.get("indicators_from_goals"))
    src_labels = [str(s.get("label", "")) for s in src_inds if s.get("label")]
    if all_inds and not src_labels:
        errors.append("[상속없음] scorecard에 지표가 있는데 inputs_echo.indicators_from_goals 비어 있음 — #3 목표 지표를 지어냈는가")
    else:
        for q, ind in all_inds:
            ref = str(ind.get("ref", ""))
            if src_labels and not any(lbl and lbl in ref for lbl in src_labels):
                errors.append(f"[지어낸지표] {q} '{ref}' — #3 indicators_from_goals에 없는 지표(상속·전사만)")

    # 9. 추정 이월 — 신뢰'하'/assumption 지표는 verify_at_review
    low_labels = []
    for s in src_inds:
        if not isinstance(s, dict):
            continue
        bl = s.get("baseline")
        bl = bl if isinstance(bl, dict) else {}
        if str(bl.get("confidence", "")) == "하" or bl.get("assumption") is True:
            low_labels.append(str(s.get("label", "")))
    for q, ind in all_inds:
        ref = str(ind.get("ref", ""))
        if any(lbl and lbl in ref for lbl in low_labels) and ind.get("verify_at_review") is not True:
            errors.append(f"[추정이월누락] {q} '{ref}'는 기준선 신뢰 '하'/추정 — verify_at_review:true로 실측 표시 필수(흐린 지표 또렷한 척 금지). #3→점검 매핑은 결정론이다.")

    # 10. 확정 게이트
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 검토·확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    # 11. 분기 무결성 — quarters는 정확히 4개(1Q~4Q)·by↔배치 정합(결정론 배치).
    dict_quarters = [q for q in quarters if isinstance(q, dict)]
    if quarters:
        qnames = [q.get("quarter") for q in dict_quarters]
        if len(quarters) != 4 or set(qnames) != {"1Q", "2Q", "3Q", "4Q"}:
            errors.append(f"[분기무결성] scorecard.quarters가 1Q~4Q 정확히 4개가 아님: {qnames} — 스키마 필수 불변식(scorecard-builder 결정론 배치)")
        for q in dict_quarters:
            qn = q.get("quarter")
            for ind in _ld(q.get("indicators")):
                by = ind.get("by")
                if by and qn and by != qn:
                    errors.append(f"[분기불일치] {qn}에 by='{by}' 지표 '{ind.get('ref','?')}' — 기한 분기와 배치가 다름(by→분기 매핑은 결정론)")

    # 12. 표어 echo 일치
    if theme and ie.get("chosen_theme") and ie.get("chosen_theme") != theme:
        warnings.append("[표어불일치] meta.chosen_theme ≠ inputs_echo.chosen_theme — 앞 단계 재확인")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_review.py <review.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            r = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(r, dict):
        print(f"[오류] 최상위가 객체(dict)가 아님: {type(r).__name__} — review.json은 객체여야 함"); sys.exit(2)

    errors, warnings = validate(r)
    print("=" * 60)
    print("churchplan-review-rhythm 점검 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for er in errors:
            print(f"  ✗ {er}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 점검을 채찍으로 만들거나, 미래값을 지어내거나, 반기 수정일을 빠뜨리지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 점검은 돌봄, 미래값 비움, 반기 공식 수정일 못박힘. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
