"""Actualiza las URLs de las herramientas de Retell con la URL real de Modal.

Uso: python scripts/update-retell-tools.py https://tu-workspace--mega-sistema-ia-api.modal.run
"""

import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def update_tools(modal_url: str):
    modal_url = modal_url.rstrip("/")
    api_key = os.environ["RETELL_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    tools = [
        {
            "type": "custom",
            "name": "buscar_vehiculos",
            "description": "Busca vehiculos disponibles en el inventario. Usa esta herramienta cuando el cliente pregunte que autos tienen disponibles, busque una marca especifica o quiera ver opciones.",
            "url": f"{modal_url}/search-products",
            "speak_during_execution": True,
            "speak_after_execution": True,
            "execution_message_description": "Revisando el inventario de vehiculos disponibles...",
            "parameters": {
                "type": "object",
                "properties": {
                    "Marca": {"type": "string", "description": "Marca del auto (Toyota, Honda, Nissan, etc.)"},
                    "Transmision": {"type": "string", "description": "Automatico o Manual"},
                    "Estado": {"type": "string", "description": "Disponible, Apartado, Vendido"},
                },
                "required": [],
            },
        },
        {
            "type": "custom",
            "name": "registrar_lead",
            "description": "Registra los datos del cliente interesado en el CRM. Usa esta herramienta cuando el cliente proporcione su nombre y telefono.",
            "url": f"{modal_url}/create-lead",
            "speak_during_execution": False,
            "speak_after_execution": False,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre completo del cliente"},
                    "phone": {"type": "string", "description": "Numero de telefono del cliente"},
                    "email": {"type": "string", "description": "Correo electronico del cliente"},
                    "Vehículo de interés": {"type": "string", "description": "El auto que le interesa al cliente"},
                    "Tipo de pago": {"type": "string", "description": "Contado, Credito, o Enganche y mensualidades"},
                },
                "required": ["name", "phone"],
            },
        },
        {
            "type": "custom",
            "name": "agendar_cita",
            "description": "Agenda una cita para que el cliente venga a ver el auto. Usa esta herramienta cuando el cliente quiera venir a la agencia.",
            "url": f"{modal_url}/book-appointment",
            "speak_during_execution": True,
            "speak_after_execution": True,
            "execution_message_description": "Verificando disponibilidad en el calendario...",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre del cliente"},
                    "phone": {"type": "string", "description": "Telefono del cliente"},
                    "email": {"type": "string", "description": "Correo del cliente"},
                    "preferred_date": {"type": "string", "description": "Fecha preferida en formato YYYY-MM-DD"},
                    "preferred_time": {"type": "string", "description": "Hora preferida en formato HH:MM (24h)"},
                },
                "required": ["name", "phone", "preferred_date"],
            },
        },
    ]

    inbound_agent_id = os.environ["RETELL_INBOUND_AGENT_ID"]
    outbound_agent_id = os.environ["RETELL_OUTBOUND_AGENT_ID"]

    for agent_id, label in [(inbound_agent_id, "inbound"), (outbound_agent_id, "outbound")]:
        r = requests.get(f"https://api.retellai.com/get-agent/{agent_id}", headers=headers)
        llm_id = r.json()["response_engine"]["llm_id"]
        r2 = requests.patch(
            f"https://api.retellai.com/update-retell-llm/{llm_id}",
            headers=headers,
            json={"tools": tools},
        )
        print(f"✅ {label} LLM tools actualizados -> {r2.status_code}")

    print(f"\n✅ Listo. El agente ahora usa: {modal_url}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/update-retell-tools.py <URL_MODAL>")
        print("Ejemplo: python scripts/update-retell-tools.py https://mi-workspace--mega-sistema-ia-api.modal.run")
        sys.exit(1)
    update_tools(sys.argv[1])
