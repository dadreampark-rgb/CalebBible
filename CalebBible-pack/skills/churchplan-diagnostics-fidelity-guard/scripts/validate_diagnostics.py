#!/usr/bin/env python3
"""
validate_diagnostics.py — churchplan-diagnostics 진단 결과(diagnosis.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 진단 거울이 아첨(추정의 사실 둔갑)도 정죄도 하지 않게 지킨다.
추정이 점값으로 둔갑했는지, 회상에 없던 수치가 끼었는지, 병목 방향이 비었는지를 검사한다.

사용:  python3 validate_diagnostics.py <diagnosis.json> [recall-dataset.json]
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import sys

REQUIRED_BLOCKS = ["meta", "trend", "funnel", "health_radar", "findings"]
CONFIDENCE_VALUES = {"상", "중", "하"}
TREND_VALUES = {"↑", "↓", "→"}
HEALTH_AREAS = ["예배", "말씀", "교제", "전도", "양육", "봉사", "선교", "재정"]


def is_missing(m):
    if not isinstance(m, dict):
        return False
    return (m.get("value", "x") is None or m.get("range", "x") is None) and m.get("status") == "미회상"


def is_number(x):
    """bool은 int 서브클래스이므로 선제 배제하고 진짜 숫자만 True."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


import re

# 점값 둔갑(문자열판): 신뢰 '하/중'인데 정밀 단일 수치를 *문자열*로 적어 숫자 게이트 우회.
# 예 "187"·"187명"·"4520만원" → 둔갑(차단).  허용: 범위표기("8~12가정")·완곡어("약 130명","130명 내외")·서술("약간 감소").
_HEDGE_MARKERS = ("약", "내외", "이상", "이하", "정도", "쯤", "여명", "여 명", "여가정",
                  "가량", "남짓", "미만", "초과", "±", "안팎")
_SPAN_MARKERS = ("~", "～", "-", "–", "—", "부터", "에서")


def is_bare_point_string(s):
    """문자열이 '범위·완곡 없는 단일 정밀 수치'면 True(점값 둔갑). 단위 접미(명/가정/원/만원/% 등)는 허용."""
    if not isinstance(s, str):
        return False
    t = s.strip()
    if any(mk in t for mk in _SPAN_MARKERS) or any(mk in t for mk in _HEDGE_MARKERS):
        return False
    nums = re.findall(r"\d+", t)
    return len(nums) == 1

# 회상→진단 매핑: recall.scale 키 ↔ diagnosis.trend 라벨 키워드
SCALE_LABEL_KEYS = {
    "sunday_attendance": ("출석",),
    "offering": ("헌금",),
    "registrations": ("등록",),
}


def value_span(v):
    """문자열/숫자 value에서 수치 범위 [lo,hi]를 추출. 못 뽑으면 None.
    예 '8~12가정'→[8,12], '2명'→[2,2], 131→[131,131], range list는 그대로."""
    if is_number(v):
        return [v, v]
    if isinstance(v, list) and len(v) == 2 and is_number(v[0]) and is_number(v[1]):
        return [v[0], v[1]]
    if isinstance(v, str):
        nums = [int(n) for n in re.findall(r"\d+", v)]
        if nums:
            return [min(nums), max(nums)]
    return None


def metric_span(m):
    """diagnosis 메트릭 dict에서 수치 범위 추출(range 우선, 없으면 value/point)."""
    if not isinstance(m, dict):
        return value_span(m)
    if isinstance(m.get("range"), list):
        return value_span(m["range"])
    for fld in ("value", "point"):
        if fld in m:
            return value_span(m[fld])
    return None


