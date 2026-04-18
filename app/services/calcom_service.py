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


def _normalize_time(time_str: str) -> str:
    """Convierte formatos de hora variables a HH:MM.

    Acepta: '10:00', '10:00:00', '10am', '10 AM', '10:30am', '10:30 PM', '10'
    """
    import re
    t = time_str.strip().upper().replace(" ", "")
    # Extraer AM/PM si viene
    am_pm = None
    if t.endswith("AM"):
        am_pm = "AM"
        t = t[:-2]
    elif t.endswith("PM"):
        am_pm = "PM"
        t = t[:-2]

    # Separar horas y minutos
    parts = t.split(":")
    hour = int(parts[0]) if parts[0].isdigit() else 0
    minute = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

    if am_pm == "PM" and hour != 12:
        hour += 12
    elif am_pm == "AM" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"


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
    except Exception as parse_err:
        print(f"[Cal.com] Error parseando fecha '{start}': {parse_err} — mandando como viene")
        start_utc = start

    payload = {
        "eventTypeId": event_type_id,
        "start": start_utc,
        "attendee": {"name": name or "Cliente", "email": email, "timeZone": timezone},
    }
    print(f"[Cal.com] POST /bookings payload={payload}")

    resp = requests.post(
        f"{CAL_BASE_URL}/bookings",
        headers=_headers(),
        json=payload,
    )

    if not resp.ok:
        body = resp.text[:500]
        print(f"[Cal.com] Error {resp.status_code}: {body}")
        raise Exception(f"Cal.com {resp.status_code}: {body}")

    data = resp.json()
    print(f"[Cal.com] Reserva creada: {data.get('data', {}).get('uid', 'ok')}")
    return data.get("data", {})
