#!/usr/bin/env python3
"""
build_reinforce.py — churchplan-plan-reinforce 보강 렌더러(자기완결).

reinforce.json → ① reinforce-dashboard.xlsx (추정 vs 실측 비교 + 이월/갱신, openpyxl 없으면 csv)
                 ② plan-v2.docx (보정 델타 문서 — 추정→실측 이력 + 갱신 진단/목표/예산 + 새 병목 + #9 이월)

렌더 전 핵심 게이트를 재강제한다(cys-insight 패턴):
  필수 블록 · status · 실측 날조(actual_source) · 추정 보존(estimate). 위반 시 렌더 거부(종료코드 1).
전체 정밀 검증(부족 비난·mismatch 조정)은 fidelity-guard의 validate_reinforce.py가 맡는다.

사용:  python3 build_reinforce.py <reinforce.json> [출력디렉토리]
종료코드: 0 = 성공, 1 = 게이트 위반(렌더 거부), 2 = 파일/JSON 오류
라이브러리 없으면 폴백(openpyxl→csv·python-docx→md).
"""
import csv
import json
import os
import sys

FONT = "나눔명조"


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def gate(r):
    """렌더 전 핵심 게이트."""
    errs = []
    for blk in ("meta", "reconciliations"):
        if blk not in r:
            errs.append(f"필수 블록 '{blk}' 없음")
    # 형식 방어 — 검증기(validate_reinforce.py)와 parity: 적대적 비-dict/비-list는 렌더 거부.
    for dpath, dval in (("meta", r.get("meta")),
                        ("meta.church_context", _d(r.get("meta")).get("church_context")),
                        ("to_review", r.get("to_review"))):
        if dval is not None and not isinstance(dval, dict):
            errs.append(f"{dpath}가 객체(dict)가 아님")
    for lst in ("reconciliations", "plan_updates", "carryovers", "verify_targets", "extracted_data"):
        val = r.get(lst)
        if val is None:
            continue
        if not isinstance(val, list):
            errs.append(f"{lst}가 배열(list)이 아님")
        elif any(not isinstance(x, dict) for x in val):
            errs.append(f"{lst}에 객체(dict)가 아닌 원소가 섞임")
    tr_ub = _d(r.get("to_review")).get("updated_baselines")
    if tr_ub is not None:
        if not isinstance(tr_ub, list):
            errs.append("to_review.updated_baselines가 배열(list)이 아님")
        elif any(not isinstance(x, dict) for x in tr_ub):
            errs.append("to_review.updated_baselines에 객체(dict)가 아닌 원소가 섞임")
    meta = _d(r.get("meta"))
    if meta.get("status") not in ("제안", "확정"):
        errs.append("meta.status 가 제안|확정 이 아님")
    for i, rc in enumerate(_l(r.get("reconciliations"))):
        if not isinstance(rc, dict):
            errs.append(f"reconciliations[{i}]가 객체(dict)가 아님")
            continue
        item = rc.get("item", f"[{i}]")
        # validate_reinforce.py와 동일하게 strip 검사 — 공백만 있는 값은 '실측 날조'·'추정 삭제'로 차단.
        if rc.get("status") == "실측교체" and not (rc.get("actual_source") and str(rc.get("actual_source")).strip()):
            errs.append(f"reconciliations '{item}' 실측교체인데 actual_source 없음 — 실측 날조 금지")
        if not (rc.get("estimate") and str(rc.get("estimate")).strip()):
            errs.append(f"reconciliations '{item}'에 estimate 없음 — 추정 보존(이력)")
    return errs


def _dicts(seq):
    """리스트에서 dict 항목만 — 적대적 비-dict 원소·비-list 값으로 인한 크래시 방지."""
    return [x for x in seq if isinstance(x, dict)] if isinstance(seq, list) else []


def _cell(x):
    """출력 셀 안전화 — dict/list 값은 산출물 오염 차단(빈칸), 비-문자열 스칼라는 str 강제."""
    if x is None or isinstance(x, (str, int, float, bool)):
        return x if x is not None else ""
    if isinstance(x, (dict, list)):
        return ""
    return str(x)


def _txt(x):
    """문서 텍스트 안전화 — dict/list는 빈 문자열, 그 외는 str 강제."""
    if isinstance(x, (dict, list)) or x is None:
        return ""
    return str(x)


