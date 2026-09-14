#!/usr/bin/env python3
"""
validate_recall_dataset.py — churchplan-guided-recall 표준 회상 데이터셋 결정론 검증기.

목적(ABSOLUTE ANCHOR #2 garbage-in 차단): 회상에 없던 임의 수치·단정값이 다음
스킬로 흘러가지 못하게, dataset-builder 산출 JSON을 구조적으로 검사한다.
목사의 기억을 검증하는 것이 아니라, AI가 데이터를 오염시켰는지 검사한다.

사용:  python3 validate_recall_dataset.py <recall-dataset.json 경로>
종료코드: 0 = 통과, 1 = 위반 발견, 2 = 파일/JSON 오류
이 스크립트는 외부 의존성이 없다(표준 라이브러리만).
"""
import json
import os
import re
import sys

# 공유 결정론 자산 — 같은 scripts/ 폴더의 byte-identical 복사본에서 import.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bible_validator import validate_reference, parse_reference


# ── 비-dict 방어 헬퍼 ('truthy 비-dict subfield' 결함 클래스 차단) ──────────
def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []

# ── 스키마 상수 (단일 진실) ───────────────────────────────────────────────
REQUIRED_BLOCKS = [
    "meta", "calendar_timeline", "people", "scale", "heart", "health_8areas",
]
CONFIDENCE_VALUES = {"상", "중", "하"}
TREND_VALUES = {"↑", "↓", "→"}
HEALTH_AREAS = ["예배", "말씀", "교제", "전도", "양육", "봉사", "선교", "재정"]
# scale/people 안에서 "수치 메트릭"으로 취급해 confidence를 요구할 블록
SCALE_METRICS = ["sunday_attendance", "offering", "registrations", "small_groups"]
PEOPLE_METRICS = ["new_families", "settled", "left", "new_leaders"]

# 헌금(offering) 절대 금액 차단 패턴 — scale-recall은 "결산 파일 없이 비율 감각·증감 방향만"
# 받도록 명시(SKILL.md). 결산서 없는 회상에 박힌 절대 금액(₩·원·만원·억·달러)은 지어낸 수치
# 위험이 크고, 그대로 resource-aligner(#8 '절대 금액 금지' 최우선 규칙)로 흘러간다 → garbage-in.
# 통화는 '숫자 선행' 시에만 금액으로 인정해 후원·원로목사·백만 영혼 등 정상 어휘 오탐을 차단.
# 순수 한글 만 단위 금액('백만원'·'천만원' — 숫자 없이 통화 직결)도 차단('백만 영혼'은 뒤가 통화(원)가
# 아니므로 통과 — 거짓양성 0 검증). (이 의미 검사는 각 스크립트 잔류 — 공유자산 아님)
# 숫자와 통화 사이 다리는 금액 자릿수(백만/천만/만/천/억)만 허용 — 과거 [가-힣]? 는 '2027 자원'·
# '2030 지원'처럼 숫자 뒤 무관한 단어를 절대금액으로 오인했다(거짓양성, resource-aligner MONEY_RE와 동일 수정).
OFFERING_MONEY_RE = re.compile(
    r"(₩|\$|(?:USD|KRW|won)\s*[0-9]|[0-9][0-9,\.]*\s*(?:백만|천만|만|천|억)?\s*(원|만원|천원|억|백만|달러|won|USD|KRW)|(백만|천만)\s*원)"
)


def is_missing(metric):
    """미회상으로 정직하게 비워졌는가: value/range가 null이고 status가 '미회상'."""
    if not isinstance(metric, dict):
        return False
    has_null_value = metric.get("value", "x") is None or metric.get("range", "x") is None
    return has_null_value and metric.get("status") == "미회상"


