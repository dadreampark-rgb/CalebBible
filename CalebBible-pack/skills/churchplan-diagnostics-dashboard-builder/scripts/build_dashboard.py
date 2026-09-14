#!/usr/bin/env python3
"""
build_dashboard.py — churchplan-diagnostics 한 장 진단 거울 결정론 렌더러.

diagnosis.json(+선택 recall-dataset.json)을 받아 diagnostics-dashboard.html 과
diagnostics.xlsx(openpyxl 없으면 .csv)를 산출한다. 차트를 LLM이 그리지 않고
스크립트가 결정론적으로 그려 할루시네이션을 차단한다.

핵심 규칙(references/dashboard-design.md):
  · 모든 수치에 신뢰 배지  · 범위는 오차 띠(점값 막대 금지)
  · 신뢰 '하'는 흐리게/점선  · 미회상은 "—"  · 따뜻한 팔레트(경보색 금지)

렌더 전 핵심 게이트를 재강제한다(검증기-렌더러 parity — garbage-in을 렌더 단계에서도 차단):
  필수 블록 형식 · 점값 둔갑 · 병목/헤드라인 누락 · 범위형/score 오류 · 근거 추적성.
  위반 시 렌더 거부(종료코드 1). 회상 대조 등 전체 정밀 검증은 fidelity-guard의
  validate_diagnostics.py가 맡는다(의도적 비대칭).

사용: python3 build_dashboard.py <diagnosis.json> [recall-dataset.json] --out <디렉터리>
종료코드: 0 = 성공, 1 = 게이트 위반(렌더 거부), 2 = 파일/JSON 오류
표준 라이브러리만 필수. openpyxl 있으면 xlsx, 없으면 csv.
"""
import json
import math
import os
import sys
import html

# ── 따뜻한 팔레트 ─────────────────────────────────────────────
BG = "#FBF8F3"; INK = "#3A3632"; SEPIA = "#594B3B"
GREEN = "#6B8E6F"; EARTH = "#C08552"; GREY = "#9A938B"
CONF_DOT = {"상": "●●●", "중": "●●○", "하": "●○○"}


def esc(x):
    return html.escape(str(x)) if x is not None else ""


def badge(conf):
    if not conf:
        return ""
    color = {"상": GREEN, "중": SEPIA, "하": EARTH}.get(conf, GREY)
    label = "추정" if conf == "하" else ""
    return (f'<span style="font-size:11px;color:{color}">{CONF_DOT.get(conf,"")}'
            f'<span style="margin-left:3px">{conf}</span>'
            f'{f" · {label}" if label else ""}</span>')


def trend_arrow(t):
    return {"↑": f'<span style="color:{GREEN}">↑</span>',
            "↓": f'<span style="color:{EARTH}">↓</span>',
            "→": f'<span style="color:{GREY}">→</span>'}.get(t, "")


