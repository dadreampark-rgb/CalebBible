#!/usr/bin/env python3
"""
classify_health.py — churchplan-diagnostics-health-radar 결정론 환원기.

recall-dataset.json의 health_8areas를 읽어 diagnosis.json의 health_radar 블록을
*결정론적으로* 생성한다. 점수는 회상에서 그대로 전사(재계산 금지)하고, strong/needs_care
분류는 비교연산자로 확정한다 — SKILL.md의 '4↑=strong, 2↓=needs_care' 규칙을 LLM 자연어
추론이 아닌 순수 함수로 강제(오분류·누락 차단). LLM은 라벨 한글화만 담당.

사용: python3 classify_health.py <recall-dataset.json>
표준 출력으로 health_radar 블록(JSON) 출력. 종료코드 0=성공, 2=입력 오류.
표준 라이브러리만 사용.
"""
import json
import sys

AREAS_ORDER = ["예배", "말씀", "교제", "전도", "양육", "봉사", "선교", "재정"]


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def classify_health(health_8areas):
    """recall.health_8areas → diagnosis.health_radar 블록(결정론).
    - score/trend/basis/confidence 원본 그대로 복사(재계산 금지)
    - strong: score>=4 또는 trend=='↑'
    - needs_care: score<=2 또는 trend=='↓'
    - 미회상(score None) 영역은 분류에서 제외(보존만)."""
    if not isinstance(health_8areas, dict):
        health_8areas = {}
    areas, strong, needs_care = [], [], []
    # 회상에 있는 영역을 표준 순서 우선으로, 그 외는 입력 순서로
    keys = [a for a in AREAS_ORDER if a in health_8areas]
    keys += [a for a in health_8areas if a not in AREAS_ORDER]
    for area in keys:
        blk = health_8areas[area]
        if not isinstance(blk, dict):
            continue
        score = blk.get("score")
        trend = blk.get("trend")
        rec = {"area": area, "score": score, "trend": trend,
               "basis": blk.get("basis"), "confidence": blk.get("confidence")}
        if blk.get("assumption"):
            rec["assumption"] = True
        if score is None:
            rec["status"] = blk.get("status", "미회상")
        areas.append(rec)
        if score is None:
            continue
        if (is_number(score) and score >= 4) or trend == "↑":
            strong.append(area)
        if (is_number(score) and score <= 2) or trend == "↓":
            needs_care.append(area)
    return {"areas": areas, "strong": strong, "needs_care": needs_care}


def main():
    if len(sys.argv) < 2:
        print("사용: python3 classify_health.py <recall-dataset.json>")
        sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            recall = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}"); sys.exit(2)
    if not isinstance(recall, dict):
        print(f"[오류] recall 최상위가 JSON 객체가 아님 (받음: {type(recall).__name__})")
        sys.exit(2)
    block = classify_health(recall.get("health_8areas"))
    print(json.dumps({"health_radar": block}, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