def build_xlsx(r, out_path):
    recs = _dicts(r.get("reconciliations"))
    updates = _dicts(r.get("plan_updates"))
    carry = _dicts(r.get("carryovers"))
    tr = _d(r.get("to_review"))
    to_review = _dicts(tr.get("updated_baselines"))

    rec_rows = [[_cell(rc.get("item", "")), _cell(rc.get("estimate", "")), _cell(rc.get("actual", "")),
                 _cell(rc.get("actual_source", "")), _cell(rc.get("delta", "")),
                 "어긋남" if rc.get("mismatch") else "", _cell(rc.get("status", "")), _cell(rc.get("new_confidence", ""))]
                for rc in recs]
    upd_rows = [[_cell(u.get("target", "")), _cell(u.get("before", "")), _cell(u.get("after", "")), _cell(u.get("reason", ""))] for u in updates]
    nxt_rows = [["이월", _cell(c.get("item", "")), _cell(c.get("reason", "")), _cell(c.get("to", ""))] for c in carry]
    nxt_rows += [["baseline 갱신", _cell(b.get("indicator", "")), _cell(b.get("new_baseline", "")), _cell(b.get("confidence", ""))] for b in to_review]

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        csv_path = out_path.rsplit(".", 1)[0] + ".csv"
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["[추정 vs 실측] 항목", "추정", "실측", "출처", "차이", "어긋남", "상태", "신뢰"])
            for row in rec_rows:
                w.writerow(row)
            w.writerow([]); w.writerow(["[계획 갱신] 대상", "이전", "이후", "이유"])
            for row in upd_rows:
                w.writerow(row)
            w.writerow([]); w.writerow(["[#9 이월·갱신] 구분", "항목", "내용", "대상/신뢰"])
            for row in nxt_rows:
                w.writerow(row)
        return csv_path

    wb = Workbook()
    head_fill = PatternFill("solid", fgColor="594B3B")
    head_font = Font(bold=True, color="FFFFFF")
    mismatch_fill = PatternFill("solid", fgColor="F6DAD2")

    ws = wb.active
    ws.title = "추정 vs 실측"
    ws.append(["항목", "추정", "실측", "출처", "차이", "어긋남", "상태", "신뢰"])
    for c in ws[1]:
        c.fill = head_fill; c.font = head_font
    for row in rec_rows:
        ws.append(row)
        if row[5] == "어긋남":
            for c in ws[ws.max_row]:
                c.fill = mismatch_fill
    for col, wd in zip("ABCDEFGH", [22, 20, 16, 22, 18, 8, 10, 6]):
        ws.column_dimensions[col].width = wd

    ws2 = wb.create_sheet("계획 갱신")
    ws2.append(["대상", "이전", "이후", "이유"])
    for c in ws2[1]:
        c.fill = head_fill; c.font = head_font
    for row in upd_rows:
        ws2.append(row)
    for col, wd in zip("ABCD", [22, 22, 24, 30]):
        ws2.column_dimensions[col].width = wd

    ws3 = wb.create_sheet("#9 이월·갱신")
    ws3.append(["구분", "항목", "내용", "대상/신뢰"])
    for c in ws3[1]:
        c.fill = head_fill; c.font = head_font
    for row in nxt_rows:
        ws3.append(row)
    for col, wd in zip("ABCD", [12, 24, 28, 20]):
        ws3.column_dimensions[col].width = wd

    wb.save(out_path)
    return out_path


def build_docx(r, path):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
    except ImportError:
        return None
    meta = _d(r.get("meta"))
    sepia = RGBColor(0x59, 0x4B, 0x3B)
    muted = RGBColor(0x8A, 0x7F, 0x70)
    accent = RGBColor(0xC7, 0x5A, 0x4A)

    def setfont(run, size, color=None, bold=False):
        run.font.name = FONT; run.font.size = Pt(size); run.font.bold = bold
        if color:
            run.font.color.rgb = color
        rPr = run._element.get_or_add_rPr()
        rF = rPr.find(qn("w:rFonts"))
        if rF is None:
            rF = rPr.makeelement(qn("w:rFonts"), {}); rPr.append(rF)
        for a in ("w:eastAsia", "w:ascii", "w:hAnsi"):
            rF.set(qn(a), FONT)

    def heading(txt):
        h = doc.add_paragraph(); setfont(h.add_run(txt), 14, sepia, True)

    doc = Document()
    t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setfont(t.add_run(f"{_txt(_d(meta.get('church_context')).get('name', ''))} 2027 목회계획서 v2 (자료 보정)".strip()), 19, sepia, True)
    sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setfont(sub.add_run("계획이 자료를 만나 또렷해졌습니다 — 추정 옆에 실측을 놓은 보정본"), 10.5, muted)

    # 추정→실측 이력
    heading("⚖️ 추정 → 실측 이력")
    for rc in _dicts(r.get("reconciliations")):
        mark = " ⚠어긋남" if rc.get("mismatch") else ""
        line = f"· {_txt(rc.get('item',''))}: 추정 [{_txt(rc.get('estimate',''))}] → 실측 [{_txt(rc.get('actual',''))}] ({_txt(rc.get('status',''))}{mark})"
        p = doc.add_paragraph(); setfont(p.add_run(line), 10.5, accent if rc.get("mismatch") else None)
        if rc.get("actual_source"):
            s = doc.add_paragraph(); setfont(s.add_run(f"    근거: {_txt(rc.get('actual_source'))} / 차이: {_txt(rc.get('delta',''))}"), 8.5, muted)

    # 갱신
    ups = _dicts(r.get("plan_updates"))
    if ups:
        heading("🌱 진단·목표·예산 갱신 (새 병목 조정)")
        for u in ups:
            p = doc.add_paragraph(); setfont(p.add_run(f"· {_txt(u.get('target',''))}: {_txt(u.get('before',''))} → {_txt(u.get('after',''))}"), 10.5)
            s = doc.add_paragraph(); setfont(s.add_run(f"    이유: {_txt(u.get('reason',''))}"), 8.5, muted)

    # #9 이월
    carry = _dicts(r.get("carryovers"))
    tr = _d(r.get("to_review"))
    heading("➡️ #9 분기 점검 첫 사이클로")
    for b in _dicts(tr.get("updated_baselines")):
        p = doc.add_paragraph(); setfont(p.add_run(f"· [실측 baseline] {_txt(b.get('indicator',''))} = {_txt(b.get('new_baseline',''))} (신뢰 {_txt(b.get('confidence',''))})"), 10.5)
    for c in carry:
        p = doc.add_paragraph(); setfont(p.add_run(f"· [이월] {_txt(c.get('item',''))} — {_txt(c.get('reason',''))} → {_txt(c.get('to',''))}"), 10.5, muted)
    if tr.get("note"):
        n = doc.add_paragraph(); setfont(n.add_run(_txt(tr.get("note"))), 9, muted)

    end = doc.add_paragraph(); end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setfont(end.add_run("확인된 만큼 확정했습니다. 나머지는 분기 점검에서 채웁니다 — 계획은 살아 움직입니다."), 9, muted)
    doc.save(path)
    return path