# ── 8영역 inline SVG 레이더 ───────────────────────────────────
def svg_radar(areas):
    order = ["예배", "말씀", "교제", "전도", "양육", "봉사", "선교", "재정"]
    by = {a.get("area"): a for a in areas if isinstance(a, dict)}
    cx = cy = 150; R = 110; n = 8
    def pt(i, r):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        return cx + r * math.cos(ang), cy + r * math.sin(ang)
    parts = ['<svg viewBox="0 0 300 320" width="300" height="320" '
             'xmlns="http://www.w3.org/2000/svg">']
    # 그리드 링 1~5
    for ring in range(1, 6):
        rr = R * ring / 5
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, rr) for i in range(n)))
        parts.append(f'<polygon points="{pts}" fill="none" stroke="#E5DDD0" stroke-width="1"/>')
    # 스포크 + 라벨
    poly = []
    for i, area in enumerate(order):
        x_out, y_out = pt(i, R)
        a = by.get(area, {})
        conf = a.get("confidence")
        dash = ' stroke-dasharray="3,3"' if conf == "하" else ""
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x_out:.1f}" y2="{y_out:.1f}" '
                     f'stroke="#D8CFC0" stroke-width="1"{dash}/>')
        lx, ly = pt(i, R + 18)
        label = area + ("*" if conf == "하" else "")
        anchor = "middle"
        if lx < cx - 5: anchor = "end"
        elif lx > cx + 5: anchor = "start"
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="12" fill="{INK}" '
                     f'text-anchor="{anchor}" dominant-baseline="middle">{esc(label)}</text>')
        score = a.get("score")
        if isinstance(score, (int, float)):
            poly.append(pt(i, R * score / 5))
    # 점수 다각형
    if len(poly) >= 3:
        pstr = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
        parts.append(f'<polygon points="{pstr}" fill="{SEPIA}" fill-opacity="0.18" '
                     f'stroke="{SEPIA}" stroke-width="2"/>')
    parts.append(f'<text x="{cx}" y="305" font-size="11" fill="{GREY}" '
                 f'text-anchor="middle">* 점선·추정(신뢰 하)</text>')
    parts.append("</svg>")
    return "".join(parts)


# ── 흐름 카드 (범위 오차 띠) ──────────────────────────────────
def valid_range(r):
    """range가 [lo,hi] 2-원소 숫자 배열인지(bool 배제)."""
    return (isinstance(r, list) and len(r) == 2
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in r))


def trend_cards(metrics):
    his = [m["range"][1] for m in metrics
           if isinstance(m, dict) and valid_range(m.get("range"))]
    # 모든 hi가 0이면(예: '올해 신규 등록 0' → range[0,0]) max(his)*1.15=0 → 0 나눗셈 방지.
    scale = (max(his) * 1.15) or 1 if his else 1
    rows = []
    for m in metrics:
        if not isinstance(m, dict):
            continue
        label = esc(m.get("label", ""))
        conf = m.get("confidence")
        if m.get("status") == "미회상" or (m.get("value") is None and "range" not in m):
            body = f'<span style="color:{GREY}">— (워크샵 후 확인)</span>'
        elif valid_range(m.get("range")):
            lo, hi = m["range"]
            left = lo / scale * 100; width = max((hi - lo) / scale * 100, 2)
            faded = "opacity:.55;" if conf == "하" else ""
            body = (f'<div style="position:relative;height:14px;background:#EFE8DC;border-radius:7px;{faded}">'
                    f'<div style="position:absolute;left:{left:.1f}%;width:{width:.1f}%;height:14px;'
                    f'background:{SEPIA};border-radius:7px;opacity:.5"></div></div>'
                    f'<span style="font-size:12px;color:{INK}">{lo}~{hi}</span>')
        else:
            body = f'<span style="color:{INK}">{esc(m.get("value",""))}</span>'
        rows.append(
            f'<div style="margin:8px 0">'
            f'<div style="display:flex;justify-content:space-between">'
            f'<b style="font-size:13px">{label} {trend_arrow(m.get("trend"))}</b>{badge(conf)}</div>'
            f'{body}'
            f'<div style="font-size:11px;color:{GREY}">{esc(m.get("basis",""))}</div></div>')
    return "".join(rows)


def funnel_html(fn):
    cells = []
    bottleneck = fn.get("bottleneck")
    stages = fn.get("stages", [])
    for st in stages if isinstance(stages, list) else []:
        if not isinstance(st, dict):
            continue
        name = st.get("name", ""); sense = st.get("sense", "")
        is_bn = bool(bottleneck and isinstance(name, str) and isinstance(bottleneck, str)
                     and bottleneck in name)
        bg = EARTH if is_bn else "#EFE8DC"
        fg = "#FFF" if is_bn else INK
        val = esc(st.get("value", ""))
        cells.append(f'<div style="flex:1;text-align:center;padding:10px 6px;background:{bg};'
                     f'color:{fg};border-radius:8px;margin:0 3px">'
                     f'<div style="font-size:12px;font-weight:bold">{esc(name)}</div>'
                     f'<div style="font-size:12px">{esc(sense)}</div>'
                     f'<div style="font-size:11px;opacity:.85">{val}</div></div>')
    arrow = '<div style="align-self:center;color:#C9BFB0">→</div>'
    flow = arrow.join(cells)
    note = esc(fn.get("care_note", ""))
    return (f'<div style="display:flex;align-items:stretch">{flow}</div>'
            f'<div style="font-size:12px;color:{EARTH};margin-top:6px">🤲 {note}</div>')


