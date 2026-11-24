"""Monthly record selection and exact-coordinate means; no ArcGIS dependency."""

from collections import defaultdict
from datetime import date, datetime
import math


def month_bounds(year, month):
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10].replace('/', '-'))
        except ValueError:
            pass
    return None


def station_means(records, year=2014, month=6):
    """Return valid-record count and means keyed by exact x/y pairs.

    Each record is (sample_date, (x, y), dissolved_oxygen_mg_l).
    Depth is deliberately not a filter in this monthly coursework workflow.
    """
    start, end = month_bounds(year, month)
    grouped = defaultdict(list)
    accepted = 0
    for sampled, xy, value in records:
        sampled = as_date(sampled)
        if sampled is None or not start <= sampled < end:
            continue
        try:
            x, y = map(float, xy)
            value = float(value)
        except (TypeError, ValueError):
            continue
        if not all(math.isfinite(v) for v in (x, y, value)) or value < 0:
            continue
        grouped[(x, y)].append(value)
        accepted += 1
    means = {xy: (math.fsum(values) / len(values), len(values))
             for xy, values in grouped.items()}
    return accepted, means
