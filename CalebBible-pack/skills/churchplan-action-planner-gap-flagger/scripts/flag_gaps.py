#!/usr/bin/env python3
"""
flag_gaps.py — churchplan-action-planner gap-flagger 결정론 공백 플래그.

각 action의 owner/resources/timing 빈 값을 결정론적으로 판정해
  · actions[].flags 에 담당미정/자원미정/시기미정 표시(중복 표시 안 함)
  · gaps[] 에 {action_id, type, text} 추가
  · 같은 owner가 OWNER_MAX(3) 이상이면 warnings 에 중복배정 경고
LLM 자연어 추론에 맡기지 않고 공백 판정·카운트를 파이썬이 확정한다
(fidelity-guard validate_action.py의 공백 정직 게이트와 정합).

사용:  python3 flag_gaps.py <action.json> [출력경로]   # 출력경로 없으면 표준출력
종료코드: 0 = 성공, 2 = 파일/JSON 오류
표준 라이브러리만 사용.
"""
import json
import sys
from collections import Counter


def _l(x):
    return x if isinstance(x, list) else []


OWNER_MAX = 3   # 같은 담당 반복 상한(중복배정·지친 리더)


def is_owner_blank(act):
    o = act.get("owner")
    return (not o) or (str(o).strip().upper() == "TBD")


def is_res_blank(act):
    r = _l(act.get("resources"))
    return len(r) == 0


def is_timing_blank(act):
    t = act.get("timing")
    return (not t) or (not str(t).strip())


def flag(a):
    actions = _l(a.get("actions"))
    gaps = []
    owner_ctr = Counter()

    for i, act in enumerate(actions):
        if not isinstance(act, dict):
            continue
        aid = act.get("id", i)
        flags = list(_l(act.get("flags")))  # 복사(비-리스트 방어)

        def ensure_flag(label, text):
            if not any(label in str(f) for f in flags):
                flags.append(label)
            gaps.append({"action_id": aid, "type": label, "text": text})

        if is_owner_blank(act):
            ensure_flag("담당미정", f"{aid} 담당자 미정 — 누가 맡을지 정해야 실행됨")
        else:
            owner_ctr[str(act.get("owner"))] += 1

        if is_res_blank(act):
            ensure_flag("자원미정", f"{aid} 필요 자원 불명확 — 무엇으로 할지 점검")

        if is_timing_blank(act):
            ensure_flag("시기미정", f"{aid} 시기 미정 — 언제 할지 점검")

        act["flags"] = flags

    a["gaps"] = gaps

    # 중복배정 경고(기계적 카운트만 — 여력 질적 판단은 resource-aligner #8)
    warns = _l(a.get("warnings"))
    warns = [w for w in warns if not (isinstance(w, dict) and w.get("type") == "중복배정")]
    for o, cnt in owner_ctr.items():
        if cnt >= OWNER_MAX:
            warns.append({
                "type": "중복배정",
                "text": f"'{o}'가 {cnt}개 action 담당 — 한 손에 몰림(지친 리더 점검)",
                "basis": "owner 반복",
            })
    a["warnings"] = warns
    return a


def main():
    if len(sys.argv) < 2:
        print("사용: python3 flag_gaps.py <action.json> [출력경로]"); sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            a = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 파일 없음: {sys.argv[1]}"); sys.exit(2)
    except json.JSONDecodeError as ex:
        print(f"[오류] JSON 파싱 실패: {ex}"); sys.exit(2)

    if not isinstance(a, dict):
        print(f"[오류] 최상위 JSON이 객체(dict)가 아님: {type(a).__name__}"); sys.exit(2)

    a = flag(a)
    out = json.dumps(a, ensure_ascii=False, indent=2)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"공백 플래그 완료 ✓ → {sys.argv[2]}  (gaps {len(a.get('gaps', []))}건)")
    else:
        print(out)
    sys.exit(0)


if __name__ == "__main__":
    main()