def spans_overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def crosscheck_recall(diag, recall, errors, warnings):
    """회상 대조 — diagnosis 수치가 recall에 근거가 있는지 교차 검사(SKILL #4·schema 3행).
    recall에 없던 수치를 새로 지어내면 위반. 회상이 단일 진실."""
    # 1) 추이(scale) 수치 대조: 라벨 키워드로 매칭, 회상 범위와 겹치지 않으면 위반.
    scale = recall.get("scale", {}) if isinstance(recall.get("scale"), dict) else {}
    r_spans = {}
    for skey, kws in SCALE_LABEL_KEYS.items():
        sblk = scale.get(skey)
        if isinstance(sblk, dict) and sblk.get("status") != "미회상":
            sp = metric_span(sblk)
            if sp is not None:
                r_spans[skey] = (kws, sp)
    trend_metrics = diag.get("trend", {}).get("metrics", []) if isinstance(diag.get("trend"), dict) else []
    for m in trend_metrics if isinstance(trend_metrics, list) else []:
        if not isinstance(m, dict):
            continue
        if m.get("status") == "미회상":
            continue
        label = str(m.get("label", ""))
        dsp = metric_span(m)
        if dsp is None:
            continue
        for skey, (kws, rsp) in r_spans.items():
            if any(kw in label for kw in kws):
                if not spans_overlap(dsp, rsp):
                    errors.append(
                        f"[회상이탈] trend.{label}: 진단 수치 {dsp}가 회상 scale.{skey} {rsp}와 겹치지 않음 "
                        f"— 회상에 없던 수치 생성 (회상으로 되돌려라)")
                break
    # 2) 8영역 점수 대조: 회상 health_8areas에 있는 영역은 점수가 그대로여야 함(재계산 금지).
    r_health = recall.get("health_8areas", {}) if isinstance(recall.get("health_8areas"), dict) else {}
    hr = diag.get("health_radar", {})
    d_area_list = hr.get("areas", []) if isinstance(hr, dict) else []
    d_areas = {a.get("area"): a for a in (d_area_list if isinstance(d_area_list, list) else [])
               if isinstance(a, dict)}
    for area, rblk in r_health.items():
        if not isinstance(rblk, dict):
            continue
        r_score = rblk.get("score")
        da = d_areas.get(area)
        if da is None or not isinstance(da, dict):
            continue
        d_score = da.get("score")
        if is_number(r_score) and is_number(d_score) and r_score != d_score:
            errors.append(
                f"[회상이탈] health_radar.{area}: 진단 score {d_score} ≠ 회상 health_8areas.{area} score {r_score} "
                f"— 점수 재계산/지어내기 금지 (회상값 전사)")


def check_metric(path, m, errors):
    """수치 메트릭 검사: 신뢰 동반·단정스칼라 금지·신뢰'하' 점값 둔갑 금지."""
    if not isinstance(m, dict):
        if is_number(m):
            errors.append(f"[단정스칼라] {path}: 범위·신뢰 없는 맨숫자 '{m}' — 추정의 사실 둔갑")
        else:
            errors.append(f"[형식오류] {path}: 메트릭은 객체여야 함")
        return
    if is_missing(m):
        return
    conf = m.get("confidence")
    if conf is None:
        errors.append(f"[신뢰누락] {path}: confidence(상/중/하) 없음")
    elif conf not in CONFIDENCE_VALUES:
        errors.append(f"[신뢰오류] {path}: confidence '{conf}'")
    # 점값 둔갑: 신뢰 '하/중'인데 정밀 정수/실수 단정 + range 없음.
    # 스키마는 스칼라 수치를 value 필드로 적으므로(예 value:131) point·value 둘 다 검사.
    if "range" not in m:
        for fld in ("point", "value"):
            if fld not in m or conf not in ("하", "중"):
                continue
            if is_number(m[fld]):
                errors.append(f"[점값둔갑] {path}: 신뢰 '{conf}' 인데 정밀 {fld}={m[fld]} 단정 (range로 되돌려라)")
            elif is_bare_point_string(m[fld]):
                errors.append(f"[점값둔갑] {path}: 신뢰 '{conf}' 인데 정밀 {fld}='{m[fld]}' 문자열 단정 — "
                              f"범위·완곡 없는 점값 둔갑 (range 또는 '약 N·N내외'로 되돌려라)")
    # range는 [lo,hi] 2-원소 숫자 배열이어야 함(렌더러가 max/곱셈하므로 형식 위반은 차단).
    if "range" in m:
        rng = m["range"]
        if not (isinstance(rng, list) and len(rng) == 2 and is_number(rng[0]) and is_number(rng[1])):
            errors.append(f"[범위형오류] {path}: range는 [lo,hi] 2-원소 숫자 배열이어야 함 (받음 '{rng}')")
        elif rng[0] > rng[1]:
            errors.append(f"[범위역전] {path}: range lo({rng[0]}) > hi({rng[1]})")
    # value/range 둘 다 없고 미회상도 아니면
    if "value" not in m and "range" not in m and "point" not in m:
        errors.append(f"[누락] {path}: value/range 없음 (미회상이면 status='미회상')")
    if m.get("trend") is not None:
        if m["trend"] not in TREND_VALUES:
            errors.append(f"[추이오류] {path}: trend '{m['trend']}'")
        elif not m.get("basis"):
            errors.append(f"[근거누락] {path}: trend 있으나 basis 없음")


