from clients import model, supabase
from models import ReportCreate, ReportResponse


def store_supabase(data: ReportCreate) -> None:
    supabase.table("reports").insert(data).execute()
