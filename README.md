# Asistente de viaje por Chile en Telegram · Grupo 3

Taller de implementación (Agentic AI, Curso 2). Un bot de Telegram recibe la pregunta, un
**coordinador** elige al agente especialista y le pregunta por **A2A**; la respuesta vuelve al
mismo chat con la etiqueta `[Nombre del agente]`.

> **Estado de la entrega (2026-11-23):** funciona en local (entrega obligatoria) y en Heroku (+1):
> los tres agentes y el coordinador están desplegados y el bot del grupo usa webhook. Este README se
> probó desde un clon nuevo. El plan está en `plan.json`, el checklist de evaluación en `SPEC.md` y
> las evidencias en `evidencias/taller-implementacion/` (LOCAL y HEROKU por separado).

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
| Daniella Fernández | Agente de Maleta (`src/agente_dani`); base del supervisor A2A y catálogo dinámico del taller anterior; saludo y memoria del coordinador (T06); datos faltantes y comparación de Maleta (T07); documentos de entrega de `integracion-grupo3`; despliegue de Maleta (T11) y coordinador/bot del grupo en Heroku (T12). |
| Cristian Meza | Agente de Sitios turísticos (`src/agente_cristian`); datos faltantes y comparación directa/coordinador de Sitios (T07); despliegue en Heroku (T11); webhook de Telegram (T09) y aviso del extra (T10). |
| Patricio Vergara | Agente de Entrenamiento (`src/agente_pato`); clave por agente (T01, T02); catálogo con agentes caídos (T03); Procfile (T04); supervisor blindado (T05); `/chat` y bot de Telegram (T08); datos faltantes y comparación de su agente (T07); preguntas con varios temas en el coordinador (varios agentes, sin alterar cifras); su agente en Heroku (T11); checklist de evaluación (T13); README parte local, `requirements-lock.txt` y evidencia de falla del proveedor (T14, T15). |

*Cada integrante debe revisar su fila antes de entregar.*

## Cómo funciona

```
Telegram ──polling──▶ src/canal/telegram.py ──POST /chat──▶ Coordinador (8002)
                                                              │ elige agente (Gemini)
                                     ┌────────────────────────┼────────────────────────┐
                                     ▼  A2A + X-API-Key       ▼                        ▼
                              Maleta (8003)          Entrenamiento (8005)     Sitios turísticos (8004)
```