def list_html(items, color):
    out = []
    for it in items:
        if isinstance(it, dict):
            t = esc(it.get("text", "")); b = esc(it.get("basis", ""))
            out.append(f'<li><b>{t}</b> <span style="font-size:11px;color:{GREY}">— {b}</span></li>')
        elif isinstance(it, (str, int, float)) and not isinstance(it, bool):
            out.append(f'<li>{esc(it)}</li>')
        # list/기타 비-스칼라 원소는 산출물 오염 방지로 제외(렌더 생략).
    return f'<ul style="margin:4px 0;padding-left:18px;color:{color}">' + "".join(out) + "</ul>"


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


REQUIRED_BLOCKS = ("meta", "trend", "funnel", "health_radar", "findings")
CONFIDENCE_VALUES = {"상", "중", "하"}


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


import re as _re

# 점값 둔갑(문자열판) — 검증기 validate_diagnostics.is_bare_point_string와 동일 규칙(parity).
_HEDGE_MARKERS = ("약", "내외", "이상", "이하", "정도", "쯤", "여명", "여 명", "여가정",
                  "가량", "남짓", "미만", "초과", "±", "안팎")
_SPAN_MARKERS = ("~", "～", "-", "–", "—", "부터", "에서")


def _is_bare_point_string(s):
    if not isinstance(s, str):
        return False
    t = s.strip()
    if any(mk in t for mk in _SPAN_MARKERS) or any(mk in t for mk in _HEDGE_MARKERS):
        return False
    return len(_re.findall(r"\d+", t)) == 1


def _check_metric_gate(path, m, conf_required, errs):
    """수치 메트릭 게이트 — 검증기 check_metric과 동일 수준(점값 둔갑·범위형·신뢰).
    conf_required=True면 confidence 누락도 위반(trend.metrics). funnel.value는 선택 필드라 False."""
    conf = m.get("confidence")
    if conf_required and conf is None:
        errs.append(f"{path}: confidence(상/중/하) 없음(렌더 거부)")
    elif conf is not None and conf not in CONFIDENCE_VALUES:
        errs.append(f"{path}: confidence '{conf}' 오류(렌더 거부)")
    if "range" not in m:
        for fld in ("point", "value"):
            if fld not in m or conf not in ("하", "중"):
                continue
            if _is_num(m[fld]):
                errs.append(f"{path}: 신뢰 '{conf}' 인데 정밀 {fld}={m[fld]} 단정 — 점값 둔갑(렌더 거부)")
            elif _is_bare_point_string(m[fld]):
                errs.append(f"{path}: 신뢰 '{conf}' 인데 정밀 {fld}='{m[fld]}' 문자열 단정 — 점값 둔갑(렌더 거부)")
    if "range" in m:
        rng = m["range"]
        if not (isinstance(rng, list) and len(rng) == 2 and _is_num(rng[0]) and _is_num(rng[1])):
            errs.append(f"{path}: range는 [lo,hi] 2-원소 숫자 배열이어야 함(렌더 거부)")
        elif rng[0] > rng[1]:
            errs.append(f"{path}: range lo({rng[0]}) > hi({rng[1]}) 역전(렌더 거부)")


