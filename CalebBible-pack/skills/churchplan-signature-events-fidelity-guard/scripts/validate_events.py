#!/usr/bin/env python3
"""
validate_events.py — churchplan-signature-events 핵심 행사(events.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 행사 기획이 세 거짓을 흘리지 않게 지킨다.
  (1) 목적 없는 행사 — serves_axes/rationale 없는 행사("작년에 했으니"의 잔재)
  (2) 행사 과다 — 핵심 행사 5개 초과(행사 수보다 깊이를 깨뜨림)
  (3) 표어 이탈 — 표어 미확정·정합 없는 행사
목사의 행사를 검증하는 것이 아니라, AI가 행사 기획을 오염시켰는지 검사한다.

사용:  python3 validate_events.py <events.json>
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 타입 계약은 검증기·렌더러 공유 모듈로 단일화(ADR-0002). 사본은 sync_shared_assets가 전파.
    from schema_guard import check_types
    from spec_signature_events import SIG_SCHEMA
except ImportError as _imp_err:
    print(f"[오류] 이식 자산 import 실패(schema_guard/spec_signature_events — sync_shared_assets 필요): {_imp_err}")
    sys.exit(2)


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


def _join(seq):
    """리스트를 ', '로 안전하게 잇는다 — build_event_plan.py._join 과 1:1 동일(결정론 대조 계약)."""
    return ", ".join(str(v) for v in _l(seq) if not isinstance(v, (dict, list)))


def _expected_event_goal_map(e):
    """signature_events에서 행사–목표 지도를 100% 결정론으로 조립 —
    blueprint-renderer의 build_event_goal_map 과 byte-for-byte 동일해야 한다(LLM 자유텍스트 차단)."""
    lines = ["| 행사 | 섬기는 축 | 섬기는 목표 | 시기 |", "|---|---|---|---|"]
    for ev in _l(e.get("signature_events")):
        if not isinstance(ev, dict):
            continue
        bp = _d(ev.get("blueprint"))
        lines.append(
            f"| {ev.get('title', '')} | {_join(ev.get('serves_axes'))} "
            f"| {_join(ev.get('serves_goals'))} | {bp.get('timing', '')} |")
    return "\n".join(lines)


AXES = {"영성", "전도", "양육"}
SIG_MAX = 5          # 핵심 행사 상한 (행사 수보다 깊이)
PLAN_YEAR = 2027     # PastorPlan 대상 연도 (절기 날짜·주차 격자 기준)

# 절기 이름 동의어 → easter_calculator weeks 사전의 정식 키
LITURGY_ALIASES = {
    "부활절": "부활주일", "부활주일": "부활주일",
    "성령강림절": "성령강림주일", "성령강림주일": "성령강림주일", "오순절": "성령강림주일",
    "추수감사절": "추수감사주일", "추수감사주일": "추수감사주일", "맥추감사주일": "맥추감사주일",
    "종려주일": "종려주일", "신년주일": "신년주일",
    "삼위일체주일": "삼위일체주일", "어린이주일": "어린이주일", "어버이주일": "어버이주일",
}


def _liturgy_grid():
    """easter_calculator로 절기 주차/날짜·주별 날짜 격자를 결정론 계산. 실패 시 (None, None)."""
    try:
        import easter_calculator as ec
    except ImportError:
        return None, None
    try:
        all_wk = ec.compute_all_week_numbers(PLAN_YEAR)
    except Exception:
        return None, None
    # week_dates 키는 JSON 직렬화로 문자열일 수 있으므로 정수로 정규화
    raw_dates = all_wk.get("week_dates") or {}
    week_dates = {}
    for k, v in raw_dates.items():
        try:
            week_dates[int(k)] = v
        except (TypeError, ValueError):
            continue
    return all_wk.get("weeks") or {}, week_dates


def _parse_week_num(text):
    """'13주(2027-03-28)'·'47주'·'13' 등에서 첫 주차 정수를 추출. 없으면 None."""
    if text is None:
        return None
    m = re.search(r"(\d+)\s*주", str(text))
    if not m:
        m = re.match(r"\s*(\d+)\s*$", str(text))
    return int(m.group(1)) if m else None


def validate(e):
    errors, warnings = [], []
    liturgy_weeks, week_dates = _liturgy_grid()

    # 1. 스키마 필수 블록
    for blk in ("meta", "inputs_echo", "signature_events"):
        if blk not in e:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    # 타입 계약 — 검증기·렌더러 공유 SPEC 한 곳(ADR-0002). 의미 검사는 아래에 잔류.
    errors.extend(check_types(e, SIG_SCHEMA))

    meta = _d(e.get("meta"))

    # 2. 표어
    theme = meta.get("chosen_theme")
    if not theme or not str(theme).strip():
        errors.append("[표어미확정] meta.chosen_theme 비어 있음 — 표어를 먼저 확정하라(vision-discernment #2로)")

    # 3. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 4. 핵심 행사 수 (signature_events 타입은 SPEC이 검사)
    sig = _l(e.get("signature_events"))
    if len(sig) == 0:
        errors.append("[행사없음] signature_events 0개 — 표어를 구현할 핵심 행사가 필요")
    if len(sig) > SIG_MAX:
        errors.append(f"[행사과다] 핵심 행사 {len(sig)}개 — 최대 {SIG_MAX}개(행사 수보다 깊이)")

    # 5. 각 핵심 행사 — 목적 없는 행사 차단
    for i, ev in enumerate(sig):
        if not isinstance(ev, dict):
            continue  # 비-dict 원소 타입 위반은 SPEC이 보고; 의미 검사는 건너뜀
        eid = ev.get("id", i)
        tag = f"signature_events[{eid}]"
        # (하위 필드 타입 — blueprint·sermon_sync·serves_axes/goals·title·원소 — 은 SPEC이 검사)
        if not ev.get("title"):
            errors.append(f"[제목누락] {tag}.title 없음")
        # 목적(섬기는 축) — 핵심
        axes = _l(ev.get("serves_axes"))
        if not axes:
            errors.append(f"[목적없음] {tag}: serves_axes 없음 — '이 행사가 표어의 무엇을 구현하나?'에 답 없는 행사 금지")
        else:
            for a in axes:
                if isinstance(a, str) and a not in AXES:
                    warnings.append(f"[축표기] {tag}: serves_axes '{a}' — 영성|전도|양육 권장(3축)")
        # 근거 추적
        if not ev.get("rationale") or not str(ev.get("rationale")).strip():
            errors.append(f"[근거누락] {tag}: rationale 없음 — 표어·병목·작년효과 중 출처를 밝혀라(garbage-in 차단)")
        # 표어 연결
        if not ev.get("theme_link"):
            warnings.append(f"[표어연결] {tag}: theme_link 없음 — 표어와의 연결 권장")
        # 1페이지 기획안 (flow·resources·purpose/timing/success_signal/audience 타입은 SPEC이 검사)
        bp = _d(ev.get("blueprint"))
        for need in ("purpose", "timing", "success_signal"):
            if not bp.get(need):
                warnings.append(f"[기획안] {tag}.blueprint.{need} 없음 — 1페이지 6필드 권장")
        # 설교 정합 (linked_weeks 타입은 SPEC이 검사)
        sync = _d(ev.get("sermon_sync"))
        if sync and sync.get("aligned") is False:
            warnings.append(f"[설교정합] {tag}: 행사 주간 설교가 행사를 떠받치지 않음(aligned=false) — 시기 재조정/설교 보강 검토")
        # linked_weeks 결정론 검증 — 1~총주차 범위 내 정수인가(존재하지 않는 주차 매핑 차단)
        if week_dates:
            total = max(week_dates) if week_dates else 52
            for lw in _l(sync.get("linked_weeks")):
                if not isinstance(lw, int) or isinstance(lw, bool) or not (1 <= lw <= total):
                    errors.append(f"[주차범위] {tag}.sermon_sync.linked_weeks {lw!r} — 1~{total}주 범위 정수 아님(존재하지 않는 주차 매핑 금지)")

    # 5a. (regular_events·pruned_events·warnings 의 list·원소 dict 타입은 SPEC이 검사)

    # 5b. 정기 행사 절기 날짜·주차 결정론 대조 (날짜 지어내기 차단)
    #     regular_events[].when의 주차/날짜를 easter_calculator 정규 절기 격자와 비교한다.
    if liturgy_weeks and week_dates:
        for i, r in enumerate(_l(e.get("regular_events"))):
            if not isinstance(r, dict):
                continue  # 비-dict 원소 타입 위반은 SPEC이 보고
            name = r.get("name", "")
            when = r.get("when", "")
            canon = LITURGY_ALIASES.get(str(name).strip())
            wk = _parse_week_num(when)
            if canon and canon in liturgy_weeks:
                ref = liturgy_weeks[canon]
                ref_week, ref_date = ref.get("week"), ref.get("date")
                if wk is not None and wk != ref_week:
                    errors.append(
                        f"[절기주차] regular_events[{i}] '{name}': when '{when}'의 주차 {wk}주 "
                        f"≠ 정규 절기 {ref_week}주({ref_date}) — 날짜/주차 지어내기 금지")
                # when에 날짜(YYYY-MM-DD)가 박혀 있으면 정규 날짜와 대조
                dm = re.search(r"(\d{4}-\d{2}-\d{2})", str(when))
                if dm and ref_date and dm.group(1) != ref_date:
                    errors.append(
                        f"[절기날짜] regular_events[{i}] '{name}': when 날짜 {dm.group(1)} "
                        f"≠ 정규 절기 날짜 {ref_date} — 절기 날짜 지어내기 금지")
            else:
                # 정규 절기 사전에 없는 행사라도, when에 주차+날짜가 둘 다 있으면 격자와 대조
                dm = re.search(r"(\d{4}-\d{2}-\d{2})", str(when))
                if wk is not None and dm:
                    grid_date = week_dates.get(wk)
                    if grid_date and dm.group(1) != grid_date:
                        errors.append(
                            f"[주차날짜] regular_events[{i}] '{name}': {wk}주 날짜 {dm.group(1)} "
                            f"≠ 주별 격자 날짜 {grid_date} — 날짜 지어내기 금지")

    # 5c. event_goal_map 결정론 대조 (LLM 자유텍스트·지어낸 지도 차단)
    #     존재하면 signature_events에서 재계산한 정규 지도와 1:1 일치해야 한다.
    #     blueprint-renderer가 결정론으로 기록하는 필드 — 일치 않으면 사람·LLM이 손댄 것.
    egm = e.get("event_goal_map")
    if egm is not None:
        if not isinstance(egm, str):
            errors.append(f"[지도형식] event_goal_map가 문자열이 아님 — {type(egm).__name__}(결정론 표여야 함)")
        elif egm.strip():
            if egm != _expected_event_goal_map(e):
                errors.append(
                    "[지도불일치] event_goal_map가 signature_events에서 계산한 정규 지도와 다름 "
                    "— LLM 자유텍스트·지어낸 행/축/목표/시기 금지(blueprint-renderer 재실행으로 재기록)")

    # 6. 확정 게이트
    confirmed = e.get("confirmed")
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 검토·확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    # 7. 표어 echo 일치
    ie = _d(e.get("inputs_echo"))
    if theme and ie.get("chosen_theme") and ie.get("chosen_theme") != theme:
        warnings.append("[표어불일치] meta.chosen_theme ≠ inputs_echo.chosen_theme — vision.chosen 재확인")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_events.py <events.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            e = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(e, dict):
        print("[오류] 최상위가 객체(dict)가 아님 — events.json은 객체여야 함"); sys.exit(2)

    errors, warnings = validate(e)
    print("=" * 60)
    print("churchplan-signature-events 행사 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for er in errors:
            print(f"  ✗ {er}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 목적 없는 행사를 만들거나 행사를 과다하게 벌이지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 모든 행사에 목적·근거 있음, 핵심 3~5개 이내, 표어 정합. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
