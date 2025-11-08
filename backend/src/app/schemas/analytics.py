from __future__ import annotations

from datetime import date, datetime
from typing import List

from pydantic import BaseModel


class SummaryStats(BaseModel):
    total_scans: int
    scans_today: int
    active_qr: int
    reuse_cycles: int


class DailyScan(BaseModel):
    day: date
    count: int


class AnalyticsSummaryResponse(BaseModel):
    summary: SummaryStats
    scans_by_day: List[DailyScan]


class QrTimelineEntry(BaseModel):
    ts: datetime
    event: str
    reuse_cycle: int
    meta: dict | None = None


class QrAnalyticsResponse(BaseModel):
    code_id: str
    product_name: str | None
    total_scans: int
    timeline: list[QrTimelineEntry]