def build_md(r):
    L = ["# 2027 목회계획서 v2 (자료 보정)", "", "계획이 자료를 만나 또렷해졌습니다.", "", "## 추정 → 실측 이력", ""]
    for rc in _dicts(r.get("reconciliations")):
        mark = " ⚠어긋남" if rc.get("mismatch") else ""
        L.append(f"- {_txt(rc.get('item',''))}: 추정 [{_txt(rc.get('estimate',''))}] → 실측 [{_txt(rc.get('actual',''))}] ({_txt(rc.get('status',''))}{mark})")
        if rc.get("actual_source"):
            L.append(f"  - 근거: {_txt(rc.get('actual_source'))} / 차이: {_txt(rc.get('delta',''))}")
    L += ["", "## 진단·목표·예산 갱신", ""]
    for u in _dicts(r.get("plan_updates")):
        L.append(f"- {_txt(u.get('target',''))}: {_txt(u.get('before',''))} → {_txt(u.get('after',''))} ({_txt(u.get('reason',''))})")
    L += ["", "## #9 분기 점검 첫 사이클로", ""]
    tr = _d(r.get("to_review"))
    for b in _dicts(tr.get("updated_baselines")):
        L.append(f"- [실측 baseline] {_txt(b.get('indicator',''))} = {_txt(b.get('new_baseline',''))} (신뢰 {_txt(b.get('confidence',''))})")
    for c in _dicts(r.get("carryovers")):
        L.append(f"- [이월] {_txt(c.get('item',''))} — {_txt(c.get('reason',''))} → {_txt(c.get('to',''))}")
    return "\n".join(L) + "\n"


def main():
    if len(sys.argv) < 2:
        print("사용: python3 build_reinforce.py <reinforce.json> [출력디렉토리]"); sys.exit(2)
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
        print("[오류] 최상위 JSON이 객체(dict)가 아님 — reinforce.json은 객체여야 함"); sys.exit(2)

    errs = gate(r)
    if errs:
        print("=" * 60)
        print("렌더 거부 — 게이트 위반 (fidelity-guard 먼저 통과시키라)")
        print("=" * 60)
        for er in errs:
            print(f"  ✗ {er}")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    made = []
    xlsx_path = build_xlsx(r, os.path.join(out_dir, "reinforce-dashboard.xlsx"))
    made.append(xlsx_path + ("  (openpyxl 없어 csv 폴백)" if xlsx_path.endswith(".csv") else ""))
    docx_path = build_docx(r, os.path.join(out_dir, "plan-v2.docx"))
    if docx_path:
        made.append(docx_path)
    else:
        mp = os.path.join(out_dir, "plan-v2.md")
        with open(mp, "w", encoding="utf-8") as f:
            f.write(build_md(r))
        made.append(mp + "  (python-docx 없어 md 폴백)")

    print("렌더 완료 ✓")
    for m in made:
        print(f"  · {m}")
    sys.exit(0)


if __name__ == "__main__":
    main()
