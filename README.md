# Asistente de viaje por Chile en Telegram · Grupo 3

Taller de implementación (Agentic AI, Curso 2). Un bot de Telegram recibe la pregunta, un
**coordinador** elige al agente especialista y le pregunta por **A2A**; la respuesta vuelve al
mismo chat con la etiqueta `[Nombre del agente]`.

> **Estado de este README (2026-11-21):** la parte **local** está completa y probada. Las secciones
> de Heroku para el coordinador y el bot (webhook) se completan en T12. El plan está en `plan.json`
> y el checklist de evaluación en `SPEC.md`.

## Opción elegida y qué resuelve

- **Opción 2 de la pauta: un canal de atención → Telegram.**
- **Problema:** preparar un viaje por Chile en un solo chat: qué llevar en la maleta, cómo seguir
  entrenando en el viaje y qué sitios visitar, cada tema respondido por su especialista.
- **Qué reutilizamos del taller A2A:** los tres agentes LangGraph de cada integrante, sus servidores
  A2A (`a2a-sdk`) y el coordinador supervisor con descubrimiento por Agent Card. Lo nuevo es el
  canal (Telegram), el control de acceso por agente, el manejo de agentes caídos, el blindaje del
  supervisor y el despliegue. La documentación del taller anterior está en
  `docs/README-taller-a2a.md`.

## Integrantes y aportes

| Integrante | Aportes |
|---|---|
| Daniella Fernández | Agente de Maleta (`src/agente_dani`); base del supervisor A2A y catálogo dinámico del taller anterior; documentos de entrega de `integracion-grupo3`. |
| Cristian Meza | Agente de Sitios turísticos (`src/agente_cristian`) y su despliegue en Heroku (T11). En su rama, pendientes de fusionar: saludo y memoria (T06), webhook (T09) y aviso a una persona (T10). |
| Patricio Vergara | Agente de Entrenamiento (`src/agente_pato`); clave por agente (T01, T02); catálogo con agentes caídos (T03); Procfile (T04); supervisor blindado (T05); `/chat` y bot de Telegram (T08); datos faltantes y comparación de su agente (T07); su agente en Heroku (T11); checklist de evaluación (T13). |

*(Actualizar esta tabla con lo que cada uno fusione antes de entregar.)*

## Cómo funciona

```
Telegram ──polling──▶ src/canal/telegram.py ──POST /chat──▶ Coordinador (8002)
                                                              │ elige agente (Gemini)
                                     ┌────────────────────────┼────────────────────────┐
                                     ▼  A2A + X-API-Key       ▼                        ▼
                              Maleta (8003)          Entrenamiento (8005)     Sitios turísticos (8004)
```

| Agente | Qué sabe | Dueño | Puerto local | Clave | Heroku |
|---|---|---|---|---|---|
| Agente de Maleta de Dani | Listas de equipaje para Punta Arenas, Pucón e Iquique según días y temporada | Daniella | 8003 | `CLAVE_DANI` | pendiente |
| Agente de Entrenamiento de Pato | Anatomía y rutinas de gimnasio con base científica | Patricio | 8005 | `CLAVE_PATO` | https://agente-pato-grupo3-8c9b06247efd.herokuapp.com |
| Agente de cristian (Sitios turísticos) | Sitios con ubicación, horarios y precios | Cristian | 8004 | `CLAVE_CRISTIAN` | https://agente-cristian-grupo3-60262a116c18.herokuapp.com |
| Coordinador | Elige el agente, no altera la respuesta y la etiqueta `[Nombre]` | Grupo | 8002 | `CLAVE_COORDINADOR` | pendiente (T12) |

Cada agente publica su ficha en `/.well-known/agent-card.json` y su estado en `/salud`.

## Versiones probadas

- Python **3.12.10** (`.python-version` fija 3.12).
- Paquetes principales (todas las versiones exactas en `requirements-lock.txt`): a2a-sdk 1.3.0, fastapi 0.163.1, uvicorn 0.54.0, httpx 0.28.1,
  langchain 1.5.0, langchain-core 1.8.1, langgraph 1.2.22, langchain-google-genai 4.5.0,
  pydantic 2.14.3, python-dotenv 1.2.4, pytest 9.2.0.