def check_metric(path, metric, errors):
    """수치 메트릭 1개 검사: confidence 동반, 단정 스칼라 금지, 가정 플래그."""
    # 1) 단정 스칼라 적발 — 메트릭이 객체가 아니라 맨 숫자/문자면 위반
    if not isinstance(metric, dict):
        if isinstance(metric, (int, float)):
            errors.append(f"[단정스칼라] {path}: 범위·신뢰 없는 맨숫자 '{metric}'. "
                          f"{{range/value, confidence}} 객체로 받아야 함")
        else:
            errors.append(f"[형식오류] {path}: 메트릭은 객체여야 함 (현재 {type(metric).__name__})")
        return

    # 2) 미회상이면 정직한 null 처리만 확인하고 통과
    if is_missing(metric):
        return

    # 3) value 또는 range 중 하나는 있어야 함
    if "value" not in metric and "range" not in metric:
        errors.append(f"[누락] {path}: value 또는 range 없음. 미회상이면 value=null + status='미회상'로 두라")

    # 3-1) value 안에 박힌 정밀 단일 숫자 적발 — '모든 수치는 범위로' 강제.
    #      범위·구간 텍스트('120~140', '약간 감소')는 문자열이므로 영향 없음.
    v = metric.get("value")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        errors.append(f"[점값위장] {path}: value에 범위·신뢰 없는 정밀 단일 숫자 '{v}' — "
                      f"범위(range:[lo,hi]) 또는 구간 표현으로 받아야 함")

    # 3-2) range 구조 검사 — [lo,hi] 2원소 숫자 리스트, lo<=hi, 음수 금지
    if "range" in metric and metric["range"] is not None:
        rng = metric["range"]
        if (not isinstance(rng, list) or len(rng) != 2
                or not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in rng)):
            errors.append(f"[범위형식오류] {path}: range는 [lo,hi] 숫자 2원소 리스트여야 함 (현재 {rng!r})")
        else:
            lo, hi = rng
            if lo > hi:
                errors.append(f"[범위순서오류] {path}: range lo({lo}) > hi({hi})")
            if lo < 0 or hi < 0:
                errors.append(f"[범위음수] {path}: range에 음수 {rng} — 출석·헌금 등은 음수일 수 없음")

    # 4) confidence 동반 필수
    conf = metric.get("confidence")
    if conf is None:
        errors.append(f"[신뢰누락] {path}: confidence(상/중/하) 없음")
    elif conf not in CONFIDENCE_VALUES:
        errors.append(f"[신뢰오류] {path}: confidence '{conf}' 는 상/중/하 중 하나여야 함")

    # 5) 신뢰 '하'는 assumption 플래그 필수
    if conf == "하" and metric.get("assumption") is not True:
        errors.append(f"[가정플래그] {path}: 신뢰 '하' 항목에 assumption:true 없음 "
                      f"(워크샵 후 확인 대상으로 표시되어야 함)")

    # 6) trend가 있으면 basis(근거) 필수 — 근거 없는 추이는 망상 위험
    if metric.get("trend") is not None:
        if metric["trend"] not in TREND_VALUES:
            errors.append(f"[추이오류] {path}: trend '{metric['trend']}' 는 ↑/↓/→ 중 하나여야 함")
        if not metric.get("basis"):
            errors.append(f"[근거누락] {path}: trend가 있으나 basis(근거) 없음")


def check_offering_money(offering, errors):
    """헌금(offering) 안에 박힌 절대 금액을 결정론으로 적발(garbage-in 차단).

    scale.offering의 텍스트 필드(value·basis·ratio_sense 값)를 스캔해 '숫자 선행'
    절대 금액이 끼었으면 위반. 비율(%)·증감 방향·범위는 정상 — 패턴이 통화 토큰만 잡는다.
    """
    if not isinstance(offering, dict):
        return
    texts = []
    v = offering.get("value")
    if isinstance(v, str):
        texts.append(("scale.offering.value", v))
    b = offering.get("basis")
    if isinstance(b, str):
        texts.append(("scale.offering.basis", b))
    rs = offering.get("ratio_sense")
    if isinstance(rs, dict):
        for rk, rv in rs.items():
            if isinstance(rv, str):
                texts.append((f"scale.offering.ratio_sense.{rk}", rv))
    for path, text in texts:
        m = OFFERING_MONEY_RE.search(text)
        if m:
            errors.append(
                f"[절대금액] {path}: '{m.group(0).strip()}' (\"{text[:30]}\") — "
                f"헌금은 결산 없이 비율(%)·증감 방향만(scale-recall). 절대 금액은 회상 단계에서 받지 않음"
            )


