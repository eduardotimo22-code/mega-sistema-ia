"""Handler de webhooks de Twilio."""

import os
import requests


def handle_inbound_voice(from_number: str, to_number: str) -> str:
    """Registra llamada entrante en Retell y devuelve TwiML para conectar via SIP."""
    agent_id = os.environ.get("RETELL_INBOUND_AGENT_ID", "")
    api_key = os.environ.get("RETELL_API_KEY", "")

    try:
        resp = requests.post(
            "https://api.retellai.com/v2/register-phone-call",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "agent_id": agent_id,
                "from_number": from_number,
                "to_number": to_number,
            },
            timeout=10,
        )
        resp.raise_for_status()
        call_id = resp.json().get("call_id", "")
        print(f"[Twilio] Llamada registrada en Retell: {call_id}")
    except Exception as e:
        err = str(e)[:200]
        print(f"[Twilio] Error registrando llamada en Retell: {err}")
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Say language="es-MX">Error: {err}</Say></Response>'

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial>
        <Sip>sip:{call_id}@sip.retellai.com;transport=tcp</Sip>
    </Dial>
</Response>"""
    return twiml


def handle_twilio_event(request: dict) -> dict:
    """Procesa eventos de Twilio: SMS entrantes, status de llamadas."""
    message_body = request.get("Body", "")
    from_number = request.get("From", "")
    event_type = request.get("EventType", request.get("MessageStatus", "sms_incoming"))

    if message_body:
        print(f"[Agent] SMS de {from_number}: {message_body}")
        return {"status": "ok", "type": "sms_received"}
    else:
        print(f"[Agent] Twilio status update: {event_type}")
        return {"status": "ok", "type": event_type}
