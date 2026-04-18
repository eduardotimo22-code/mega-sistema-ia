"""Backend principal — Modal + FastAPI.

Todos los endpoints son genericos: leen del sofia.config.yaml
y el template de la industria para adaptarse a cualquier negocio.
"""

import modal
from fastapi import FastAPI, Request, Response

app = modal.App("mega-sistema-ia")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "retell-sdk>=5.0.0",
        "twilio>=9.0.0",
        "anthropic>=0.42.0",
        "notion-client>=2.2.0,<3.0.0",
        "requests>=2.32.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.0",
        "fastapi>=0.115.0",
    )
    .add_local_dir("app", remote_path="/root/app")
    .add_local_dir("prompts", remote_path="/root/prompts")
    .add_local_file("sofia.config.yaml", remote_path="/root/sofia.config.yaml")
)

sofia_secret = modal.Secret.from_name("mega-sistema-credentials")

web_app = FastAPI(title="Mega Sistema IA")


@web_app.get("/health")
def health():
    from app.config import BUSINESS, AGENT
    return {
        "status": "ok",
        "business": BUSINESS.get("name", ""),
        "agent": AGENT.get("name", "Sofia"),
        "industry": BUSINESS.get("industry", ""),
        "version": "1.0.0",
    }


@web_app.post("/retell-webhook")
def retell_webhook(request: dict):
    import os as _os, requests as _req
    event = request.get("event", "")
    call_obj = request.get("call", {})
    call_id = call_obj.get("call_id", "") if isinstance(call_obj, dict) else request.get("call_id", "")
    print(f"[retell-webhook] event={event} call_id={call_id}")

    if event == "call_ended" and call_id:
        from app.webhooks.retell_handler import process_post_call
        try:
            return process_post_call(call_id)
        except Exception as e:
            print(f"[retell-webhook] post-call error: {e}")
            return {"status": "error", "error": str(e)}

    return {"status": "ok", "event": event}


@web_app.post("/twilio-voice")
async def twilio_voice(request: Request):
    """Webhook de voz inbound de Twilio — registra en Retell y devuelve TwiML."""
    import os, requests as req_lib
    from urllib.parse import parse_qs
    body = await request.body()
    parsed = parse_qs(body.decode())
    from_number = (parsed.get("From") or parsed.get("from") or [""])[0]
    to_number = (parsed.get("To") or parsed.get("to") or [""])[0]
    agent_id = os.environ.get("RETELL_INBOUND_AGENT_ID", "")
    api_key = os.environ.get("RETELL_API_KEY", "")
    print(f"[twilio-voice] from={from_number} to={to_number} agent={agent_id[:20]}")
    try:
        r = req_lib.post(
            "https://api.retellai.com/v2/register-phone-call",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"agent_id": agent_id, "from_number": from_number, "to_number": to_number},
            timeout=10,
        )
        r.raise_for_status()
        call_id = r.json().get("call_id", "")
        print(f"[twilio-voice] call_id={call_id}")
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Dial timeout="60" record="do-not-record"><Sip>sip:{call_id}@sip.retellai.com;transport=tcp</Sip></Dial></Response>'
    except Exception as e:
        err = str(e)[:150]
        print(f"[twilio-voice] ERROR: {err}")
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Say language="es-MX">Error tecnico: {err}</Say></Response>'
    return Response(content=twiml, media_type="application/xml")


@web_app.post("/twilio-webhook")
def twilio_webhook(request: dict):
    from app.webhooks.twilio_handler import handle_twilio_event
    return handle_twilio_event(request)


@web_app.post("/search-products")
def search_products(request: dict):
    from app.services.notion_service import search_products as _search
    from app.config import CRM_PRODUCT_NAME

    # Retell envía args en snake_case — mapear a nombres reales de Notion
    FIELD_MAP = {
        "marca": "Marca", "transmision": "Transmisión", "transmisión": "Transmisión",
        "estado": "Estado", "año": "Año", "anio": "Año", "color": "Color",
        "modelo": "Modelo", "precio": "Precio",
    }
    TRANSMISION_MAP = {"automatico": "Automático", "manual": "Manual", "automatica": "Automático"}

    raw = request.get("args", request)
    if isinstance(raw, str):
        import json as _json
        raw = _json.loads(raw)
    raw.pop("query", None)

    query = {}
    for k, v in raw.items():
        notion_key = FIELD_MAP.get(k.lower(), k)
        if notion_key == "Transmisión":
            v = TRANSMISION_MAP.get(str(v).lower(), v)
        if v:
            query[notion_key] = v

    results = _search(query=query if query else None)
    return {"status": "ok", "count": len(results), CRM_PRODUCT_NAME.lower(): results}


@web_app.post("/create-lead")
def create_lead(request: dict):
    from app.services.notion_service import create_lead as _create

    args = request.get("args", request)

    # Separar campos base de campos extra
    base_keys = {"name", "phone", "email", "fuente", "notas"}
    base = {k: args[k] for k in base_keys if k in args}
    extra = {k: args[k] for k in args if k not in base_keys}

    lead = _create(**base, extra_fields=extra if extra else None)
    return {"status": "ok", "lead": lead}


