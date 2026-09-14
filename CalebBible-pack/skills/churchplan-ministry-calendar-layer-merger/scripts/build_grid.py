#!/usr/bin/env python3
"""
build_grid.py — churchplan-ministry-calendar 52주 격자 골격 결정론 생성.

year 입력 → 1~52 주차 각각의 date·quarter·month 를 순수 계산해 빈 격자 골격을 만든다.
layer-merger 는 이 골격 위에 상속 콘텐츠(observance·sermon·events·campaigns·milestones)만
전사한다 — 날짜·분기·월의 hallucination 을 원천 차단(determinism_candidate).

날짜 격자는 공유 자산 easter_calculator.compute_week_date_grid 로 계산(byte-identical 복사본).
분기 경계는 calendar-schema 고정: 1Q 1~13 · 2Q 14~26 · 3Q 27~39 · 4Q 40~52.

사용:  python3 build_grid.py <year>   → 52주 골격 JSON(weeks[]) 출력
표준 라이브러리 + easter_calculator 만 사용.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from easter_calculator import compute_week_date_grid

WEEKS_TOTAL = 52
# calendar-schema 고정 분기 경계
Q_RANGES = {1: range(1, 14), 2: range(14, 27), 3: range(27, 40), 4: range(40, 53)}


def quarter_of(week):
    for q, rng in Q_RANGES.items():
        if week in rng:
            return q
    return None


def build_grid(year):
    """year → [{week, date, quarter, month}] 52주 빈 골격(콘텐츠 없음)."""
    grid = compute_week_date_grid(year)  # {week: 'YYYY-MM-DD'}
    weeks = []
    for n in range(1, WEEKS_TOTAL + 1):
        date = grid.get(n, "")
        month = int(date.split("-")[1]) if date else None
        weeks.append({
            "week": n,
            "date": date,
            "quarter": quarter_of(n),
            "month": month,
            "observance": None,
            "sermon": {},
            "events": [],
            "campaigns": [],
            "milestones": [],
        })
    return weeks


def main():
    if len(sys.argv) != 2:
        print("사용: python3 build_grid.py <year>"); sys.exit(2)
    try:
        year = int(sys.argv[1])
    except ValueError:
        print(f"[오류] year 정수여야 함: {sys.argv[1]}"); sys.exit(2)
    # year 범위 가드 — dt.date 유효범위(1~9999) + Computus 관례(1583~9999) 밖이면 raw traceback 대신 EXIT 2.
    if not (1583 <= year <= 9999):
        print(f"[오류] year 범위 밖(1583~9999 필요): {year}"); sys.exit(2)
    try:
        weeks = build_grid(year)
    except (ValueError, OverflowError) as e:
        print(f"[오류] 격자 산출 실패(year={year}): {e}"); sys.exit(2)
    print(json.dumps({"weeks": weeks}, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
