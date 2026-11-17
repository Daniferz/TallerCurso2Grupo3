# Agentes A2A de viajes, restaurantes y agentes personales

## Integrantes · Grupo 3

- Daniella Fernández
- Cristian Meza
- Patricio Vergara

Proyecto con dos agentes base, agentes personales de integrantes y un coordinador
supervisor que puede descubrir agentes remotos mediante sus Agent Cards.

- `agente_viajes`: vuelos y hoteles (LangGraph).
- `agente_restaurantes`: recomendaciones de restaurantes (CrewAI).
- `agente_pato`: anatomía muscular y rutinas de entrenamiento (LangGraph).
- `agente_dani`: listas de equipaje (LangGraph).
- `agente_cristian`: recomendaciones de sitios turísticos (LangGraph).
- `coordinador`: elige entre viajes, restaurantes y las URLs remotas configuradas.

## Versión instalada de a2a-sdk

```
Name: a2a-sdk
Version: 1.3.0
```

La necesitamos más adelante para levantar los servidores A2A de cada agente.
Se instala con el extra `[fastapi]`, porque el servidor HTTP de la librería
depende de `sse-starlette` y `starlette`.

## Activar el entorno virtual

Mac / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Windows (símbolo del sistema / cmd):

```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

El agente de restaurantes usa CrewAI, que choca con LangChain si se instalan
juntos. Por eso tiene su propio entorno:

```bash
python -m venv .venv-crew
source .venv-crew/bin/activate          # Mac / Linux
.venv-crew\Scripts\Activate.ps1         # Windows PowerShell
pip install -r requirements-crew.txt
```

Para salir del entorno: `deactivate`.

## Configuración

1. Copia `.env.example` a `.env`.
2. Pega tu clave de Gemini en `GOOGLE_API_KEY`.
3. Cambia `CLAVE_API` por una clave propia (ver "Control de acceso").

`.env` está en `.gitignore`: las claves nunca se suben al repositorio.

## Control de acceso (taller de implementación)

Todos los servidores A2A (viajes, restaurantes, Pato, coordinador y los agentes
personales) se crean con `crear_app` en `src/comun/servidor.py`, que exige el
encabezado `X-API-Key` con el valor de `CLAVE_API` del `.env`:

| Ruta | Acceso |
|---|---|
| `GET /salud` | Pública |
| `GET /.well-known/agent-card.json` | Pública (la spec A2A pide fichas descubribles) |
| `POST /` (mensajes A2A) y el resto | Requiere `X-API-Key` válida |

- Sin encabezado o con clave incorrecta: **HTTP 401** con un mensaje claro.
- Si el servidor no tiene `CLAVE_API` configurada: **HTTP 503**, no acepta nada.
- La consola web pide la clave en el campo **"Clave de acceso"** y su servidor la
  valida antes de reenviar el mensaje. La clave **no** está en el HTML ni en el JS.
- El coordinador y la consola agregan la clave del `.env` al llamar a los agentes.
- Cada intento queda en la terminal del servidor, sin mostrar la clave:
  `[acceso 2026-11-16 20:41:03] Agente de viajes POST / desde 127.0.0.1: RECHAZADO (Clave de acceso inválida.)`

Para conectar agentes entre computadores, todos deben usar la misma `CLAVE_API`
(compártanla por un canal privado, nunca en el repo ni en capturas).

Probar desde la terminal (con viajes levantado en el 8000):

```bash
# Rechazado: sin clave -> 401
curl -i -X POST http://127.0.0.1:8000/ -H "Content-Type: application/json" -d "{}"

