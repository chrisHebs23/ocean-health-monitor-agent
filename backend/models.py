from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


# ── Incoming data from Coral Watch API ──────────────────────
class CoralWatchData(BaseModel):
    location: str
    station_id: str
    sst: Optional[float] = None
    bleaching_threshold: Optional[float] = None
    dhw: Optional[float] = None
    alert_level: Optional[str] = None
    date: Optional[str] = None


# ── What gets stored in Supabase ────────────────────────────
class ReportCreate(BaseModel):
    location: str
    report: str
    alert_level: Optional[str] = None
    sea_surface_temp: Optional[float] = None
    source: str


# ── What gets returned from Supabase ────────────────────────
class ReportResponse(BaseModel):
    id: int
    location: str
    report: str
    alert_level: Optional[str] = None
    sea_surface_temp: Optional[float] = None
    source: str
    created_at: datetime