def validate(data):
    errors, warnings = [], []

    # A) 필수 블록 존재 + 비-dict/비-list 형식 차단 (조용한 통과 금지)
    #    dict-기대 블록이 truthy 비-dict면 _d로 안전 환원하되 [형식오류] 등록.
    DICT_BLOCKS = {"meta", "people", "scale", "heart", "health_8areas"}
    for blk in REQUIRED_BLOCKS:
        if blk not in data:
            errors.append(f"[블록누락] 최상위 '{blk}' 블록 없음")
            continue
        if blk in DICT_BLOCKS and not isinstance(data[blk], dict):
            errors.append(f"[형식오류] 최상위 '{blk}' 블록은 객체(dict)여야 함 "
                          f"(현재 {type(data[blk]).__name__}) — 안전 환원 후 검사")
        elif blk == "calendar_timeline" and not isinstance(data[blk], list):
            errors.append(f"[형식오류] 최상위 'calendar_timeline' 블록은 리스트여야 함 "
                          f"(현재 {type(data[blk]).__name__}) — 안전 환원 후 검사")

    # B) meta.church_context (hardcoding 금지 — 컨텍스트가 비면 안 됨)
    meta = _d(data.get("meta"))
    raw_ctx = meta.get("church_context")
    ctx = _d(raw_ctx)
    if raw_ctx is not None and not isinstance(raw_ctx, dict):
        errors.append(f"[형식오류] meta.church_context 는 객체(dict)여야 함 "
                      f"(현재 {type(raw_ctx).__name__})")
    elif not ctx:
        errors.append("[컨텍스트누락] meta.church_context 비어 있음 — 시작 시 교단/규모/지역 1회 질문 결과가 없음")

    # C) calendar_timeline — 1~12월 커버
    cal = _l(data.get("calendar_timeline"))
    if isinstance(cal, list):
        months = {m.get("month") for m in cal if isinstance(m, dict)}
        # 최신 편향 차단 게이트: month 1~12 항목이 *물리적으로 모두 존재*해야 함.
        # 내용(events)은 비워도 되나, 항목 자체 누락은 위반(calendar-walk 1→12월 강제 순회).
        missing_months = [m for m in range(1, 13) if m not in months]
        if missing_months:
            errors.append(f"[달항목누락] calendar_timeline에 month 항목 자체가 없음: {missing_months} "
                          f"(내용은 비워도 항목은 1~12 모두 존재해야 함 — 최신 편향 차단)")
        for m in cal:
            if isinstance(m, dict) and m.get("confidence") and m["confidence"] not in CONFIDENCE_VALUES:
                errors.append(f"[신뢰오류] calendar_timeline 월{m.get('month')}: confidence '{m['confidence']}'")

    # D) people 메트릭
    people = _d(data.get("people"))
    for key in PEOPLE_METRICS:
        if key in people:
            check_metric(f"people.{key}", people[key], errors)
    if "funnel_bottleneck" not in people:
        warnings.append("[병목누락] people.funnel_bottleneck 없음 — 깔때기 어디가 새는지 방향이 비었음")

    # E) scale 메트릭
    scale = _d(data.get("scale"))
    for key in SCALE_METRICS:
        if key in scale:
            check_metric(f"scale.{key}", scale[key], errors)
    # E-1) 헌금 절대 금액 차단 — 결산 없는 회상에 박힌 통화 금액은 garbage-in (resource-aligner #8 최우선 규칙 상류 보호)
    check_offering_money(scale.get("offering"), errors)

    # F) heart — 본문/이름 창작 차단 (결정론 게이트 + 휴리스틱)
    heart = _d(data.get("heart"))
    if not any(heart.get(k) for k in ("joys_top3", "pains_top3", "prayer_keywords", "one_wish")):
        warnings.append("[마음공백] heart 블록이 사실상 비어 있음 — vision-discernment(#2) 입력이 부족")

    # F-1) gripping_scriptures 본문 창작 차단 (bible_validator 결정론 검증)
    scriptures = heart.get("gripping_scriptures")
    # 스키마상 리스트. 리스트가 아닌 truthy 값(예 맨 문자열 '로마서 99장')으로 오면
    # 아래 list 검증을 통째로 건너뛰어 가짜 본문이 새는 누수가 생긴다 → 형식오류로 차단.
    if scriptures is not None and not isinstance(scriptures, list):
        errors.append(f"[본문형식오류] heart.gripping_scriptures 는 리스트여야 함 "
                      f"(현재 {type(scriptures).__name__}: {scriptures!r}) — 본문 검증 우회 차단")
    if isinstance(scriptures, list):
        for s in scriptures:
            if not isinstance(s, str):
                errors.append(f"[본문형식오류] heart.gripping_scriptures 항목이 문자열 아님: {s!r}")
                continue
            parsed = parse_reference(s)
            if parsed is None:
                # 파싱 실패가 ① 가짜 책이름+장:절('에녹서 1:1'·'도마복음 3:5')인지 ② 숫자 없는
                # 자유 서술('말씀에 붙들림')인지 구분: 한글 뒤 숫자(장:절 꼴)가 보이면 가짜 책이름
                # 본문창작으로 차단, 숫자 없는 순수 서술만 통과(정경 밖 책 위장 누수 차단).
                if re.search(r"[가-힣]\s*\d", s):
                    errors.append(f"[본문창작] heart.gripping_scriptures '{s}': 정경 66권에 없는 책이름(가짜 본문)")
                continue
            ok, msg = validate_reference(s)
            if not ok:
                # 정경 범위 밖 인용 = 객관적 본문 창작 → 위반(차단).
                errors.append(f"[본문창작] heart.gripping_scriptures '{s}': {msg}")
            elif parsed.get("verse_start") is not None:
                # 정경 범위 안이나 절 단위까지 정밀 인용 — 회상은 통상 장 단위.
                # 절 정밀 인용은 창작 위험 → '미확정' 표기 권고 경고.
                warnings.append(f"[본문정밀인용] heart.gripping_scriptures '{s}': 절 단위 정밀 인용 — "
                                f"목사가 정확 장·절을 말한 게 아니면 장 단위로 되돌리거나 '본문 미확정' 표시")

    # F-2) names_recalled 인명 창작 신호 — 회상 근거(confidence '하'/assumption)와 교차 플래그
    names = heart.get("names_recalled")
    if isinstance(names, list):
        for n in names:
            if not isinstance(n, str):
                errors.append(f"[인명형식오류] heart.names_recalled 항목이 문자열 아님: {n!r}")

    # G) health_8areas — 8영역 score 1~5 + 근거
    health = _d(data.get("health_8areas"))
    for area in HEALTH_AREAS:
        if area not in health:
            warnings.append(f"[영역누락] health_8areas.{area} 없음")
            continue
        a = health[area]
        if not isinstance(a, dict):
            errors.append(f"[형식오류] health_8areas.{area}: 객체여야 함")
            continue
        score = a.get("score")
        if score is None:
            if a.get("status") != "미회상":
                errors.append(f"[점수누락] health_8areas.{area}: score 없음 (미회상이면 status='미회상')")
        elif not (isinstance(score, int) and not isinstance(score, bool) and 1 <= score <= 5):
            errors.append(f"[점수범위] health_8areas.{area}: score '{score}' 는 1~5 정수여야 함")
        else:
            if not a.get("basis"):
                errors.append(f"[근거누락] health_8areas.{area}: score는 있으나 basis(근거) 없음 — 점수 단독 금지")
            if a.get("confidence") and a["confidence"] not in CONFIDENCE_VALUES:
                errors.append(f"[신뢰오류] health_8areas.{area}: confidence '{a['confidence']}'")
            if a.get("trend") and a["trend"] not in TREND_VALUES:
                errors.append(f"[추이오류] health_8areas.{area}: trend '{a['trend']}'")

    # H) integrity 블록 교차검증 (존재할 때만 — fidelity-guard가 채운 뒤 일관성 확인)
    integrity = data.get("integrity")
    if isinstance(integrity, dict):
        # 실제 데이터에서 신뢰 카운트·가정 표시 항목을 결정론으로 수집
        actual_conf = {"상": 0, "중": 0, "하": 0}
        actual_assumptions = set()
        scan = []
        for key in PEOPLE_METRICS:
            if isinstance(people.get(key), dict):
                scan.append((f"people.{key}", people[key]))
        for key in SCALE_METRICS:
            if isinstance(scale.get(key), dict):
                scan.append((f"scale.{key}", scale[key]))
        for area in HEALTH_AREAS:
            if isinstance(health.get(area), dict):
                scan.append((f"health_8areas.{area}", health[area]))
        for mpath, m in scan:
            c = m.get("confidence")
            if c in actual_conf:
                actual_conf[c] += 1
            if c == "하" or m.get("assumption") is True:
                actual_assumptions.add(mpath)

        cs = integrity.get("confidence_summary")
        if isinstance(cs, dict):
            for lvl in ("상", "중", "하"):
                claimed = cs.get(lvl)
                if isinstance(claimed, int) and claimed != actual_conf[lvl]:
                    errors.append(f"[무결성불일치] integrity.confidence_summary['{lvl}']={claimed} 이나 "
                                  f"실제 confidence '{lvl}' 항목은 {actual_conf[lvl]}개")

        af = integrity.get("assumptions_flagged")
        if isinstance(af, list):
            claimed_set = {x for x in af if isinstance(x, str)}
            if claimed_set != actual_assumptions:
                missing = actual_assumptions - claimed_set
                extra = claimed_set - actual_assumptions
                detail = []
                if missing:
                    detail.append(f"누락 {sorted(missing)}")
                if extra:
                    detail.append(f"근거없음 {sorted(extra)}")
                errors.append("[무결성불일치] integrity.assumptions_flagged 가 실제 가정 항목과 불일치: "
                              + ", ".join(detail))

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_recall_dataset.py <recall-dataset.json 경로>")
        sys.exit(2)
    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {path}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}")
        sys.exit(2)

    if not isinstance(data, dict):
        print(f"[오류] 최상위가 객체(dict)가 아님 (현재 {type(data).__name__}) — "
              f"recall-dataset.json은 {{...}} 객체여야 함")
        sys.exit(2)

    errors, warnings = validate(data)

    print("=" * 60)
    print("churchplan-guided-recall 회상 데이터셋 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for e in errors:
            print(f"  ✗ {e}")
        print("\n결과: 실패 — 위 항목을 보완 질문으로 되돌려라. 임의로 메우지 말 것.")
        sys.exit(1)
    else:
        print("\n결과: 통과 ✓ — garbage-in 차단 검사 통과. integrity 블록을 채우고 완료 표시 가능.")
        sys.exit(0)


if __name__ == "__main__":
    main()
