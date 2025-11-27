"""Utility helpers for date range handling."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

_DATE_INPUT_FMT = "%Y%m%d"
_DATE_DISPLAY_FMT = "%Y-%m-%d"


def split_range(start_raw: str, end_raw: str, chunk_days: int = 7) -> List[Tuple[str, str]]:
    """Split [start_raw, end_raw] into segments of at most chunk_days."""
    start = datetime.strptime(start_raw, _DATE_INPUT_FMT)
    end = datetime.strptime(end_raw, _DATE_INPUT_FMT)

    if start > end:
        raise ValueError("start date must be <= end date")
    if chunk_days <= 0:
        raise ValueError("chunk size must be positive")

    ranges: List[Tuple[str, str]] = []
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        ranges.append((current.strftime(_DATE_DISPLAY_FMT), chunk_end.strftime(_DATE_DISPLAY_FMT)))
        current = chunk_end + timedelta(days=1)
    return ranges
