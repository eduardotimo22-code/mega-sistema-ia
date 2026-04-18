"""Configuracion central del sistema.

Carga sofia.config.yaml (datos del negocio) + el template de la industria
+ credenciales desde .env / variables de entorno.
"""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env for local dev
load_dotenv(PROJECT_ROOT / ".env")


def _load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


# --- Sofia config (datos del negocio) ---
_config = _load_yaml(PROJECT_ROOT / "sofia.config.yaml")

BUSINESS = _config.get("business", {})
AGENT = _config.get("agent", {})
OUTBOUND = _config.get("outbound", {})
BRANDING = _config.get("branding", {})

# --- Template de la industria ---
_industry = BUSINESS.get("industry", "")
TEMPLATE: dict = {}

if _industry:
    template_path = PROJECT_ROOT / f"prompts/{_industry}.yaml"
    if template_path.exists():
        TEMPLATE = _load_yaml(template_path)

# CRM fields: usa los del config si estan definidos, si no los del template
_config_crm = _config.get("crm", {})
CRM_PRODUCT_NAME = _config_crm.get("product_name") or TEMPLATE.get("product_label", "Productos")
CRM_PRODUCT_FIELDS = _config_crm.get("product_fields") or TEMPLATE.get("crm_fields", {}).get("product_fields", [])
CRM_LEAD_EXTRA_FIELDS = _config_crm.get("lead_extra_fields") or TEMPLATE.get("crm_fields", {}).get("lead_extra_fields", [])

# --- Reglas universales que se agregan a TODOS los prompts ---
# Estas reglas previenen bugs comunes en produccion:
# - Pronunciacion robotica ("MXN", "6.2 millones", "m2")
# - Listas eternas que cansan al cliente
# - Saludos artificiales ("hablo con Cliente?")
# - Validacion deficiente de datos

PRONUNCIATION_RULES = """

---
## Reglas de pronunciacion obligatorias
- Nunca digas "MXN" ni "USD". Di "pesos", "pesos mexicanos" o "dolares".
- Nunca uses formato decimal ni abreviado para precios:
  - MAL: "6.2 millones" -> BIEN: "seis millones doscientos mil pesos"
  - MAL: "850k" -> BIEN: "ochocientos cincuenta mil pesos"
  - MAL: "$1.5M" -> BIEN: "un millon quinientos mil pesos"
- Precios de renta, mensualidades o membresias: siempre agrega "al mes" al final.
- Medidas: di "metros cuadrados", no "m2" ni "m cuadrados".

## Conversacion natural
- NUNCA enlistes mas de 3 opciones seguidas. Si hay mas, menciona 2-3 y pregunta si quiere escuchar mas.
- NUNCA presentes mas de 2 alternativas (productos, servicios, propiedades, tratamientos) juntas.
- Usa muletillas naturales para sonar humano: "mire", "dejeme ver", "claro que si", "permitame".
- Si no conoces el nombre del cliente, NO digas literalmente "¿hablo con Cliente?".
  Pregunta naturalmente: "¿con quien tengo el gusto?" o "¿me podria dar su nombre?".

## Validacion de datos (muy importante)
- Telefonos mexicanos tienen 10 digitos. Si el cliente da menos digitos, repite cada digito y pide confirmacion.
- Emails: siempre confirma deletreando letra por letra antes de guardar.
- Fechas: confirma incluyendo el dia de la semana (ej: "lunes 15 de abril").
- Horas: siempre confirma AM o PM para evitar confusiones.
"""

OUTBOUND_DIRECTIVE = """TU ESTAS LLAMANDO AL CLIENTE (no al reves). En todo momento TU tomas la iniciativa y explicas por que le llamas. NUNCA digas "¿en que le puedo ayudar?" — esa frase es solo de llamadas entrantes (inbound).

"""


# --- Prompts (del template, con variables + reglas universales) ---
def get_inbound_prompt() -> str:
    raw = TEMPLATE.get("inbound_prompt", "")
    return _replace_variables(raw) + PRONUNCIATION_RULES

def get_outbound_prompt() -> str:
    raw = TEMPLATE.get("outbound_prompt", "")
    return OUTBOUND_DIRECTIVE + _replace_variables(raw) + PRONUNCIATION_RULES

def get_post_call_prompt() -> str:
    raw = TEMPLATE.get("post_call_analysis", "")
    return _replace_variables(raw)

def get_whatsapp_message(scenario: str) -> str:
    """Retorna el template de WhatsApp para el escenario dado."""
    msgs = TEMPLATE.get("whatsapp_messages", {})
    # Fallback a mensajes genericos si el template no los define
    defaults = {
        "cita_confirmada": (
            "Hola {nombre_cliente}, te confirmo tu cita en {business_name} "
            "para el {fecha} a las {hora}. "
            "Cualquier duda estamos a tus ordenes. — {agent_name}"
        ),
        "seguimiento": (
            "Hola {nombre_cliente}, te escribo de {business_name}. "
            "Fue un placer hablar contigo. "
            "Quedamos a tus ordenes para cuando quieras dar el siguiente paso. — {agent_name}"
        ),
        "primer_contacto": (
            "Hola, te escribo de {business_name}. "
            "Intentamos comunicarnos contigo. "
            "Escribenos cuando puedas y con gusto te atendemos. — {agent_name}"
        ),
    }
    return msgs.get(scenario) or defaults.get(scenario, "")

def _replace_variables(text: str) -> str:
    """Reemplaza {agent.name}, {business.name}, etc. con valores del config."""
    replacements = {
        "{agent.name}": AGENT.get("name", "Sofia"),
        "{agent.personality}": AGENT.get("personality", "amable, profesional"),
        "{business.name}": BUSINESS.get("name", ""),
        "{business.address}": BUSINESS.get("address", ""),
        "{business.hours}": BUSINESS.get("hours", ""),
        "{business.website}": BUSINESS.get("website", ""),
        "{business.phone}": BUSINESS.get("phone", ""),
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


# --- Credenciales (siempre de env, nunca del YAML) ---
RETELL_API_KEY = os.environ.get("RETELL_API_KEY", "")
RETELL_INBOUND_AGENT_ID = os.environ.get("RETELL_INBOUND_AGENT_ID", "")
RETELL_OUTBOUND_AGENT_ID = os.environ.get("RETELL_OUTBOUND_AGENT_ID", "")

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "")
NOTION_PRODUCTS_DB_ID = os.environ.get("NOTION_PRODUCTS_DB_ID", "")
NOTION_LEADS_DB_ID = os.environ.get("NOTION_LEADS_DB_ID", "")
NOTION_CALLS_DB_ID = os.environ.get("NOTION_CALLS_DB_ID", "")

CAL_API_KEY = os.environ.get("CAL_API_KEY", "")
CAL_EVENT_TYPE_ID = os.environ.get("CAL_EVENT_TYPE_ID", "")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER", "")
