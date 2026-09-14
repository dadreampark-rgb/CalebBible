#!/usr/bin/env python3
"""
validate_calendar.py — churchplan-ministry-calendar 통합 캘린더(calendar.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 통합이 세 거짓을 흘리지 않게 지킨다.
  (1) 지어낸 통합 — 상속되지 않은 주차·설교(series_id)·행사(event id)·캠페인(name)을 캘린더가 새로 만듦
  (2) 깨진 격자 — 52주 중복·범위 이탈
  (3) 소진 은폐 — 밀집 경고·안식 계획 누락(꽉 찬 달력을 좋아 보이게)
목사의 계획을 검증하는 것이 아니라, AI가 통합을 오염시켰는지 검사한다.

사용:  python3 validate_calendar.py <calendar.json>
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_load import compute_all_loads, detect_density  # 부하 점수·연속고강도 결정론 재계산(rubric 단일 진실)
from build_grid import build_grid  # 52주 date·quarter·month 결정론 격자(layer-merger 골격과 동일)

WEEKS_TOTAL = 52


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


def validate(c):
    errors, warnings = [], []

    # 1. 스키마 필수 블록
    for blk in ("meta", "inputs_echo", "weeks"):
        if blk not in c:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    # 1-b. 필수 dict 필드가 비-dict면 형식오류 등록(조용한 통과 금지) 후 안전 환원
    if "meta" in c and not isinstance(c.get("meta"), dict):
        errors.append(f"[형식오류] meta 가 객체(JSON object)가 아님: {type(c.get('meta')).__name__}")
    if "inputs_echo" in c and not isinstance(c.get("inputs_echo"), dict):
        errors.append(f"[형식오류] inputs_echo 가 객체(JSON object)가 아님: {type(c.get('inputs_echo')).__name__}")

    meta = _d(c.get("meta"))
    ie = _d(c.get("inputs_echo"))

    # 2. 표어
    theme = meta.get("chosen_theme")
    if not theme or not str(theme).strip():
        errors.append("[표어미확정] meta.chosen_theme 비어 있음 — 표어를 먼저 확정하라(앞 단계로)")

    # 3. year — 정수 + 결정론 격자 산출 가능 범위(그레고리력 computus 1583~ · datetime 상한 9999).
    #    범위 밖(0·음수·>9999 등)은 build_grid 가 raw ValueError 로 크래시하므로 여기서 clean 차단.
    year = meta.get("year")
    year_ok = isinstance(year, int) and not isinstance(year, bool) and 1583 <= year <= 9999
    if not year_ok:
        errors.append(f"[연도오류] meta.year '{year}' — 1583~9999 정수여야 함(절기·날짜 정합·격자 산출 가능 범위)")

    # 4. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 5. 52주 격자 무결성
    weeks = _l(c.get("weeks"))
    seen = {}
    valid_weeks = []  # range 통과한 모든 week dict(중복 survivor 아님) — fabrication 검사 대상
    for i, wk in enumerate(weeks):
        if not isinstance(wk, dict):
            errors.append(f"[형식오류] weeks[{i}]: 객체여야 함"); continue
        n = wk.get("week")
        if not isinstance(n, int) or n < 1 or n > WEEKS_TOTAL:
            errors.append(f"[격자범위] weeks[{i}].week '{n}' — 1~{WEEKS_TOTAL} 정수여야 함")
            continue
        if n in seen:
            errors.append(f"[격자중복] week {n} 중복 — 통합 격자가 깨짐")
        seen[n] = wk
        valid_weeks.append(wk)  # 중복 앞 항목도 포함 — fabrication을 중복 뒤에 숨기지 못하게
    present = sorted(seen.keys())
    if not present:
        errors.append("[격자없음] 유효 주차 0개 — layer-merger가 52주 격자를 세웠는가(weeks 누락/전부 범위 이탈)")
    elif len(present) < WEEKS_TOTAL:
        missing = [w for w in range(1, WEEKS_TOTAL + 1) if w not in seen]
        warnings.append(f"[격자누락] {len(missing)}개 주차 누락 {missing[:8]}{'…' if len(missing) > 8 else ''} — 완전 52주 격자 권장")

    # 6. 상속 id 충실 (지어낸 통합 차단 — ANCHOR #2 핵심)
    fsp = _d(ie.get("from_sermon_plan"))
    fev = _d(ie.get("from_events"))
    series_ids = {s for s in _l(fsp.get("series_ids")) if isinstance(s, (str, int))}
    event_ids = {e for e in _l(fev.get("event_ids")) if isinstance(e, (str, int))}
    campaign_names = {x.get("name") for x in _ld(ie.get("campaigns_input"))}

    # weeks에 sermon/events/campaigns가 실제로 존재하는지(출처 집합이 비었을 때 검사 무력화 여부 판단용)
    has_sermon = has_event = has_campaign = False
    for wk in valid_weeks:
        n = wk.get("week")
        sm = _d(wk.get("sermon"))
        sid = sm.get("series_id")
        if sid:
            has_sermon = True
            if series_ids and sid not in series_ids:
                errors.append(f"[지어낸설교] week {n}: sermon.series_id '{sid}' — inputs_echo.from_sermon_plan.series_ids에 없음(상속 안 된 시리즈)")
        for ev in _ld(wk.get("events")):
            eid = ev.get("id")
            if eid:
                has_event = True
                if event_ids and eid not in event_ids:
                    errors.append(f"[지어낸행사] week {n}: events.id '{eid}' — inputs_echo.from_events.event_ids에 없음(상속 안 된 행사)")
        for cp in _ld(wk.get("campaigns")):
            nm = cp.get("name")
            if nm:
                has_campaign = True
                if campaign_names and nm not in campaign_names:
                    errors.append(f"[지어낸캠페인] week {n}: campaigns.name '{nm}' — inputs_echo.campaigns_input에 없음(상속/입력 안 된 캠페인)")

    # 출처 없이 통합 불가 — weeks엔 콘텐츠가 있는데 대응 inputs_echo 출처 집합이 비면 위반(garbage-in 차단)
    if has_sermon and not series_ids:
        errors.append("[출처없음] weeks에 sermon이 있는데 inputs_echo.from_sermon_plan.series_ids 비어 있음 — 출처 없이 통합 불가(상속 충실 검사 무력화)")
    if has_event and not event_ids:
        errors.append("[출처없음] weeks에 events가 있는데 inputs_echo.from_events.event_ids 비어 있음 — 출처 없이 통합 불가(상속 충실 검사 무력화)")
    if has_campaign and not campaign_names:
        errors.append("[출처없음] weeks에 campaigns가 있는데 inputs_echo.campaigns_input 비어 있음 — 출처 없이 통합 불가(상속 충실 검사 무력화)")

    # 6-b. 부하 점수 재계산 대조 (LLM 임의 부풀림 차단 — season-frame-catalog rubric 단일 진실)
    recalc = compute_all_loads(valid_weeks)
    for wk in valid_weeks:
        n = wk.get("week")
        load = wk.get("load")
        if not isinstance(load, dict):
            continue  # load 미표기는 7번 소진 점검에서 별도 안내(overload-marker 미실행)
        exp = recalc.get(n)
        if not exp:
            continue
        sc = load.get("score")
        lv = load.get("level")
        if sc is not None and sc != exp["score"]:
            errors.append(f"[부하조작] week {n}: load.score '{sc}' ≠ rubric 재계산 {exp['score']} — 점수를 임의로 바꿈(season-frame-catalog rubric으로만)")
        if lv is not None and lv != exp["level"]:
            errors.append(f"[부하조작] week {n}: load.level '{lv}' ≠ rubric 재계산 '{exp['level']}'(score {exp['score']}) — level을 임의로 바꿈")

    # 6-c. 격자 날짜·분기·월 대조 (build_grid 결정론 격자 — 날짜/분기/월 hallucination 차단)
    if year_ok:
        grid = {g["week"]: g for g in build_grid(year)}
        for wk in valid_weeks:
            n = wk.get("week")
            exp = grid.get(n)
            if not exp:
                continue
            d, q, mo = wk.get("date"), wk.get("quarter"), wk.get("month")
            if d and d != exp["date"]:
                errors.append(f"[격자날짜] week {n}: date '{d}' ≠ 결정론 격자 '{exp['date']}' — layer-merger build_grid 격자로 전사")
            if q is not None and q != exp["quarter"]:
                errors.append(f"[격자분기] week {n}: quarter '{q}' ≠ 결정론 격자 {exp['quarter']} — 분기 경계(1Q1~13·2Q14~26·3Q27~39·4Q40~52) 어긋남")
            if mo is not None and mo != exp["month"]:
                errors.append(f"[격자월] week {n}: month '{mo}' ≠ 결정론 격자 {exp['month']}(date {exp['date']}) — 날짜와 월 불일치")

    # 7. 소진 방지 — 밀집/안식 존재 (소진 은폐 차단)
    if "density_warnings" not in c:
        warnings.append("[밀집미점검] density_warnings 키 없음 — overload-marker가 부하를 비췄는가")

    # 7-a. 연속고강도 은폐 차단 — detect_density(결정론 연속 '높음' 구간)가 density_warnings에 반드시 표시돼야
    #      (load.score 재계산처럼, 진짜 연속 고강도 run을 빼서 꽉 찬 달력을 좋아 보이게 하는 소진 은폐를 적발)
    declared_density_weeks = set()
    for d in _ld(c.get("density_warnings")):
        for w in _l(d.get("weeks")):
            if isinstance(w, int):
                declared_density_weeks.add(w)
    for run in detect_density(valid_weeks):
        run_weeks = [w for w in _l(run.get("weeks")) if isinstance(w, int)]
        missing = [w for w in run_weeks if w not in declared_density_weeks]
        if missing:
            errors.append(
                f"[밀집은폐] 연속고강도 {run_weeks[0]}~{run_weeks[-1]}주(부하 높음 {len(run_weeks)}주 연속)가 "
                f"density_warnings에 표시 안 됨 — 소진을 숨기지 말 것(가드레일 ④, overload-marker 자동 표시 누락)")

    rest_plan = c.get("rest_plan")
    if rest_plan is None:
        warnings.append("[안식미계획] rest_plan 키 없음 — sabbath-protector가 안식을 보호했는가")
    elif not _l(rest_plan):
        warnings.append("[안식없음] rest_plan 비어 있음 — 목자 지속가능성 점검(여백도 계획·가드레일 ④)")

    # 7-b. 안식 보호 교차검증 — pastor_rest_input의 모든 주간이 rest_plan에 보호로 존재해야(무조건 사수)
    rest_input_weeks = set()
    for r in _ld(ie.get("pastor_rest_input")):
        for w in _l(r.get("weeks")):
            if isinstance(w, int):
                rest_input_weeks.add(w)
    protected_weeks = set()
    for r in _ld(rest_plan):
        for w in _l(r.get("weeks")):
            if isinstance(w, int):
                protected_weeks.add(w)
    for w in sorted(rest_input_weeks - protected_weeks):
        errors.append(f"[안식미보호] week {w}: 목사가 비운 주간(pastor_rest_input)인데 rest_plan에 보호로 없음 — 휴식 주간을 행사로 덮어쓰지 말 것(가드레일 ④)")
    # 보호 주간은 weeks[].rest_protected=true 여야
    for wk in valid_weeks:
        n = wk.get("week")
        if n in rest_input_weeks and wk.get("rest_protected") is not True:
            errors.append(f"[안식플래그누락] week {n}: 보호 주간인데 weeks[].rest_protected≠true — sabbath-protector 표기 누락")

    # 8. 3중 정합 — 간극 경고
    for tc in _ld(c.get("tri_consistency")):
        if tc.get("aligned") is False:
            warnings.append(f"[정합간극] {tc.get('quarter')}분기 설교–행사–사역 어긋남: {tc.get('gap', '간극 미서술')}")

    # 9. 시즌 정렬 — 어긋남 경고
    for sa in _ld(c.get("season_alignment")):
        if sa.get("aligned") is False:
            warnings.append(f"[시즌어긋남] {sa.get('quarter')}분기 시즌 강조와 어긋남: {sa.get('note', '미서술')}")

    # 10. 확정 게이트
    confirmed = c.get("confirmed")
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 검토·확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    # 11. 표어 echo 일치
    if theme and ie.get("chosen_theme") and ie.get("chosen_theme") != theme:
        warnings.append("[표어불일치] meta.chosen_theme ≠ inputs_echo.chosen_theme — vision.chosen 재확인")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_calendar.py <calendar.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            c = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)
    if not isinstance(c, dict):
        print("[오류] 최상위가 객체(JSON object)가 아님 — calendar.json은 {meta,inputs_echo,weeks,…} 구조여야 함"); sys.exit(2)

    errors, warnings = validate(c)
    print("=" * 60)
    print("churchplan-ministry-calendar 통합 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for er in errors:
            print(f"  ✗ {er}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 상속되지 않은 것을 지어내거나 격자를 깨뜨리지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 모든 통합이 상속에서 왔고, 52주 격자 온전, 밀집·안식 표시됨. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
