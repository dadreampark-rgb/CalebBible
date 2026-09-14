#!/usr/bin/env python3
"""signature-events 그룹 JSON 타입 계약 (SPEC) — 검증기·렌더러가 공유 (ADR-0002).

schema_guard.check_types(events_json, SIG_SCHEMA) 로 호출. "어느 필드가 dict/list/str인가"의
단일 진실. 의미 검사(절기·linked_weeks 범위·목적·근거·행사상한·확정 게이트)는 각 스크립트에 잔류.
사본은 sync_shared_assets.py 가 fidelity-guard·blueprint-renderer 폴더에 전파.
"""

SIG_SCHEMA = [
    ("meta", "dict"),
    ("inputs_echo", "dict"),
    ("signature_events", "list_of_dict"),
    ("signature_events[].title", "str"),
    ("signature_events[].serves_axes", "list"),
    ("signature_events[].serves_axes[]", "str"),
    ("signature_events[].serves_goals", "list"),
    ("signature_events[].serves_goals[]", "str"),
    ("signature_events[].blueprint", "dict"),
    ("signature_events[].blueprint.flow", "list"),
    ("signature_events[].blueprint.resources", "list"),
    ("signature_events[].blueprint.purpose", "str"),
    ("signature_events[].blueprint.timing", "str"),
    ("signature_events[].blueprint.success_signal", "str"),
    ("signature_events[].blueprint.audience", "str"),
    ("signature_events[].sermon_sync", "dict"),
    ("signature_events[].sermon_sync.linked_weeks", "list"),
    ("regular_events", "list_of_dict"),
    ("pruned_events", "list_of_dict"),
    ("warnings", "list_of_dict"),
]
