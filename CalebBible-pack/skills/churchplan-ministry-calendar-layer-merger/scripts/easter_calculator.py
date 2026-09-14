#!/usr/bin/env python3
"""부활절·절기 정확 계산 (Computus: Anonymous Gregorian Algorithm).

LLM 할루시네이션을 차단하기 위한 결정적(deterministic) 계산기.
sermon-planner-52week 스킬이 호출하여 모든 절기 주차를 산출한다.

Reference:
- Anonymous Gregorian computus, Meeus J. "Astronomical Algorithms" (1991)
- 한국 개신교 일반적 ISO 주차 셈법(첫 일요일을 1주차로)

Usage:
    python3 easter_calculator.py 2027
    python3 easter_calculator.py 2027 --json
"""
from __future__ import annotations
import datetime as dt
import json
import sys
from dataclasses import dataclass, asdict
from typing import Optional


def compute_easter_gregorian(year: int) -> dt.date:
    """그레고리력 부활주일 날짜 — Anonymous Gregorian Algorithm (Meeus/Jones/Butcher).

    1583 이후 모든 그레고리력 연도에 정확. 1700~2299 사이는 학계 검증값과 1:1 일치.
    """
    if year < 1583:
        raise ValueError(f"Gregorian Computus는 1583년 이상에만 유효. 입력: {year}")
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) // 451
    month = (h + L - 7 * m + 114) // 31
    day = ((h + L - 7 * m + 114) % 31) + 1
    return dt.date(year, month, day)


def first_sunday_of_year(year: int) -> dt.date:
    """그 해 1월 1일 이후 첫 일요일.

    한국교회는 '1월 1일이 일요일이면 1주차, 아니면 첫 일요일이 1주차'를 일반적으로 따른다.
    """
    jan1 = dt.date(year, 1, 1)
    days_until_sunday = (6 - jan1.weekday()) % 7
    return jan1 + dt.timedelta(days=days_until_sunday)


def sunday_to_week(target: dt.date, anchor_first_sunday: dt.date) -> int:
    """첫 일요일(1주차) 기준으로 임의 일요일이 몇 주차인지 산출."""
    if target.weekday() != 6:
        raise ValueError(f"{target}: 일요일이 아님 (weekday={target.weekday()})")
    delta = (target - anchor_first_sunday).days
    if delta < 0:
        raise ValueError(f"{target}: 첫 일요일({anchor_first_sunday})보다 앞섬")
    if delta % 7 != 0:
        raise ValueError(f"{target}: {anchor_first_sunday}와의 간격이 7의 배수가 아님")
    return delta // 7 + 1


@dataclass
class LiturgicalYear:
    year: int
    first_sunday: dt.date
    ash_wednesday: dt.date          # 재의 수요일(사순절 시작) = 부활주일 - 46일
    lent_first_sunday: dt.date      # 사순절 1주(재의 수요일 이후 첫 주일)
    palm_sunday: dt.date            # 종려주일 = 부활주일 - 7일
    good_friday: dt.date            # 성금요일 = 부활주일 - 2일
    easter_sunday: dt.date          # 부활주일
    ascension: dt.date              # 승천일 = 부활주일 + 39일
    pentecost: dt.date              # 성령강림주일 = 부활주일 + 49일
    trinity_sunday: dt.date         # 삼위일체주일 = 성령강림 + 7일
    # 한국교회 고정 절기
    new_year_sunday: dt.date        # 신년주일 = 그 해 첫 일요일
    children_sunday: dt.date        # 어린이 주일 = 5월 첫째 주일
    parents_sunday: dt.date         # 어버이 주일 = 5월 둘째 주일
    early_harvest: dt.date          # 맥추감사주일 = 7월 첫째 주일
    liberation_sunday: dt.date      # 광복절/통일주일 = 8월 셋째 주일
    memorial_sunday: dt.date        # 추도주일 = 11월 첫째 주일
    reformation_sunday: dt.date     # 종교개혁주일 = 10월 마지막 주일
    thanksgiving_sunday: dt.date    # 추수감사주일 = 11월 셋째 주일
    advent_1: dt.date               # 대강절 1주
    advent_2: dt.date
    advent_3: dt.date
    advent_4: dt.date
    christmas_day: dt.date          # 12월 25일
    christmas_sunday: dt.date       # 성탄주일(12월 25일 포함 주의 주일)
    new_year_eve_sunday: dt.date    # 송년/송구영신 주일 = 12월 마지막 주일

    def to_dict(self) -> dict:
        d = {}
        for k, v in asdict(self).items():
            d[k] = v.isoformat() if isinstance(v, dt.date) else v
        return d