def gate(diag):
    """렌더 전 핵심 게이트 — 검증기(validate_diagnostics.py)와 동일 수준의 형식·필수블록
    안전선을 재강제한다(CLAUDE.md '렌더러 게이트 재강제' + '검증기-렌더러 parity').
    추정의 점값 둔갑·병목/헤드라인 누락·범위형 오류 등 정직성 위반을 렌더 단계에서도 차단.
    전체 정밀 검증(회상 대조 등)은 fidelity-guard의 validate_diagnostics.py가 맡는다.
    위반 1건이라도 있으면 렌더 거부(EXIT 1). garbage-in을 한 장 거울로 둔갑시키지 않는다."""
    errs = []
    # 1) 필수 블록 존재 + dict 형식(검증기 parity — truthy 비-dict 조용한 통과 금지)
    for blk in REQUIRED_BLOCKS:
        if blk not in diag:
            errs.append(f"필수 블록 '{blk}' 없음")
        elif not isinstance(diag.get(blk), dict):
            errs.append(f"최상위 '{blk}'가 객체가 아님 — 형식오류(렌더 거부)")
    # 2) trend.metrics — 점값 둔갑·맨숫자·신뢰누락·범위형 (검증기 check_metric 수준)
    tr = _d(diag.get("trend"))
    if "metrics" in tr and not isinstance(tr.get("metrics"), list):
        errs.append("trend.metrics가 배열이 아님 — 형식오류(렌더 거부)")
    for i, m in enumerate(_l(tr.get("metrics"))):
        lbl = (m.get("label", i) if isinstance(m, dict) else i)
        if not isinstance(m, dict):
            if _is_num(m):
                errs.append(f"trend.metrics[{i}]: 범위·신뢰 없는 맨숫자 '{m}' — 추정의 사실 둔갑(렌더 거부)")
            else:
                errs.append(f"trend.metrics[{i}]: 메트릭은 객체여야 함(렌더 거부)")
            continue
        if m.get("status") == "미회상":
            continue
        if "value" in m or "range" in m or "point" in m:
            _check_metric_gate(f"trend.metrics[{lbl}]", m, True, errs)
    # 3) funnel — 병목 방향(진단의 심장) + stages 형식 + value 점값 둔갑(검증기 parity)
    fn = _d(diag.get("funnel"))
    if "stages" in fn and not isinstance(fn.get("stages"), list):
        errs.append("funnel.stages가 배열이 아님 — 형식오류(렌더 거부)")
    for i, st in enumerate(_l(fn.get("stages"))):
        if not isinstance(st, dict):
            errs.append(f"funnel.stages[{i}]: 객체여야 함(렌더 거부)")
            continue
        if "value" in st:
            _check_metric_gate(f"funnel.{st.get('name','?')}", st, False, errs)
    if not fn.get("bottleneck_direction"):
        errs.append("funnel.bottleneck_direction 비어 있음 — 진단의 심장(렌더 거부)")
    # 4) health_radar — areas 형식 + score 1~5
    hr = _d(diag.get("health_radar"))
    if "areas" in hr and not isinstance(hr.get("areas"), list):
        errs.append("health_radar.areas가 배열이 아님 — 형식오류(렌더 거부)")
    for i, a in enumerate(_l(hr.get("areas"))):
        if not isinstance(a, dict):
            errs.append(f"health_radar.areas[{i}]: 객체여야 함(렌더 거부)")
            continue
        sc = a.get("score")
        if sc is not None and a.get("status") != "미회상":
            if isinstance(sc, bool) or not (_is_num(sc) and 1 <= sc <= 5):
                errs.append(f"health_radar.{a.get('area','?')}: score '{sc}' 1~5 아님(렌더 거부)")
    # 5) findings — 헤드라인(진단의 첫 문장) + 근거 추적성
    fd = _d(diag.get("findings"))
    if not fd.get("bottleneck_headline"):
        errs.append("findings.bottleneck_headline 비어 있음 — 진단의 첫 문장(렌더 거부)")
    for key in ("strengths_top3", "needs_care_top3"):
        if key in fd and not isinstance(fd.get(key), list):
            errs.append(f"findings.{key}가 배열이 아님 — 형식오류(렌더 거부)")
        for i, it in enumerate(_l(fd.get(key))):
            if isinstance(it, dict):
                if not it.get("basis"):
                    errs.append(f"findings.{key}[{i}]: basis 없음 — 회상 추적 불가(렌더 거부)")
            else:
                errs.append(f"findings.{key}[{i}]: basis 없는 비-객체 항목 — {{text,basis}}여야 함(렌더 거부)")
    return errs


