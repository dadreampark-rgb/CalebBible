#!/usr/bin/env python3
"""
validate_sermon_plan.py — churchplan-sermon-planner-52 설교 계획(sermon-plan.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 강단 계획이 네 거짓을 흘리지 않게 지킨다.
  (1) 본문 할루시네이션 — 없는 장·절·가짜 책이름 (bible_validator로 결정론 검사)
  (2) 절기 날조 — easter_calculator 산출과 어긋난 절기 주차
  (3) 곡 단정 — 음악 방향에 특정 찬송 번호·제목을 박음(방향만 허용)
  (4) 주해 월권 — Claude가 본문 해석을 "유일·반드시"로 단정
목사의 설교를 검증하는 것이 아니라, AI가 강단 계획을 오염시켰는지 검사한다.

같은 폴더의 easter_calculator.py·bible_validator.py(sermon-planner-52week 이식 자산)를 import한다.

사용:  python3 validate_sermon_plan.py <sermon-plan.json>
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON/의존 오류
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))


def _d(x):
    """truthy 비-dict(리스트·문자열·정수 등)도 안전하게 {}로 치환 — `(x or {})` 결함 차단."""
    return x if isinstance(x, dict) else {}


def _l(x):
    """비-list(문자열·정수 등)는 빈 리스트로 — 문자열 char 순회·crash 차단."""
    return x if isinstance(x, list) else []

try:
    from bible_validator import validate_reference
    from easter_calculator import compute_all_week_numbers, compute_week_date_grid
except ImportError as e:
    print(f"[오류] 이식 자산 import 실패(easter_calculator/bible_validator 동일 폴더 필요): {e}")
    sys.exit(2)

# 곡 단정 패턴 (방향만 허용, 특정 곡 금지)
# 찬송 번호는 ① 찬송/찬양 키워드 + (조사·공백) + N장, 또는 ② 책이름이 선행하지 않는 bare N장.
# 성경 장(예 '로마서 8장'·'시편 23장')은 한글 책이름이 N 앞에 오므로 제외(거짓양성 차단).
# `(?<!\d)`로 번호 첫 자리에 앵커 — 없으면 \d+가 다자리 번호의 끝자리('시편 23장'→'3장')로
# 백트랙해 한글-책이름 lookbehind를 건너뛰는 거짓양성이 난다(다자리 성경 장 오인 차단).
# 키워드는 '찬송가'뿐 아니라 '찬송·찬양' + 조사('찬송은 488장')도 — 책이름(로마서…)은 아니므로
# 거짓양성 없이 한글단어+N장이 bare로 새는 곡 단정('부를 찬송은 488장')을 잡는다.
HYMN_KEYWORD = re.compile(r"(?:찬송가|새찬송가|통일찬송가|찬송|찬양|찬)(?:가|을|를|은|는|이|\s)*\d+\s*장")
HYMN_BARE = re.compile(r"(?<!\d)(?<![가-힣])(?<![가-힣]\s)\d+\s*장")
# 곡 '제목' 인용 — 「…」(홑낫표)와 『…』(겹낫표) 모두. 한국어에서 곡·작품 제목은
# 『…』가 「…」만큼(또는 더) 흔하다. 한쪽만 잡으면 '찬송 405장 『제목』'이 [곡단정의심]
# 경고로 강등돼 EXIT 0으로 새는 누수가 난다 — 번호+제목은 둘 다 hard 위반으로 잡는다.
TITLE_QUOTE = re.compile(r"「[^」]+」|『[^』]+』")
# 주해 월권 패턴
OVERREACH = re.compile(r"유일한\s*해석|해석은\s*하나|반드시\s*\S+\s*(뜻|의미)|이\s*본문은\s*반드시")


def has_hymn_number(blob: str) -> bool:
    """worship_direction에 찬송 '번호'가 박혔는지 — 성경 장 인용은 제외."""
    return bool(HYMN_KEYWORD.search(blob) or HYMN_BARE.search(blob))


# 절기 이름 정규화 — 공백/구두점 제거 + 동의어 매핑으로 변형 표기 흡수.
_OBS_PUNCT = re.compile(r"[\s·,.()\-–~/]")
_OBS_ALIASES = {
    "부활절": "부활주일",
    "추수감사절": "추수감사주일",
    "맥추절": "맥추감사주일",
    "맥추감사절": "맥추감사주일",
    "성탄절": "성탄주일",
    "송구영신": "송구영신주일",
    "광복절": "광복절통일주일",
    "통일주일": "광복절통일주일",
}


def normalize_observance(name: str) -> str:
    n = _OBS_PUNCT.sub("", str(name))
    return _OBS_ALIASES.get(n, n)


def observance_matches(obs: str, expected: list) -> bool:
    """절기 라벨 매칭 — 정규화 후 부분일치(변형 표기·공백·동의어 흡수)."""
    o = normalize_observance(obs)
    for e in expected:
        en = normalize_observance(e)
        if o == en or o in en or en in o:
            return True
    return False


def validate(p):
    errors, warnings = [], []

    # 1. 스키마 필수 블록
    for blk in ("meta", "inputs_echo", "weeks"):
        if blk not in p:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    meta = p.get("meta")
    if not isinstance(meta, dict):
        if meta is not None:
            errors.append(f"[형식오류] meta가 객체(dict)가 아님: {type(meta).__name__}")
        meta = {}

    # inputs_echo는 schema상 dict — 비-dict면 형식오류 등록(조용한 통과 금지) 후 안전 환원
    if "inputs_echo" in p and not isinstance(p.get("inputs_echo"), dict):
        errors.append(f"[형식오류] inputs_echo가 객체(dict)가 아님: {type(p.get('inputs_echo')).__name__}")
    # weeks는 schema상 list — 비-list 비-None이면 형식오류 등록(아래 _l로 안전 순회)
    if "weeks" in p and p.get("weeks") is not None and not isinstance(p.get("weeks"), list):
        errors.append(f"[형식오류] weeks가 배열(list)이 아님: {type(p.get('weeks')).__name__}")

    # 2. 표어
    theme = meta.get("chosen_theme")
    if not theme or not str(theme).strip():
        errors.append("[표어미확정] meta.chosen_theme 비어 있음 — 표어를 먼저 확정하라(vision-discernment #2로)")

    # 3. 연도 — 유효 정수 + datetime/Computus 유효 범위(1583~9999). 범위 밖 정수(0·음수·>9999·bool)는
    #    절기·날짜격자 산출이 조용히 실패해 절기 오배치·격자 정직성 게이트가 무력화되므로 위반으로 막는다.
    year = meta.get("year")
    year_ok = isinstance(year, int) and not isinstance(year, bool) and 1583 <= year <= 9999
    if not year_ok:
        errors.append(f"[연도오류] meta.year '{year}' — 절기 산출에 1583~9999 정수 연도 필요")

    # 4. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 절기 산출 (연도 정상일 때) + 주차→일요일 날짜 격자 + 절기명→정답주차 역매핑
    expected_obs = {}
    name_to_week = {}  # 정규화 절기명 → 산출상 정답 주차(절기 오배치 역검사용)
    date_grid = {}
    if year_ok:
        try:
            cal = compute_all_week_numbers(year)
            for name, info in cal["weeks"].items():
                wk = info["week"]
                if isinstance(wk, int):
                    expected_obs.setdefault(wk, []).append(name)
                    name_to_week[normalize_observance(name)] = wk
        except Exception as e:
            warnings.append(f"[절기산출] {year}년 절기 산출 실패: {e}")
        try:
            date_grid = compute_week_date_grid(year)  # {주차: 'YYYY-MM-DD'}
        except Exception as e:
            warnings.append(f"[날짜격자] {year}년 주차 날짜 격자 산출 실패: {e}")

    # 5~9. 주차별 검사 — weeks가 비-list(문자열·정수)면 빈 순회로 안전 환원(char 순회 차단)
    weeks = _l(p.get("weeks"))
    seen = set()
    for w in weeks:
        if not isinstance(w, dict):
            errors.append(f"[형식오류] weeks 항목이 객체 아님: {w}"); continue
        wn = w.get("week")
        if not isinstance(wn, int):
            errors.append(f"[주차오류] week 번호 정수 아님: {w.get('week')}"); continue
        if wn in seen:
            errors.append(f"[주차중복] {wn}주차 중복 등록")
        seen.add(wn)

        # 날짜 결정론 검증 (위반) — 유효한 ISO 날짜·일요일·week 격자 일치
        date_str = str(w.get("date") or "").strip()
        if date_str:
            try:
                d = date.fromisoformat(date_str)
            except ValueError:
                errors.append(f"[날짜오류] {wn}주차 date '{date_str}' — 유효한 날짜 아님(YYYY-MM-DD)")
            else:
                if d.weekday() != 6:
                    errors.append(f"[비일요일] {wn}주차 date '{date_str}'가 일요일 아님(weekday={d.weekday()})")
                expected_date = date_grid.get(wn)
                if expected_date and date_str != expected_date:
                    errors.append(f"[날짜불일치] {wn}주차 date '{date_str}' != 산출 격자 '{expected_date}'(날짜 지어내기 금지)")

        # 본문 실재 (위반) — 비-문자열(정수 등)은 str 강제(raw traceback 차단)
        primary = str(w.get("primary_text") or "").strip()
        if primary and primary != "본문 미정":
            ok, msg = validate_reference(primary)
            if not ok:
                errors.append(f"[가짜본문] {wn}주차 주본문 '{primary}': {msg}")
        pts = w.get("parallel_texts")
        if pts is not None and not isinstance(pts, list):
            errors.append(f"[형식오류] {wn}주차 parallel_texts가 배열(list)이 아님: {type(pts).__name__}")
        for pt in (pts if isinstance(pts, list) else ([pts] if pts else [])):
            if isinstance(pt, (list, dict)):
                errors.append(f"[형식오류] {wn}주차 parallel_texts 원소가 본문 문자열 아님: {type(pt).__name__}"); continue
            pt = str(pt).strip()
            if pt and pt != "본문 미정":
                ok, msg = validate_reference(pt)
                if not ok:
                    errors.append(f"[가짜본문] {wn}주차 병행본문 '{pt}': {msg}")

        # 절기 일치 (위반) — schema 'observance 있으면 절기 주차 일치(easter_calculator)'는
        # 필수 블록 검사·가드레일 기둥3 '계산값을 따른다'에 따른 hard gate.
        # ① 역검사: obs가 알려진 절기명이면 산출상 정답 주차에 있어야 함(부활주일을 30주에 박는 날조 차단).
        # ② 순검사: 이 주에 산출 절기가 있는데 obs가 그것과 불일치.
        obs = str(w.get("observance") or "").strip()
        if obs and obs != "—":
            norm_obs = normalize_observance(obs)
            if name_to_week and norm_obs in name_to_week:
                correct = name_to_week[norm_obs]
                if correct != wn:
                    errors.append(f"[절기오배치] {wn}주차 '{obs}'는 산출상 {correct}주차 절기 — 절기는 계산값을 따른다(지어내기 금지)")
            elif expected_obs:
                exp = expected_obs.get(wn, [])
                if exp and not observance_matches(obs, exp):
                    errors.append(f"[절기불일치] {wn}주차 '{obs}'가 산출 절기({', '.join(exp)})와 불일치 — 절기는 계산값을 따른다(지어내기 금지)")

        # 곡 단정 (번호+제목 동시 = 위반 / 하나 = 경고)
        # worship_direction이 truthy 비-dict(리스트·문자열)면 .values() raw traceback — _d로 차단 + 형식오류 등록.
        wd_raw = w.get("worship_direction")
        if wd_raw is not None and not isinstance(wd_raw, dict):
            errors.append(f"[형식오류] {wn}주차 worship_direction이 객체(dict)가 아님: {type(wd_raw).__name__}")
        wd = _d(wd_raw)
        wd_blob = " ".join(str(v) for v in wd.values())
        has_num = has_hymn_number(wd_blob)
        has_title = bool(TITLE_QUOTE.search(wd_blob))
        if has_num and has_title:
            errors.append(f"[곡단정] {wn}주차 worship_direction에 특정 곡(번호+제목) 박음 — 방향만 남기라(할루시네이션)")
        elif has_num or has_title:
            warnings.append(f"[곡단정의심] {wn}주차 worship_direction에 곡 번호/제목 추정 — 방향(주제·정서·모티프·스타일)만 권장")

        # 주해 월권 (경고)
        blob = " ".join(str(w.get(k, "")) for k in ("title", "core_message", "application"))
        if OVERREACH.search(blob):
            warnings.append(f"[주해월권] {wn}주차: 해석 단정 어휘 — 초안으로 제시(강단 권한은 목사)")

    # 완전성 (경고)
    if isinstance(year, int) and expected_obs:
        try:
            total = compute_all_week_numbers(year).get("total_weeks")
            if total and abs(len(seen) - total) > 1:
                warnings.append(f"[완전성] 주차 {len(seen)}개 — 그 해 총 {total}주와 차이(롤링이면 무방, 격자 확인)")
        except Exception:
            pass

    # 9-b. 선택 구조 필드 형식 검사 — 존재하되 schema 형(list/dict)과 어긋나면 [형식오류]
    #      (truthy 비-dict·비-list 오염을 조용히 흘리지 않고 클린 EXIT 1로 잡는다).
    sr_raw = p.get("series")
    if sr_raw is not None and not isinstance(sr_raw, list):
        errors.append(f"[형식오류] series가 배열(list)이 아님: {type(sr_raw).__name__}")
    for i, s in enumerate(_l(sr_raw)):
        if not isinstance(s, dict):
            errors.append(f"[형식오류] series[{i}] 원소가 객체(dict)가 아님: {type(s).__name__}")
        elif s.get("goal_link") is not None and not isinstance(s.get("goal_link"), list):
            errors.append(f"[형식오류] series[{i}].goal_link가 배열(list)이 아님: {type(s.get('goal_link')).__name__}")
    nc_raw = p.get("narrative_check")
    if nc_raw is not None and not isinstance(nc_raw, dict):
        errors.append(f"[형식오류] narrative_check가 객체(dict)가 아님: {type(nc_raw).__name__}")
    sgm_raw = _d(nc_raw).get("sermon_goal_map")
    if sgm_raw is not None and not isinstance(sgm_raw, list):
        errors.append(f"[형식오류] narrative_check.sermon_goal_map이 배열(list)이 아님: {type(sgm_raw).__name__}")
    for i, m in enumerate(_l(sgm_raw)):
        if not isinstance(m, dict):
            errors.append(f"[형식오류] sermon_goal_map[{i}] 원소가 객체(dict)가 아님: {type(m).__name__}")
        elif m.get("serves_axes") is not None and not isinstance(m.get("serves_axes"), list):
            errors.append(f"[형식오류] sermon_goal_map[{i}].serves_axes가 배열(list)이 아님: {type(m.get('serves_axes')).__name__}")
    lw_raw = p.get("load_warnings")
    if lw_raw is not None and not isinstance(lw_raw, list):
        errors.append(f"[형식오류] load_warnings가 배열(list)이 아님: {type(lw_raw).__name__}")
    for i, lwi in enumerate(_l(lw_raw)):
        if not isinstance(lwi, dict):
            errors.append(f"[형식오류] load_warnings[{i}] 원소가 객체(dict)가 아님: {type(lwi).__name__}")
        elif lwi.get("weeks") is not None and not isinstance(lwi.get("weeks"), list):
            errors.append(f"[형식오류] load_warnings[{i}].weeks가 배열(list)이 아님: {type(lwi.get('weeks')).__name__}")

    # 10. 표어/목표 정합 (경고) — series가 비-list(문자열·dict)면 빈 순회로 안전 환원
    series = _l(p.get("series"))
    has_goal_link = any((s.get("goal_link") for s in series if isinstance(s, dict)))
    nc_blk = p.get("narrative_check")
    nc_blk = nc_blk if isinstance(nc_blk, dict) else {}
    has_map = bool(nc_blk.get("sermon_goal_map"))
    if not has_goal_link and not has_map:
        warnings.append("[정합없음] series.goal_link·narrative_check.sermon_goal_map 모두 없음 — 표어가 강단으로 번역됐는지 확인")

    # 10-b. 시리즈 참조 무결성 — series_id가 정의된 series.id를 가리키는가 + series.weeks 범위 일치
    if series:
        sids = {s.get("id") for s in series if isinstance(s, dict) and s.get("id")}
        # 실제 weeks[].series_id별 주차 집합
        actual_by_sid = {}
        for w in weeks:
            if not isinstance(w, dict):
                continue
            sid = w.get("series_id")
            wn = w.get("week")
            if sid:
                if sid not in sids:
                    errors.append(f"[시리즈참조] {wn}주차 series_id='{sid}' 미정의 — series.id에 없음")
                if isinstance(wn, int):
                    actual_by_sid.setdefault(sid, set()).add(wn)
        # series.weeks 선언 범위 vs 실제 배정 주차 비교 (경고)
        for s in series:
            if not isinstance(s, dict):
                continue
            sid = s.get("id")
            declared = {wk for wk in _l(s.get("weeks")) if isinstance(wk, int)}
            actual = actual_by_sid.get(sid, set())
            if declared and actual and declared != actual:
                warnings.append(
                    f"[시리즈주차불일치] series '{sid}' 선언 주차 {sorted(declared)} != 실제 배정 {sorted(actual)}")

    # 11. 확정 게이트
    confirmed = p.get("confirmed")
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 검토·확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_sermon_plan.py <sermon-plan.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            p = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}"); sys.exit(2)

    if not isinstance(p, dict):
        print(f"[오류] 최상위 JSON이 객체(dict) 아님: {type(p).__name__}"); sys.exit(2)

    errors, warnings = validate(p)
    print("=" * 60)
    print("churchplan-sermon-planner-52 강단 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for e in errors:
            print(f"  ✗ {e}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 본문·절기를 지어내거나 곡을 단정하거나 해석을 못박지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 본문 실재, 절기 정확, 곡 단정 없음, 해석 월권 없음. 강단을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
