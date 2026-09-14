#!/usr/bin/env python3
"""
build_resource.py — churchplan-resource-aligner 자원 정렬표 렌더러.

resource.json → ① resource-plan.md (예산 배분안 + 조직 배치표 + 담임 시간 가이드 + 빼기 + 경고)
                ② resource-plan.xlsx (예산·조직·담임시간 3시트 + 경고 시트, openpyxl 없으면 .csv)

렌더 전 핵심 게이트를 재강제한다(cys-insight 패턴):
  필수 블록 · 표어 · 절대금액 금지 · status. 위반 시 렌더 거부(종료코드 1).
전체 정밀 검증(빼기·목자 자원)은 fidelity-guard의 validate_resource.py가 맡는다.

사용:  python3 build_resource.py <resource.json> [출력디렉토리]
종료코드: 0 = 성공, 1 = 게이트 위반(렌더 거부), 2 = 파일/JSON 오류
표준 라이브러리만 사용(xlsx는 openpyxl 있을 때만, 없으면 csv).
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    # 타입 계약은 검증기·렌더러 공유 SPEC으로 단일화(ADR-0002) — parity 구조화.
    from schema_guard import check_types
    from spec_resource_aligner import RESOURCE_SCHEMA
except ImportError as _imp_err:
    print(f"[오류] 이식 자산 import 실패(schema_guard/spec_resource_aligner — sync_shared_assets 필요): {_imp_err}")
    sys.exit(2)


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


# 절대 금액/통화 패턴 — fidelity-guard의 validate_resource.py MONEY_RE 와 동일(단일 진실).
# 패턴 변경 시 두 스크립트(validate_resource.py·build_resource.py)를 함께 변경(resource-schema.md).
# 절대 금액만 차단(비율·증감 허용). 음절 단위는 '숫자 선행' 시에만 — 후원·자원·임원·충원 등 오탐 차단.
# 순수 한글 만 단위('백만원'·'천만원')도 차단('백만 영혼'은 통과). validate_resource.py와 동일(parity).
# 숫자와 통화 사이의 다리는 금액 자릿수(백만/천만/만/천/억)만 허용 — 과거 [가-힣]? 는 '2027 자원'·
# '2030 지원'처럼 숫자 뒤 무관한 단어를 절대금액으로 오인했다(거짓양성). '5만 원' 같은 띄어쓴 금액은
# 자릿수 그룹으로 계속 포착. validate_resource.py MONEY_RE와 동일·함께 변경(parity·단일 진실).
MONEY_RE = re.compile(r"(₩|\$|(?:USD|KRW|won)\s*[0-9]|[0-9][0-9,\.]*\s*(?:백만|천만|만|천|억)?\s*(원|만원|천원|억|백만|달러|won|USD|KRW)|(백만|천만)\s*원)")


def _find_money(obj, path):
    """블록 내 절대 금액 패턴 탐색(validate_resource.find_money와 동일 로직, .note 경로는 호출부에서 제외)."""
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits += _find_money(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += _find_money(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        m = MONEY_RE.search(obj)
        if m:
            hits.append((path, m.group(0)))
    return hits


def gate(r):
    """렌더 전 핵심 게이트."""
    errs = []
    for blk in ("meta", "budget_plan", "pastor_time"):
        if blk not in r:
            errs.append(f"필수 블록 '{blk}' 없음")
    # 타입 계약 — 검증기와 같은 SPEC(ADR-0002). parity 구조화(둘이 같은 guard를 부르므로 어긋날 수 없음).
    # 렌더 본문은 별도로 _ld/_cell 필터로 산출물 오염도 차단(이중 방어).
    errs.extend(check_types(r, RESOURCE_SCHEMA))
    meta = _d(r.get("meta"))
    if not str(meta.get("chosen_theme") or "").strip():
        errs.append("meta.chosen_theme 비어 있음 — 표어 먼저 확정")
    if meta.get("status") not in ("제안", "확정"):
        errs.append("meta.status 가 제안|확정 이 아님")
    # 절대 금액 검사 — budget_plan뿐 아니라 org_plan(조직 배치표로 렌더)·demand_gaps·subtractions·
    # warnings·pastor_time·inputs_echo까지 스캔. .note 경로는 예외(설명文, validate와 동일 정책).
    for blk in ("budget_plan", "org_plan", "demand_gaps", "subtractions", "warnings", "pastor_time", "inputs_echo"):
        if blk not in r:
            continue
        for path, tok in _find_money(r.get(blk), blk):
            if path.endswith(".note"):
                continue
            errs.append(f"{path}에 절대 금액 '{tok}' — 비율·증감만")
    return errs


def build_md(r):
    meta = _d(r.get("meta"))
    L = []
    L.append("# 2027 자원 정렬 — 예산·조직·담임 시간")
    L.append("")
    L.append(f"- 표어: **{meta.get('chosen_theme', '(미확정)')}**")
    L.append(f"- 상태: " + ("✅ 목사 확정" if r.get("confirmed") else "🙏 목사 확정 대기"))
    L.append("")

    # 예산 배분안
    bp = _d(r.get("budget_plan"))
    L.append("## 💰 예산 배분안 (비율·증감 — 절대 금액은 재정 담당과 확정)")
    L.append("")
    cbf = _d(bp.get("current_by_function"))
    if cbf:
        L.append("**기능별 현황(기억 비율)**: " + " · ".join(f"{k} {v}%" for k, v in cbf.items()))
        L.append("")
    realloc = _ld(bp.get("realloc_by_strategy"))
    if realloc:
        L.append("**전략별 재배분(표어·목표 반영)**")
        L.append("")
        L.append("| 차원 | 항목 | 작년 | 올해 | 증감 | 근거 |")
        L.append("|---|---|---|---|---|---|")
        for a in realloc:
            if not isinstance(a, dict):
                continue
            L.append(f"| {a.get('dimension','')} | {a.get('item','')} | {a.get('last','')} "
                     f"| {a.get('this','')} | {a.get('change','')} | {a.get('rationale','')} |")
        L.append("")
    if bp.get("note"):
        L.append(f"> {bp.get('note')}")
        L.append("")

    # 조직 배치표
    org = _d(r.get("org_plan"))
    L.append("## 👥 조직 배치표")
    L.append("")
    lg = _ld(org.get("leader_gaps"))
    if lg:
        L.append("**리더 공백(담당 미정 사역 — #7)**")
        for g in lg:
            L.append(f"- {g.get('ministry','')} — 필요: {g.get('need','')} _(출처: {g.get('from_action_gap','')})_")
        L.append("")
    dn = _ld(org.get("develop_needed"))
    if dn:
        L.append("**양성 필요**: " + ", ".join(f"{d.get('role','')} {d.get('count','')}" for d in dn))
        L.append("")
    pl = _ld(org.get("placements"))
    if pl:
        L.append("| 일꾼 | 역할 | 부하 | 근거 |")
        L.append("|---|---|---|---|")
        for p in pl:
            load = p.get("load", "")
            mark = "⚠ " if load == "과중" else ""
            L.append(f"| {p.get('name','')} | {p.get('role','')} | {mark}{load} | {p.get('basis','')} |")
        L.append("")

    # 담임 시간 가이드
    pt = _d(r.get("pastor_time"))
    L.append("## ⏳ 담임목사 주간 시간 가이드")
    L.append("")
    L.append("| 영역 | 비중 | 보호 |")
    L.append("|---|---|---|")
    for b in _ld(pt.get("blocks")):
        prot = "🛡️ 보호" if b.get("protected") else ""
        L.append(f"| {b.get('area','')} | {b.get('hours','')} | {prot} |")
    L.append("")
    if pt.get("warning"):
        L.append(f"> ⚠️ {pt.get('warning')}")
        L.append("")

    # 빼기 — 비-문자열(dict·list) 원소는 MD에 literal repr로 누출되지 않게 필터(xlsx와 parity).
    subs = [s for s in _l(r.get("subtractions")) if isinstance(s, (str, int, float))]
    L.append("## ➖ 더하기 전 빼기 (무엇을 멈출 것인가)")
    L.append("")
    if subs:
        for s in subs:
            L.append(f"- {str(s)}")
    else:
        L.append("- (빼기 없음 — 새 수요가 있다면 무엇을 멈출지 점검 필요)")
    L.append("")

    # 경고
    warns = _ld(r.get("warnings"))
    if warns:
        L.append("## ⚖️ 자원 경고")
        L.append("")
        for w in warns:
            L.append(f"- **[{w.get('type','')}]** {w.get('text','')}  _(근거: {w.get('basis','')})_")
        L.append("")

    L.append("> 자원이 적은 교회의 정렬은 곧 실현 가능성입니다. 더하기 전에 빼고, 절대 금액은 재정 담당과 확정하며, 목자의 기도·쉼을 자원으로 지킵니다.")
    return "\n".join(L) + "\n"


def build_xlsx(r, out_path):
    bp = _d(r.get("budget_plan"))
    org = _d(r.get("org_plan"))
    pt = _d(r.get("pastor_time"))
    warns = _ld(r.get("warnings"))
    subs = [s for s in _l(r.get("subtractions")) if isinstance(s, (str, int, float))]

    realloc = _ld(bp.get("realloc_by_strategy"))
    budget_rows = [[a.get("dimension", ""), a.get("item", ""), a.get("last", ""),
                    a.get("this", ""), a.get("change", ""), a.get("rationale", "")]
                   for a in realloc]
    org_rows = [[p.get("name", ""), p.get("role", ""), p.get("load", ""), p.get("basis", "")]
                for p in _ld(org.get("placements"))]
    time_rows = [[b.get("area", ""), b.get("hours", ""), "보호" if b.get("protected") else ""]
                 for b in _ld(pt.get("blocks"))]

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill
    except ImportError:
        csv_path = out_path.rsplit(".", 1)[0] + ".csv"
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["[예산 재배분] 차원", "항목", "작년", "올해", "증감", "근거"])
            for row in budget_rows:
                w.writerow(row)
            w.writerow([]); w.writerow(["[조직 배치] 일꾼", "역할", "부하", "근거"])
            for row in org_rows:
                w.writerow(row)
            w.writerow([]); w.writerow(["[담임 시간] 영역", "비중", "보호"])
            for row in time_rows:
                w.writerow(row)
            w.writerow([]); w.writerow(["[빼기]"])
            for s in subs:
                w.writerow([s])
            w.writerow([]); w.writerow(["[경고] 유형", "내용", "근거"])
            for wn in warns:
                w.writerow([wn.get("type", ""), wn.get("text", ""), wn.get("basis", "")])
        return csv_path

    wb = Workbook()
    head_fill = PatternFill("solid", fgColor="594B3B")
    head_font = Font(bold=True, color="FFFFFF")
    prot_fill = PatternFill("solid", fgColor="EAF0F7")
    over_fill = PatternFill("solid", fgColor="F6DAD2")

    ws = wb.active
    ws.title = "예산 배분"
    cbf = _d(bp.get("current_by_function"))
    ws.append(["기능별 현황(%)"] + list(cbf.keys()))
    ws.append([""] + list(cbf.values()))
    ws.append([])
    ws.append(["차원", "항목", "작년", "올해", "증감", "근거"])
    hdr_row = ws.max_row
    for c in ws[hdr_row]:
        c.fill = head_fill; c.font = head_font
    for row in budget_rows:
        ws.append(row)
    for col, wd in zip("ABCDEF", [10, 14, 10, 10, 10, 34]):
        ws.column_dimensions[col].width = wd

    ws2 = wb.create_sheet("조직 배치")
    ws2.append(["일꾼", "역할", "부하", "근거"])
    for c in ws2[1]:
        c.fill = head_fill; c.font = head_font
    for row in org_rows:
        ws2.append(row)
        if row[2] == "과중":
            for c in ws2[ws2.max_row]:
                c.fill = over_fill
    for col, wd in zip("ABCD", [14, 18, 10, 30]):
        ws2.column_dimensions[col].width = wd

    ws3 = wb.create_sheet("담임 시간")
    ws3.append(["영역", "비중", "보호"])
    for c in ws3[1]:
        c.fill = head_fill; c.font = head_font
    for row in time_rows:
        ws3.append(row)
        if row[2] == "보호":
            for c in ws3[ws3.max_row]:
                c.fill = prot_fill
    for col, wd in zip("ABC", [16, 12, 10]):
        ws3.column_dimensions[col].width = wd

    if subs or warns:
        ws4 = wb.create_sheet("빼기·경고")
        ws4.append(["구분", "내용", "근거"])
        for c in ws4[1]:
            c.fill = head_fill; c.font = head_font
        for s in subs:
            ws4.append(["빼기", s, ""])
        for wn in warns:
            ws4.append([wn.get("type", ""), wn.get("text", ""), wn.get("basis", "")])
        for col, wd in zip("ABC", [12, 40, 28]):
            ws4.column_dimensions[col].width = wd

    wb.save(out_path)
    return out_path


def main():
    if len(sys.argv) < 2:
        print("사용: python3 build_resource.py <resource.json> [출력디렉토리]"); sys.exit(2)
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(src))
    try:
        with open(src, encoding="utf-8") as f:
            r = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {src}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(r, dict):
        print(f"[오류] 최상위 JSON이 객체가 아님(type={type(r).__name__}) — resource.json 은 dict 여야 함"); sys.exit(2)

    errs = gate(r)
    if errs:
        print("=" * 60)
        print("렌더 거부 — 게이트 위반 (fidelity-guard 먼저 통과시키라)")
        print("=" * 60)
        for er in errs:
            print(f"  ✗ {er}")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "resource-plan.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(build_md(r))
    xlsx_path = build_xlsx(r, os.path.join(out_dir, "resource-plan.xlsx"))

    print("렌더 완료 ✓")
    print(f"  · {md_path}")
    print(f"  · {xlsx_path}" + ("  (openpyxl 없어 csv 폴백)" if xlsx_path.endswith(".csv") else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
