#!/usr/bin/env python3
"""
validate_reinforce.py — churchplan-plan-reinforce 자료 보강(reinforce.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 자료 보강이 세 거짓을 흘리지 않게 지킨다.
  (1) 실측 날조 — status='실측교체'인데 actual_source 없음(자료 근거 없는 실측)
  (2) 추정 삭제 — estimate 미보존(추정→실측 이력 상실)
  (3) 부족 비난 — "자료가 이것밖에·왜 없나" 류 책망
목사의 자료를 검증하는 것이 아니라, AI가 보강을 오염시켰는지 검사한다.

사용:  python3 validate_reinforce.py <reinforce.json>
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import re
import sys


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


# 부족 비난 어휘 (계획이 스스로 자란다 — 부족을 비난하지 않는다)
BLAME = ["이것밖에", "왜 없", "왜 안", "부실", "게을", "성의가", "성의 없", "준비 안", "왜 이거"]
# 명시적 면제 표지 — 비난을 뒤집는 단어만 (예 "…부실하다는 비난이 *아니라*").
# 흔한 형태소(되·좋·괜찮)는 무관한 문장도 면제시키는 거짓음성 구멍이라 제외한다.
EXEMPT = ["아니라", "아닙", "않습니다", "않다", "말고", "금지", "아니다"]
# 매칭된 blame 토큰 뒤 이 거리(문자) 안에 면제 표지가 와야 면제(로컬 컨텍스트 한정).
EXEMPT_WINDOW = 12
# 다어절 blame 토큰의 공백은 가변(공백 0~다수·탭·개행)으로 매칭 — "왜 없"이 "왜  없"·"왜없"으로 새지 않게.
_BLAME_RE = [(w, re.compile(re.escape(w).replace("\\ ", r"\s*"))) for w in BLAME]


def blame_hits(text):
    if not isinstance(text, str) or not text.strip():
        return []
    hits = []
    for w, pat in _BLAME_RE:
        # 토큰의 *모든* 출현을 검사(첫 출현만 보면 1번째가 면제될 때 뒤의 진짜 비난이 샌다).
        for m in pat.finditer(text):
            # blame 토큰 직후 작은 윈도우에 명시적 면제 표지가 있으면 그 출현만 면제
            tail = text[m.end(): m.end() + EXEMPT_WINDOW]
            if any(e in tail for e in EXEMPT):
                continue
            hits.append(w)
            break  # 토큰당 1회만 보고(중복 메시지 방지)
    return hits


def _norm(s):
    """연결 매칭용 정규화 — 공백·구두점 제거(축 토큰 비교를 견고하게)."""
    return re.sub(r"[\s·,，.\-_/()\[\]]+", "", str(s or ""))


def collect_strings(obj):
    out = []
    if isinstance(obj, dict):
        for v in obj.values():
            out += collect_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            out += collect_strings(v)
    elif isinstance(obj, str):
        out.append(obj)
    return out


def validate(r):
    errors, warnings = [], []

    # 1. 필수 블록
    for blk in ("meta", "verify_targets", "reconciliations"):
        if blk not in r:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    # 1-b. 형식 방어 — truthy 비-dict/비-list도 안전 환원하되 위반 1건 등록(조용한 통과 금지).
    #   정상 dict/list 입력은 등록 없이 그대로 통과(회귀 보존).
    #   (a) dict-기대 필드가 dict가 아니면 위반
    for dpath, dval in (("meta", r.get("meta")),
                        ("meta.church_context", _d(r.get("meta")).get("church_context")),
                        ("to_review", r.get("to_review"))):
        if dval is not None and not isinstance(dval, dict):
            errors.append(f"[형식오류] {dpath}가 객체(dict)가 아님 — {dpath}는 dict여야 함")
    #   (b) list-기대 필드가 list가 아니거나, 원소에 비-dict가 섞이면 위반(렌더 시 무시되더라도 검증은 고지)
    for lst in ("verify_targets", "reconciliations", "extracted_data", "plan_updates", "carryovers"):
        val = r.get(lst)
        if val is None:
            continue
        if not isinstance(val, list):
            errors.append(f"[형식오류] {lst}가 배열(list)이 아님 — {lst}는 list여야 함")
        elif any(not isinstance(x, dict) for x in val):
            errors.append(f"[형식오류] {lst}에 객체(dict)가 아닌 원소가 섞임 — 원소는 dict여야 함")
    tr_ub = _d(r.get("to_review")).get("updated_baselines")
    if tr_ub is not None:
        if not isinstance(tr_ub, list):
            errors.append("[형식오류] to_review.updated_baselines가 배열(list)이 아님")
        elif any(not isinstance(x, dict) for x in tr_ub):
            errors.append("[형식오류] to_review.updated_baselines에 객체(dict)가 아닌 원소가 섞임")

    meta = _d(r.get("meta"))
    recs = _l(r.get("reconciliations"))
    extracted = _l(r.get("extracted_data"))

    # 2. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 3. 실측 날조 + 추정 보존
    has_extracted = len(extracted) > 0
    for i, rc in enumerate(recs):
        if not isinstance(rc, dict):
            errors.append(f"[형식오류] reconciliations[{i}]가 객체(dict)가 아님")
            continue
        st = rc.get("status")
        item = rc.get("item", f"[{i}]")
        if st == "실측교체":
            if not (rc.get("actual_source") and str(rc.get("actual_source")).strip()):
                errors.append(f"[실측날조] reconciliations '{item}' 실측교체인데 actual_source 없음 — 자료 근거 없는 실측")
            if not has_extracted:
                warnings.append(f"[근거의심] '{item}' 실측교체인데 extracted_data 비어 있음 — 자료에서 추출했는가(없으면 이월)")
        # 추정 보존
        if not (rc.get("estimate") and str(rc.get("estimate")).strip()):
            errors.append(f"[추정삭제] reconciliations '{item}'에 estimate 없음 — 추정→실측 이력 보존(추정 지우지 않음)")

    # 4. 부족 비난
    for s in collect_strings(r):
        for hit in blame_hits(s):
            errors.append(f"[부족비난] '{hit}' — 자료 부족을 비난하지 않는다(계획이 스스로 자란다): \"{s[:30]}\"")

    # 5. 어긋남 → 조정 연결 (스키마의 trigger 필드로 연결 검사 — raw 부분문자열 금지)
    #   mismatch 항목이 어떤 plan_update의 trigger(연결 전용 필드)에 정규화 토큰 매칭되면 통과.
    #   trigger가 전혀 없는 레거시 산출만 target으로 폴백.
    mismatches = [rc.get("item") for rc in recs if isinstance(rc, dict) and rc.get("mismatch") is True]
    pus = _ld(r.get("plan_updates"))
    triggers = [_norm(u.get("trigger", "")) for u in pus]
    targets = [_norm(u.get("target", "")) for u in pus]
    any_trigger = any(t for t in triggers)
    link_fields = triggers if any_trigger else targets
    for it in mismatches:
        nit = _norm(it)
        if not nit:
            continue
        if not any(nit in field for field in link_fields):
            warnings.append(f"[새병목누락] '{it}' mismatch인데 plan_updates에 조정 없음 — 어긋남은 새 병목 신호")

    # 6. 이월 → #9
    for c in _l(r.get("carryovers")):
        if not isinstance(c, dict):
            errors.append("[형식오류] carryovers 항목이 객체(dict)가 아님")
            continue
        if "review-rhythm" not in str(c.get("to", "")) and "#9" not in str(c.get("to", "")):
            warnings.append(f"[이월대상] carryover '{c.get('item','?')}'의 to에 review-rhythm(#9) 없음")

    # 7. 확정 게이트
    confirmed = r.get("confirmed")
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 검토·확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    # 8. 닫힌 고리(보완A) — to_review 권장
    if recs and not r.get("to_review"):
        warnings.append("[닫힌고리누락] to_review 없음 — 실측 baseline·이월을 #9 분기 점검 첫 사이클로 넘기는가")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_reinforce.py <reinforce.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            r = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(r, dict):
        print("[오류] 최상위 JSON이 객체(dict)가 아님 — reinforce.json은 객체여야 함"); sys.exit(2)

    errors, warnings = validate(r)
    print("=" * 60)
    print("churchplan-plan-reinforce 자료 보강 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for er in errors:
            print(f"  ✗ {er}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 실측을 날조하거나, 추정을 지우거나, 부족을 비난하지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 실측 근거 있음, 추정 보존, 비난 없음. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