# Permitido: con clave -> 200
python scripts/probar_acceso.py
```

```bash
pytest tests/test_acceso.py -v
```

## Estructura

```
.
├── main.py                    entrada por terminal para los agentes
├── AGENTS.md                  reglas del proyecto
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── comun/                 código compartido: registro.py, executor.py, servidor.py, tarjeta.py
│   ├── portal/                consola web: app.py, cliente.py, estatico/
│   ├── agente_viajes/         tools.py, prompts.py, graph.py, server.py
│   ├── agente_restaurantes/   tools.py, prompts.py, crew.py, server.py
│   ├── agente_pato/           tools.py, prompts.py, graph.py, server.py
│   ├── agente_dani/           tools.py, prompts.py, graph.py, server.py
│   ├── agente_cristian/       tools.py, prompts.py, graph.py, server.py
│   └── coordinador/           cliente.py, graph.py, server.py
├── scripts/                   utilidades para probar los agentes desde la terminal
└── tests/
```

## Uso por terminal (sin servidor)

```bash
python main.py viajes "vuelo a Lima el 15 de marzo" --saltos
python main.py restaurantes "¿Dónde comer barato en Providencia?" --saltos
python main.py pato "Quiero entrenar piernas, ¿qué rutina hago?" --saltos
python main.py dani "Voy cinco días a Punta Arenas en julio, ¿qué llevo?" --saltos
python main.py cristian "¿Qué sitios turísticos puedo visitar en Lima el sábado?" --saltos
python main.py coordinador "Arma un fin de semana gastronómico en Valparaíso" --diagrama
```

- Sin banderas: responde con `responder(texto, context_id)`.
- `--saltos`: muestra por qué nodos y herramientas pasó (`saltos(texto)`).
- `--diagrama`: imprime la estructura en Mermaid sin ejecutar el agente (`diagrama()`).

## Consola web

`src/portal` es una app FastAPI aparte que muestra el registro de agentes y les
envía mensajes por A2A. No llama a los modelos: solo reenvía el método
`message/send` al servidor de cada agente.

```bash
# 1. levanta el agente con el que quieras conversar (ejemplo: viajes)
uvicorn src.agente_viajes.server:app --port 8000