def nth_sunday_of_month(year: int, month: int, n: int) -> dt.date:
    """그 해 그 달의 N번째 일요일."""
    first = dt.date(year, month, 1)
    offset = (6 - first.weekday()) % 7
    first_sun = first + dt.timedelta(days=offset)
    target = first_sun + dt.timedelta(days=7 * (n - 1))
    if target.month != month:
        raise ValueError(f"{year}년 {month}월에 {n}번째 일요일이 없음")
    return target


def last_sunday_of_month(year: int, month: int) -> dt.date:
    """그 해 그 달의 마지막 일요일."""
    # 다음 달 1일 - 1일부터 거꾸로
    if month == 12:
        next_first = dt.date(year + 1, 1, 1)
    else:
        next_first = dt.date(year, month + 1, 1)
    last = next_first - dt.timedelta(days=1)
    offset = (last.weekday() - 6) % 7
    return last - dt.timedelta(days=offset)


def nearest_sunday(d: dt.date) -> dt.date:
    """주어진 날짜와 가장 가까운 일요일 (같은 주 일요일 우선)."""
    if d.weekday() == 6:
        return d
    forward = (6 - d.weekday()) % 7
    backward = (d.weekday() + 1) % 7
    if forward <= backward:
        return d + dt.timedelta(days=forward)
    return d - dt.timedelta(days=backward)


def sunday_of_week_containing(d: dt.date) -> dt.date:
    """주어진 날짜를 포함하는 '주'(월요일~일요일)의 일요일.

    한국교회는 일반적으로 '12월 25일이 포함된 주의 일요일'을 성탄주일로 본다.
    여기서는 그 일요일 = (월요일 시작 주의 마지막 일요일)으로 정의한다.
    구체적으로 '그 날짜 이상 직후 첫 일요일'을 반환.
    """
    if d.weekday() == 6:
        return d
    return d + dt.timedelta(days=(6 - d.weekday()) % 7)


def first_sunday_after(d: dt.date) -> dt.date:
    """주어진 날짜 *이후* 첫 일요일(같은 날짜가 일요일이면 그 일요일 반환)."""
    if d.weekday() == 6:
        return d
    return d + dt.timedelta(days=(6 - d.weekday()) % 7)