def build_html(diag, out_dir):
    meta = _d(diag.get("meta")); ctx = _d(meta.get("church_context"))
    fd = _d(diag.get("findings"))
    church = " · ".join(str(v) for v in [ctx.get("denomination"), ctx.get("size_band"),
                                         ctx.get("region")] if v) or "교회"
    # 회상연도: guided-recall dataset-schema는 meta.recall_year에 둔다(church_context 형제).
    # meta 레벨 우선, 하위호환으로 church_context도 조회. source_recall 결합 제거.
    year = meta.get("recall_year") or ctx.get("recall_year", "")
    headline = esc(fd.get("bottleneck_headline", ""))
    radar = svg_radar(_l(_d(diag.get("health_radar")).get("areas")))
    trends = trend_cards(_l(_d(diag.get("trend")).get("metrics")))
    funnel = funnel_html(_d(diag.get("funnel")))
    strengths = list_html(_l(fd.get("strengths_top3")), GREEN)
    care = list_html(_l(fd.get("needs_care_top3")), EARTH)
    verify = "".join(f"<li>☐ {esc(v)}</li>" for v in _l(fd.get("verify_after_workshop"))
                     if isinstance(v, (str, int, float)) and not isinstance(v, bool))
    doc = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>교회 현황 진단 거울</title>