# 2. en otra terminal, levanta la consola
uvicorn src.portal.app:app --port 9000
```

Abre <http://127.0.0.1:9000>. La página lista cada agente del registro con su
estado:

- **En línea**: el agente existe y su `/salud` responde.
- **Sin conexión**: el agente está implementado, pero su servidor no está levantado.
- **Pendiente**: todavía no tiene `graph.py`/`crew.py` o `server.py`.

Al elegir un agente, la consola descarga su **Agent Card** desde
`/.well-known/agent-card.json` y muestra versión, protocolo, modos de entrada y
salida y sus skills. Clicar un skill deja su ejemplo de prueba en la caja de
texto, listo para mandarlo. Si la URL de la ficha no coincide con la del
registro aparece un aviso, y si el agente está en línea pero no publica ficha,
también.

Un agente nuevo no tiene que hacer nada extra: si su `server.py` usa
`crear_app(tarjeta, responder)`, la ficha se publica sola y la consola la lee.
Lo único obligatorio son los skills: `crear_tarjeta` falla con un error de una
línea si se le pasa la lista vacía, porque la spec A2A los exige.

Las direcciones salen de `.env` (`URL_VIAJES`, `URL_RESTAURANTES`,
`URL_COORDINADOR`, `URL_PATO`, `URL_DANI`, `URL_CRISTIAN`). `URL_PUBLICA` permite publicar la URL
de un túnel en la ficha; `URLS_AGENTES` agrega túneles de compañeros al catálogo
del supervisor. Los servidores base conservan sus URLs locales; los agentes
personales (`pato`, `dani` y `cristian`) usan el override por defecto. Cada conversación conserva su `context_id`, que el agente usa
como memoria; el botón "Nueva conversación" genera uno nuevo. La espera máxima
por respuesta se ajusta con `TIEMPO_ESPERA_A2A` (120 segundos por defecto) y la
de la ficha con `TIEMPO_FICHA_A2A` (3 segundos por defecto).

Los servidores base de viajes, restaurantes y coordinador excluyen `URL_PUBLICA`
para conservar sus propias direcciones; los agentes personales usan el override.

## Agente de viajes

LangGraph con Gemini y dos herramientas con datos inventados:

- `buscar_vuelos(origen, destino, fecha)`: rutas entre SCL, LIM, BOG y EZE, en ambos sentidos, dos vuelos por ruta.
- `buscar_hoteles(ciudad, noches)`: dos hoteles por ciudad con precio por noche y total de la estadía.

Acepta códigos IATA o nombres de ciudad (con o sin tilde). Si la ruta o la
ciudad no existe, devuelve una lista vacía. No reserva ni cobra.

```bash
python main.py viajes "vuelo a Lima" --saltos
python main.py viajes --diagrama
uvicorn src.agente_viajes.server:app --port 8000 --reload
```

El servidor acepta los dos dialectos de JSON-RPC: `SendMessage` (A2A 1.0, con el
encabezado `A2A-Version: 1.0`) y `message/send` (A2A 0.3, sin encabezado).

## Agente de restaurantes

CrewAI, en su propio entorno (`.venv-crew`) para no chocar con LangChain. Usa
datos inventados de Lima, Bogotá y Buenos Aires:

- `buscar_restaurantes(ciudad, tipo)`: 5 restaurantes por ciudad, con zona, tipo de comida, precio medio en CLP y horario.
- `detalle_restaurante(nombre)`: ficha completa de uno, con plato recomendado.

CrewAI no guarda memoria entre mensajes, así que el agente mantiene un historial
por `context_id` y lo inyecta en cada `Task`.

Este agente corre **solo con `.venv-crew` activo**, no con `.venv`. Si al
levantar el servidor aparece `ModuleNotFoundError: No module named 'crewai'`,
estás en el entorno equivocado: sal con `deactivate` y activa `.venv-crew`.

```powershell
.venv-crew\Scripts\Activate.ps1
python main.py restaurantes "parrillas en Buenos Aires" --saltos
python main.py restaurantes --diagrama
uvicorn src.agente_restaurantes.server:app --port 8001
```

## Agente de Entrenamiento de Pato

LangGraph con Gemini y herramientas con datos estáticos sobre anatomía muscular y
rutinas de entrenamiento basadas en referencias científicas. No ofrece dietas ni
suplementos, no trata lesiones o dolores, y deriva los temas fuera de su ficha.

- `musculo(nombre)`: origen, inserción, función y ejercicios para músculos del catálogo.
- `rutina(grupo_muscular, objetivo, nivel, dias_por_semana)`: ejercicios, series,
  repeticiones, descansos y referencias.

```powershell
python main.py pato "Quiero entrenar piernas, ¿qué rutina hago?" --saltos
python main.py pato --diagrama
uvicorn src.agente_pato.server:app --port 8005 --reload
```

## Agente de Maleta de Dani

LangGraph con Gemini y una herramienta local que arma listas desde guías estáticas
para Punta Arenas (invierno y verano), Pucón (invierno y verano) e Iquique
(verano). Acepta temporadas o meses del calendario chileno; no consulta ni afirma
conocer el clima real. Destinos y combinaciones no incluidos devuelven un mensaje
de una línea sin inventar una lista.

```powershell
python main.py dani "Voy cinco días a Punta Arenas en julio, ¿qué llevo?" --saltos
python main.py dani --diagrama
uvicorn src.agente_dani.server:app --port 8003 --reload
```

El Agente de Maleta se puede probar directamente en el puerto 8003 o desde la
consola web. Un coordinador remoto puede incluirlo mediante `URLS_AGENTES`.

## Agente de sitios turísticos de Cristian

LangGraph con Gemini y herramientas con información estática de ejemplo para
Santiago, Lima, Bogotá y Cusco. No consulta datos en tiempo real ni confirma
horarios o restricciones con los recintos.

- `listado_sitios_turisticos(ciudad, fecha)`: entrega sitios, descripción,
  ubicación, horario, precio referencial e imagen.
- `horario_atencion(nombre_sitio, dia)`: devuelve el horario registrado o indica
  en una línea cuando no hay dato para el día.

```powershell
python main.py cristian "¿Qué sitios turísticos puedo visitar en Lima el sábado?" --saltos
python main.py cristian --diagrama
uvicorn src.agente_cristian.server:app --port 8004 --reload
```

El servidor publica `URL_PUBLICA` en la Agent Card cuando se configura un túnel;
`URL_CRISTIAN` conserva la dirección local del servidor.

## Coordinador

El supervisor de LangGraph descubre al arrancar las fichas de viajes,
restaurantes y las URLs incluidas en `URLS_AGENTES`. Con cada pregunta elige una
usando las descripciones de las fichas como datos; si ninguna aplica, responde
que no hay un agente para ese tema. Las respuestas delegadas incluyen el nombre
del agente entre corchetes y el motivo de selección.

- `catalogo.py`: obtiene una vez las fichas y clientes A2A de viajes, restaurantes
  y URLs de compañeros; si uno no responde, informa en una línea y sigue con los demás.
- `graph.py`: `START → supervisor → agente_remoto | sin_agente → END`, con
  `MemorySaver`, `responder`, `saltos` y `diagrama`.
- `server.py`: al iniciar imprime `Supervisor con N agentes`.

```bash
python main.py coordinador "¿Cuánto cuesta volar de Santiago a Lima?" --saltos
python main.py coordinador --diagrama
uvicorn src.coordinador.server:app --port 8002
```

Levanta primero viajes en el 8000 y restaurantes en el 8001; luego inicia el
coordinador en el 8002 para que descubra las fichas y los agentes remotos.

`scripts/probar_coordinador.py` le hace dos preguntas con el mismo
`context_id` y comprueba que la segunda respuesta recuerda la primera:

```bash
python scripts/probar_coordinador.py
```

Para revisar las seis decisiones del supervisor:

```bash
python scripts/probar_supervisor.py
```

## Generar `compañeros.md`

La Agent Card no incluye el nombre de quien creó el agente, así que `companeros.json` relaciona cada autor con su URL pública. Parte de la plantilla:

```powershell
Copy-Item companeros.json.example companeros.json
# Completa autor y URL por cada compañero y luego ejecuta:
.\.venv\Scripts\python.exe scripts\generar_companeros.py
```

El script descarga cada ficha A2A con timeout y genera `compañeros.md` con autor, nombre, skills, URL y JSON completo. Si una ficha no responde, registra el error en una línea y continúa con las demás.

## Probar entre computadores

1. Levanta el agente personal que quieres compartir: Dani usa el puerto 8003, Cristian el 8004 y Pato el 8005.
2. En otra terminal, abre el túnel de Cloudflare al mismo puerto. En Mac/Linux ejecuta `bash scripts/tunel.sh PUERTO`; en Windows usa `.\scripts/tunel.ps1 -Puerto PUERTO`. Mantén la terminal abierta.
3. Copia la URL HTTPS a `URL_PUBLICA` del `.env` del dueño y reinicia ese agente. Comprueba su ficha con `curl.exe -sS https://TU-URL.trycloudflare.com/.well-known/agent-card.json`.
4. Agrega las URLs públicas a `URLS_AGENTES` en el `.env` del coordinador, separadas por comas. Incluye el agente propio para que participe en la ronda y reinicia el coordinador.
5. Prueba el enrutamiento con `python scripts/probar_supervisor.py`.

Las tarjetas de viajes, restaurantes y coordinador conservan sus URLs locales; `URL_PUBLICA` se usa por defecto en los agentes personales. Las URLs rápidas cambian al reiniciar el túnel. Ciérralo con Ctrl+C y comparte la URL solo con personas de confianza: cualquiera que la conozca podrá consultar el agente mientras esté activo.

## Pruebas

```bash
pytest
```
