#!/usr/bin/env python3
"""
validate_package.py — churchplan-plan-compiler 통합 패키지(plan-package.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 통합이 세 거짓을 흘리지 않게 지킨다.
  (1) 재생산 — 앞 산출물에 없는 표어·수치·본문을 지어냄(표어 불일치 포함)
  (2) 미확정 산출물 문서화 — sources.missing/unconfirmed가 있는데 묶음(garbage-in)
  (3) 9요소 깨짐 — 계획서 본문이 정확한 9요소가 아님(콘텐츠 생산)
목사의 계획을 검증하는 것이 아니라, AI가 통합을 오염시켰는지 검사한다.

사용:  python3 validate_package.py <plan-package.json> [source-dir]
       source-dir 주면 vision.json 등 원본을 열어 전사 충실·확정 게이트를 결정론 대조한다.
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리 + 공유 결정론 자산(bible_validator)만 사용.
"""
import json
import os
import sys

# 공유 결정론 자산 — 성경 본문 검증(canonical, 같은 scripts/에 복사본 존재)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bible_validator import validate_reference


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []

# 계획서 본문 9요소 (01 라인 316 — 고정)
NINE = ["표어", "방향 선언문", "3축 목표", "설교계획", "핵심행사",
        "실행계획", "예산", "조직", "점검계획"]

# source-collector가 모으는 필수 8개 산출물 (compile-schema.md)
REQUIRED_SOURCES = {
    "vision.json", "goals.json", "sermon-plan.json", "events.json",
    "calendar.json", "action.json", "resource.json", "review.json",
}


def _norm(s):
    """공백·구두점 정규화 — 전사 부분일치 대조용."""
    import re
    return re.sub(r"[\s　.,·:;!?'\"()\[\]<>{}\-–~]+", "", str(s or ""))


