"""Servicio Cal.com — agenda de citas."""

import os

import requests

CAL_BASE_URL = "https://api.cal.com/v2"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['CAL_API_KEY']}",
        "Content-Type": "application/json",
        "cal-api-version": "2024-08-13",
    }


def get_available_slots(event_type_id: int, start_date: str, end_date: str) -> list:
    """Obtiene slots disponibles y los devuelve en hora local del negocio."""
    from app.config import BUSINESS
    from zoneinfo import ZoneInfo
    from datetime import datetime, timedelta, date as _date

    # Cal.com devuelve 0 slots cuando startTime == endTime; siempre usar end+1
    try:
        d = _date.fromisoformat(end_date[:10])
        end_date_exclusive = (d + timedelta(days=1)).isoformat()
    except Exception:
        end_date_exclusive = end_date

    resp = requests.get(
        f"{CAL_BASE_URL}/slots/available",
        headers=_headers(),
        params={
            "startTime": start_date,
            "endTime": end_date_exclusive,
            "eventTypeId": event_type_id,
        },
    )
    resp.raise_for_status()
    slots_by_date = resp.json().get("data", {}).get("slots", {})

    timezone = BUSINESS.get("timezone", "America/Cancun")
    tz = ZoneInfo(timezone)
    result = []
    for _date, times in sorted(slots_by_date.items()):
        for slot in times:
            utc_str = slot.get("time", "")
            try:
                dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
                dt_local = dt_utc.astimezone(tz)
                result.append(dt_local.strftime("%Y-%m-%dT%H:%M:%S"))
            except Exception:
                result.append(utc_str)
    return result


def create_booking(event_type_id: int, start: str, name: str, email: str) -> dict:
    """Crea una reserva en Cal.com usando la timezone del config."""
    from app.config import BUSINESS
    from zoneinfo import ZoneInfo
    from datetime import datetime

    timezone = BUSINESS.get("timezone", "America/Cancun")

    # Cal.com requiere el start en UTC. Convertimos desde la TZ local del negocio.
    try:
        tz = ZoneInfo(timezone)
        dt_naive = datetime.fromisoformat(start)
        if dt_naive.tzinfo is None:
            dt_local = dt_naive.replace(tzinfo=tz)
        else:
            dt_local = dt_naive
        dt_utc = dt_local.astimezone(ZoneInfo("UTC"))
        start_utc = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except Exception:
        start_utc = start  # fallback: mandar como viene

    resp = requests.post(
        f"{CAL_BASE_URL}/bookings",
        headers=_headers(),
        json={
            "eventTypeId": event_type_id,
            "start": start_utc,
            "attendee": {"name": name, "email": email, "timeZone": timezone},
        },
    )
    resp.raise_for_status()
    return resp.json().get("data", {})