def compute_liturgical_year(year: int) -> LiturgicalYear:
    easter = compute_easter_gregorian(year)
    ash_wed = easter - dt.timedelta(days=46)
    lent_1 = first_sunday_after(ash_wed + dt.timedelta(days=1))  # 재의 수요일 이후 첫 주일
    palm = easter - dt.timedelta(days=7)
    good_fri = easter - dt.timedelta(days=2)
    ascension = easter + dt.timedelta(days=39)
    pentecost = easter + dt.timedelta(days=49)
    trinity = pentecost + dt.timedelta(days=7)

    # 신년주일: 1월 첫째 주일
    new_year_sun = first_sunday_of_year(year)
    children = nth_sunday_of_month(year, 5, 1)
    parents = nth_sunday_of_month(year, 5, 2)
    early_harvest = nth_sunday_of_month(year, 7, 1)
    liberation = nth_sunday_of_month(year, 8, 3)
    memorial = nth_sunday_of_month(year, 11, 1)
    thanksgiving = nth_sunday_of_month(year, 11, 3)

    # 종교개혁: 10월 31일 또는 그 직전 주일 = 10월 마지막 주일
    reformation = last_sunday_of_month(year, 10)

    # 성탄주일: 12월 25일 직전 또는 당일 일요일 (12/25가 일요일이면 당일)
    christmas_day = dt.date(year, 12, 25)
    if christmas_day.weekday() == 6:
        christmas_sun = christmas_day
    else:
        christmas_sun = christmas_day - dt.timedelta(days=(christmas_day.weekday() + 1) % 7)

    # 대강절 1주: 서방교회 표준 — 11월 27일~12월 3일 사이의 일요일 (성 안드레의 날 11/30 가장 가까운 일요일)
    # 11월 27일부터 12월 3일까지 7일 중 유일한 일요일을 찾는다.
    advent_1 = None
    for d_off in range(7):
        cand = dt.date(year, 11, 27) + dt.timedelta(days=d_off)
        if cand.weekday() == 6:
            advent_1 = cand
            break
    if advent_1 is None:
        raise RuntimeError(f"{year}년 대강절 1주 산출 실패")
    advent_2 = advent_1 + dt.timedelta(days=7)
    advent_3 = advent_1 + dt.timedelta(days=14)
    advent_4 = advent_1 + dt.timedelta(days=21)
    # 대강절 4주와 성탄주일이 같은 일요일이면(드물게 발생), 한국교회 관행상
    # 성탄주일이 우선 적용되고 대강절 4주는 한 주 앞당겨 advent_3 위치로 통합되거나,
    # 대강절 4주 메시지를 성탄주일에 통합한다. 본 함수는 표준 계산값을 반환하고,
    # 충돌 처리는 호출자(SKILL.md 절기 우선순위 규약)가 담당.

    # 송구영신/송년: 12월 마지막 일요일
    new_year_eve = last_sunday_of_month(year, 12)

    return LiturgicalYear(
        year=year,
        first_sunday=new_year_sun,
        ash_wednesday=ash_wed,
        lent_first_sunday=lent_1,
        palm_sunday=palm,
        good_friday=good_fri,
        easter_sunday=easter,
        ascension=ascension,
        pentecost=pentecost,
        trinity_sunday=trinity,
        new_year_sunday=new_year_sun,
        children_sunday=children,
        parents_sunday=parents,
        early_harvest=early_harvest,
        liberation_sunday=liberation,
        memorial_sunday=memorial,
        reformation_sunday=reformation,
        thanksgiving_sunday=thanksgiving,
        advent_1=advent_1,
        advent_2=advent_2,
        advent_3=advent_3,
        advent_4=advent_4,
        christmas_day=christmas_day,
        christmas_sunday=christmas_sun,
        new_year_eve_sunday=new_year_eve,
    )


def week_of(target: dt.date, year: int) -> int:
    """그 해의 첫 주일 기준 N주차 산출."""
    first = first_sunday_of_year(year)
    return sunday_to_week(target, first)


def total_weeks_of_year(year: int) -> int:
    """그 해 총 주일 수(첫 주일~마지막 주일, 52 또는 53)."""
    first = first_sunday_of_year(year)
    last = first
    while (last + dt.timedelta(days=7)).year == year:
        last += dt.timedelta(days=7)
    return sunday_to_week(last, first)


def compute_week_date_grid(year: int) -> dict:
    """그 해 모든 주차(1..total_weeks)의 일요일 날짜 격자 — {week번호: 'YYYY-MM-DD'}.

    week-composer·liturgical-mapper가 weeks[].date를 머릿셈 없이 결정론으로 전사하고,
    fidelity-guard가 date를 이 격자로 대조하도록 한다(날짜 지어내기 차단).
    """
    first = first_sunday_of_year(year)
    total = total_weeks_of_year(year)
    return {w: (first + dt.timedelta(weeks=w - 1)).isoformat() for w in range(1, total + 1)}


