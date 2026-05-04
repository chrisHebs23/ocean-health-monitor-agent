import httpx
import time
from clients import model, supabase
from fastapi import HTTPException
from models import ReportCreate, ReportResponse, CoralWatchData
from constants import CORAL_STATIONS, ALERT_LEVELS


def store_supabase(data: ReportCreate) -> dict:
    response = supabase.table("reports").insert(data.model_dump()).execute()
    return response.data


def gemini_execution(data: CoralWatchData) -> ReportCreate:
    try:
        from constants import system_messages  # just the system prompt messages

        local_messages = system_messages.copy()
        json_data = data.model_dump_json()
        new_prompt = (
            "human",
            f"Generate an ocean health report for this data: {json_data}",
        )
        local_messages.append(new_prompt)

        response = model.invoke(local_messages)

        if response is None:
            raise ValueError("Gemini returned an empty response")

        return ReportCreate(**response)

    except KeyError as e:
        raise HTTPException(
            status_code=500, detail=f"Missing field in Gemini response: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500, detail=f"Invalid response from Gemini: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report for {data.location}: {str(e)}",
        )


def fetch_coral_watch(location: str, station_id: str) -> CoralWatchData:
    """
    Fetches current coral reef conditions from the Coral Watch API
    for a given station. Returns sea surface temperature, bleaching
    threshold, degree heating weeks and alert level.

    Args:
        location: Human readable location name e.g. "Florida"
        station_id: Coral Watch station slug e.g. "southeast_florida"
    """
    try:
        response = httpx.get(
            f"https://api.coral.tsr.lol/stations/{station_id}/current", timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        stress_level = current.get("stress_level", 0)

        return CoralWatchData(
            location=location,
            station_id=station_id,
            sst=current.get("sst_max"),
            bleaching_threshold=data.get("bleaching_threshold"),
            dhw=current.get("dhw"),
            alert_level=ALERT_LEVELS.get(stress_level, "Unknown"),
            date=current.get("date"),
        )

    except httpx.HTTPStatusError as e:
        raise Exception(f"Coral Watch API error for {location}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to fetch coral data for {location}: {str(e)}")


def fetch_all_data():
    for location in CORAL_STATIONS:
        try:
            response = fetch_coral_watch(location["name"], location["station"])
            model_response = gemini_execution(response)
            store_supabase(model_response)
            time.sleep(5)
        except Exception as e:
            print(f"Failed to process {location['name']}: {str(e)}")
            continue  # move to next location regardless