## Preparación manual (una vez)

1. **Gemini:** crea una API key en Google AI Studio. Va en `GOOGLE_API_KEY`.
2. **Bot de Telegram de prueba:** en Telegram habla con **@BotFather**, escribe `/newbot` y sigue los
   pasos. El token que entrega va en `TELEGRAM_TOKEN`. Cada persona usa **su propio bot de prueba**:
   un mismo bot no puede leer mensajes en dos computadores a la vez.
3. **Tu ID de Telegram:** escríbele a **@userinfobot**; el número que responde va en
   `TELEGRAM_USUARIOS_PERMITIDOS` (varios IDs separados por comas). Si un usuario no autorizado le
   escribe al bot, el bot le responde con su ID para que lo agreguen.
4. **Claves de acceso:** inventa una clave distinta para cada agente y para el coordinador, por
   ejemplo con `python -c "import secrets; print(secrets.token_urlsafe(24))"`.

## Para el evaluador

Hay dos formas de probar, según lo que prefieras:

1. **Con tus propias credenciales (recomendado para la entrega local):** sigue "Preparación manual",
   "Instalación" y "Configuración". Necesitas tu API key de Gemini y un bot de prueba creado con
   @BotFather; en `TELEGRAM_USUARIOS_PERMITIDOS` pones tu propio ID de Telegram. Las claves de los
   agentes y del coordinador las inventas tú: no hace falta pedirnos nada.
2. **Con acceso que te damos nosotros:** si prefieres usar nuestro bot o el despliegue en Heroku,
   escríbenos por una **vía privada** (correo o mensaje directo, nunca en el repositorio) con tu ID de
   Telegram. Lo agregamos a `TELEGRAM_USUARIOS_PERMITIDOS` y, si hace falta, te enviamos por la misma
   vía las claves de prueba. No hay secretos reales en este repositorio.

Si le escribes al bot sin estar autorizado, te responde "No tienes acceso a este bot. Tu ID es ...":
ese es el número que tienes que mandarnos.

## Instalación

```bash
git clone https://github.com/Daniferz/TallerCurso2Grupo3.git
cd TallerCurso2Grupo3
git checkout taller-sistema-agentes
python -m venv .venv
```

Activa el entorno:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Windows (cmd): `.venv\Scripts\activate.bat`
- Mac / Linux: `source .venv/bin/activate`

Luego instala las **versiones exactas que probamos**:

```bash
pip install -r requirements-lock.txt
```

`requirements.txt` tiene la lista base con rangos; `requirements-lock.txt` fija cada versión
(salida de `pip freeze` con Python 3.12.10) para que una instalación nueva quede igual a la nuestra.

## Configuración (`.env`)

Copia `.env.example` a `.env` y completa:

| Variable | Qué poner |
|---|---|
| `GOOGLE_API_KEY` | Tu API key de Gemini |
| `MODELO` | `gemini-3.5-flash-lite` (ya viene) |
| `CLAVE_PATO`, `CLAVE_DANI`, `CLAVE_CRISTIAN` | Una clave distinta por agente |
| `CLAVE_COORDINADOR` | La clave que exige el coordinador en `/chat` |
| `URLS_AGENTES` | `http://127.0.0.1:8003,http://127.0.0.1:8005,http://127.0.0.1:8004` |
| `CLAVES_AGENTES` | Las claves de esos agentes, **en el mismo orden**: `CLAVE_DANI,CLAVE_PATO,CLAVE_CRISTIAN` (sus valores) |
| `TELEGRAM_TOKEN` | El token de tu bot de prueba |
| `TELEGRAM_USUARIOS_PERMITIDOS` | Tu ID de Telegram |

Opcionales: `TIEMPO_ESPERA_A2A` (120 s), `TIEMPO_FICHA_A2A` (3 s; 30 en Heroku),
`REINTENTO_AGENTES_SEG` (60 s). `APP_MODULO` y `PORT` solo se usan en Heroku.

