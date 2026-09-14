#!/usr/bin/env python3
"""
build_event_plan.py — churchplan-signature-events 핵심 행사 기획안 렌더러.

events.json → ① event-plan.md (핵심 행사 1페이지 기획안 + 정기 행사 + 행사–목표 지도 + 정리 제안 + 경고)
              ② event-plan.xlsx (행사–목표 지도 시트 + 기획안 시트, openpyxl 없으면 .csv)

렌더 전 핵심 게이트를 재강제한다(cys-insight 패턴):
  필수 블록 · 표어 · 핵심 행사 목적(serves_axes) · 행사 상한(≤5). 위반 시 렌더 거부(종료코드 1).
전체 정밀 검증은 fidelity-guard의 validate_events.py가 맡는다.

사용:  python3 build_event_plan.py <events.json> [출력디렉토리]
종료코드: 0 = 성공, 1 = 게이트 위반(렌더 거부), 2 = 파일/JSON 오류
표준 라이브러리만 사용(xlsx는 openpyxl 있을 때만, 없으면 csv).
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    # 타입 계약은 검증기·렌더러 공유 SPEC으로 단일화(ADR-0002) — parity 구조화.
    from schema_guard import check_types
    from spec_signature_events import SIG_SCHEMA
except ImportError as _imp_err:
    print(f"[오류] 이식 자산 import 실패(schema_guard/spec_signature_events — sync_shared_assets 필요): {_imp_err}")
    sys.exit(2)

SIG_MAX = 5


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


def _join(seq):
    """리스트를 ', '로 안전하게 잇는다 — 비-문자열 원소도 str()로 방어(검증기-렌더러 계약).

    dict·list 원소는 산출물 오염을 막기 위해 제외한다(스칼라만 join)."""
    return ", ".join(str(v) for v in _l(seq) if not isinstance(v, (dict, list)))


def _cell(v):
    """xlsx/csv 셀 값 — dict·list는 산출물 오염을 막기 위해 빈 문자열로(스칼라만 통과)."""
    return "" if isinstance(v, (dict, list)) else v


def gate(e):
    """렌더 전 핵심 게이트."""
    errs = []
    for blk in ("meta", "signature_events"):
        if blk not in e:
            errs.append(f"필수 블록 '{blk}' 없음")
    # 타입 계약 — 검증기와 같은 SPEC(ADR-0002). parity 구조화(둘이 같은 guard를 부르므로 어긋날 수 없음).
    errs.extend(check_types(e, SIG_SCHEMA))
    if not str(_d(e.get("meta")).get("chosen_theme") or "").strip():
        errs.append("meta.chosen_theme 비어 있음 — 표어 먼저 확정(#2)")
    sig = _l(e.get("signature_events"))
    if len(sig) == 0:
        errs.append("핵심 행사 0개")
    if len(sig) > SIG_MAX:
        errs.append(f"핵심 행사 {len(sig)}개 — 최대 {SIG_MAX}(행사 수보다 깊이)")
    for i, ev in enumerate(sig):
        if not isinstance(ev, dict):
            continue  # 비-dict 원소 타입 위반은 SPEC(check_types)이 보고
        eid = ev.get("id", i)
        # (하위 필드 타입은 모두 SPEC이 검사 — 여기서는 의미 게이트만)
        if not _l(ev.get("serves_axes")):
            errs.append(f"행사[{eid}] serves_axes 없음 — 목적 없는 행사")
    return errs


def build_event_goal_map(e):
    """행사–목표 연결 지도를 signature_events에서 100% 결정론으로 조립한다(LLM 자유텍스트 금지).

    plan-compiler(#10)가 읽는 events.json의 event_goal_map 필드를 채운다. 행 수 = 핵심 행사 수.
    """
    sig = _l(e.get("signature_events"))
    lines = ["| 행사 | 섬기는 축 | 섬기는 목표 | 시기 |", "|---|---|---|---|"]
    for ev in sig:
        if not isinstance(ev, dict):
            continue
        bp = _d(ev.get("blueprint"))
        lines.append(
            f"| {ev.get('title', '')} | {_join(ev.get('serves_axes'))} "
            f"| {_join(ev.get('serves_goals'))} | {bp.get('timing', '')} |")
    return "\n".join(lines)


def build_md(e):
    meta = _d(e.get("meta"))
    L = []
    L.append("# 2027 연간 핵심 행사 기획")
    L.append("")
    L.append(f"- 표어: **{meta.get('chosen_theme', '(미확정)')}**")
    L.append(f"- 무게중심: {meta.get('focus', '')}  ·  "
             + ("✅ 목사 확정" if e.get("confirmed") else "🙏 목사 확정 대기"))
    L.append("")

    # 행사–목표 연결 지도 (event_goal_map과 동일한 결정론 표 — 단일 진실)
    sig = _l(e.get("signature_events"))
    L.append("## 행사–목표 연결 지도")
    L.append("")
    L.append(build_event_goal_map(e))
    L.append("")
    L.append("> 이 지도는 #4 설교–목표 지도(sermon_goal_map)와 짝입니다 — 강단(듣기)과 행사(겪기)가 같은 목표를 향합니다.")
    L.append("")

    # 핵심 행사 1페이지 기획안
    L.append("## 핵심 행사 기획안")
    L.append("")
    for ev in sig:
        if not isinstance(ev, dict):
            continue
        bp = _d(ev.get("blueprint"))
        sync = _d(ev.get("sermon_sync"))
        L.append(f"### {ev.get('title','')}")
        L.append(f"- 표어 연결: {ev.get('theme_link','')}")
        L.append(f"- 섬기는 축·목표: {_join(ev.get('serves_axes'))} / {_join(ev.get('serves_goals'))}")
        L.append(f"- 근거: {ev.get('rationale','')}")
        L.append(f"- **목적**: {bp.get('purpose','')}")
        L.append(f"- **대상**: {bp.get('audience','')}")
        L.append(f"- **시기**: {bp.get('timing','')}")
        flow = [v for v in _l(bp.get("flow")) if not isinstance(v, (dict, list))]
        L.append(f"- **핵심 흐름**: {' → '.join(str(v) for v in flow) if flow else ''}")
        res = _join(bp.get("resources"))
        L.append(f"- **필요 자원**: {res}")
        L.append(f"- **성공 신호**: {bp.get('success_signal','')}")
        if sync:
            L.append(f"- 설교 정합: {sync.get('supports','')} "
                     f"({'정합' if sync.get('aligned') else '점검 필요'})")
        L.append("")

    # 정기 행사
    reg = _l(e.get("regular_events"))
    if reg:
        L.append("## 정기 행사 (배치만)")
        L.append("")
        for r in reg:
            if not isinstance(r, dict):
                continue
            L.append(f"- {r.get('name','')} — {r.get('when','')} ({r.get('type','')})")
        L.append("")

    # 정리 제안
    pruned = _l(e.get("pruned_events"))
    if pruned:
        L.append("## ➖ 정리 제안 (목적 약한 행사)")
        L.append("")
        for p in pruned:
            if not isinstance(p, dict):
                continue
            L.append(f"- {p.get('name','')} — {p.get('reason','')}")
        L.append("")

    # 경고
    warns = _l(e.get("warnings"))
    if warns:
        L.append("## ⚖️ 과밀·자원·인력 경고")
        L.append("")
        for w in warns:
            if not isinstance(w, dict):
                continue
            L.append(f"- **[{w.get('type','')}]** {w.get('text','')}  _(근거: {w.get('basis','')})_")
        L.append("")

    L.append("> 행사는 표어를 살아내는 그릇입니다. 목적 약한 행사는 덜어내고, 한정된 일꾼을 과밀로 소진시키지 않습니다.")
    return "\n".join(L) + "\n"


FONT = "나눔명조"


def build_docx(e, path):
    """핵심 행사 1페이지 기획안 docx (마스터 문서: '각 1페이지, docx'). python-docx 없으면 None."""
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
    except ImportError:
        return None
    meta = _d(e.get("meta"))
    sepia = RGBColor(0x59, 0x4B, 0x3B)
    muted = RGBColor(0x8A, 0x7F, 0x70)

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

    doc = Document()
    t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setfont(t.add_run("2027 연간 핵심 행사 기획"), 20, sepia, True)
    th = doc.add_paragraph(); th.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setfont(th.add_run(str(meta.get("chosen_theme", "(미확정)"))), 12.5, sepia)
    fp = doc.add_paragraph(); fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setfont(fp.add_run(
        f"무게중심: {meta.get('focus', '')}  ·  "
        + ("✅ 목사 확정" if e.get("confirmed") else "🙏 목사 확정 대기")), 10, muted)

    sig = _l(e.get("signature_events"))
    for ev in sig:
        if not isinstance(ev, dict):
            continue
        bp = _d(ev.get("blueprint"))
        sync = _d(ev.get("sermon_sync"))
        h = doc.add_paragraph(); setfont(h.add_run(str(ev.get("title", ""))), 14, sepia, True)

        def line(label, val):
            p = doc.add_paragraph(); setfont(p.add_run(f"{label}: "), 10.5, bold=True)
            setfont(p.add_run(str(val)), 10.5)

        line("표어 연결", ev.get("theme_link", ""))
        line("섬기는 축·목표", f"{_join(ev.get('serves_axes'))} / {_join(ev.get('serves_goals'))}")
        line("근거", ev.get("rationale", ""))
        line("목적", bp.get("purpose", ""))
        line("대상", bp.get("audience", ""))
        line("시기", bp.get("timing", ""))
        flow = [v for v in _l(bp.get("flow")) if not isinstance(v, (dict, list))]
        line("핵심 흐름", " → ".join(str(v) for v in flow) if flow else "")
        line("필요 자원", _join(bp.get("resources")))
        line("성공 신호", bp.get("success_signal", ""))
        if sync:
            line("설교 정합", f"{sync.get('supports', '')} "
                 f"({'정합' if sync.get('aligned') else '점검 필요'})")

    reg = _l(e.get("regular_events"))
    if reg:
        h = doc.add_paragraph(); setfont(h.add_run("정기 행사 (배치만)"), 13, sepia, True)
        for r in reg:
            if not isinstance(r, dict):
                continue
            p = doc.add_paragraph()
            setfont(p.add_run(f"· {r.get('name','')} — {r.get('when','')} ({r.get('type','')})"), 10.5)

    end = doc.add_paragraph(); end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setfont(end.add_run("행사는 표어를 살아내는 그릇입니다 — 목적 약한 행사는 덜어내고, 일꾼을 과밀로 소진시키지 않습니다."), 9, muted)
    doc.save(path)
    return path


MAP_HEADER = ["행사", "섬기는 축", "섬기는 목표", "시기", "목적", "성공 신호"]


def build_xlsx(e, out_path):
    sig = _l(e.get("signature_events"))
    rows = []
    for ev in sig:
        if not isinstance(ev, dict):
            continue
        bp = _d(ev.get("blueprint"))
        rows.append([
            _cell(ev.get("title", "")), _join(ev.get("serves_axes")),
            _join(ev.get("serves_goals")), _cell(bp.get("timing", "")),
            _cell(bp.get("purpose", "")), _cell(bp.get("success_signal", "")),
        ])
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill
    except ImportError:
        csv_path = out_path.rsplit(".", 1)[0] + ".csv"
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(MAP_HEADER)
            for r in rows:
                w.writerow(r)
            w.writerow([])
            w.writerow(["[정리 제안]"])
            for p in _l(e.get("pruned_events")):
                if not isinstance(p, dict):
                    continue
                w.writerow([p.get("name", ""), p.get("reason", "")])
        return csv_path

    wb = Workbook()
    head_fill = PatternFill("solid", fgColor="594B3B")
    head_font = Font(bold=True, color="FFFFFF")
    ws = wb.active
    ws.title = "행사–목표 지도"
    ws.append(MAP_HEADER)
    for c in ws[1]:
        c.fill = head_fill; c.font = head_font; c.alignment = Alignment(horizontal="center", vertical="center")
    for r in rows:
        ws.append(r)
    for col, wd in zip("ABCDEF", [22, 14, 20, 14, 34, 30]):
        ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")

    warns = _l(e.get("warnings"))
    pruned = _l(e.get("pruned_events"))
    if warns or pruned:
        ws2 = wb.create_sheet("경고·정리")
        ws2.append(["구분", "내용", "근거/사유"])
        for c in ws2[1]:
            c.fill = head_fill; c.font = head_font
        for w in warns:
            if not isinstance(w, dict):
                continue
            ws2.append([_cell(w.get("type", "")), _cell(w.get("text", "")), _cell(w.get("basis", ""))])
        for p in pruned:
            if not isinstance(p, dict):
                continue
            ws2.append(["정리제안", _cell(p.get("name", "")), _cell(p.get("reason", ""))])
        for col, wd in zip("ABC", [12, 36, 30]):
            ws2.column_dimensions[col].width = wd

    wb.save(out_path)
    return out_path


def main():
    if len(sys.argv) < 2:
        print("사용: python3 build_event_plan.py <events.json> [출력디렉토리]"); sys.exit(2)
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(src))
    try:
        with open(src, encoding="utf-8") as f:
            e = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {src}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(e, dict):
        print("[오류] 최상위가 객체(dict)가 아님 — events.json은 객체여야 함"); sys.exit(2)

    errs = gate(e)
    if errs:
        print("=" * 60)
        print("렌더 거부 — 게이트 위반 (fidelity-guard 먼저 통과시키라)")
        print("=" * 60)
        for er in errs:
            print(f"  ✗ {er}")
        sys.exit(1)

    # event_goal_map을 결정론으로 계산해 events.json에 기록(plan-compiler #10가 읽음 — LLM 자유텍스트 금지)
    e["event_goal_map"] = build_event_goal_map(e)
    with open(src, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=2)

    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "event-plan.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(build_md(e))
    xlsx_path = build_xlsx(e, os.path.join(out_dir, "event-plan.xlsx"))
    docx_path = build_docx(e, os.path.join(out_dir, "event-plan.docx"))

    print("렌더 완료 ✓")
    print(f"  · {md_path}")
    if docx_path:
        print(f"  · {docx_path}")
    else:
        print("  · (python-docx 없어 docx 생략 — md가 후편집 포맷)")
    print(f"  · {xlsx_path}" + ("  (openpyxl 없어 csv 폴백)" if xlsx_path.endswith(".csv") else ""))
    print(f"  · events.json에 event_goal_map 기록({src})")
    sys.exit(0)


if __name__ == "__main__":
    main()
