#!/usr/bin/env python3
"""schema_guard — 그룹 JSON의 타입 계약을 단일 구현으로 강제 (공유 결정론 자산, ADR-0001).

검증기(validate_*.py)와 렌더러(build_*.py)가 *둘 다* 같은 SPEC으로 호출 →
"필드 X는 dict" 같은 타입검사가 한 곳에 산다. 검증기-렌더러 parity가 규율이 아닌 구조.
의미 검사(정직성 게이트 — 가짜본문·절대금액 등)는 각 검증기에 잔류; 여기는 *타입*만 본다.

stdlib only. 스킬 폴더 로컬 사본을 `from schema_guard import check_types` 로 import
(self-containment — sync_shared_assets.py가 전파).

SPEC = 규칙 리스트. 각 규칙 = (path, kind):
  path 세그먼트: 점(.)으로 필드 진입, `[]` 로 리스트 각 원소 순회. 임의 깊이.
    "field"                     최상위 필드
    "field[]"                   그 리스트의 각 원소
    "field[].sub"               각 원소(dict)의 하위 필드
    "field[].sub[]"             각 원소의 하위 리스트의 각 원소
    "field[].sub.deep"          각 원소의 하위 dict의 더 깊은 필드
  kind:
    "dict"         값이 있으면(None 아니면) dict 여야 함
    "list"         값이 있으면 list 여야 함
    "list_of_dict" 값이 list 이고 각 원소가 dict 여야 함
    "str" / "int"  값이 str / (bool 제외) int 여야 함 (원소·leaf 검사)
    "scalar"       값이 str·int·float(스칼라) 여야 함 — dict·list 금지 (예: subtractions[] 문자열 리스트)
검사는 값을 *변형하지 않고* 위반을 한국어 문자열로 보고만 한다(환원은 호출자 _d/_l 몫).
중간 컨테이너가 기대 타입이 아니면 그 leaf는 건너뛴다(그 컨테이너용 별도 규칙이 담당).
"""
from __future__ import annotations
import re

_SEG = re.compile(r"\[\]|[^.\[\]]+")


def _typename(v):
    return type(v).__name__


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _check_leaf(val, kind, path, errors):
    if kind == "dict":
        if val is not None and not isinstance(val, dict):
            errors.append(f"[형식오류] {path}가 객체(dict)가 아님 — {_typename(val)}")
    elif kind == "list":
        if val is not None and not isinstance(val, list):
            errors.append(f"[형식오류] {path}가 배열(list)이 아님 — {_typename(val)}")
    elif kind == "list_of_dict":
        if val is None:
            return
        if not isinstance(val, list):
            errors.append(f"[형식오류] {path}가 배열(list)이 아님 — {_typename(val)}")
            return
        for i, el in enumerate(val):
            if not isinstance(el, dict):
                errors.append(f"[형식오류] {path}[{i}]가 객체(dict)가 아님 — {_typename(el)}")
    elif kind == "str":
        if val is not None and not isinstance(val, str):
            errors.append(f"[형식오류] {path}가 문자열이 아님 — {_typename(val)}")
    elif kind == "int":
        if val is not None and not _is_int(val):
            errors.append(f"[형식오류] {path}가 정수가 아님 — {_typename(val)}")
    elif kind == "scalar":
        if not isinstance(val, (str, int, float)):
            errors.append(f"[형식오류] {path}가 스칼라(문자열·수)가 아님 — {_typename(val)}")
    else:
        errors.append(f"[내부오류] 알 수 없는 kind '{kind}' (path {path})")


def _walk(node, segs, kind, path_str, errors):
    """segs(남은 경로 세그먼트)를 따라 node를 순회하며 leaf에서 kind 검사."""
    if not segs:
        _check_leaf(node, kind, path_str, errors)
        return
    seg, rest = segs[0], segs[1:]
    if seg == "[]":
        if not isinstance(node, list):
            return  # 컨테이너 비-list는 별도 규칙이 담당
        for i, el in enumerate(node):
            _walk(el, rest, kind, f"{path_str}[{i}]", errors)
    else:
        if not isinstance(node, dict):
            return  # 중간이 dict 아니면 leaf 건너뜀(그 컨테이너용 규칙이 담당)
        nxt = node.get(seg)
        _walk(nxt, rest, kind, f"{path_str}.{seg}" if path_str else seg, errors)


def check_types(data, spec):
    """data가 spec(타입 계약)을 위반하면 한국어 오류 문자열 리스트 반환(없으면 [])."""
    if not isinstance(data, dict):
        return [f"[형식오류] 최상위가 객체(dict)가 아님 — {_typename(data)}"]
    errors = []
    for path, kind in spec:
        segs = _SEG.findall(path)
        _walk(data, segs, kind, "", errors)
    return errors


def _selftest():
    """결정론 자가 검증 — `python3 schema_guard.py` 로 실행. 종료코드 0=통과/1=실패."""
    spec = [("meta", "dict"), ("inputs_echo", "dict"), ("events", "list_of_dict"),
            ("events[].title", "str"), ("events[].axes", "list"), ("events[].axes[]", "str"),
            ("events[].bp", "dict"), ("events[].bp.flow", "list"), ("events[].sync.weeks", "list"),
            ("subs[]", "scalar")]
    ok = check_types(
        {"meta": {}, "inputs_echo": {}, "events": [
            {"title": "t", "axes": ["a"], "bp": {"flow": ["x"]}, "sync": {"weeks": [1]}}], "subs": ["멈춤", 3]}, spec)
    bad = check_types(
        {"meta": "s", "inputs_echo": ["l"], "events": [
            {"title": ["L"], "axes": ["a", 7], "bp": "str", "sync": {"weeks": "s"}}, "str", 9],
         "subs": ["ok", {"d": 1}, ["nest"]]}, spec)
    cases = [
        ("정상 0위반", ok == []),
        ("최상위 비-dict", check_types(["x"], spec) and "최상위" in check_types(["x"], spec)[0]),
        ("meta=str 적발", any("meta" in e for e in bad)),
        ("events[1]=str 적발", any("events[1]" in e for e in bad)),
        ("events[2]=int 적발", any("events[2]" in e for e in bad)),
        ("title=list 적발", any("events[0].title" in e for e in bad)),
        ("axes[1]=int 적발", any("events[0].axes[1]" in e for e in bad)),
        ("bp=str 적발", any("events[0].bp가 객체" in e for e in bad)),
        ("sync.weeks=str 적발", any("sync.weeks" in e for e in bad)),
        ("subs[1]=dict 적발(scalar)", any("subs[1]" in e for e in bad)),
        ("subs[2]=list 적발(scalar)", any("subs[2]" in e for e in bad)),
    ]
    failed = [n for n, p in cases if not p]
    if failed:
        print("schema_guard 자가검증 실패:", failed)
        return 1
    print(f"schema_guard 자가검증 통과 ✓ — {len(cases)}건")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
