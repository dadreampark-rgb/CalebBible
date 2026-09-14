#!/usr/bin/env python3
"""allocate_track.py — 연간 통독 트랙의 일별 권·장 배정(결정론).

정경 권·장 수(bible_validator.BOOK_CHAPTERS)로 트랙별 일별 배정을 *결정론* 생성한다.
권 경계를 존중하고(한 portion은 한 권 안의 연속 장), 장을 누락·중복 없이 모두 배정한다.
LLM 자연어 추론이 아니라 산술로 schedule[]을 만든다(권 경계 침범·장 오산 차단).

지원 트랙(references/scripture-track-catalog.md §1):
  1년 통독   — 창세기→요한계시록 1189장 / days(기본 365)
  신약 1년   — 마태복음→요한계시록 260장 / days(기본 365)
  시편잠언   — 시편 150편 + 잠언 31장 / days

사용:
  python3 allocate_track.py "1년 통독" [일수]            # JSON schedule[] 출력
  python3 allocate_track.py "신약 1년" 365
종료코드: 0 = 성공, 2 = 알 수 없는 트랙/인자 오류
"""
from __future__ import annotations
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bible_validator as bv  # noqa: E402

# 정경 권 순서(BOOK_CHAPTERS 삽입 순서 = 창세기…요한계시록). OT 39 + NT 27.
ALL_BOOKS = list(bv.BOOK_CHAPTERS.keys())
NT_BOOKS = ALL_BOOKS[39:]  # 마태복음부터
OT_BOOKS = ALL_BOOKS[:39]

# 트랙명 → (책 목록, 기본 일수). 동의어 허용.
TRACKS = {
    "1년 통독": (ALL_BOOKS, 365),
    "1년통독": (ALL_BOOKS, 365),
    "신약 1년": (NT_BOOKS, 365),
    "신약1년": (NT_BOOKS, 365),
    "시편잠언": (["시편", "잠언"], 181),
    "시편·잠언": (["시편", "잠언"], 181),
}


def _flatten_chapters(books):
    """[(책, 장번호), ...] 정경 순서대로."""
    seq = []
    for b in books:
        for ch in range(1, len(bv.BOOK_CHAPTERS[b]) + 1):
            seq.append((b, ch))
    return seq


def _portions_from_run(run):
    """연속 (책,장) run을 권 경계로 끊어 ['책 a-b', ...] 표기로."""
    portions = []
    i = 0
    while i < len(run):
        book, start = run[i]
        end = start
        j = i + 1
        while j < len(run) and run[j][0] == book and run[j][1] == end + 1:
            end = run[j][1]
            j += 1
        portions.append(f"{book} {start}" if start == end else f"{book} {start}-{end}")
        i = j
    return portions


def allocate_track(track: str, days: int | None = None):
    """트랙·일수 → schedule[] = [{'unit':'N일','portions':[...]}]. 결정론."""
    if track not in TRACKS:
        raise ValueError(f"알 수 없는 트랙: {track} (지원: {', '.join(sorted(set(TRACKS)))})")
    books, default_days = TRACKS[track]
    # days=None(미지정) → 기본값. days=0·음수(명시) → 오류(0 or default 누수 차단).
    n_days = default_days if days is None else days
    if n_days < 1:
        raise ValueError(f"일수는 1 이상: {n_days}")
    seq = _flatten_chapters(books)
    total = len(seq)
    n_days = min(n_days, total)  # 장수보다 많은 일수는 의미 없음
    schedule = []
    pos = 0
    for d in range(n_days):
        remaining_days = n_days - d
        take = (total - pos + remaining_days - 1) // remaining_days  # 남은 장 균등 올림 분배
        run = seq[pos:pos + take]
        pos += take
        schedule.append({"unit": f"{d + 1}일", "portions": _portions_from_run(run)})
    return schedule


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    track = sys.argv[1]
    try:
        days = int(sys.argv[2]) if len(sys.argv) > 2 else None
        sched = allocate_track(track, days)
    except ValueError as ex:
        print(f"[오류] {ex}")
        return 2
    print(json.dumps(sched, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