<style>
  body{{background:{BG};color:{INK};font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif;
        margin:0;padding:24px;}}
  .sheet{{max-width:900px;margin:0 auto;background:#fff;padding:28px 32px;border-radius:12px;
          box-shadow:0 2px 12px rgba(89,75,59,.08);}}
  h1{{font-size:20px;color:{SEPIA};margin:0 0 2px}}
  .note{{font-size:12px;color:{GREY};margin-bottom:14px}}
  .headline{{font-size:22px;color:{SEPIA};font-weight:bold;border-left:5px solid {EARTH};
             padding:8px 14px;background:#FAF5EC;border-radius:0 8px 8px 0;margin:14px 0}}
  .row{{display:flex;gap:24px;flex-wrap:wrap}}
  .col{{flex:1;min-width:280px}}
  .card-title{{font-size:14px;font-weight:bold;color:{SEPIA};margin:14px 0 6px;
               border-bottom:1px solid #EAE2D5;padding-bottom:3px}}
  .legend{{font-size:11px;color:{GREY};border-top:1px solid #EAE2D5;margin-top:18px;padding-top:8px}}
</style></head><body><div class="sheet">
  <h1>🪞 교회 현황 진단 거울 — {esc(church)}{f' · {year}' if year else ''}</h1>
  <div class="note">추정 기반 진단 — 신뢰수준 표기. 흐린 곳(추정)은 워크샵 후 보강을 권합니다. 숫자는 돌봄의 신호입니다.</div>
  <div class="headline">🔑 {headline}</div>
  <div class="row">
    <div class="col"><div class="card-title">여덟 영역</div>{radar}</div>
    <div class="col"><div class="card-title">흐름</div>{trends}</div>
  </div>
  <div class="card-title">어디서 새는가 (깔때기)</div>{funnel}
  <div class="row">
    <div class="col"><div class="card-title">✅ 감사할 곳 (강점)</div>{strengths}</div>
    <div class="col"><div class="card-title">🤲 먼저 돌봄이 필요한 곳</div>{care}</div>
  </div>
  <div class="card-title">📌 귀가 후 확인할 항목 (신뢰 '하')</div>
  <ul style="color:{GREY};font-size:13px">{verify}</ul>
  <div class="legend">범례 — 신뢰: ●●●상 ●●○중 ●○○하(추정) · 범위는 띠로 표기(점값 단정 아님) ·
    미회상은 "—" · 색은 정죄가 아닌 돌봄을 뜻합니다.</div>
</div></body></html>"""
    path = os.path.join(out_dir, "diagnostics-dashboard.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


def _cell(x):
    """표 셀 값 정규화: dict/list 등 비-스칼라는 산출물 오염 방지로 문자열화,
    None은 빈칸. xlsx/csv 둘 다 list 셀을 거부·오염하므로 셀 경계에서 강제 환원."""
    if x is None:
        return ""
    if isinstance(x, (str, int, float)) and not isinstance(x, bool):
        return x
    return str(x)


def build_table(diag, out_dir):
    areas = _l(_d(diag.get("health_radar")).get("areas"))
    verify = _l(_d(diag.get("findings")).get("verify_after_workshop"))
    rows = [("영역", "점수", "추이", "신뢰", "근거")]
    for a in areas:
        if not isinstance(a, dict):
            continue
        rows.append((_cell(a.get("area")), _cell(a.get("score")), _cell(a.get("trend")),
                     _cell(a.get("confidence")), _cell(a.get("basis"))))
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active; ws.title = "진단요약"
        for r in rows:
            ws.append([_cell(c) for c in r])
        ws2 = wb.create_sheet("확인목록")
        ws2.append(["귀가 후 확인할 항목 (신뢰 '하')"])
        for v in verify:
            ws2.append([_cell(v)])
        path = os.path.join(out_dir, "diagnostics.xlsx")
        wb.save(path)
        return path
    except ImportError:
        import csv
        path = os.path.join(out_dir, "diagnostics.csv")
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            for r in rows:
                w.writerow([_cell(c) for c in r])
            w.writerow([]); w.writerow(["귀가 후 확인 항목"])
            for v in verify:
                w.writerow([_cell(v)])
        return path


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("사용: python3 build_dashboard.py <diagnosis.json> [recall.json] --out <디렉터리>")
        sys.exit(2)
    out_dir = None
    if "--out" in sys.argv:
        idx = sys.argv.index("--out")
        if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--"):
            out_dir = sys.argv[idx + 1]
        else:
            print("[오류] --out 뒤에 디렉터리 경로가 필요합니다.")
            sys.exit(2)
    if out_dir is None:
        # --out 미지정 시 diagnosis.json 디렉터리를 기본 출력 위치로(cwd 오염 방지).
        out_dir = os.path.dirname(os.path.abspath(args[0])) or "."
        print(f"[안내] --out 미지정 — 산출물을 입력 디렉터리에 생성합니다: {out_dir}",
              file=sys.stderr)
    try:
        with open(args[0], encoding="utf-8") as f:
            diag = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {args[0]}"); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}"); sys.exit(2)
    if not isinstance(diag, dict):
        print(f"[오류] diagnosis.json 최상위가 JSON 객체가 아님 (받음: {type(diag).__name__})")
        sys.exit(2)
    errs = gate(diag)
    if errs:
        print("=" * 60)
        print("렌더 거부 — 게이트 위반 (fidelity-guard 먼저 통과시키라)")
        print("=" * 60)
        for e in errs:
            print(f"  ✗ {e}")
        print("\n결과: 차단 — 추정을 점값으로 둔갑시키거나 병목/근거를 비운 거울은 렌더하지 않는다.")
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    html_path = build_html(diag, out_dir)
    table_path = build_table(diag, out_dir)
    print(f"✓ 대시보드: {html_path}")
    print(f"✓ 정리표:   {table_path}")


if __name__ == "__main__":
    main()
