#!/usr/bin/env python3
"""
validate_vision.py — churchplan-vision-discernment 분별 결과(vision.json) 결정론 검증기.

목적(ABSOLUTE ANCHOR #2): 분별 거울이 두 거짓을 흘리지 않게 지킨다.
  (1) 본문 할루시네이션 — 없는 장·절·가짜 책이름
  (2) 결정 월권 — Claude가 표어를 정하거나 "하나님의 뜻"을 단정하거나 선택 전 선언문을 씀
목사의 분별을 검증하는 것이 아니라, AI가 분별을 오염시켰는지 검사한다.

사용:  python3 validate_vision.py <vision.json> [--final]
  --final: 최종 완료 게이트(chosen·direction_declaration 채워짐 강제).
종료코드: 0 = 통과, 1 = 위반, 2 = 파일/JSON 오류
표준 라이브러리 + 공유 결정론 자산 bible_validator(같은 scripts/ 폴더).
"""
import json
import re
import sys

# 공유 결정론 자산: 책이름+장+절+범위+불연속절 완전 검증(canonical 복사본)
from bible_validator import validate_reference


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


# 계시 단정(절대 금지 — guardrails.md:9 '하나님의 뜻은 …입니다').
# 핵심: '뜻을 분별/구하다'(권장)는 살리고 '뜻은/이 X입니다'(단정)만 잡는다 —
# 그래서 주격/주제격(은/이)에 한해, 뒤에 서술 단정(입니다/이다/…로)이 따라올 때만 적발.
# 조사 변형(은→이)·'의' 생략·동의어(방향/길)로 같은 단정이 새는 것까지 차단.
REVELATION_PAT = re.compile(
    r"하나님의?\s*뜻[은이]\s*\S.*?(입니다|이다|로\s*정|로\s*결정)"
    r"|하나님이\s*원하시는\s*(것은|것이|바는|방향은|길은)\s*\S+\s*(입니다|이다)"
)
# 우열/추천/순위/별점(절대 금지 — discernment-guardrails.md:11 '별점·순위·합격/불합격', SKILL.md:32 '순위' 어휘).
# 후보를 '표어' 또는 '안'으로 부를 때 모두, 추천·최선·가장 좋은(적합한·알맞은·나은)·수치 순위·
# 별점(단어 없이 ★ 나열 포함)·합격/불합격(우열 판정)을 적발. (표어|안) 근접 한정으로 거짓양성 차단.
RANKING_PAT = re.compile(
    r"(최선|최고)의?\s*(표어|안)|가장\s*(좋은|적합한|알맞은|나은|우수한|뛰어난)\s*(표어|안)"
    r"|(표어|안)[^\n]{0,4}(으뜸|최고|최선)|추천\s*(표어|안|합니다|함|드립니다|드림)"
    r"|(이\s*)?(표어|안)[를을]\s*(선택하|택하|고르|골라)(세요|십시오|주세요|주십시오)"
    r"|\b\d+\s*순위|\b\d+\s*위\s*(표어|안|입니다|로)|순위\s*(매김|를\s*매|표)"
    r"|(?<!특)별점\s*[★☆◐0-9]|별점\s*\S{0,3}(개|점)|[★☆⭐]{2,}"
    r"|(표어|안|후보)[^\n]{0,8}(합격|불합격|탈락|당락)|(합격|불합격|탈락|당락)[^\n]{0,8}(표어|안)"
)
# 표어 단정(절대 금지 1순위 — discernment-guardrails.md:8 '올해 표어는 X입니다').
# '표어는 X입니다'뿐 아니라 '표어로 X를 정했/표어를 X로 하겠다/했다' 등 Claude의 확정 어휘도 월권.
THEME_ASSERT_PAT = re.compile(
    r"(올해\s*)?표어는\s*\S.*?(입니다|이다|로\s*정합?니다|로\s*결정)"
    r"|표어[로을를]\s*\S.*?(정했|정함|정합니다|결정했|결정함|결정합니다)"
    r"|표어[을를]\s*\S+\s*[으]?로\s*(하겠습니다|하기로|합니다)"
)


