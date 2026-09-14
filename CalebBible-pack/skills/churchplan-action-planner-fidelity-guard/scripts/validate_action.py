#!/usr/bin/env python3
"""
validate_action.py — churchplan-action-planner 실행계획(action.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 실행계획이 세 거짓을 흘리지 않게 지킨다.
  (1) 지어낸 행동 — 목표에 추적되지 않는 source_goal·지어낸 캘린더 행사 연계
  (2) 공백 숨김 — owner=TBD인데 flag 없이 채워진 척(가짜 담당)
  (3) 부서 위장 — departments에 없는 부서 배치
목사의 계획을 검증하는 것이 아니라, AI가 실행계획을 오염시켰는지 검사한다.

사용:  python3 validate_action.py <action.json>
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


DEPT_MAX = 5         # 부서당 행동 권장 상한(과잉분해)
OWNER_MAX = 3        # 같은 담당 반복 상한(중복배정·지친 리더)
GAP_TYPES = {"담당미정", "자원미정", "시기미정"}


def _tokens(s):
    """공백·구두점 정규화 후 토큰 집합."""
    cleaned = re.sub(r"[\s\.,:;\-_/()·~]+", " ", str(s)).strip()
    return {t for t in cleaned.split() if t}


def _goal_matched(sg, goal_keys):
    """source_goal이 from_goals의 (axis, direction_goal) 중 하나에 토큰 일치하는가.

    축 글자만 섞여도 통과하던 약한 substring을 토큰 기반으로 강화한다:
    axis 토큰이 모두 등장하고(부분 문자열 우연일치 차단) + direction_goal 핵심 토큰이
    하나 이상 동반되어야 매칭(axis 단독 매칭 금지). milestone-decomposer가 발급하는
    'axis: direction_goal' 형태와 정확 매칭된다.
    """
    sg_t = _tokens(sg)
    for ax, dg in goal_keys:
        ax_t = _tokens(ax)
        dg_t = _tokens(dg)
        ax_ok = bool(ax_t) and ax_t.issubset(sg_t)
        if not ax_ok:
            continue
        # direction_goal 핵심 토큰(축 단어 제외)이 하나 이상 동반돼야 매칭 —
        # 축 단어가 direction_goal에 재등장해도(예 '섬김'/'이웃 섬김 정례화') 축 단어만으론
        # 매칭 불가(지어낸 목표 차단). direction_goal에 축 외 토큰이 없으면 axis 일치로 충분.
        dg_core = dg_t - ax_t
        if not dg_core or (dg_core & sg_t):
            return True
    return False


def validate(a):
    errors, warnings = [], []

    # 1. 스키마 필수 블록
    for blk in ("meta", "inputs_echo", "actions"):
        if blk not in a:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    # 스키마 필드 형식 오염 검사 — 비-dict/비-list 오염을 조용히 통과시키지 않는다.
    #   (truthy 비-dict subfield 결함 클래스: 안전 환원하되 위반으로 드러냄)
    for k in ("meta", "inputs_echo", "department_table"):
        if k in a and not isinstance(a.get(k), dict):
            errors.append(f"[형식오류] 최상위 '{k}'가 객체(dict)가 아님 — 스키마 필드 오염")
    for k in ("actions", "gaps", "warnings"):
        if k in a and not isinstance(a.get(k), list):
            errors.append(f"[형식오류] 최상위 '{k}'가 리스트가 아님 — 스키마 필드 오염")

    meta = _d(a.get("meta"))
    ie = _d(a.get("inputs_echo"))

    # inputs_echo 하위 dict/list 필드 형식 검사
    if "from_goals" in ie and not isinstance(ie.get("from_goals"), list):
        errors.append("[형식오류] inputs_echo.from_goals가 리스트가 아님 — 목표 출처 오염")
    if "from_calendar" in ie and not isinstance(ie.get("from_calendar"), dict):
        errors.append("[형식오류] inputs_echo.from_calendar가 객체(dict)가 아님 — 캘린더 출처 오염")

    # list-of-dict 필드에 비-dict 원소가 섞이면 위반(조용한 필터링만 하지 않음).
    #   가드(_ld)로 crash는 막되, 오염 원소 존재 자체를 errors로 드러낸다.
    def _check_dict_elems(lst, label):
        if isinstance(lst, list):
            for j, el in enumerate(lst):
                if not isinstance(el, dict):
                    errors.append(f"[형식오류] {label}[{j}]가 객체(dict)가 아님 — 리스트 원소 오염")
    _check_dict_elems(ie.get("from_goals"), "inputs_echo.from_goals")
    _check_dict_elems(_d(ie.get("from_calendar")).get("event_weeks"), "inputs_echo.from_calendar.event_weeks")
    _check_dict_elems(a.get("gaps"), "gaps")
    _check_dict_elems(a.get("warnings"), "warnings")

    # 2. 표어
    theme = meta.get("chosen_theme")
    if not theme or not str(theme).strip():
        errors.append("[표어미확정] meta.chosen_theme 비어 있음 — 표어·목표를 먼저 확정하라(앞 단계로)")

    # 3. 부서
    depts = _l(meta.get("departments"))
    if not depts:
        errors.append("[부서없음] meta.departments 비어 있음 — 교회 부서 구조를 먼저 입력")

    # 4. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 5. 행동 존재
    actions = _l(a.get("actions"))
    if len(actions) == 0:
        errors.append("[행동없음] actions 0개 — 분해할 목표·행동이 필요")

    # 근거 추적 기준 (from_goals 형식 오염은 위에서 이미 등록)
    goal_keys = []
    for g in _ld(ie.get("from_goals")):
        ax = g.get("axis", "")
        dg = g.get("direction_goal", "")
        goal_keys.append((ax, dg))
    event_ids = {e.get("id") for e in _ld(_d(ie.get("from_calendar")).get("event_weeks"))}

    owner_count = {}
    dept_count = {}
    blank_map = {}   # action id → 실제 공백 type 집합(gaps[] 정합 교차검증용)

    # 6. 각 행동
    for i, act in enumerate(actions):
        if not isinstance(act, dict):
            errors.append(f"[형식오류] actions[{i}]: 객체여야 함"); continue
        aid = act.get("id", i)
        tag = f"actions[{aid}]"

        # 행동 하위 dict/list 필드 형식 오염 검사(조용한 통과 금지)
        if "milestone" in act and not isinstance(act.get("milestone"), dict):
            errors.append(f"[형식오류] {tag}.milestone가 객체(dict)가 아님 — 마일스톤 오염")
        for k in ("resources", "flags", "monthly_steps"):
            if k in act and not isinstance(act.get(k), list):
                errors.append(f"[형식오류] {tag}.{k}가 리스트가 아님 — 필드 오염")
        # monthly_steps는 list-of-dict, resources/flags는 list-of-scalar:
        #   각 리스트 원소 계약 위반(오염 원소)을 errors로 드러낸다.
        _check_dict_elems(act.get("monthly_steps"), f"{tag}.monthly_steps")
        for k in ("resources", "flags"):
            if isinstance(act.get(k), list):
                for j, el in enumerate(act.get(k)):
                    if isinstance(el, (dict, list)):
                        errors.append(f"[형식오류] {tag}.{k}[{j}]가 dict/list — 스칼라 원소만 허용(원소 오염)")

        # 근거 추적 — 추적 안 되면 위반(지어낸 목표 차단, ANCHOR #2)
        sg = act.get("source_goal")
        if not sg or not str(sg).strip():
            errors.append(f"[근거누락] {tag}.source_goal 없음 — '이 행동이 어느 목표를 이루나?'에 답하라(지어낸 행동 차단)")
        elif goal_keys and not _goal_matched(sg, goal_keys):
            errors.append(f"[근거추적] {tag}.source_goal '{sg}' — inputs_echo.from_goals에 추적 안 됨(지어낸 목표 차단)")

        # 부서 실재
        dept = act.get("department")
        if not dept:
            errors.append(f"[부서누락] {tag}.department 없음")
        elif depts and dept not in depts:
            errors.append(f"[부서위장] {tag}.department '{dept}' — meta.departments에 없음(없는 부서 배치)")
        else:
            dept_count[dept] = dept_count.get(dept, 0) + 1

        # 목적 (schema '필수 블록 (fidelity-guard 검사)' line 83 — source_goal·department과 동급 필수)
        purpose = act.get("purpose")
        if not purpose or not str(purpose).strip():
            errors.append(f"[목적누락] {tag}.purpose 없음 — '왜 이 행동인지'(목적)는 필수(schema 필수 블록)")

        # 공백 정직 (가짜 담당·자원·시기 차단 — gap-flagger 세 공백 모두)
        flags = _l(act.get("flags"))
        blanks = set()

        # 담당 공백
        owner = act.get("owner")
        is_blank = (not owner) or (str(owner).strip().upper() == "TBD")
        if is_blank:
            blanks.add("담당미정")
            if not any("담당" in str(f) for f in flags):
                errors.append(f"[공백숨김] {tag}: owner 미정(TBD)인데 flags에 담당미정 없음 — 공백을 숨기지 말고 드러내라")
        else:
            owner_count[str(owner)] = owner_count.get(str(owner), 0) + 1

        # 자원 공백 (resources 빈 배열인데 자원미정 flag 없으면 위반)
        resources = _l(act.get("resources"))
        if not resources:
            blanks.add("자원미정")
            if not any("자원" in str(f) for f in flags):
                errors.append(f"[공백숨김] {tag}: resources 비었는데 flags에 자원미정 없음 — 무엇으로 할지 공백을 드러내라")

        # 시기 공백 (timing 비거나 공백인데 시기미정 flag 없으면 위반)
        timing = act.get("timing")
        if not timing or not str(timing).strip():
            blanks.add("시기미정")
            if not any("시기" in str(f) for f in flags):
                errors.append(f"[공백숨김] {tag}: timing 비었는데 flags에 시기미정 없음 — 언제 할지 공백을 드러내라")

        blank_map[str(aid)] = blanks

        # 캘린더 정합 (지어낸 행사 연계 차단)
        #   linked_event를 단 행동은 그 행사가 event_weeks에 실재해야 한다 —
        #   event_weeks가 비었거나 없으면(선언된 행사 0) 어떤 linked_event든 지어낸 것이므로 위반.
        #   (event_ids 비-공백을 전제로 두면 '행사 0일 때 가짜 행사 연계'가 새는 구멍이 생김)
        le = act.get("linked_event")
        if le and str(le).strip() and le not in event_ids:
            errors.append(f"[행사위장] {tag}.linked_event '{le}' — inputs_echo.from_calendar.event_weeks에 없음(지어낸 행사 연계)")

        # 월 범위 (지어낸 달 차단) — monthly_steps[].month는 1~12 정수
        for ms in _ld(act.get("monthly_steps")):
            mo = ms.get("month")
            if mo is not None and (isinstance(mo, bool) or not isinstance(mo, int) or not (1 <= mo <= 12)):
                errors.append(f"[월오류] {tag} monthly_steps month '{mo}' — 1~12 범위 밖(지어낸 달 차단)")

    # 6-b. gaps[] 정합 (gap-flagger 산출 ↔ 실제 행동 공백 교차검증)
    #   - gaps[].type ∈ GAP_TYPES
    #   - gaps에 올린 공백이 실제 행동 상태와 일치(채워진 행동을 공백이라 거짓 보고 차단)
    reported = {}   # action id → 보고된 공백 type 집합 (gaps 형식 오염은 위에서 이미 등록)
    for g in _l(a.get("gaps")):
        if not isinstance(g, dict):
            errors.append("[형식오류] gaps 항목: 객체여야 함"); continue
        gtype = g.get("type")
        if gtype not in GAP_TYPES:
            errors.append(f"[공백유형오류] gaps.type '{gtype}' — {sorted(GAP_TYPES)} 중 하나여야 함")
            continue
        gid = str(g.get("action_id", ""))
        reported.setdefault(gid, set()).add(gtype)
        if gid in blank_map and gtype not in blank_map[gid]:
            errors.append(f"[공백오보] gaps action_id '{gid}' type '{gtype}' — 해당 행동은 채워져 있음(가짜 공백 보고)")
    # 실제 공백인데 gaps에 누락된 것(공백 숨김의 다른 형태)
    for aid, blanks in blank_map.items():
        missing = blanks - reported.get(aid, set())
        for m in missing:
            errors.append(f"[공백누락] actions[{aid}] {m} 상태인데 gaps[]에 없음 — 공백을 보고에 드러내라")

    # 7. 과잉·중복 경고
    for d, cnt in dept_count.items():
        if cnt > DEPT_MAX:
            warnings.append(f"[과잉분해] 부서 '{d}'에 행동 {cnt}개 — 권장 {DEPT_MAX}개(작은 교회 감당 점검)")
    for o, cnt in owner_count.items():
        if cnt >= OWNER_MAX:
            warnings.append(f"[중복배정] '{o}'가 {cnt}개 행동 담당 — 한 손에 몰림(지친 리더 점검·여력 판단은 #8)")

    # 8. 확정 게이트
    confirmed = a.get("confirmed")
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
        print("사용: python3 validate_action.py <action.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            a = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(a, dict):
        print(f"[오류] 최상위 JSON이 객체(dict)가 아님: {type(a).__name__} — action.json 구조 확인"); sys.exit(2)

    errors, warnings = validate(a)
    print("=" * 60)
    print("churchplan-action-planner 실행계획 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for er in errors:
            print(f"  ✗ {er}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 목표 없는 행동을 짓거나 공백을 가짜로 메우지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 모든 행동이 목표에서 왔고, 공백 정직히 표시, 부서 실재. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