`.env` está en `.gitignore`: nunca se sube.

## Iniciar en local

Cada componente en su propia terminal, con el entorno activado y desde la raíz del proyecto:

```bash
python -m uvicorn src.agente_dani.server:app --port 8003
```

```bash
python -m uvicorn src.agente_pato.server:app --port 8005
```

```bash
python -m uvicorn src.agente_cristian.server:app --port 8004
```

```bash
python -m uvicorn src.coordinador.server:app --port 8002
```

El coordinador debe mostrar `Supervisor con 3 agentes`. Por último, el bot:

```bash
python -m src.canal.telegram
```

Debe mostrar `Bot @tu_bot escuchando por polling`. Ya puedes escribirle en Telegram.

## Probar

**En Telegram** (con todo levantado):

| Escribe | Qué debería pasar |
|---|---|
| `/start` | Bienvenida |
| `Qué llevo en la maleta para Pucón 3 días en invierno` | Responde `[Agente de Maleta de Dani] ...` |
| `Arma una rutina de pecho para fuerza, 5 días por semana` | Responde `[Agente de Entrenamiento de Pato] ...` con la rutina completa |
| `¿A qué hora puedo visitar el Cerro San Cristóbal el domingo?` | Responde `[Agente de cristian] ...` |
| Una foto o un sticker | "No puedo leer ese tipo de mensaje" |
| Desde una cuenta no autorizada | "No tienes acceso a este bot. Tu ID es ..." |

**Sin Telegram:**

```bash
python main.py pato "Arma una rutina de espalda para hipertrofia"
```

```bash
python main.py coordinador "Qué llevo en la maleta para Iquique 5 días en verano" --saltos
```

```bash
curl -X POST http://127.0.0.1:8002/chat -H "Content-Type: application/json" -H "X-API-Key: TU_CLAVE_COORDINADOR" -d "{\"texto\": \"Rutina de piernas\", \"conversacion_id\": \"prueba-1\"}"
```

`--saltos` muestra por qué nodos y herramientas pasó; `--diagrama` imprime el grafo en Mermaid.

**Scripts de prueba** (con los servidores levantados):

```bash
python scripts/probar_acceso.py pato
```

```bash
python scripts/probar_blindaje_supervisor.py
```

```bash
python scripts/comparar_directo_coordinador.py pato "Arma una rutina de pecho para fuerza, 5 días"
```

**Tests automáticos** (no necesitan servidores ni Gemini):

```bash
pytest
```

## Detener y evitar envíos accidentales

- Cada servidor y el bot se detienen con **Ctrl+C** en su terminal.
- Con el bot detenido no se lee ni se responde ningún mensaje de Telegram.
- El bot **solo atiende** a los IDs de `TELEGRAM_USUARIOS_PERMITIDOS`; a los demás les responde que
  no tienen acceso y no llama al coordinador ni a Gemini.
- Usa solo **bots y chats de prueba**. Para dejar de usar un bot por completo, revoca su token en
  @BotFather (`/revoke`).

## Control de acceso y secretos

| Dónde | Cómo se protege |
|---|---|
| Mensajes A2A a cada agente (`POST /`) | `X-API-Key`; **cada agente exige su propia clave** y rechaza la de los otros (401) |
| Coordinador → agentes | Envía a cada agente su clave según `URLS_AGENTES` / `CLAVES_AGENTES` |
| `POST /chat` del coordinador | `X-API-Key` = `CLAVE_COORDINADOR` |
| Bot de Telegram | Solo responde a `TELEGRAM_USUARIOS_PERMITIDOS` |
| Ficha y `/salud` | Públicas (la spec A2A pide fichas descubribles) |

Si un agente responde **503**, le falta su clave en `.env`; si responde **401**, la clave no
coincide. Las claves y tokens viven solo en `.env` o en las variables de Heroku: nunca en el repo,
en los logs ni en las capturas. El log del bot reemplaza el token por `<token>`.

## Qué pasa si algo falla

