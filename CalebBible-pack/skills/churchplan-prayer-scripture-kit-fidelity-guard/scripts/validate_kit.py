#!/usr/bin/env python3
"""
validate_kit.py — churchplan-prayer-scripture-kit 영성 키트(prayer-kit.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 영성 키트가 세 거짓을 흘리지 않게 지킨다.
  (1) 율법적 압박 — "완주 못하면·해야만·의무·죄책" 식 강제·정죄(grace_frame 누락 포함)
  (2) 가짜 성경·곡해 — 통독·가정예배·새벽 본문이 정경 66권 밖·없는 권·장
  (3) 지어내기 — 없는 약속·수치 단언
목사의 영성 도구를 검증하는 것이 아니라, AI가 영성 키트를 오염시켰는지 검사한다.

사용:  python3 validate_kit.py <prayer-kit.json>
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
정경 데이터: 같은 폴더 bible_validator.py (이식·diff 0).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bible_validator as bv  # noqa: E402


def _d(x):
    """dict면 그대로, 아니면 빈 dict(truthy 비-dict 방어)."""
    return x if isinstance(x, dict) else {}


def _l(x):
    """list면 그대로, 아니면 빈 list(truthy 비-list 방어)."""
    return x if isinstance(x, list) else []


def _ld(x):
    """list-of-dict — dict 원소만 추려 반환, list 아니면 빈 list."""
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


# 율법·정죄 어휘 (은혜의 초청이지 율법적 압박이 아니다)
# 가드레일/스키마 단일 진실(kit-guardrails.md 라인18·kit-schema.md 라인77)이 열거한 금지 어휘:
# "매일 …해야·완주 못하면·반드시·의무·죄책·게으름·빠지면 안". '반드시'는 *단독* 토큰(예전 '반드시 매일'
# bigram은 '반드시 통독을 마치십시오' 같은 단독 강제를 놓쳤다). '매일 …해야'는 DAILY_OBLIG 근접 규칙이 맡는다.
LEGALISM = ["완주 못하면", "해야만", "해야 한다", "의무", "죄책", "게으름", "빠지면 안", "낙오", "반드시"]
# '매일 …해야' 일일 강제 패턴(스키마 라인77의 ellipsis 토큰): '매일' 직후 근접한 '-야(만)' 의무 활용
# (읽어야 합니다·통독해야 합니다·나와야 합니다·읽어야만)을 검출. 단독 '매일'(매일의 은혜)은 잡지 않는다.
DAILY_OBLIG = r"매일[가-힣\s]{0,14}?[가-힣]야(?:만|\s*(?:하|합|한|해|된|돼))"
# 부정·면제 표지 — 어휘가 *뒤집힌* 맥락("낙오는 실패가 아닙니다"·"의무가 아니라")일 때만 면제.
# '아닙니다'는 '아니'로 분절되지 않으므로(받침 ㅂ→'닙') '아닙'도 포함.
# 무관한 위치의 '없/않/뿐' 단독으로는 면제하지 않는다(문자열 전체 면제 차단).
NEGATE = r"(?:아니|아닙|않|말고)"
# 면제 윈도: 율법 어휘 출현 직후 일정 거리 안에 부정 표지가 와야 면제(어휘-부정 결합).
NEGATE_WINDOW = 12
# 다어절 토큰('해야 한다'·'완주 못하면'·'빠지면 안')의 리터럴 공백을 \s*로 — 이중공백·무공백·탭
# 변형('해야  한다'·'해야한다')으로 율법 어휘를 새는 우회 차단(plan-reinforce _BLAME_RE와 동일 클래스·동일 처리).
_LEGALISM_RE = [(w, re.compile(re.escape(w).replace("\\ ", r"\s*"))) for w in LEGALISM]


def legalism_hits(text):
    """문자열에서 율법 어휘를 검출하되, 어휘 직후 윈도 안에 부정 표지가 있으면(뒤집힌 맥락) 그 어휘만 면제."""
    if not isinstance(text, str) or not text.strip():
        return []
    hits = []
    for w, pat in _LEGALISM_RE:
        for m in pat.finditer(text):
            window = text[m.end():m.end() + NEGATE_WINDOW]
            if re.search(NEGATE, window):
                continue  # 어휘-부정 결합(예: '낙오는 실패가 아닙니다') — 면제
            hits.append(w)
            break  # 같은 어휘는 한 번만 보고
    # '매일 …해야' 근접 패턴(스키마 라인77) — 의무 활용 직후 부정 표지 없으면 위반.
    for m in re.finditer(DAILY_OBLIG, text):
        window = text[m.end():m.end() + NEGATE_WINDOW]
        if re.search(NEGATE, window):
            continue  # '매일 완주해야 하는 것은 아닙니다' 등 — 면제
        hits.append("매일 …해야")
        break
    return hits


def collect_strings(obj):
    """JSON 전체에서 문자열 값을 모은다(율법 톤 검사용)."""
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


def check_scripture(text):
    """본문 표기가 정경 실재인지 — 책·장·절·장범위 끝까지 완전 검증.

    통독 portions·가정예배/새벽 scripture 표기를 받아 (True, info) | (False, 사유) 반환.
    - 절 표기('눅 15:1-7')는 bible_validator.validate_reference로 절 번호·절 범위 끝까지 검증.
    - 장 범위('창세기 49-52')·단일 장('마태복음 5장')은 시작·끝 장을 분해해
      각각 1..len(BOOK_CHAPTERS[book]) 이내인지 검증(권 경계 끝 누락 차단).
    bible_validator는 콜론 없는 '49-52'를 49장의 절 범위로 읽으므로(끝 장 미검증),
    콜론 유무로 갈라 장 범위를 직접 정경 장수와 대조한다.
    """
    raw = str(text).strip()
    if not raw:
        return (False, raw)
    # 책 이름 추출
    m = re.match(r"^\s*([가-힣]+)\s*(.*)$", raw)
    if not m:
        return (False, raw)
    book = bv.normalize_book(m.group(1).strip())
    if not book:
        return (False, raw)
    rest = m.group(2).strip()
    if not rest:
        return (True, book)  # 책이름만(권 전체) — 책 실재만 확인
    # 절 표기(콜론)는 validate_reference에 위임 — 절·절범위 끝까지 검증
    if ":" in rest:
        ok, msg = bv.validate_reference(raw)
        return (ok, raw if ok else msg)
    # 콜론 없음 → 장 또는 장범위. 시작·끝 장을 분해해 각각 정경 장수 이내인지.
    # 장 표기는 '장'·'편'(시편) 모두 허용 — 시편 본문은 관례상 '편'을 쓴다(카탈로그 §1 "시편 150편").
    nch = len(bv.BOOK_CHAPTERS[book])
    rng = re.match(r"^(\d+)\s*(?:장|편)?\s*(?:[-–~]\s*(\d+)\s*(?:장|편)?)?$", rest)
    if not rng:
        return (False, raw)
    start = int(rng.group(1))
    end = int(rng.group(2)) if rng.group(2) else start
    if start < 1 or start > nch:
        return (False, f"{raw} — {book}는 총 {nch}장. {start}장은 정경 범위 밖")
    if end < start:
        return (False, f"{raw} — 끝 장({end})이 시작 장({start})보다 작음")
    if end > nch:
        return (False, f"{raw} — {book}는 총 {nch}장. {end}장은 정경 범위 밖")
    return (True, book)


def validate(p):
    errors, warnings = [], []

    # 1. 필수 블록 — 존재 여부 + 비-dict(truthy 문자열·리스트·정수 포함) 형식오류 등록
    for blk in ("meta", "reading_track", "prayer_topics", "family_worship", "dawn_prayer_season"):
        if blk not in p:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")
        elif not isinstance(p.get(blk), dict):
            errors.append(f"[형식오류] 최상위 '{blk}'가 dict가 아님: {type(p.get(blk)).__name__} — 검증을 위해 빈 객체로 환원")

    meta = _d(p.get("meta"))
    rt = _d(p.get("reading_track"))
    fw = _d(p.get("family_worship"))
    dp = _d(p.get("dawn_prayer_season"))

    # 2. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 3. 성경 실재 — 통독 portions
    if "schedule" in rt and not isinstance(rt.get("schedule"), list):
        errors.append("[형오류] reading_track.schedule가 list가 아님 — 일별 배정 검증 불가")
    sched = _l(rt.get("schedule"))
    for i, day in enumerate(sched):
        if not isinstance(day, dict):
            errors.append(f"[형오류] reading_track.schedule[{i}]가 dict가 아님")
            continue
        if "portions" in day and not isinstance(day.get("portions"), list):
            errors.append(f"[형오류] reading_track.schedule[{i}].portions가 list가 아님")
            continue
        for portion in _l(day.get("portions")):
            ok, info = check_scripture(portion)
            if not ok:
                errors.append(f"[가짜성경] reading_track.schedule[{i}] '{portion}' — {info}")
    # 가정예배 samples
    if "samples" in fw and not isinstance(fw.get("samples"), list):
        errors.append("[형오류] family_worship.samples가 list가 아님")
    for i, s in enumerate(_l(fw.get("samples"))):
        if not isinstance(s, dict):
            errors.append(f"[형오류] family_worship.samples[{i}]가 dict가 아님")
            continue
        scr = s.get("scripture")
        if scr:
            ok, info = check_scripture(scr)
            if not ok:
                errors.append(f"[가짜성경] family_worship.samples[{i}] '{scr}' — {info}")
    # 새벽 시즌
    if "seasons" in dp and not isinstance(dp.get("seasons"), list):
        errors.append("[형오류] dawn_prayer_season.seasons가 list가 아님")
    for i, s in enumerate(_l(dp.get("seasons"))):
        if not isinstance(s, dict):
            errors.append(f"[형오류] dawn_prayer_season.seasons[{i}]가 dict가 아님")
            continue
        scr = s.get("scripture")
        if scr:
            ok, info = check_scripture(scr)
            if not ok:
                errors.append(f"[가짜성경] dawn_prayer_season.seasons[{i}] '{scr}' — {info}")

    # 4. 율법 톤
    for s in collect_strings(p):
        for hit in legalism_hits(s):
            errors.append(f"[율법어휘] '{hit}' — 은혜의 초청이지 율법적 압박이 아니다: \"{s[:30]}\"")

    # 5. 통독 은혜 융통성
    if not rt.get("grace_frame") or not str(rt.get("grace_frame")).strip():
        errors.append("[융통성누락] reading_track.grace_frame 없음 — '낙오=실패 아님·다시 합류·읽은 만큼'(통독 율법화 차단)")

    # 6. 전사 — 기도제목 출처 (prayer_topics 비-dict는 §1 필수 블록 루프에서 [형식오류] 등록됨)
    pt = _d(p.get("prayer_topics"))
    if "months" in pt and not isinstance(pt.get("months"), list):
        errors.append("[형오류] prayer_topics.months가 list가 아님")
    for m_ in _l(pt.get("months")):
        if not isinstance(m_, dict):
            errors.append("[형오류] prayer_topics.months 원소가 dict가 아님")
            continue
        if not str(m_.get("source") or "").strip():
            errors.append(f"[출처누락] prayer_topics {m_.get('month','?')}월에 source 없음 — 표어·목표·형편에서 전사(지어내기 차단)")

    # 7. 영성 지표 연결(보완A — 권장)
    if not rt.get("serves_indicator"):
        warnings.append("[지표연결누락] reading_track.serves_indicator 없음 — 통독 완주 신호(#9·격려용) 연결 권장")
    if not dp.get("serves_indicator"):
        warnings.append("[지표연결누락] dawn_prayer_season.serves_indicator 없음 — 새벽 참여 신호(#9·격려용) 연결 권장")

    # 8. 확정 게이트
    confirmed = p.get("confirmed")
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 검토·확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 validate_kit.py <prayer-kit.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            p = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(p, dict):
        print(f"[오류] 최상위 JSON이 객체(dict)가 아님: {type(p).__name__}"); sys.exit(2)

    errors, warnings = validate(p)
    print("=" * 60)
    print("churchplan-prayer-scripture-kit 영성 키트 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for er in errors:
            print(f"  ✗ {er}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 율법으로 압박하거나, 없는 성경을 쓰거나, 약속을 지어내지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 성경 실재, 은혜의 초청, 전사 충실. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
