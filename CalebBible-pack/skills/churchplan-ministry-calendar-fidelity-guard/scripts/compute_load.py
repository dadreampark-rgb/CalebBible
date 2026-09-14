#!/usr/bin/env python3
"""
compute_load.py — churchplan-ministry-calendar 부하 점수(load) 결정론 산식.

season-frame-catalog.md §2 rubric을 파이썬으로 환원한다(LLM 임의 부풀림 금지):
  절기 고강도 +2 / 절기 일반 +1 / 핵심 행사 +2(개당) / 정기 행사 +1(개당)
  / 캠페인 진행 +1(개당) / 연속 강해 4주째 이상 +1 / 마일스톤 점검 +1
level 매핑: score ≤1 낮음 · 2~3 보통 · ≥4 높음.

overload-marker가 weeks[].load 를 결정론 산출하고, validate_calendar.py 가
표기 load 와 재계산값을 대조한다(불일치 시 위반).

사용(독립 실행):  python3 compute_load.py <calendar.json>  → 재계산 load 출력
표준 라이브러리만 사용.
"""
import json
import sys

# season-frame-catalog.md §2 — 절기 고강도 집합(+2). 그 외 observance 존재 시 +1.
HIGH_OBSERVANCES = {
    "종려주일", "부활주일", "성탄절", "추수감사주일", "맥추감사", "성령강림주일", "송구영신",
}


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _ld(x):
    return [v for v in x if isinstance(v, dict)] if isinstance(x, list) else []


def compute_week_load(wk, prev_series_streak):
    """한 주의 load(score·level·factors)를 rubric으로 결정론 산출.

    prev_series_streak: (series_id, 연속 주 수) — 직전까지 같은 series가 몇 주 연속됐는지.
    반환: (load_dict, new_streak) — new_streak 은 다음 주 계산용.
    """
    score = 0
    factors = []

    obs = wk.get("observance")
    if obs:
        if obs in HIGH_OBSERVANCES:
            score += 2
            factors.append(f"절기 고강도 {obs}")
        else:
            score += 1
            factors.append(f"절기 일반 {obs}")

    n_core = n_reg = 0
    for ev in _ld(wk.get("events")):
        if ev.get("type") == "핵심":
            n_core += 1
        else:
            n_reg += 1
    if n_core:
        score += 2 * n_core
        factors.append(f"핵심 행사 {n_core}")
    if n_reg:
        score += 1 * n_reg
        factors.append(f"정기 행사 {n_reg}")

    n_camp = len(_ld(wk.get("campaigns")))
    if n_camp:
        score += n_camp
        factors.append(f"캠페인 진행 {n_camp}")

    # 연속 강해 4주째 이상 +1
    sm = _d(wk.get("sermon"))
    sid = sm.get("series_id")
    prev_sid, streak = prev_series_streak
    if sid and sid == prev_sid:
        streak = streak + 1
    elif sid:
        streak = 1
    else:
        streak = 0
    if streak >= 4:
        score += 1
        factors.append(f"연속 강해 {streak}주째")

    if _ld(wk.get("milestones")):
        score += 1
        factors.append("마일스톤 점검")

    level = "낮음" if score <= 1 else ("보통" if score <= 3 else "높음")
    return {"score": score, "level": level, "factors": factors}, (sid, streak)


def compute_all_loads(weeks):
    """주차 순서대로 각 주의 load 를 재계산. {week_number: load_dict} 반환."""
    out = {}
    prev = (None, 0)
    for wk in sorted((w for w in _l(weeks) if isinstance(w, dict) and isinstance(w.get("week"), int)),
                     key=lambda x: x.get("week")):
        load, prev = compute_week_load(wk, prev)
        out[wk.get("week")] = load
    return out


def detect_density(weeks):
    """연속 고강도/절기 고강도 인접 구간을 결정론 스캔해 density_warnings 를 생성.

    season-frame-catalog §2: 높음(score≥4) 2주 이상 연속 → type='연속고강도', level='고'.
    반환: density_warnings 리스트(각 type·weeks·text·level·basis).
    """
    ordered = sorted((w for w in _l(weeks) if isinstance(w, dict) and isinstance(w.get("week"), int)),
                     key=lambda x: x.get("week"))
    loads = compute_all_loads(weeks)
    warnings = []

    # 연속 '높음' 구간(인접 주차 번호) 스캔
    run = []
    prev_n = None
    nums = [wk.get("week") for wk in ordered]
    for n in nums:
        lvl = loads.get(n, {}).get("level")
        if lvl == "높음" and (prev_n is None or n == prev_n + 1):
            run.append(n)
        else:
            if len(run) >= 2:
                warnings.append({
                    "type": "연속고강도", "weeks": list(run),
                    "text": f"{run[0]}~{run[-1]}주 {len(run)}주 연속 고강도(부하 높음)",
                    "level": "고", "basis": "compute_load rubric level=높음 연속"})
            run = [n] if lvl == "높음" else []
        prev_n = n
    if len(run) >= 2:
        warnings.append({
            "type": "연속고강도", "weeks": list(run),
            "text": f"{run[0]}~{run[-1]}주 {len(run)}주 연속 고강도(부하 높음)",
            "level": "고", "basis": "compute_load rubric level=높음 연속"})
    return warnings


def main():
    if len(sys.argv) != 2:
        print("사용: python3 compute_load.py <calendar.json>"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            c = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)
    if not isinstance(c, dict):
        print("[오류] 최상위가 객체(JSON object)가 아님"); sys.exit(2)
    weeks = _l(c.get("weeks"))
    loads = compute_all_loads(weeks)
    for n in sorted(loads):
        ld = loads[n]
        print(f"week {n}: score={ld['score']} level={ld['level']} factors={ld['factors']}")
    dens = detect_density(weeks)
    if dens:
        print("\n[density_warnings]")
        for d in dens:
            print(f"  {d['type']} weeks={d['weeks']} level={d['level']} — {d['text']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
