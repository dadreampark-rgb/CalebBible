#!/usr/bin/env python3
"""
validate_resource.py — churchplan-resource-aligner 자원 정렬(resource.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 자원 정렬이 세 거짓을 흘리지 않게 지킨다.
  (1) 절대 금액 환상 — 비율·증감만 다뤄야 하는데 원·만원 등 절대 금액을 지어냄
  (2) 무한 자원 가정 — 새 수요(증액·증원)가 있는데 빼기(subtractions) 없음
  (3) 목자 소진 — 담임 시간에 기도·쉼(protected) 자원 누락
목사의 자원을 검증하는 것이 아니라, AI가 자원 정렬을 오염시켰는지 검사한다.

사용:  python3 validate_resource.py <resource.json>
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    # 타입 계약은 검증기·렌더러 공유 SPEC으로 단일화(ADR-0002) — parity 구조화.
    from schema_guard import check_types
    from spec_resource_aligner import RESOURCE_SCHEMA
except ImportError as _imp_err:
    print(f"[오류] 이식 자산 import 실패(schema_guard/spec_resource_aligner — sync_shared_assets 필요): {_imp_err}")
    sys.exit(2)


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


# 절대 금액/통화 패턴 (비율·증감만 허용) — '%'·'증감'은 허용, 통화·금액은 위반
# 절대 금액만 차단(비율·증감 허용). 음절 단위(원·억·달러 등)는 '숫자 선행' 시에만 금액으로 인정 —
# 후원·자원봉사·임원·충원·원로목사·백만 영혼·달러 환율 같은 정상 어휘 오탐 차단(거짓양성 제거).
# 순수 한글 만 단위 금액('백만원'·'천만원' — 숫자 없이 통화 직결)도 차단('백만 영혼'은 뒤가 통화(원)가
# 아니라 통과 — 거짓양성 0 검증). build_resource.py MONEY_RE와 동일·함께 변경(parity).
# 숫자와 통화 사이의 다리는 금액 자릿수(백만/천만/만/천/억)만 허용 — 과거 [가-힣]? 는 '2027 자원'·
# '2030 지원'처럼 숫자 뒤 무관한 단어(자+원·지+원)를 절대금액으로 오인했다(거짓양성). '5만 원' 같은
# 띄어쓴 금액은 자릿수 그룹으로 계속 포착.
MONEY_RE = re.compile(r"(₩|\$|(?:USD|KRW|won)\s*[0-9]|[0-9][0-9,\.]*\s*(?:백만|천만|만|천|억)?\s*(원|만원|천원|억|백만|달러|won|USD|KRW)|(백만|천만)\s*원)")
# 증액·증원·시간추가 수요 키워드 (더하기 신호) — 한국어 증가/부족 동의어 보강
# 키워드 운에 기대지 않도록 구조 신호(subtract_candidate 채워짐)와 병행하되, 자연어 동의어도 넓게 포착
# (보충·상향·충당·확보·배가·증대·증강·요망·키우·충원·상승·확장 — 키워드 없이 빼기 누락 우회 차단).
ADD_RE = re.compile(r"(증액|증원|추가|늘|확대|신규|더|강화|보강|부족|모자|필요|확충|증설|증가|보충|상향|충당|확보|배가|증대|증강|요망|키우|충원|상승|확장)")

# action_id 토큰 (예: A2, B12) — 출처 cross-check 시 정확일치 우선
ACTION_ID_RE = re.compile(r"[A-Z]+[0-9]+")
# 출처 어절 부분일치의 boilerplate 우회를 막는 불용어 — 이 어절만으론 상속 인정 금지
SRC_STOPWORDS = {"미정", "공석", "담당", "미배정", "필요", "리더", "명", "담당자", "미확정", "배정"}


def find_money(obj, path="budget_plan"):
    """주어진 블록 내 절대 금액 패턴 탐색."""
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits += find_money(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += find_money(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        m = MONEY_RE.search(obj)
        if m:
            hits.append((path, obj, m.group(0)))
    return hits


def validate(r):
    errors, warnings = [], []

    # 1. 스키마 필수 블록
    for blk in ("meta", "inputs_echo", "budget_plan", "pastor_time"):
        if blk not in r:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    # 타입 계약 — 검증기·렌더러 공유 SPEC 한 곳(ADR-0002). 최상위 dict·list-of-dict·중첩 dict·
    # subtractions 스칼라까지 RESOURCE_SCHEMA가 검사. 의미 검사(절대금액·빼기·목자·상속)는 아래에 잔류.
    errors.extend(check_types(r, RESOURCE_SCHEMA))

    meta = _d(r.get("meta"))
    ie = _d(r.get("inputs_echo"))

    # 2. 표어
    theme = meta.get("chosen_theme")
    if not theme or not str(theme).strip():
        errors.append("[표어미확정] meta.chosen_theme 비어 있음 — 표어·계획을 먼저 확정하라(앞 단계로)")

    # 3. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 4. 절대 금액 금지 (비율·증감만) — budget_plan 외 금액 누출 경로까지 스캔
    #    (ANCHOR #2 '최우선': demand_gaps·subtractions·warnings·pastor_time에 지어낸 절대금액도 차단)
    bp = _d(r.get("budget_plan"))
    money_hits = find_money(bp)
    # org_plan은 조직 배치표로 그대로 렌더되는 1차 산출 — 절대금액('사례비 250만원' 등) 누출을 반드시 차단.
    for blk in ("demand_gaps", "subtractions", "warnings", "pastor_time", "org_plan", "inputs_echo"):
        if blk in r:
            money_hits += find_money(r.get(blk), blk)
    # note의 "재정 담당과 확정" 설명은 예외(금액 언급 아님) — note 경로는 경고로 완화
    for path, text, tok in money_hits:
        if path.endswith(".note"):
            warnings.append(f"[금액표현] {path}: '{tok}' — note에 금액 표현. 비율·증감 위주로 권장")
        else:
            errors.append(f"[절대금액] {path}: '{tok}' (\"{text[:30]}\") — 예산은 비율(%)·증감 방향만(자료 없이 작동)")

    # 5. 더하기 전 빼기 — 자연어 키워드(ADD_RE) + 구조 신호(subtract_candidate 채워짐) 병행
    #    LLM이 빼기 후보를 단 항목 = 새 수요로 판정(어휘 운에 의존하지 않음)
    demand = _l(r.get("demand_gaps"))
    has_add = False
    for d in demand:
        if not isinstance(d, dict):
            continue
        need = d.get("need", {}) or {}
        if isinstance(need, dict):
            need_blob = " ".join(str(v) for v in need.values())
        else:
            need_blob = str(need)
        blob = need_blob + " " + str(d.get("gap", ""))
        sc = d.get("subtract_candidate")
        if ADD_RE.search(blob) or (sc is not None and str(sc).strip()):
            has_add = True
            break
    subs = _l(r.get("subtractions"))
    if has_add and not subs:
        errors.append("[빼기없음] 새 자원 수요(증액·증원·강화·보강 등)가 있는데 subtractions 비어 있음 — 더하기 전 빼기(무엇을 멈출 것인가)")

    # 6. 목자 자원 (기도·쉼 보호)
    pt = _d(r.get("pastor_time"))
    blocks = _l(pt.get("blocks"))
    protected = [b for b in blocks if isinstance(b, dict) and b.get("protected") is True]
    if blocks and not protected:
        errors.append("[목자소진] pastor_time.blocks에 protected(기도/쉼) 항목 없음 — 목자가 소진되면 계획도 무너진다(가드레일 ④)")
    elif not blocks:
        warnings.append("[시간미배분] pastor_time.blocks 비어 있음 — 담임 주간 시간을 배분했는가")

    # 7. 상속 충실 — 리더 공백이 #7 담당미정과 연결되는지 + from_action_gap 출처 cross-check
    from_action = _d(ie.get("from_action"))
    action_gaps = _l(from_action.get("gaps"))
    org = _d(r.get("org_plan"))
    leader_gaps = _l(org.get("leader_gaps"))
    if action_gaps and not leader_gaps:
        warnings.append("[리더공백누락] #7 담당미정(from_action.gaps)이 있는데 org_plan.leader_gaps 비어 있음 — 리더 공백으로 이었는가")

    # 7-b. 출처 무결성 — leader_gaps[].from_action_gap 이 실제 #7 gaps(action_id/text)에서 상속됐는지
    #      (상속되지 않은 부서/gap을 지어내지 않는다 — 할루시네이션 구조적 차단)
    gap_tokens = []
    gap_action_ids = set()
    for g in action_gaps:
        if isinstance(g, dict):
            aid = str(g.get("action_id", "")).strip()
            txt = str(g.get("text", "")).strip()
            gap_tokens += [aid, txt]
            if aid:
                gap_action_ids.add(aid)
            gap_action_ids.update(ACTION_ID_RE.findall(txt))
        else:
            t = str(g).strip()
            gap_tokens.append(t)
            gap_action_ids.update(ACTION_ID_RE.findall(t))
    gap_tokens = [t for t in gap_tokens if t]
    for lg in leader_gaps:
        if not isinstance(lg, dict):
            continue
        src = str(lg.get("from_action_gap", "")).strip()
        if not src:
            warnings.append(f"[출처미표기] org_plan.leader_gaps '{lg.get('ministry','')}' — from_action_gap 비어 있음(상속 출처 명시)")
            continue
        # ① action_id 토큰 정확일치 우선 — src에 action_id가 있으면 그 id가 #7 gaps에 있어야 함
        src_action_ids = set(ACTION_ID_RE.findall(src))
        if src_action_ids:
            matched = bool(src_action_ids & gap_action_ids)
        else:
            # ② action_id 없으면 불용어(boilerplate 어절) 제거 후 의미 어절로만 부분일치.
            #    src가 전부 boilerplate(의미 어절 0)면 상속을 증명할 내용이 없으므로 — src in t 같은
            #    substring 통과를 허용하면 "담당자 미정"·"공석" 한 마디로 지어낸 부서가 통과(할루시네이션 우회).
            #    따라서 의미 어절이 있을 때만 substring/어절 부분일치를 인정하고, 어절이 0이면 전체 토큰
            #    정확일치(src == t)만 상속으로 인정한다(주석 "의미 어절로만"의 의도와 일치).
            src_words = [w for w in re.split(r"[\s·,]+", src) if w and w not in SRC_STOPWORDS]
            if src_words:
                matched = any(
                    src == t or src in t or t in src or any(w in t for w in src_words)
                    for t in gap_tokens
                )
            else:
                matched = any(src == t for t in gap_tokens)
        if not matched:
            errors.append(f"[출처불일치] org_plan.leader_gaps.from_action_gap '{src}' 이 #7 from_action.gaps 에 없음 — 상속되지 않은 갭을 지어내지 마라")

    # 8. 확정 게이트
    confirmed = r.get("confirmed")
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 검토·확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    # 9. 표어 echo 일치
    if theme and ie.get("chosen_theme") and ie.get("chosen_theme") != theme:
        warnings.append("[표어불일치] meta.chosen_theme ≠ inputs_echo.chosen_theme — vision.chosen 재확인")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_resource.py <resource.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            r = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(r, dict):
        print(f"[오류] 최상위 JSON이 객체가 아님(type={type(r).__name__}) — resource.json 은 dict 여야 함"); sys.exit(2)

    errors, warnings = validate(r)
    print("=" * 60)
    print("churchplan-resource-aligner 자원 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for er in errors:
            print(f"  ✗ {er}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 절대 금액을 지어내거나, 빼기 없이 더하거나, 목자를 소진시키지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 비율만 다룸, 더하기 전 빼기 있음, 목자 기도·쉼 보호. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