def validate(p, source_dir=None):
    errors, warnings = [], []

    # 1. 스키마 필수 블록
    for blk in ("meta", "sources", "plan_document", "slide_deck", "vision_onepager"):
        if blk not in p:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    # 최상위 필수 dict 필드가 비-dict면 안전 환원 + [형식오류] 위반 1건(조용한 통과 금지)
    for blk in ("meta", "sources", "plan_document", "slide_deck", "vision_onepager"):
        if blk in p and not isinstance(p.get(blk), dict):
            errors.append(f"[형식오류] 최상위 '{blk}'가 객체(dict)가 아님: {type(p.get(blk)).__name__}")

    # 타입 위반 게이트(truthy 비-dict/비-list 차단) — 필드가 *있는데* 컨테이너 타입이 틀리면 위반.
    # 정상 입력(필드 없음 또는 올바른 타입)은 회귀 없이 통과한다(과잉 차단 금지).
    def _type_violation(container, key, want, label):
        if isinstance(container, dict) and key in container:
            v = container.get(key)
            if want == "dict" and not isinstance(v, dict):
                errors.append(f"[형식오류] {label}이(가) 객체(dict)가 아님: {type(v).__name__}")
            elif want == "list" and not isinstance(v, list):
                errors.append(f"[형식오류] {label}이(가) 리스트가 아님: {type(v).__name__}")

    _meta_raw = p.get("meta")
    _sources_raw = p.get("sources")
    _pd_raw = p.get("plan_document")
    _deck_raw = p.get("slide_deck")
    _vp_raw = p.get("vision_onepager")
    _type_violation(_sources_raw, "missing", "list", "sources.missing")
    _type_violation(_sources_raw, "unconfirmed", "list", "sources.unconfirmed")
    _type_violation(_pd_raw, "intro_optional", "dict", "plan_document.intro_optional")
    _type_violation(_deck_raw, "slides", "list", "slide_deck.slides")
    _type_violation(_vp_raw, "directions", "list", "vision_onepager.directions")
    if "reinforce_guide" in p and not isinstance(p.get("reinforce_guide"), dict):
        errors.append(f"[형식오류] 최상위 'reinforce_guide'가 객체(dict)가 아님: {type(p.get('reinforce_guide')).__name__}")
    if "bundle" in p and not isinstance(p.get("bundle"), list):
        errors.append(f"[형식오류] 최상위 'bundle'이 리스트가 아님: {type(p.get('bundle')).__name__}")
    _rg_raw = p.get("reinforce_guide")
    _type_violation(_rg_raw, "verify_seeds", "list", "reinforce_guide.verify_seeds")

    # 리스트 원소 타입 위반 — dict-리스트에 비-dict 원소, scalar-리스트에 dict/list 원소.
    def _bad_dict_elems(container, key, label):
        if isinstance(container, dict) and isinstance(container.get(key), list):
            bad = [i for i, v in enumerate(container[key]) if not isinstance(v, dict)]
            if bad:
                errors.append(f"[형식오류] {label}에 dict 아닌 항목 {bad} — 각 항목은 객체여야 함")

    def _bad_scalar_elems(container, key, label):
        if isinstance(container, dict) and isinstance(container.get(key), list):
            bad = [i for i, v in enumerate(container[key]) if isinstance(v, (dict, list))]
            if bad:
                errors.append(f"[형식오류] {label}에 dict/list 항목 {bad} — 문자열 등 단순값이어야 함")

    _bad_dict_elems(_sources_raw, "loaded", "sources.loaded")
    _bad_dict_elems(_deck_raw, "slides", "slide_deck.slides")
    _bad_dict_elems(_rg_raw, "verify_seeds", "reinforce_guide.verify_seeds")
    if isinstance(p.get("bundle"), list):
        bad = [i for i, v in enumerate(p["bundle"]) if not isinstance(v, dict)]
        if bad:
            errors.append(f"[형식오류] bundle에 dict 아닌 항목 {bad} — 각 번들은 객체여야 함")
    _bad_scalar_elems(_vp_raw, "directions", "vision_onepager.directions")
    for _i, _sl in enumerate(_l((_deck_raw or {}).get("slides") if isinstance(_deck_raw, dict) else None)):
        _type_violation(_sl, "bullets", "list", f"slide_deck.slides[{_i}].bullets")
        _bad_scalar_elems(_sl, "bullets", f"slide_deck.slides[{_i}].bullets")
    for _i, _bn in enumerate(_l(p.get("bundle"))):
        _type_violation(_bn, "files", "list", f"bundle[{_i}].files")
        _bad_scalar_elems(_bn, "files", f"bundle[{_i}].files")

    meta = _d(p.get("meta"))
    sources = _d(p.get("sources"))
    pd = _d(p.get("plan_document"))
    deck = _d(p.get("slide_deck"))

    # 2. 표어
    theme = meta.get("chosen_theme")
    if not theme or not str(theme).strip():
        errors.append("[표어미확정] meta.chosen_theme 비어 있음 — 표어 없이 계획서 불가(앞 단계로)")

    # 3. status
    status = meta.get("status")
    if status not in ("제안", "확정"):
        errors.append(f"[상태오류] meta.status '{status}' — 제안|확정 여야 함")

    # 4. 확정 게이트 (garbage-in 차단 — #10 고유)
    missing = _l(sources.get("missing"))
    unconfirmed = _l(sources.get("unconfirmed"))
    if missing:
        errors.append(f"[산출물누락] sources.missing 비어 있지 않음: {missing} — 빠진 산출물을 먼저 만들라(앞 단계로)")
    if unconfirmed:
        errors.append(f"[미확정문서화] sources.unconfirmed 비어 있지 않음: {unconfirmed} — 미확정 산출물로 최종 문서를 만들지 않는다(확정 먼저)")

    # 5. 9요소 고정
    chapters_raw = pd.get("chapters")
    if "chapters" in pd and not isinstance(chapters_raw, list):
        errors.append("[형식오류] plan_document.chapters가 리스트가 아님")
    chapters = _l(chapters_raw)
    bad_ch = [i for i, c in enumerate(chapters) if not isinstance(c, dict)]
    if bad_ch:
        errors.append(f"[형식오류] plan_document.chapters에 dict 아닌 항목 {bad_ch} — 각 장은 객체여야 함")
    chapters = [c for c in chapters if isinstance(c, dict)]
    keys = [c.get("key") for c in chapters]
    for need in NINE:
        if need not in keys:
            errors.append(f"[9요소누락] plan_document.chapters에 '{need}' 없음 — 계획서 본문은 정확한 9요소(01 라인 316)")
    if "연간 캘린더" in keys or "캘린더" in keys:
        warnings.append("[캘린더위치] 캘린더가 chapters에 있음 — 본문 9요소 아님(bundle 별첨으로)")
    extra = [k for k in keys if k not in NINE]
    if extra:
        warnings.append(f"[추가장] 9요소 밖의 장: {extra} — 본문은 9요소 고정(콘텐츠 생산 주의)")

    # 6. 전사 충실
    for c in chapters:
        if c.get("key") in NINE and not (c.get("source") and str(c.get("source")).strip()):
            errors.append(f"[출처없음] chapters '{c.get('key')}'에 source 없음 — 출처 없는 본문은 지어낸 것")
    # 표어 장은 *모두* 대조한다 — 중복 표어 장 중 하나라도 meta.chosen_theme와 다르면 위반
    # (next()로 첫 장만 보면, 뒤에 붙인 모순 표어가 전사 게이트를 빠져나가 문서에 박힌다)
    if theme:
        for c in chapters:
            if c.get("key") == "표어" and c.get("content") and c.get("content") != theme:
                errors.append("[표어불일치] chapters[표어].content ≠ meta.chosen_theme — 표어를 새로 쓰지 않는다(전사)")
                break

    # 6b. 성경 본문 결정론 검증 (7차원 할루시네이션 1순위 — 존재하지 않는 장·절 차단)
    vp = _d(p.get("vision_onepager"))
    cs = vp.get("core_scripture")
    if cs and str(cs).strip():
        ok, msg = validate_reference(str(cs))
        if not ok:
            errors.append(f"[본문조작] vision_onepager.core_scripture '{cs}' — {msg}(지어낸 장·절 금지)")

    # 7. 재생산 금지 — bundle은 파일 참조만
    for b in _ld(p.get("bundle")):
        if not b.get("files"):
            warnings.append(f"[번들참조누락] bundle '{b.get('name','?')}'에 files 없음 — 앞 산출물 파일을 참조(재생산 금지)")

    # 8. 살아있는 마무리
    rg = _d(p.get("reinforce_guide"))
    if not rg:
        warnings.append("[마무리누락] reinforce_guide 없음 — 패키지는 끝이 아니라 시작(#12·#9로 다리)")
    elif "plan-reinforce" not in str(rg.get("next", "")):
        warnings.append("[다리누락] reinforce_guide.next에 plan-reinforce 언급 없음 — 보강으로 가는 다리")

    # 9. 슬라이드 분량 (slide_deck 필수 블록 — 0장 빈 덱도 경고)
    slides = _l(deck.get("slides"))
    if not slides:
        warnings.append("[슬라이드없음] slide_deck.slides 비어 있음 — 당회/제직회 슬라이드 10장 내외 필요")
    elif not (7 <= len(slides) <= 12):
        warnings.append(f"[슬라이드분량] slide_deck.slides {len(slides)}장 — 10장 내외(7~12) 권장")

    # 10. 확정 게이트
    confirmed = p.get("confirmed")
    if status == "확정" and not confirmed:
        errors.append("[확정월권] status='확정'인데 confirmed 없음 — 목사 검토·확정 HITL 전 확정 표기 금지")
    if status == "제안" and confirmed:
        warnings.append("[상태불일치] status='제안'인데 confirmed 존재 — status를 '확정'으로")

    # 11. 교회명
    if not meta.get("church_name"):
        warnings.append("[교회명미입력] meta.church_name 비어 있음 — 목사 1회 입력 권장")

    # 12. 원본 산출물 결정론 대조 (source_dir 주어졌을 때만)
    #     LLM 자기보고(sources.missing/unconfirmed)를 믿지 않고 실제 파일 status를 다시 연다.
    if source_dir:
        errors += _cross_check_sources(p, source_dir, sources, chapters, theme)

    return errors, warnings


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _cross_check_sources(p, source_dir, sources, chapters, theme):
    """원본 파일을 실제로 열어 garbage-in 게이트와 전사 충실을 재대조한다(LLM 보고 불신)."""
    errs = []

    # (1) 확정 게이트 재계산 — 실제 파일 존재·status로 missing/unconfirmed를 다시 센다.
    real_missing, real_unconfirmed = [], []
    for fname in sorted(REQUIRED_SOURCES):
        fpath = os.path.join(source_dir, fname)
        if not os.path.exists(fpath):
            real_missing.append(fname)
            continue
        sj = _load_json(fpath)
        st = _d(sj.get("meta") if isinstance(sj, dict) else None).get("status")
        if st != "확정":
            real_unconfirmed.append(fname)
    rep_missing = {x for x in _l(sources.get("missing")) if isinstance(x, str)}
    rep_unconfirmed = {x for x in _l(sources.get("unconfirmed")) if isinstance(x, str)}
    if real_missing:
        errs.append(f"[원본누락] 실제 누락 산출물 {real_missing} — 먼저 만들라(LLM 보고 무관·파일 사실)")
    if real_unconfirmed:
        errs.append(f"[원본미확정] 실제 status≠확정 산출물 {real_unconfirmed} — 확정 먼저(LLM 보고 무관·파일 사실)")
    silently = [f for f in (real_missing + real_unconfirmed)
                if f not in rep_missing and f not in rep_unconfirmed]
    if silently:
        errs.append(f"[보고조작] sources에 {silently}의 누락/미확정이 누락됨 — 자기보고가 원본과 불일치")

    # (2) 전사 충실 — vision.json 원본과 표어·방향 선언문·핵심 본문 대조.
    vj = _load_json(os.path.join(source_dir, "vision.json"))
    if isinstance(vj, dict):
        chosen = _d(vj.get("chosen"))
        src_theme = chosen.get("theme")
        if theme and src_theme and _norm(theme) != _norm(src_theme):
            errs.append(f"[표어조작] meta.chosen_theme가 vision.chosen.theme와 다름 — 표어 전사 위반")
        src_decl = vj.get("direction_declaration")
        # 첫 '방향 선언문' 장만 보지 않고 *모든* 선언문 장을 순회 — 둘째 장에 AI 재작성을 덧붙여
        # 첫 장만 통과시키는 우회 차단([표어불일치]와 동일 클래스·동일 처리).
        if src_decl:
            for c in chapters:
                if c.get("key") == "방향 선언문" and _norm(src_decl) not in _norm(c.get("content", "")):
                    errs.append("[선언문조작] chapters[방향 선언문].content에 vision.direction_declaration 원문이 없음 "
                                "— 목사 문장 그대로 전사해야 함(AI 재작성 금지)")
                    break
        # 핵심 본문 — vision_onepager.core_scripture가 vision 후보 본문 집합의 멤버인지
        vp = _d(p.get("vision_onepager"))
        cs = vp.get("core_scripture")
        if cs and str(cs).strip():
            refs = set()
            for cand in _ld(vj.get("candidates")):
                for sc in _ld(cand.get("core_scriptures")):
                    if sc.get("ref"):
                        refs.add(_norm(sc["ref"]))
            if refs and _norm(cs) not in refs:
                errs.append(f"[본문조작] vision_onepager.core_scripture '{cs}'가 vision 원본 본문 집합에 없음 — 전사 위반")

    return errs


def main():
    if len(sys.argv) not in (2, 3):
        print("사용: python3 validate_package.py <plan-package.json> [source-dir]"); sys.exit(2)
    source_dir = sys.argv[2] if len(sys.argv) == 3 else None
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            p = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(p, dict):
        print(f"[오류] 최상위 JSON이 객체(dict)가 아님: {type(p).__name__} — plan-package.json은 객체여야 함"); sys.exit(2)

    errors, warnings = validate(p, source_dir)
    print("=" * 60)
    print("churchplan-plan-compiler 통합 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for er in errors:
            print(f"  ✗ {er}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 앞 산출물을 재생산하거나, 미확정으로 묶거나, 9요소를 깨지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 전사 충실, 다 확정됨, 9요소 고정. 확정을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