def compute_all_week_numbers(year: int) -> dict:
    ly = compute_liturgical_year(year)
    first = ly.first_sunday
    result = {"year": year, "first_sunday": first.isoformat(), "weeks": {}}
    label_map = {
        "신년주일": ly.new_year_sunday,
        "사순절1주": ly.lent_first_sunday,
        "종려주일": ly.palm_sunday,
        "부활주일": ly.easter_sunday,
        "성령강림주일": ly.pentecost,
        "삼위일체주일": ly.trinity_sunday,
        "어린이주일": ly.children_sunday,
        "어버이주일": ly.parents_sunday,
        "맥추감사주일": ly.early_harvest,
        "광복절통일주일": ly.liberation_sunday,
        "추도주일": ly.memorial_sunday,
        "종교개혁주일": ly.reformation_sunday,
        "추수감사주일": ly.thanksgiving_sunday,
        "대강절1주": ly.advent_1,
        "대강절2주": ly.advent_2,
        "대강절3주": ly.advent_3,
        "대강절4주": ly.advent_4,
        "성탄주일": ly.christmas_sunday,
        "송구영신주일": ly.new_year_eve_sunday,
    }
    # 주차별 누적 — 절기 충돌 감지
    week_to_observances: dict = {}
    for name, day in label_map.items():
        try:
            wk = sunday_to_week(day, first)
        except ValueError as e:
            wk = f"ERROR: {e}"
        result["weeks"][name] = {"date": day.isoformat(), "week": wk}
        if isinstance(wk, int):
            week_to_observances.setdefault(wk, []).append(name)
    # 충돌(같은 주차에 둘 이상의 절기) 보고
    conflicts = {wk: obs for wk, obs in week_to_observances.items() if len(obs) > 1}
    result["conflicts"] = {str(wk): obs for wk, obs in conflicts.items()}
    # 비-일요일 절기는 별도 기록
    result["non_sunday_observances"] = {
        "재의수요일": ly.ash_wednesday.isoformat(),
        "성금요일": ly.good_friday.isoformat(),
        "승천일": ly.ascension.isoformat(),
        "성탄일": ly.christmas_day.isoformat(),
    }
    # 그 해 총 주일 수(첫 주일~마지막 주일)
    last_sunday = first
    while (last_sunday + dt.timedelta(days=7)).year == year:
        last_sunday += dt.timedelta(days=7)
    result["total_weeks"] = sunday_to_week(last_sunday, first)
    # 전체 주차→일요일 날짜 격자(weeks[].date 결정론 전사·검증용)
    result["week_dates"] = {str(w): d for w, d in compute_week_date_grid(year).items()}
    return result


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    try:
        year = int(sys.argv[1])
    except ValueError:
        print(f"잘못된 연도 입력: {sys.argv[1]}", file=sys.stderr)
        return 2
    if "--grid" in sys.argv:
        grid = compute_week_date_grid(year)
        print(json.dumps(grid, ensure_ascii=False, indent=2))
        return 0
    use_json = "--json" in sys.argv
    data = compute_all_week_numbers(year)
    if use_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"=== {year}년 한국교회 절기 캘린더 (자동 산출) ===")
        print(f"첫 일요일(1주차): {data['first_sunday']}")
        print()
        for name, info in data["weeks"].items():
            print(f"  {name:14}  {info['date']}  ({info['week']}주차)")
        print()
        print("--- 비-일요일 절기 ---")
        for name, day in data["non_sunday_observances"].items():
            print(f"  {name:10}  {day}")
        print()
        print(f"총 주일 수: {data['total_weeks']}주")
        if data["conflicts"]:
            print("⚠️ 절기 충돌(같은 주차):")
            for wk, names in data["conflicts"].items():
                print(f"  {wk}주차: {' + '.join(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