| Agente | Qué sabe | Dueño | Puerto local | Clave | Ficha Heroku y comprobación pública |
|---|---|---|---|---|---|
| Agente de Maleta de Dani | Listas de equipaje para Punta Arenas, Pucón e Iquique según días y temporada | Daniella | 8003 | `CLAVE_DANI` | [Ficha](https://agente-dani-grupo3-3494821f347d.herokuapp.com/.well-known/agent-card.json); `curl.exe -i https://agente-dani-grupo3-3494821f347d.herokuapp.com/salud` |
| Agente de Entrenamiento de Pato | Anatomía y rutinas de gimnasio con base científica | Patricio | 8005 | `CLAVE_PATO` | [Ficha](https://agente-pato-grupo3-8c9b06247efd.herokuapp.com/.well-known/agent-card.json); `curl.exe -i https://agente-pato-grupo3-8c9b06247efd.herokuapp.com/salud` |
| Agente de cristian (Sitios turísticos) | Sitios con ubicación, horarios y precios | Cristian | 8004 | `CLAVE_CRISTIAN` | [Ficha](https://agente-cristian-grupo3-60262a116c18.herokuapp.com/.well-known/agent-card.json); `curl.exe -i https://agente-cristian-grupo3-60262a116c18.herokuapp.com/salud` |
| Coordinador | Elige el agente, no altera la respuesta y la etiqueta `[Nombre]` | Grupo | 8002 | `CLAVE_COORDINADOR` | [Ficha](https://coordinador-grupo3-dani-2026-1dde01e29291.herokuapp.com/.well-known/agent-card.json); `curl.exe -i https://coordinador-grupo3-dani-2026-1dde01e29291.herokuapp.com/salud` |

Cada servicio publica su ficha en `/.well-known/agent-card.json` y su estado en `/salud`. El bot del
grupo es **@grupo3_asistente_bot**.

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

Los tests usan **modelos y agentes simulados** (dobles de prueba): verifican la lógica del código
(enrutamiento, control de acceso, mensajes de error, que la respuesta no altere cifras), pero **no**
demuestran que Gemini responda. Esa parte está en las evidencias, todas hechas con **Gemini real**
(`evidencias/taller-implementacion/README.md`). Cuando una prueba real falló y se repitió (por
ejemplo, la saturación de Gemini del 23-11), el índice muestra el primer intento y el definitivo por
separado.

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

## Probado, pendiente y simulado

- **Real:** Gemini, la comunicación A2A entre procesos, el control de acceso y los mensajes de
  Telegram.
- **Simulado (datos estáticos en cada `tools.py`):** las guías de equipaje, los músculos y rutinas y
  los sitios turísticos con sus horarios y precios.
- **Probado:** cada caso de la pauta, en LOCAL y en HEROKU, con fecha, solicitud, resultado esperado
  y obtenido en `evidencias/taller-implementacion/README.md`.
- **Pendiente:** los registros internos de Heroku del agente de Sitios; autorizar el ID de
  Telegram del evaluador en el bot de Heroku cuando lo envíe por vía privada; y volver a desplegar
  en Heroku el coordinador y los agentes de Maleta y Sitios para que tomen los últimos ajustes del
  2026-11-23 (rótulo del saludo y reglas de seguridad y datos referenciales en sus prompts). En local
  ya están aplicados y probados.

## Qué datos deben conservarse

Ninguno es obligatorio: los agentes no tienen base de datos. La memoria de cada conversación
(`MemorySaver`) y las tareas A2A viven en RAM y se pierden al reiniciar un proceso o cuando Heroku
reinicia la app (por ejemplo, al despertarla). Lo único que hay que guardar entre despliegues es la
**configuración**: las variables de `.env` en local, o las *Config Vars* de cada app en Heroku
(claves, `URLS_AGENTES`/`CLAVES_AGENTES`, token y secreto del bot). Los puertos, direcciones y
secretos se configuran por variables, sin tocar el código.

## Dependencias externas y costos

- **Internet:** sí, aunque se ejecute en local (Gemini y Telegram).
- **Gemini:** cuota gratuita de Google AI Studio; si se acaba, los agentes responden un error claro (429).
- **Telegram:** gratis.
- **Heroku (para el +1):** el coordinador del grupo está en un dyno Basic, con costo indicado por
  Heroku de aproximadamente US$0,01/h (máximo US$7/mes). Esta cuenta no tiene una suscripción Eco;
  consulta **Resources** y **Billing** para conocer el plan y costo de cada app de los integrantes.

## Límites conocidos

- La memoria de las conversaciones (`MemorySaver`) vive en RAM: se pierde al reiniciar.
- Los datos de cada agente son estáticos: solo cubren las ciudades y casos que tienen cargados.
- Un bot de Telegram no puede usarse por polling en dos computadores a la vez, ni por polling y
  webhook al mismo tiempo.
- El bot atiende los mensajes de a uno: una respuesta lenta retrasa la siguiente.

## Despliegue en Heroku (+1)

Hay una app por agente y una para el coordinador, todas desde este repo. El `Procfile` arranca el
módulo indicado por `APP_MODULO`:

```
web: uvicorn $APP_MODULO:app --host 0.0.0.0 --port $PORT
```

Variables de cada app de agente: `APP_MODULO` (ej.: `src.agente_pato.server`), `MODELO`,
`URL_PUBLICA` (la URL de la app, sin `/` final), `GOOGLE_API_KEY` y su clave (`CLAVE_PATO`,
`CLAVE_DANI` o `CLAVE_CRISTIAN`). Se despliega desde **Deploy → GitHub → Manual deploy** con la rama
`taller-sistema-agentes` (si el repo no es tuyo, conéctalo desde un fork y usa **Sync fork** antes de
cada despliegue).

La app del coordinador es `coordinador-grupo3-dani-2026`. Sus variables incluyen `APP_MODULO` (valor
`src.coordinador.server`), `GOOGLE_API_KEY`, `MODELO`, `CLAVE_COORDINADOR`, `URL_COORDINADOR`,
`URLS_AGENTES`, `CLAVES_AGENTES`, `TIEMPO_FICHA_A2A=30`, `TELEGRAM_TOKEN`,
`TELEGRAM_SECRETO_WEBHOOK`, `TELEGRAM_USUARIOS_PERMITIDOS` y `TELEGRAM_CHAT_AVISO`. En
`URLS_AGENTES` y `CLAVES_AGENTES`, el orden debe ser siempre Maleta (Dani), Entrenamiento (Pato) y
Sitios (Cristian). No copies valores secretos a este README.

El coordinador público es
`https://coordinador-grupo3-dani-2026-1dde01e29291.herokuapp.com`; el webhook de Telegram se registra
en su ruta `/telegram`:

```powershell
python scripts/registrar_webhook.py registrar https://coordinador-grupo3-dani-2026-1dde01e29291.herokuapp.com
python scripts/registrar_webhook.py info
```

El script lee `TELEGRAM_TOKEN` y `TELEGRAM_SECRETO_WEBHOOK` del `.env` local y no muestra sus valores.
No ejecutes `borrar` ni uses el bot del grupo por polling local salvo que quieras interrumpir
temporalmente su webhook de Heroku.

Para apagar una app, usa `heroku ps:scale web=0 --app <nombre-de-app>`; para volver a iniciarla,
`heroku ps:scale web=1 --app <nombre-de-app>`. Cada responsable puede apagar su propia app. El bot
local se detiene con Ctrl+C en su terminal. El proceso del coordinador está actualmente en Basic;
el cambio a Eco requiere una suscripción Eco en la cuenta.

## Evidencias

**Índice con el formato de la pauta (entorno y fecha, solicitud, esperado, obtenido y observaciones):
`evidencias/taller-implementacion/README.md`.** Las evidencias están separadas en `local/` y
`heroku/`; el checklist de evaluación está en `SPEC.md`.

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