def check_scripture(path, ref, errors, warnings):
    # ref는 schema상 문자열("책 장:절"). truthy 비-문자열(list·dict·int 등)이 오면
    # startswith/validate_reference에서 raw traceback이 나므로 형식오류로 차단(EXIT 1).
    if not isinstance(ref, str):
        if ref not in (None, ""):
            errors.append(f"[형식오류] {path}: 본문 ref는 문자열이어야 함('{type(ref).__name__}' 받음)")
        return
    if not ref or ref == "본문 미확정" or ref.startswith("본문 미확정"):
        return
    ok, msg = validate_reference(ref)
    if not ok:
        errors.append(f"[가짜본문] {path}: '{ref}' — {msg}")


def validate(v, final=False):
    errors, warnings = [], []

    # 스키마 필수
    for blk in ("meta", "candidates"):
        if blk not in v:
            errors.append(f"[블록누락] 최상위 '{blk}' 없음")

    if "meta" in v and not isinstance(v.get("meta"), dict):
        errors.append("[형식오류] meta: 객체여야 함")
    meta = _d(v.get("meta"))
    mode = meta.get("mode")
    if mode not in ("option1", "option2"):
        errors.append(f"[모드오류] meta.mode '{mode}' — option1|option2 여야 함")

    if "candidates" in v and not isinstance(v.get("candidates"), list):
        errors.append("[형식오류] candidates: 배열이어야 함")
    cands = _l(v.get("candidates"))
    if not cands:
        errors.append("[후보없음] candidates 비어 있음")

    fams = set()
    for i, c in enumerate(cands):
        if not isinstance(c, dict):
            errors.append(f"[형식오류] candidates[{i}]: 객체여야 함"); continue
        cid = c.get("id", i)
        fam = c.get("family")
        # family는 문자열 라벨이어야 함. 비-문자열(list·dict 등 unhashable 포함)은
        # set에 넣으면 raw traceback이 나므로 차단하고, "원안" 매칭에서도 제외한다.
        if isinstance(fam, str):
            fams.add(fam)
        if not c.get("theme"):
            errors.append(f"[표어누락] candidates[{cid}].theme 없음")
        elif not isinstance(c.get("theme"), str):
            # 표어는 문자열이어야 — theme-generator가 list/dict 등 비문자열을 내면 형식오류
            #   (하류 sermon·goal·compiler가 chosen_theme를 문자열로 전사하므로 타입 오염 차단).
            errors.append(f"[형식오류] candidates[{cid}].theme가 문자열이 아님: {type(c.get('theme')).__name__}")
        # 본문
        if "core_scriptures" in c and not isinstance(c.get("core_scriptures"), list):
            errors.append(f"[형식오류] candidates[{cid}].core_scriptures: 배열이어야 함")
        for j, s in enumerate(_l(c.get("core_scriptures"))):
            if isinstance(s, dict):
                check_scripture(f"candidates[{cid}].core_scriptures[{j}].ref", s.get("ref", ""), errors, warnings)
            else:
                errors.append(f"[형식오류] candidates[{cid}].core_scriptures[{j}]: 객체여야 함")
        # 분별 재료 구비 (vision-schema.md:56-57 필수 블록)
        # family는 schema상 문자열 라벨(영성형|전도형|공동체형 / 원안|변주) — 비-str이면 형식오류
        if "family" in c and not isinstance(c.get("family"), str):
            errors.append(f"[형식오류] candidates[{cid}].family: 문자열 라벨이어야 함")
        for need in ("axis_mapping", "abstraction", "criteria_check"):
            if need not in c:
                errors.append(f"[재료누락] candidates[{cid}].{need} 없음 — 필수 분별 재료")
            elif not isinstance(c.get(need), dict):
                errors.append(f"[형식오류] candidates[{cid}].{need}: 객체(dict)여야 함 — 분별 재료 형식 오염")
        # 후보 텍스트의 계시 단정/우열/표어 단정
        blob = " ".join(str(c.get(k, "")) for k in ("rationale", "blindspot", "theme"))
        if REVELATION_PAT.search(blob):
            errors.append(f"[계시단정] candidates[{cid}]: '하나님의 뜻' 단정 어휘 — 결정 월권")
        if THEME_ASSERT_PAT.search(blob):
            errors.append(f"[표어단정] candidates[{cid}]: '표어는 …입니다' 단정 — 결정 월권")
        if RANKING_PAT.search(blob):
            errors.append(f"[우열표기] candidates[{cid}]: 추천/최선 어휘 — 결정 월권(우열 금지)")

    # option2 무결성
    if mode == "option2":
        if not v.get("original_theme"):
            errors.append("[원안누락] option2인데 original_theme 없음")
        if "원안" not in fams:
            errors.append("[원안후보] option2인데 family='원안' 후보 없음 — 원안 보존 필수")

    # 선택/선언문 — 결정 월권의 핵심
    chosen = v.get("chosen")
    decl = v.get("direction_declaration")
    if not chosen and decl:
        errors.append("[월권] chosen 없는데 direction_declaration 존재 — 목사 선택 전 선언문 금지")

    # 계시 단정·표어 단정·우열 (선언문/비교노트)
    for field in ("direction_declaration", "comparison_note"):
        text = v.get(field) or ""
        if not isinstance(text, str):
            text = str(text)
        if REVELATION_PAT.search(text):
            errors.append(f"[계시단정] {field}: '하나님의 뜻' 단정 — 결정 월권")
        if THEME_ASSERT_PAT.search(text):
            errors.append(f"[표어단정] {field}: '표어는 …입니다' 단정 — 결정 월권")
        if RANKING_PAT.search(text):
            errors.append(f"[우열표기] {field}: 추천/최선 어휘 — 결정 월권(우열 금지)")
    # comparison_table 우열·표어 단정
    ctable = v.get("comparison_table") or ""
    if not isinstance(ctable, str):
        ctable = str(ctable)
    if THEME_ASSERT_PAT.search(ctable):
        errors.append("[표어단정] comparison_table: '표어는 …입니다' 단정 — 결정 월권")
    if RANKING_PAT.search(ctable):
        errors.append("[우열표기] comparison_table: 추천/최선/순위 어휘 — 결정 월권(우열 금지)")

    # 최종 완료 게이트(--final): chosen·direction_declaration 채워짐 + 타입 강제.
    # chosen은 schema상 {theme,by,synthesized_from} dict, direction_declaration은 문자열 —
    # 하류(goal-architect·plan-compiler·prayer-kit)가 chosen.theme를 dict로 읽으므로 타입 위반은 위반.
    if final:
        if not chosen:
            errors.append("[미완료] --final인데 chosen 없음 — 표어 미선택(목사 HITL 선택 필요)")
        elif not isinstance(chosen, dict) or not str(chosen.get("theme", "")).strip():
            errors.append("[형식오류] --final인데 chosen이 {theme,…} 객체가 아님 — 하류가 chosen.theme를 읽음")
        elif not decl:
            errors.append("[미완료] --final인데 chosen 있으나 direction_declaration 없음 — 선언문 미작성")
        elif not isinstance(decl, str):
            errors.append("[형식오류] --final인데 direction_declaration이 문자열이 아님")

    return errors, warnings


