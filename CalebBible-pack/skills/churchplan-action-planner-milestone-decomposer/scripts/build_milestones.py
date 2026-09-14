#!/usr/bin/env python3
"""
build_milestones.py — churchplan-action-planner milestone-decomposer 결정론 골격 생성.

goals.json(중첩 axes[].goals[]) → action.json 골격을 결정론적으로 생성:
  · inputs_echo.from_goals — axes[].goals[]를 평탄 [{axis,direction_goal,indicators}] 로 전사
  · actions[] 골격 — 각 indicator마다 한 action:
      id, source_goal="<axis>: <direction_goal>"(근거 추적 키·정확 매칭),
      milestone={label, by, from_indicator}(indicators[].by/label 전사),
      timing="", owner="TBD", resources=[], flags=[](공백은 후속 gap-flagger가 채움)
  · meta.chosen_theme/departments/status 전사(목표 일부 누락·키 오전사를 LLM에 맡기지 않음)

source_goal을 'axis: direction_goal' 키로 발급하므로 fidelity-guard validate_action.py의
근거추적이 토큰 정확 매칭으로 강화된다(garbage-in이 garbage-gate를 통과하지 못함).

사용:  python3 build_milestones.py <goals.json> [departments_csv] [출력경로]
  departments_csv: 쉼표 구분 부서명(예: "예배,교육,전도,선교,양육,행정"). 생략 시 빈 배열.
종료코드: 0 = 성공, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import sys


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def build(goals, departments):
    meta_in = _d(goals.get("meta"))
    chosen_theme = meta_in.get("chosen_theme", "")

    from_goals = []
    actions = []
    seq = 0
    for ax in _l(goals.get("axes")):
        if not isinstance(ax, dict):
            continue
        axis = ax.get("axis", "")
        for g in _l(ax.get("goals")):
            if not isinstance(g, dict):
                continue
            direction_goal = g.get("direction_goal", "")
            indicators = [ind for ind in _l(g.get("indicators")) if isinstance(ind, dict)]
            from_goals.append({
                "axis": axis,
                "direction_goal": direction_goal,
                "indicators": [
                    {"label": ind.get("label", ""), "target": ind.get("target", ""), "by": ind.get("by", "")}
                    for ind in indicators
                ],
            })
            for ind in indicators:
                seq += 1
                actions.append({
                    "id": f"A{seq}",
                    "source_goal": f"{axis}: {direction_goal}",
                    "milestone": {
                        "label": ind.get("label", ""),
                        "by": ind.get("by", ""),
                        "from_indicator": ind.get("label", ""),
                        "target": ind.get("target", ""),
                    },
                    "department": "",      # department-router가 배치
                    "purpose": "",
                    "timing": "",          # gap-flagger가 시기미정 플래그
                    "owner": "TBD",        # gap-flagger가 담당미정 플래그
                    "resources": [],       # gap-flagger가 자원미정 플래그
                    "monthly_steps": [],
                    "flags": [],
                })

    out = {
        "meta": {
            "generated_by": "churchplan-action-planner",
            "schema_version": "1.0",
            "chosen_theme": chosen_theme,
            "departments": departments,
            "status": "제안",
        },
        "inputs_echo": {
            "chosen_theme": chosen_theme,
            "from_goals": from_goals,
        },
        "actions": actions,
        "department_table": {d: [] for d in departments},
        "gaps": [],
        "warnings": [],
        "confirmed": None,
    }
    return out


def main():
    if len(sys.argv) < 2:
        print("사용: python3 build_milestones.py <goals.json> [departments_csv] [출력경로]"); sys.exit(2)
    departments = []
    if len(sys.argv) > 2 and sys.argv[2].strip():
        departments = [d.strip() for d in sys.argv[2].split(",") if d.strip()]
    out_path = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            goals = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(goals, dict):
        print(f"[오류] 최상위 JSON이 객체(dict)가 아님: {type(goals).__name__}"); sys.exit(2)

    out = build(goals, departments)
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"마일스톤 골격 생성 ✓ → {out_path}  (from_goals {len(out['inputs_echo']['from_goals'])}건·actions {len(out['actions'])}건)")
    else:
        print(text)
    sys.exit(0)


if __name__ == "__main__":
    main()
