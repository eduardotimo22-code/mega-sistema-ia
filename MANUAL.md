# Manual de Uso — Mega Sistema IA

Sistema completo de agente de voz con inteligencia artificial.  
Atiende llamadas, agenda citas y llena tu CRM automaticamente para cualquier negocio.

**Creado por Santiago Munoz** — [Horizontes IA](https://iahorizontesacademy.com)

---

## Contenido

1. [Que es este sistema](#1-que-es-este-sistema)
2. [Arquitectura y servicios](#2-arquitectura-y-servicios)
3. [Requisitos previos](#3-requisitos-previos)
4. [Instalacion completa](#4-instalacion-completa)
5. [Configuracion del negocio](#5-configuracion-del-negocio)
6. [Comandos de Claude Code](#6-comandos-de-claude-code)
7. [Como funciona cada parte](#7-como-funciona-cada-parte)
8. [Industrias y templates](#8-industrias-y-templates)
9. [Panel de control (Dashboard)](#9-panel-de-control-dashboard)
10. [Personalizacion avanzada](#10-personalizacion-avanzada)
11. [Solucion de problemas](#11-solucion-de-problemas)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Costos estimados](#13-costos-estimados)

---

## 1. Que es este sistema

El Mega Sistema IA es una plantilla reutilizable que convierte cualquier negocio en uno con recepcionista virtual de inteligencia artificial disponible las 24 horas.

### Lo que hace el agente

- Contesta llamadas entrantes como una recepcionista profesional
- Responde preguntas sobre productos, servicios, precios y horarios
- Agenda citas y visitas directamente en el calendario
- Registra cada prospecto en el CRM con nombre, telefono y notas
- Llama automaticamente a leads que no han sido atendidos
- Analiza cada llamada y genera un resumen con puntuacion del lead
- Clasifica el nivel de interes: Frio, Tibio o Caliente

### Para quien es

- Agencias de bienes raices
- Clinicas dentales y de salud
- Despachos de abogados
- Gimnasios y centros deportivos
- Restaurantes con reservaciones
- Cualquier negocio que reciba llamadas y quiera automatizarlas

---

## 2. Arquitectura y servicios

```
Cliente llama
     │
     ▼
 TWILIO (numero de telefono)
     │  SIP trunk
     ▼
 RETELL AI (agente de voz con IA)
     │  habla con el cliente
     │  consulta productos y agenda citas en tiempo real
     ▼
 MODAL (backend serverless — Python / FastAPI)
     ├── /search-products  → busca en Notion CRM
     ├── /book-appointment → agenda en Cal.com
     ├── /create-lead      → guarda prospecto en Notion
     └── /update-lead-status → actualiza estatus del lead
     │
     ▼ (al terminar la llamada)
 CLAUDE SONNET (analisis post-llamada)
     │  resumen, puntuacion, siguiente accion
     ▼
 NOTION (CRM — leads, productos, historial de llamadas)
```

### Servicios utilizados

| Servicio | Funcion | Plan minimo |
|----------|---------|-------------|
| Retell AI | Motor del agente de voz | Free ($0) |
| Twilio | Numero de telefono + SIP | Trial ($15 credito) |
| Notion | CRM / base de datos | Free |
| Cal.com | Agenda de citas | Free |
| Anthropic | Analisis con Claude Sonnet | Pay-per-use |
| Modal | Hosting del backend | Free tier |

---

## 3. Requisitos previos

### Software en tu computadora

- **Python 3.11+** — [python.org](https://python.org)
- **Node.js 18+** — [nodejs.org](https://nodejs.org) (solo para el dashboard)
- **Git** — [git-scm.com](https://git-scm.com)
- **Claude Code** — instalar con: `npm install -g @anthropic-ai/claude-code`
- **Modal CLI** — instalar con: `pip install modal`

### Cuentas necesarias

Crea una cuenta gratuita en cada uno antes de empezar:

1. **Retell AI** → [retellai.com](https://retellai.com)
2. **Twilio** → [twilio.com](https://twilio.com)
3. **Notion** → [notion.so](https://notion.so)
4. **Cal.com** → [cal.com](https://cal.com)
5. **Anthropic** → [console.anthropic.com](https://console.anthropic.com)
6. **Modal** → [modal.com](https://modal.com)

---

## 4. Instalacion completa

### Paso 1 — Clona el repositorio

```bash
git clone https://github.com/santmun/mega-sistema-ia.git
cd mega-sistema-ia
```

### Paso 2 — Crea el evento en Cal.com (OBLIGATORIO antes del setup)

Entra a [app.cal.com](https://app.cal.com) → **Event Types** → **New Event Type**.

Ejemplos por industria:

| Industria | Nombre del evento | Duracion |
|-----------|------------------|----------|
| Inmobiliaria | Visita a propiedad | 45 min |
| Clinica dental | Consulta dental | 30 min |
| Abogados | Consulta inicial | 60 min |
| Gimnasio | Prueba gratis | 60 min |
| Restaurante | Reservacion | 120 min |

Cuando lo crees, abre el evento y copia el numero que aparece al final de la URL. Por ejemplo, si la URL es `cal.com/event-types/123456`, tu ID es `123456`. Lo necesitaras en el Paso 4.

### Paso 3 — Autenticate en Modal

```bash
modal token new
```

Se va a abrir el navegador. Inicia sesion o crea tu cuenta en Modal. Esto guarda tus credenciales localmente.

### Paso 4 — Crea las credenciales del sistema en Modal

Modal guarda los secretos de forma segura. Crea el secreto con todas las variables:

```bash
modal secret create mega-sistema-credentials \
  RETELL_API_KEY=tu_clave_aqui \
  TWILIO_ACCOUNT_SID=tu_sid_aqui \
  TWILIO_AUTH_TOKEN=tu_token_aqui \
  TWILIO_PHONE_NUMBER=+1XXXXXXXXXX \
  NOTION_API_KEY=secret_tu_clave_aqui \
  NOTION_PARENT_PAGE_ID=id_de_tu_pagina \
  CAL_API_KEY=tu_clave_cal_aqui \
  CAL_EVENT_TYPE_ID=123456 \
  ANTHROPIC_API_KEY=sk-ant-tu_clave_aqui
```

> Si no tienes alguna credencial todavia, ejecuta `/setup` desde Claude Code y te guia para obtener cada una.

### Paso 5 — Copia el archivo de entorno

```bash
cp .env.example .env
```

Llena el `.env` con las mismas credenciales del paso anterior. Este archivo es para correr el proyecto en local (scripts de setup y testing).

### Paso 6 — Abre el proyecto en Claude Code

```bash
claude
```

### Paso 7 — Ejecuta el setup

```
/setup
```

El asistente te va a guiar para:
- Configurar los datos del negocio en `sofia.config.yaml`
- Verificar las credenciales
- Crear las bases de datos en Notion
- Crear el agente en Retell AI
- Conectar el numero de Twilio
- Desplegar el backend en Modal

### Paso 8 — Verifica que todo funciona

```
/test
```

Si los 5 checks pasan, tu agente esta listo. Llama al numero de telefono para probarlo.

---

## 5. Configuracion del negocio

Toda la configuracion del negocio vive en `sofia.config.yaml`. Puedes editarlo directamente o usar `/setup` para que Claude lo genere por ti.

### Estructura del archivo

```yaml
business:
  name: "Nombre del Negocio"
  industry: "inmobiliaria"          # inmobiliaria | dental | abogados | gimnasio | restaurante
  timezone: "America/Mexico_City"   # Zona horaria del negocio
  address: "Calle, Ciudad"
  hours: "Lunes a Viernes 9am-6pm"
  website: "https://tunegocio.com"
  phone: "+52XXXXXXXXXX"

agent:
  name: "Sofia"                     # Nombre del agente virtual
  personality: "profesional y amable"
  language: "es-MX"

outbound:
  enabled: true
  schedule: "weekdays_9_to_6"       # Horario de llamadas salientes
  max_attempts: 3                   # Intentos maximos por lead
```

### Variables de entorno (`.env`)

```bash
# Retell AI
RETELL_API_KEY=              # API Key de Retell
RETELL_INBOUND_AGENT_ID=     # ID del agente inbound (lo crea /setup)
RETELL_OUTBOUND_AGENT_ID=    # ID del agente outbound (lo crea /setup)

# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Notion
NOTION_API_KEY=
NOTION_PARENT_PAGE_ID=
NOTION_LEADS_DB_ID=          # Lo crea /setup automaticamente
NOTION_PRODUCTS_DB_ID=       # Lo crea /setup automaticamente
NOTION_CALLS_DB_ID=          # Lo crea /setup automaticamente

# Cal.com
CAL_API_KEY=
CAL_EVENT_TYPE_ID=

# Anthropic
ANTHROPIC_API_KEY=
```

---

## 6. Comandos de Claude Code

Abre Claude Code en la carpeta del proyecto (`claude`) y usa estos comandos:

### `/setup` — Configuracion completa

Configura todo el sistema de principio a fin. Ideal para la primera vez o para un cliente nuevo.

```
/setup              ← Entrevista interactiva (recomendado para principiantes)
/setup --skip-interview  ← Lee directo del sofia.config.yaml y .env
```

**Que hace:**
1. Pregunta los datos del negocio uno por uno
2. Genera o actualiza `sofia.config.yaml`
3. Guia para obtener cada credencial con links directos
4. Crea las 3 bases de datos en Notion
5. Configura el agente en Retell AI
6. Conecta el numero de Twilio
7. Despliega el backend en Modal

---

### `/test` — Verificacion del sistema

Verifica que todos los servicios estan funcionando correctamente.

```
/test
```

**Checks que hace:**

```
[1/5] Retell AI       → Agente activo y configurado
[2/5] Twilio          → Numero conectado via SIP
[3/5] Notion CRM      → 3 bases de datos accesibles
[4/5] Cal.com         → Calendario con disponibilidad
[5/5] Modal Backend   → Endpoints respondiendo
```

Corre esto despues de `/setup` y cuando algo deje de funcionar.

---

### `/customize` — Modificaciones post-setup

Para hacer cambios sin tener que correr todo el setup de nuevo.

```
/customize
```

**Opciones:**
1. Prompt del agente (cambiar tono, agregar instrucciones)
2. Campos del CRM (agregar o quitar columnas en Notion)
3. Horario de llamadas salientes
4. Datos del negocio (nombre, direccion, horario)
5. Voz del agente

---

### `/status` — Estado de los servicios

Muestra el estado actual de todos los servicios en tiempo real.

```
/status
```

**Ejemplo de salida:**

```
Estado del sistema — Clinica Dental Sonrisa
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Retell AI        ✅ Online    Agente: Sofia (inbound + outbound)
Twilio           ✅ Online    Numero: +52 55 1234 5678
Notion CRM       ✅ Online    Leads: 47 | Llamadas: 123
Cal.com          ✅ Online    Citas esta semana: 8
Modal Backend    ✅ Online    Ultimo deploy: hace 2 dias

Ultima llamada: Juan Perez — Consulta dental — Caliente — hace 3 horas
```

---

## 7. Como funciona cada parte

### Llamadas entrantes (inbound)

1. El cliente llama al numero de Twilio
2. Twilio enruta la llamada via SIP trunk a Retell AI
3. Retell conecta al agente de voz (Sofia)
4. El agente:
   - Saluda al cliente con el nombre del negocio
   - Escucha su necesidad
   - Consulta productos/servicios en Notion (en tiempo real)
   - Agenda la cita en Cal.com si el cliente quiere
   - Guarda al cliente como lead en Notion
5. Al terminar la llamada, Claude analiza la transcripcion completa y genera:
   - Resumen ejecutivo
   - Puntuacion del lead (1-10)
   - Nivel de interes (Frio / Tibio / Caliente)
   - Siguiente accion recomendada

### Llamadas salientes (outbound)

El worker outbound corre automaticamente cada hora:

1. Consulta Notion por leads con estatus "Nuevo" o "Pendiente"
2. Filtra los que estan dentro del horario configurado
3. Llama a cada uno (maximo 3 intentos)
4. Si contestan, el agente hace el seguimiento
5. Actualiza el estatus en Notion

Para disparar manualmente:
```bash
curl -X POST https://tu-url-modal.modal.run/trigger-outbound
```

### Analisis post-llamada

Al terminar cada llamada, el sistema hace lo siguiente de forma automatica:

1. Descarga la transcripcion de Retell AI
2. Envia la transcripcion a Claude Sonnet con el contexto del negocio
3. Claude genera un JSON estructurado con:
   - Resumen (3-5 oraciones)
   - Puntuacion del lead (1-10)
   - Temperatura (Frio / Tibio / Caliente)
   - Productos/servicios mencionados
   - Objeciones del cliente
   - Siguiente accion recomendada
4. Guarda el analisis en la base de datos de Llamadas en Notion
5. Actualiza el estatus del lead

---

## 8. Industrias y templates

Cada industria tiene su template en `prompts/{industria}.yaml` con:
- Prompt del agente (personalidad, instrucciones, limites)
- Productos/servicios de ejemplo para cargar en Notion
- Campos del CRM especificos
- Etiquetas de acciones (visita, cita, consulta, reservacion)

### Inmobiliaria (`prompts/inmobiliaria.yaml`)

- **Accion principal**: Agendar visita a la propiedad
- **Productos en Notion**: Propiedades (Zona, Precio, Tipo, Recamaras, M2)
- **Filtros de busqueda**: Zona, tipo (Casa/Dpto), precio, recamaras

### Clinica Dental (`prompts/dental.yaml`)

- **Accion principal**: Agendar cita dental
- **Productos en Notion**: Tratamientos (Categoria, Precio, Duracion)
- **Filtros de busqueda**: Tipo de tratamiento, precio

### Despacho de Abogados (`prompts/abogados.yaml`)

- **Accion principal**: Agendar consulta inicial
- **Productos en Notion**: Servicios legales (Area, Descripcion, Honorarios)
- **Filtros de busqueda**: Area del derecho

### Gimnasio (`prompts/gimnasio.yaml`)

- **Accion principal**: Agendar prueba gratis / clase de muestra
- **Productos en Notion**: Membresias y clases (Tipo, Precio, Horario)
- **Filtros de busqueda**: Tipo de membresia, horario

### Restaurante (`prompts/restaurante.yaml`)

- **Accion principal**: Hacer reservacion
- **Productos en Notion**: Menu / eventos (Categoria, Precio, Disponibilidad)
- **Filtros de busqueda**: Tipo de evento, fecha

### Seminuevos (`prompts/seminuevos.yaml`)

- **Accion principal**: Agendar prueba de manejo
- **Productos en Notion**: Autos (Marca, Modelo, Año, Precio, Transmision, Color)
- **Filtros de busqueda**: Marca, modelo, año, precio, transmision, color

---

## 9. Panel de control (Dashboard)

El dashboard es una aplicacion web (Next.js) que muestra las metricas del sistema.

### Instalacion del dashboard

```bash
cd dashboard
npm install
cp .env.example .env.local
# Llena .env.local con tus credenciales de Notion y el URL del backend en Modal
npm run dev
```

Accede en: `http://localhost:3002`

> El dashboard siempre corre en el puerto 3002.

### Pantallas disponibles

- **Inicio** — Metricas generales (llamadas hoy, leads nuevos, citas agendadas)
- **Leads** — Lista de prospectos con estatus, temperatura y ultima interaccion
- **Llamadas** — Historial de llamadas con resumen y puntuacion de cada una
- **Configuracion** — Ver y editar parametros del sistema

---

## 10. Personalizacion avanzada

### Cambiar la voz del agente

El agente usa la voz configurada en Retell AI. Para cambiarla:

1. Entra a [retellai.com/dashboard](https://retellai.com/dashboard)
2. Ve a tu agente → Voice
3. Escoge entre las voces disponibles en espanol
4. Guarda — el cambio aplica en la siguiente llamada

O usa:
```
/customize → [5] Voz del agente
```

### Agregar nuevas industrias

1. Crea `prompts/mi-industria.yaml` basandote en un template existente
2. Agrega la industria a las opciones en `sofia.config.yaml`
3. Corre `/setup --skip-interview` para aplicar el nuevo template

### Modificar el prompt del agente

El prompt controla todo el comportamiento del agente. Para editarlo de forma segura:

```
/customize → [1] Prompt del agente
```

Claude te mostrara el prompt actual y te ayudara a modificarlo sin romper el formato requerido por Retell.

### Agregar campos al CRM

Para agregar un campo nuevo a la base de datos de Leads en Notion:

```
/customize → [2] Campos del CRM
```

O agrega manualmente desde Notion y el sistema lo reconocera en la siguiente llamada.

### Webhooks y endpoints disponibles

El backend expone estos endpoints en Modal:

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/health` | GET | Estado del sistema |
| `/retell-webhook` | POST | Eventos de Retell (llamadas) |
| `/twilio-voice` | POST | Llamadas entrantes de Twilio |
| `/twilio-webhook` | POST | Eventos de Twilio (SMS, status) |
| `/search-products` | POST | Buscar en el catalogo |
| `/create-lead` | POST | Crear nuevo prospecto |
| `/book-appointment` | POST | Agendar cita en Cal.com |
| `/update-lead-status` | POST | Actualizar estatus de lead |
| `/post-call-summary` | POST | Analisis manual de una llamada |
| `/trigger-outbound` | POST | Disparar ciclo outbound manualmente |

---

## 11. Solucion de problemas

### El agente no contesta las llamadas

1. Verifica que el numero de Twilio tiene el webhook correcto:
   - Twilio Console → Phone Numbers → tu numero → Voice & Fax
   - Webhook URL: `https://tu-url.modal.run/twilio-voice`
   - Metodo: HTTP POST
2. Verifica que el agente en Retell AI esta activo
3. Corre `/test` para diagnosticar

### El agente no puede agendar citas

**Error mas comun**: `CAL_EVENT_TYPE_ID` no esta configurado.

Solucion:
1. Ve a [app.cal.com](https://app.cal.com) → Event Types
2. Abre el evento y copia el ID del final de la URL
3. Agrega al `.env`: `CAL_EVENT_TYPE_ID=123456`
4. Actualiza el secreto en Modal: `modal secret create mega-sistema-credentials CAL_EVENT_TYPE_ID=123456`

### El agente no encuentra productos en Notion

1. Verifica que `NOTION_PRODUCTS_DB_ID` esta en el `.env`
2. Verifica que la integracion de Notion tiene acceso a la base de datos:
   - Notion → la base de datos → ··· → Connections → tu integracion
3. Verifica que los productos tienen datos cargados

### El backend no responde (Modal)

1. Verifica que el deploy esta activo:
   ```bash
   modal app list
   ```
2. Redespliega si es necesario:
   ```bash
   modal deploy app/main.py
   ```
3. Revisa los logs:
   ```bash
   modal app logs mega-sistema-ia
   ```

### No se genera el resumen post-llamada

1. Verifica `ANTHROPIC_API_KEY` en el secreto de Modal
2. Verifica que `NOTION_CALLS_DB_ID` este configurado
3. Revisa los logs del backend para ver el error especifico:
   ```bash
   modal app logs mega-sistema-ia
   ```

### Los slots de Cal.com aparecen en horario incorrecto

El sistema convierte automaticamente los horarios de UTC a la zona horaria del negocio. Verifica que `timezone` en `sofia.config.yaml` sea correcto.

Zonas horarias comunes en Latinoamerica:
- Mexico City: `America/Mexico_City`
- Cancun: `America/Cancun`
- Bogota: `America/Bogota`
- Lima: `America/Lima`
- Buenos Aires: `America/Argentina/Buenos_Aires`
- Santiago: `America/Santiago`

---

## 12. Preguntas frecuentes

**Cuanto cuesta operar el sistema?**

Con volumenes bajos (menos de 100 llamadas al mes), todos los servicios pueden funcionar en plan gratuito o con costos minimos. Ver seccion [Costos estimados](#13-costos-estimados).

**Puedo usarlo para una industria que no esta en la lista?**

Si. Usa cualquier template existente como base, copiales el archivo, renombra y modifica los prompts y campos del CRM con `/customize`. El sistema es completamente generico.

**Puedo tener varios agentes para diferentes clientes?**

Si. Clona el repositorio para cada cliente y usa su propio `sofia.config.yaml` y archivo `.env` con credenciales separadas. Cada cliente tiene su propia instancia independiente.

**Puedo cambiar el nombre del agente?**

Si. En `sofia.config.yaml` → `agent.name`. Corre `/customize → [4] Datos del negocio` para aplicar el cambio en Retell.

**El agente puede hablar en otros idiomas?**

Retell AI soporta multiples idiomas. Cambia `agent.language` en `sofia.config.yaml` y actualiza el prompt a ese idioma con `/customize`.

**Que pasa si Cal.com no tiene disponibilidad?**

El agente le informa al cliente honestamente que no hay slots disponibles y ofrece alternativas (dejar datos para que un asesor humano se comunique).

**Que pasa si algo falla durante una llamada?**

El sistema esta blindado: si Cal.com falla, el agente no confirma la cita al cliente sino que ofrece seguimiento humano. Si Notion falla, los datos de la llamada se guardan en los logs de Retell.

**Como evito que el agente diga cosas incorrectas?**

El prompt de cada industria incluye reglas explicitas de lo que el agente puede y no puede decir. Usa `/customize → [1] Prompt del agente` para agregar restricciones adicionales.

---

## 13. Costos estimados

### Plan gratuito (para pruebas)

| Servicio | Costo | Limite |
|----------|-------|--------|
| Retell AI | $0 | 10 min / mes |
| Twilio | $0 | $15 credito de prueba |
| Notion | $0 | Ilimitado |
| Cal.com | $0 | Ilimitado |
| Modal | $0 | 30 GB-seg / mes |
| Anthropic | ~$0.01 | Por llamada analizada |

### Operacion real (estimado para 100 llamadas/mes)

| Servicio | Costo mensual estimado |
|----------|----------------------|
| Retell AI | $10 - $20 USD |
| Twilio | $5 - $10 USD |
| Anthropic | $2 - $5 USD |
| Notion | $0 (plan free) |
| Cal.com | $0 (plan free) |
| Modal | $0 (dentro del free tier) |
| **Total** | **~$17 - $35 USD/mes** |

Los costos escalan linealmente con el volumen de llamadas. Para mas de 500 llamadas al mes considera los planes de pago de Retell AI.

---

## Soporte

- **Comunidad**: [Horizontes IA Academy](https://iahorizontesacademy.com)
- **YouTube**: Tutoriales en el canal de Horizontes IA
- **GitHub Issues**: Reporta bugs en el repositorio
- **Creado por**: Santiago Munoz (@santmun)
