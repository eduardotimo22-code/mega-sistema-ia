"""Servicio WhatsApp — mensajes automaticos via Twilio WhatsApp API."""

import os
from typing import Optional


def _client():
    from twilio.rest import Client
    return Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])


def send_message(to: str, body: str) -> Optional[str]:
    """Envia un mensaje de WhatsApp. Retorna el SID o None si falla.

    'to' debe ser el numero en formato E.164 (+521234567890).
    TWILIO_WHATSAPP_NUMBER debe tener el numero de WhatsApp aprobado o sandbox.
    Si la variable no esta configurada, el envio se omite silenciosamente.
    """
    wa_number = os.environ.get("TWILIO_WHATSAPP_NUMBER", "")
    if not wa_number:
        print("[WhatsApp] TWILIO_WHATSAPP_NUMBER no configurado — omitiendo envio")
        return None

    if not to:
        print("[WhatsApp] Numero de destino vacio — omitiendo envio")
        return None

    # Normalizar: quitar whatsapp: prefix si ya viene incluido
    from_wa = f"whatsapp:{wa_number}" if not wa_number.startswith("whatsapp:") else wa_number
    to_wa = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to

    try:
        msg = _client().messages.create(from_=from_wa, to=to_wa, body=body)
        print(f"[WhatsApp] Enviado a {to} — SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        print(f"[WhatsApp] Error enviando a {to}: {e}")
        return None


def send_post_call(phone: str, scenario: str, variables: dict) -> Optional[str]:
    """Envia el mensaje de WhatsApp post-llamada segun el escenario.

    scenario: "cita_confirmada" | "seguimiento" | "primer_contacto"
    variables: dict con valores para reemplazar en el template
    """
    from app.config import get_whatsapp_message

    template = get_whatsapp_message(scenario)
    if not template:
        print(f"[WhatsApp] No hay template para escenario '{scenario}' — omitiendo")
        return None

    body = _replace_vars(template, variables)
    return send_message(phone, body)


def _replace_vars(template: str, variables: dict) -> str:
    for key, value in variables.items():
        template = template.replace(f"{{{key}}}", str(value or ""))
    return template