def _dict(x):
    """블록 값이 dict가 아니면 빈 dict로 방어(적대적 입력 크래시 차단)."""
    return x if isinstance(x, dict) else {}


def _list(x):
    return x if isinstance(x, list) else []


def _require_list(parent, key, path, errors):
    """parent[key]가 존재하지만 truthy 비-list(문자열·정수·dict)면 형식오류 1건 등록 후 []로 환원.
    부재(None·미존재)는 조용히 []. 조용한 통과 차단(클린 EXIT 1)."""
    v = parent.get(key)
    if v is None:
        return []
    if not isinstance(v, list):
        errors.append(f"[형식오류] {path}는 배열이어야 함 (받음: {type(v).__name__})")
        return []
    return v


def validate(diag, recall):
    errors, warnings = [], []

    for blk in REQUIRED_BLOCKS:
        if blk not in diag:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")
        elif not isinstance(diag.get(blk), dict):
            # 필수 dict 블록이 truthy 비-dict(문자열·리스트·정수)면 _dict로 안전 환원하되
            # 조용한 통과 금지 — 형식오류 위반 1건 등록해 클린 EXIT 1 보장.
            errors.append(f"[형식오류] 최상위 '{blk}'는 객체여야 함 (받음: {type(diag.get(blk)).__name__})")

    # meta.church_context
    ctx = _dict(_dict(diag.get("meta")).get("church_context"))
    if not ctx:
        warnings.append("[컨텍스트] meta.church_context 비어 있음 — recall에서 복사 권장")

    # trend
    for i, m in enumerate(_require_list(_dict(diag.get("trend")), "metrics", "trend.metrics", errors)):
        label = m.get("label", i) if isinstance(m, dict) else i
        check_metric(f"trend.metrics[{label}]", m, errors)

    # funnel — 병목 방향(진단의 심장) 필수
    fn = _dict(diag.get("funnel"))
    for i, st in enumerate(_require_list(fn, "stages", "funnel.stages", errors)):
        if not isinstance(st, dict):
            errors.append(f"[형식오류] funnel.stages[{i}]: 객체여야 함 (받음: {type(st).__name__})")
            continue
        # value·range·point 중 무엇으로 와도 메트릭 검사(범위형·역전·점값 둔갑) — range만 있고
        # value 없는 stage가 역전/오염 범위로 새던 누수 차단(funnel-analysis 산출 정직성).
        if "value" in st or "range" in st or "point" in st:
            check_metric(f"funnel.{st.get('name','?')}", st, errors)
    if not fn.get("bottleneck_direction"):
        errors.append("[병목누락] funnel.bottleneck_direction 비어 있음 — 진단의 심장")

    # health_radar
    hr = _dict(diag.get("health_radar"))
    area_items = _require_list(hr, "areas", "health_radar.areas", errors)
    for i, a in enumerate(area_items):
        if not isinstance(a, dict):
            errors.append(f"[형식오류] health_radar.areas[{i}]: 객체여야 함 (받음: {type(a).__name__})")
    areas = {a.get("area"): a for a in area_items if isinstance(a, dict)}
    for area in HEALTH_AREAS:
        if area not in areas:
            warnings.append(f"[영역누락] health_radar.{area} 없음")
            continue
        a = areas[area]
        score = a.get("score")
        if score is None:
            if a.get("status") != "미회상":
                errors.append(f"[점수누락] health_radar.{area}: score 없음")
        elif isinstance(score, bool):
            errors.append(f"[점수형오류] health_radar.{area}: score가 boolean({score}) — 1~5 숫자여야 함")
        elif not (is_number(score) and 1 <= score <= 5):
            errors.append(f"[점수범위] health_radar.{area}: score '{score}' 1~5 아님")
        elif not a.get("basis"):
            errors.append(f"[근거누락] health_radar.{area}: score 있으나 basis 없음")
        if a.get("confidence") and a["confidence"] not in CONFIDENCE_VALUES:
            errors.append(f"[신뢰오류] health_radar.{area}: confidence '{a['confidence']}'")

    # findings — 병목 헤드라인 + 근거 추적성
    fd = _dict(diag.get("findings"))
    if not str(fd.get("bottleneck_headline") or "").strip():
        errors.append("[헤드라인누락] findings.bottleneck_headline 비어 있음 — 진단의 첫 문장")
    for key in ("strengths_top3", "needs_care_top3"):
        for i, item in enumerate(_require_list(fd, key, f"findings.{key}", errors)):
            if isinstance(item, dict):
                if not item.get("basis"):
                    errors.append(f"[근거누락] findings.{key}[{i}]: basis 없음 (회상 추적 불가)")
            else:
                # 문자열 항목은 basis 추적 불가 — 근거 없는 과장 서술이 우회 통과하지 못하게 위반.
                errors.append(f"[근거누락] findings.{key}[{i}]: basis 없는 문자열 '{item}' — {{text,basis}} 객체로 (회상 추적 불가)")

    # recall 대조 (주어진 경우)
    if isinstance(recall, dict):
        r_ctx = _dict(_dict(recall.get("meta")).get("church_context"))
        if r_ctx and ctx and r_ctx.get("denomination") != ctx.get("denomination"):
            warnings.append("[컨텍스트불일치] diagnosis와 recall의 denomination 다름 — 확인")
        if not _dict(diag.get("meta")).get("source_recall"):
            warnings.append("[출처표기] meta.source_recall 비어 있음 — recall 출처 표기 권장")
        # 회상 수치·점수 교차 대조 (지어낸 수치 차단)
        crosscheck_recall(diag, recall, errors, warnings)
    elif recall is not None:
        warnings.append("[회상형오류] recall이 JSON 객체가 아님 — 대조 생략")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("사용: python3 validate_diagnostics.py <diagnosis.json> [recall-dataset.json]")
        sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            diag = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}"); sys.exit(2)

    if not isinstance(diag, dict):
        print(f"[오류] diagnosis.json 최상위가 JSON 객체가 아님 (받음: {type(diag).__name__})")
        sys.exit(2)

    recall = None
    if len(sys.argv) >= 3:
        try:
            with open(sys.argv[2], encoding="utf-8") as f:
                recall = json.load(f)
        except Exception as e:
            print(f"[경고] recall 파일 로드 실패(대조 생략): {e}")

    errors, warnings = validate(diag, recall)

    print("=" * 60)
    print("churchplan-diagnostics 진단 거울 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for e in errors:
            print(f"  ✗ {e}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 추정을 점값으로 단정하지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 아첨도 정죄도 없는 정직한 거울. 완료 표시 가능.")
    sys.exit(0)


if __name__ == "__main__":
    main()
