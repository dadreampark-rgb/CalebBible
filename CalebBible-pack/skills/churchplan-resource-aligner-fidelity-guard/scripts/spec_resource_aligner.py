#!/usr/bin/env python3
"""resource-aligner 그룹 JSON 타입 계약 (SPEC) — 검증기·렌더러가 공유 (ADR-0002).

schema_guard.check_types(resource_json, RESOURCE_SCHEMA) 로 호출. "어느 필드가 dict/list/스칼라인가"의
단일 진실. 의미 검사(절대금액 MONEY_RE·더하기전빼기·목자소진·상속위조)는 각 스크립트에 잔류.
사본은 sync_shared_assets.py 가 fidelity-guard·aligner-renderer 폴더에 전파.
"""

RESOURCE_SCHEMA = [
    ("meta", "dict"),
    ("inputs_echo", "dict"),
    ("budget_plan", "dict"),
    ("org_plan", "dict"),
    ("pastor_time", "dict"),
    ("demand_gaps", "list_of_dict"),
    ("warnings", "list_of_dict"),
    ("budget_plan.realloc_by_strategy", "list_of_dict"),
    ("budget_plan.current_by_function", "dict"),
    ("org_plan.leader_gaps", "list_of_dict"),
    ("org_plan.develop_needed", "list_of_dict"),
    ("org_plan.placements", "list_of_dict"),
    ("pastor_time.blocks", "list_of_dict"),
    ("inputs_echo.from_action.gaps", "list_of_dict"),
    ("demand_gaps[].need", "dict"),
    ("subtractions[]", "scalar"),
]
