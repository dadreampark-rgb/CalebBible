#!/usr/bin/env python3
"""
collect_verify.py — churchplan-diagnostics-findings-synthesis 결정론 환원기.

diagnosis.json의 trend·funnel·health_radar·resolution_review를 순회하며
confidence=='하' 또는 assumption==true 또는 status=='미회상'인 항목을 *전부* 모아
findings.verify_after_workshop(귀가 후 확인 목록)를 결정론적으로 생성한다.
SKILL.md의 '모든 블록에서 신뢰 하/assumption/미회상을 모음' 규칙을 LLM 자연어 판단이 아닌
순수 필터로 강제(누락 차단). bottleneck_headline은 funnel.bottleneck_direction 직접 복사.

사용: python3 collect_verify.py <diagnosis.json>
표준 출력으로 {bottleneck_headline, verify_after_workshop}(JSON) 출력.
종료코드 0=성공, 2=입력 오류. 표준 라이브러리만 사용.
"""
import json
import sys


def _list(x):
    return x if isinstance(x, list) else []


def _dict(x):
    return x if isinstance(x, dict) else {}


def needs_verify(item):
    """신뢰 '하'·assumption true·미회상이면 확인 대상."""
    if not isinstance(item, dict):
        return False
    return (item.get("confidence") == "하"
            or item.get("assumption") is True
            or item.get("status") == "미회상")


def label_of(prefix, item, idx):
    name = item.get("label") or item.get("area") or item.get("name") or idx
    reason = []
    if item.get("confidence") == "하":
        reason.append("신뢰 하")
    if item.get("assumption") is True:
        reason.append("가정")
    if item.get("status") == "미회상":
        reason.append("미회상")
    tag = ("·".join(reason)) if reason else "확인"
    return f"{prefix}.{name} ({tag})"


def collect_verify(diag):
    out = []
    # trend.metrics
    for i, m in enumerate(_list(_dict(diag.get("trend")).get("metrics"))):
        if needs_verify(m):
            out.append(label_of("trend", m, i))
    # funnel.stages
    for i, st in enumerate(_list(_dict(diag.get("funnel")).get("stages"))):
        if needs_verify(st):
            out.append(label_of("funnel", st, i))
    # health_radar.areas
    for i, a in enumerate(_list(_dict(diag.get("health_radar")).get("areas"))):
        if needs_verify(a):
            out.append(label_of("health_radar", a, i))
    # resolution_review.items
    for i, it in enumerate(_list(_dict(diag.get("resolution_review")).get("items"))):
        if needs_verify(it):
            out.append(label_of("resolution_review", it, i))
    headline = _dict(diag.get("funnel")).get("bottleneck_direction", "")
    return {"bottleneck_headline": headline, "verify_after_workshop": out}


def main():
    if len(sys.argv) < 2:
        print("사용: python3 collect_verify.py <diagnosis.json>")
        sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            diag = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}"); sys.exit(2)
    if not isinstance(diag, dict):
        print(f"[오류] diagnosis 최상위가 JSON 객체가 아님 (받음: {type(diag).__name__})")
        sys.exit(2)
    print(json.dumps(collect_verify(diag), ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