- **Un agente apagado:** el coordinador responde "La parte de [agente] no está disponible en este
  momento. Puedes seguir preguntando sobre los otros temas." y los otros siguen funcionando. Lo
  vuelve a intentar cada 60 s, sin reiniciar el coordinador.
- **Coordinador apagado:** el bot responde en el chat "No pude responder en este momento: el
  asistente no está disponible. Intenta de nuevo en unos minutos."
- **Pregunta fuera de tema:** "No tengo un agente para eso. Puedo ayudarte con: ..."
- **Falla de Gemini** (cuota, clave): error en una línea, nunca una respuesta inventada; `/chat`
  responde 502 y el bot avisa en el chat. Evidencia: `evidencias/taller-implementacion/local/falla-proveedor-gemini.md`.
- **Texto vacío en `/chat`:** 422 "El texto está vacío: escribe una pregunta."

## Qué es real y qué es simulado

- **Real:** Gemini, la comunicación A2A entre procesos, el control de acceso y los mensajes de
  Telegram.
- **Simulado (datos estáticos en cada `tools.py`):** las guías de equipaje, los músculos y rutinas y
  los sitios turísticos con sus horarios y precios.

## Dependencias externas y costos

- **Internet:** sí, aunque se ejecute en local (Gemini y Telegram).
- **Gemini:** cuota gratuita de Google AI Studio; si se acaba, los agentes responden un error claro (429).
- **Telegram:** gratis.
- **Heroku (solo para el +1):** plan Eco, unos 5 USD al mes por cuenta; las apps duermen tras 30 min
  sin uso y tardan 10-20 s en despertar.

## Límites conocidos

- La memoria de las conversaciones (`MemorySaver`) vive en RAM: se pierde al reiniciar.
- Los datos de cada agente son estáticos: solo cubren las ciudades y casos que tienen cargados.
- Un bot de Telegram no puede usarse por polling en dos computadores a la vez, ni por polling y
  webhook al mismo tiempo.
- El bot atiende los mensajes de a uno: una respuesta lenta retrasa la siguiente.

## Despliegue en Heroku (+1, en curso)

Una app por agente desde este mismo repo; el `Procfile` arranca el módulo de `APP_MODULO`:

```
web: uvicorn $APP_MODULO:app --host 0.0.0.0 --port $PORT
```

Variables de cada app de agente: `APP_MODULO` (ej.: `src.agente_pato.server`), `MODELO`,
`URL_PUBLICA` (la URL de la app, sin `/` final), `GOOGLE_API_KEY` y su clave (`CLAVE_PATO`,
`CLAVE_DANI` o `CLAVE_CRISTIAN`). Se despliega desde **Deploy → GitHub → Manual deploy** con la rama
`taller-sistema-agentes` (si el repo no es tuyo, conéctalo desde un fork y usa **Sync fork** antes de
cada despliegue).

*Pendiente (T12): app del coordinador con `URLS_AGENTES`, `CLAVES_AGENTES`, `CLAVE_COORDINADOR`,
`TIEMPO_FICHA_A2A=30` y el bot del grupo por webhook.*

## Evidencias

En `evidencias/taller-implementacion/local/` y `evidencias/taller-implementacion/heroku/`. Qué
evidencia cubre cada resultado de la pauta: `SPEC.md`, "Checklist de evaluación".

## Estructura

```
src/
  agente_dani/        Maleta (LangGraph)
  agente_pato/        Entrenamiento (LangGraph)
  agente_cristian/    Sitios turísticos (LangGraph)
  coordinador/        Supervisor, catálogo, cliente A2A, prompts y POST /chat
  canal/telegram.py   Bot de Telegram por polling
  comun/              Servidor A2A común, control de acceso, registro de agentes y errores
scripts/              Pruebas manuales (acceso, blindaje, comparación directo vs. coordinador)
tests/                pytest
main.py               python main.py {agente} "pregunta" [--saltos | --diagrama]
requirements.txt      Lista base de dependencias (rangos)
requirements-lock.txt Versiones exactas probadas
Procfile, .python-version   Heroku
```

Los agentes de ejemplo `agente_viajes` y `agente_restaurantes` quedan del taller anterior y no
participan en el coordinador.