@web_app.post("/book-appointment")
def book_appointment(request: dict):
    """Agenda una cita (generico: visita, consulta, prueba, reservacion).

    Usa CAL_EVENT_TYPE_ID del .env como default si el agente no especifica uno.
    Envuelto en try/except para que el agente NUNCA le mienta al cliente
    diciendo "ya quedo agendado" cuando la llamada a Cal.com fallo.
    """
    import os as _os
    from app.services.calcom_service import create_booking, get_available_slots
    from app.services.notion_service import find_lead_by_phone, update_lead

    args = request.get("args", request)
    phone = args.get("phone", "")
    name = args.get("name", "")
    email = args.get("email", "cliente@negocio.com")

    # Usa CAL_EVENT_TYPE_ID del env como default — el alumno lo configura en .env
    # para que el agente no necesite saber el ID hardcodeado.
    default_event_type = _os.environ.get("CAL_EVENT_TYPE_ID", "")
    event_type_id_raw = args.get("event_type_id") or default_event_type
    try:
        event_type_id = int(event_type_id_raw) if event_type_id_raw else 0
    except (TypeError, ValueError):
        event_type_id = 0

    if not event_type_id:
        return {
            "status": "error",
            "message": (
                "No hay un tipo de evento configurado en Cal.com. "
                "Dile al cliente que un asesor humano se va a comunicar para "
                "confirmar la cita."
            ),
            "error_detail": "CAL_EVENT_TYPE_ID no esta en .env",
        }

    preferred_date = args.get("preferred_date", "")
    preferred_time = args.get("preferred_time", "")

    if preferred_date and preferred_time:
        # Normalizar tiempo a HH:MM antes de armar el ISO string
        from app.services.calcom_service import _normalize_time
        try:
            preferred_time = _normalize_time(preferred_time)
        except Exception:
            pass  # si falla la normalizacion, usamos el valor tal cual
        start = f"{preferred_date}T{preferred_time}:00"
        print(f"[book_appointment] name={name!r} email={email!r} start={start} event_type={event_type_id}")

        try:
            booking = create_booking(
                event_type_id=event_type_id,
                start=start,
                name=name,
                email=email,
            )
        except Exception as e:
            detail = str(e)[:300]
            print(f"[book_appointment] FALLO Cal.com: {detail}")
            return {
                "status": "error",
                "message": (
                    "No se pudo agendar la cita en este momento. Dile al cliente "
                    "honestamente que hubo un problema tecnico y que un asesor "
                    "humano se va a comunicar para confirmar la cita."
                ),
                "error_detail": detail,
            }

        if phone:
            try:
                lead = find_lead_by_phone(phone)
                if lead:
                    from app.config import TEMPLATE
                    action_label = TEMPLATE.get("action_label", "Cita agendada")
                    update_lead(
                        page_id=lead["id"],
                        estatus="Cita agendada",
                        siguiente_accion=f"{action_label}: {preferred_date} {preferred_time}",
                    )
            except Exception as e:
                print(f"[book_appointment] Cita agendada pero no se pudo actualizar lead: {e}")

        return {"status": "ok", "booking": booking}

    if preferred_date:
        try:
            slots = get_available_slots(
                event_type_id=event_type_id,
                start_date=preferred_date,
                end_date=preferred_date,
            )
            return {"status": "ok", "available_slots": slots}
        except Exception as e:
            return {
                "status": "error",
                "message": (
                    "No se pudo consultar disponibilidad en este momento. "
                    "Dile al cliente que un asesor humano le llama en breve."
                ),
                "error_detail": str(e)[:300],
            }

    return {"status": "error", "message": "Se necesita al menos preferred_date"}


@web_app.post("/update-lead-status")
def update_lead_status(request: dict):
    from app.services.notion_service import find_lead_by_phone, update_lead

    args = request.get("args", request)
    phone = args.get("phone", "")
    page_id = args.get("lead_id", "")

    if not page_id and phone:
        lead = find_lead_by_phone(phone)
        if not lead:
            return {"status": "error", "message": f"No se encontro lead con telefono {phone}"}
        page_id = lead["id"]

    if not page_id:
        return {"status": "error", "message": "Se necesita phone o lead_id"}

    result = update_lead(
        page_id=page_id,
        estatus=args.get("estatus"),
        temperatura=args.get("temperatura"),
        siguiente_accion=args.get("siguiente_accion"),
    )
    return {"status": "ok", "result": result}


@web_app.post("/post-call-summary")
def post_call_summary(request: dict):
    from app.webhooks.retell_handler import process_post_call

    call_id = request.get("call_id", "")
    if not call_id:
        return {"status": "error", "message": "Se necesita call_id"}
    return process_post_call(call_id)


@web_app.post("/send-whatsapp")
def send_whatsapp(request: dict):
    """Envia un WhatsApp manual a un numero.

    Body: {"phone": "+521234567890", "scenario": "seguimiento", "variables": {...}}
    scenario: cita_confirmada | seguimiento | primer_contacto
    Si 'message' viene en el body, lo usa directamente ignorando el template.
    """
    from app.services import whatsapp_service

    phone = request.get("phone", "")
    message = request.get("message", "")
    scenario = request.get("scenario", "seguimiento")
    variables = request.get("variables", {})

    if not phone:
        return {"status": "error", "message": "Se necesita 'phone'"}

    if message:
        sid = whatsapp_service.send_message(phone, message)
    else:
        sid = whatsapp_service.send_post_call(phone=phone, scenario=scenario, variables=variables)

    if sid:
        return {"status": "ok", "sid": sid}
    return {"status": "error", "message": "No se pudo enviar. Revisa TWILIO_WHATSAPP_NUMBER en el secreto de Modal."}


@web_app.post("/trigger-outbound")
def trigger_outbound():
    """Trigger manual del worker outbound."""
    from app.outbound_worker import run_outbound_cycle
    return run_outbound_cycle()


@app.function(image=image, secrets=[sofia_secret], min_containers=1)
@modal.asgi_app()
def api():
    return web_app


# ── Worker outbound automatico ──

@app.function(
    image=image,
    secrets=[sofia_secret],
    schedule=modal.Cron("0 * * * *"),
    timeout=600,
)
def outbound_cron():
    """Cron: revisa leads pendientes y les llama cada hora."""
    from app.outbound_worker import run_outbound_cycle
    return run_outbound_cycle()