def main():
    args = [a for a in sys.argv[1:] if a != "--final"]
    final = "--final" in sys.argv[1:]
    if len(args) != 1:
        print("사용: python3 validate_vision.py <vision.json> [--final]"); sys.exit(2)
    try:
        with open(args[0], encoding="utf-8") as f:
            v = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {args[0]}"); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}"); sys.exit(2)

    if not isinstance(v, dict):
        print(f"[오류] 최상위 JSON이 객체(dict)가 아님: {type(v).__name__} — vision.json 형식 위반"); sys.exit(2)

    errors, warnings = validate(v, final=final)
    print("=" * 60)
    print("churchplan-vision-discernment 분별 정직성 검증 리포트")
    print("=" * 60)
    if warnings:
        print(f"\n경고 {len(warnings)}건 (통과 가능, 확인 권장):")
        for w in warnings:
            print(f"  · {w}")
    if errors:
        print(f"\n위반 {len(errors)}건 (보완 필요):")
        for e in errors:
            print(f"  ✗ {e}")
        print("\n결과: 실패 — 해당 분석으로 되돌려라. 본문을 지어내거나 표어를 정하지 말 것.")
        sys.exit(1)
    print("\n결과: 통과 ✓ — 본문 정직, 결정 월권 없음. 분별을 목사께 돌린다.")
    sys.exit(0)


if __name__ == "__main__":
    main()
