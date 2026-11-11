# Agentes de viajes, restaurantes y coordinación A2A

## Integrantes · Grupo 3

- Daniella Fernández
- Cristian Meza
- Patricio Vergara

Proyecto con dos agentes de dominio, un coordinador y soporte para agentes A2A de compañeros.

- `agente_viajes`: responde consultas de viajes.
- `agente_restaurantes`: responde consultas de restaurantes.
- `coordinador`: elige un agente por tema entre viajes, restaurantes y URLs remotas configuradas.

El agente de viajes usa LangGraph, el de restaurantes usa CrewAI y el coordinador
usa LangGraph como supervisor.

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

`.env` está en `.gitignore`: la clave nunca se sube al repositorio.

## Estructura

```
.
├── main.py                    entrada por terminal para los tres agentes
├── AGENTS.md                  reglas del proyecto
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── comun/                 código compartido: registro.py, executor.py, servidor.py, tarjeta.py
│   ├── portal/                consola web: app.py, cliente.py, estatico/
│   ├── agente_viajes/         tools.py, prompts.py, graph.py (o crew.py), server.py
│   ├── agente_restaurantes/   tools.py, prompts.py, graph.py (o crew.py), server.py
│   └── coordinador/           cliente.py, graph.py, server.py
├── scripts/                   utilidades para probar los agentes desde la terminal
└── tests/
```

## Uso por terminal (sin servidor)

```bash
python main.py viajes "vuelo a Lima el 15 de marzo" --saltos
python main.py restaurantes "¿Dónde comer barato en Providencia?" --saltos
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
`URL_COORDINADOR`). `URL_PUBLICA` permite publicar la URL de un túnel en la Agent
Card y `URLS_AGENTES` agrega túneles de compañeros al catálogo del supervisor.
Los servidores base de viajes, restaurantes y coordinador conservan sus URLs
locales aunque `URL_PUBLICA` esté configurada; los agentes personales nuevos usan
el override por defecto.
Cada conversación conserva su `context_id`, que el agente usa
como memoria; el botón "Nueva conversación" genera uno nuevo. La espera máxima
por respuesta se ajusta con `TIEMPO_ESPERA_A2A` (120 segundos por defecto) y la
de la ficha con `TIEMPO_FICHA_A2A` (3 segundos por defecto).

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

## Probar entre computadores

1. Levanta el agente que quieras compartir en su puerto local. Por ejemplo,
   viajes escucha en el 8000 y los agentes personales suelen usar el 8003:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn src.agente_viajes.server:app --port 8000 --reload
   ```

2. En otra terminal, crea el túnel para ese puerto. En Mac/Linux:
   `bash scripts/tunel.sh 8000`; en Windows: `.\scripts\tunel.ps1 -Puerto 8000`.
   Si falta Cloudflare Tunnel, el script indica cómo instalarlo. Mantén esta
   terminal abierta.

3. Copia la URL HTTPS del túnel a `URL_PUBLICA` en `.env` y reinicia el servidor
   del agente para que su Agent Card publique esa URL. Verifícala con
   `curl.exe -sS https://TU-URL.trycloudflare.com/.well-known/agent-card.json`.

4. Pasa la URL a tus compañeros para que la agreguen a `URLS_AGENTES` en su
   `.env`; separen varias URLs con comas. Deben reiniciar el coordinador para
   que vuelva a leer las fichas al arrancar.

5. Prueben la selección con `python scripts/probar_supervisor.py`.

La URL temporal cambia al reiniciar el túnel. Ciérralo con Ctrl+C al terminar y
compártelo solo con personas de confianza: cualquiera con la URL puede enviar
consultas mientras el túnel esté activo.

## Pruebas

```bash
pytest
```
