# Documento de entrega · Taller A2A

**Grupo 3 · versión de trabajo colaborativa**  
Este documento contiene por ahora la información del Agente de Maleta de Daniella. Cristian y Patricio pueden completar sus blueprints, evidencias y ronda en las secciones reservadas. Este Markdown es la fuente editable; el PDF es una versión exportada de su estado actual.

## Integrantes

| Integrante | Agente / especialidad | Estado |
|---|---|---|
| Daniella Fernández | Agente de Maleta · listas de equipaje | Implementado; evidencias parciales |
| Cristian Meza | Pendiente de definir | Completar en esta versión del documento |
| Patricio Vergara | Pendiente de definir | Completar en esta versión del documento |

## Grupo

**Grupo:** 3  
**Entrega:** un ZIP grupal con el proyecto completo, este documento exportado a PDF, los blueprints individuales, `compañeros.md` y la carpeta `evidencias/`.

## Blueprints

### Daniella Fernández · Agente de Maleta

Archivo individual: `blueprint-DANI.md`.

| Qué definir | Mi agente |
|---|---|
| Quién soy | Dani · experta en maletas: decido qué llevar a un viaje según destino, días y temporada. |
| Hace | Prepara una lista de objetos para empacar por categorías y señala lo que se suele olvidar. |
| No hace | No busca ni compara vuelos u hoteles, no da precios, no informa el clima ni las políticas de equipaje de las aerolíneas. |
| Herramientas | `lista_equipaje(destino, dias, temporada)`: devuelve objetos por categoría y una sección “no te olvides”, usando guías estáticas en `tools.py`. |
| Decide solo | Selecciona categorías y cantidades orientativas según los días y la guía estática del destino y la temporada. |
| Nunca sin persona | No supone el clima, las reglas de una aerolínea ni requisitos migratorios cuando esos datos no fueron proporcionados. |
| Deriva a otro | Si preguntan por vuelos, hoteles, precios, clima o visas, indica en una frase que corresponde al agente de viajes y no responde esa parte. |
| Dónde se ejecuta | `http://127.0.0.1:8003` · `src/agente_dani/` · `python main.py dani "pregunta"`. |
| Dirección pública | `https://starting-pics-infrastructure-persian.trycloudflare.com` (URL temporal; puede cambiar). |

#### Prompt usado por Daniella (sin cambios)

```text
Quiero crear un agente nuevo que represente lo que yo sé hacer.especializado en preparar listas de equipaje. Mi nombre es Dani y mi especialidad es decidir qué llevar a un viaje según el destino, la cantidad de días y la temporada. Hazlo copiando el molde del agente de viajes, en src/agente_NOMBRE/ con los mismos cuatro archivos y siguiendo AGENTS.md: 

1) tools.py. Crea una herramienta con `@tool` llamada `lista_equipaje(destino, dias, temporada)`, con datos de referencia estáticos, creíbles y definidos dentro del archivo. Debe devolver una lista de objetos para empacar, agrupados por categorías como ropa, documentos, tecnología y botiquín, más una sección “no te olvides”. Si el destino o la combinación no está en los datos, dilo en una línea y no inventes información. No devuelvas vuelos, hoteles, precios, clima, requisitos de visa ni políticas de equipaje de aerolíneas.

2) prompts.py. Define un `SYSTEM_PROMPT` que diga: eres Dani, especialista en equipaje y preparación de maletas. Responde solo sobre qué llevar, en español y de forma breve, usando la herramienta antes de contestar y sin inventar datos. La temporada es un dato que proporciona la persona: no consultes ni supongas el clima real. Si preguntan por vuelos, hoteles, precios, clima, visas o políticas de equipaje de aerolíneas, dilo en una frase y no respondas esa parte; corresponde al agente de viajes. Si te preguntan quién eres, di tu nombre y tu especialidad.

3) graph.py. Igual que el molde del agente de viajes: `create_agent` con el modelo de Gemini configurado por el proyecto, mi herramienta, el `SYSTEM_PROMPT` y `MemorySaver`, con las funciones `responder`, `saltos` y `diagrama`. Conéctalo a `main.py` para que funcionen `python main.py dani "pregunta"`, `--saltos` y `--diagrama`.

4) server.py. Crea la ficha con `crear_tarjeta`: nombre “Agente de Maleta de Dani”, una descripción de dos frases (qué hago y qué no hago) y una skill por herramienta con una pregunta de ejemplo. Lee `URL_DANI` del `.env` y agrégala a `.env.example` apuntando a `http://127.0.0.1:8003`; arma `app = crear_app(tarjeta, responder)`. No incluyas claves ni secretos en `.env.example`.

No lo levantes tú. Dime cómo probarlo sin servidor y después el comando: `uvicorn src.agente_dani.server:app --port 8003 --reload`.
```

#### Ficha del agente

Descripción anterior al prompt 2: “Prepara listas de objetos para empacar según destino, cantidad de días y temporada. No busca vuelos ni hoteles, ni informa precios, clima, visas o políticas de equipaje de aerolíneas.”

Descripción final: “Prepara listas de equipaje con ropa, documentos, tecnología y botiquín para Punta Arenas, Pucón e Iquique, según los días y la temporada. No busca ni compara vuelos, hoteles o precios, ni informa clima, visas o políticas de equipaje de aerolíneas.”

Se concretó la descripción para que un supervisor pueda distinguir las listas de equipaje de las consultas de reservas y servicios de viaje. La ficha final descargada está en `evidencias/02-ficha.json`.

### Cristian Meza · blueprint pendiente

Completar aquí su blueprint y, si corresponde, agregar `blueprint-CRISTIAN.md` al ZIP.

| Qué definir | Completar |
|---|---|
| Quién soy | Pendiente |
| Hace / No hace | Pendiente |
| Herramientas y datos | Pendiente |
| Decide solo / Nunca sin persona | Pendiente |
| Deriva a otro | Pendiente |
| Dónde se ejecuta / Dirección pública | Pendiente |

### Patricio Vergara · blueprint pendiente

Completar aquí su blueprint y, si corresponde, agregar `blueprint-PATRICIO.md` al ZIP.

| Qué definir | Completar |
|---|---|
| Quién soy | Pendiente |
| Hace / No hace | Pendiente |
| Herramientas y datos | Pendiente |
| Decide solo / Nunca sin persona | Pendiente |
| Deriva a otro | Pendiente |
| Dónde se ejecuta / Dirección pública | Pendiente |

## Evidencias

La raíz de `evidencias/` conserva los nombres canónicos que muestra la pauta. Las copias individuales se organizan por integrante para que no se sobreescriban entre sí.

| Archivo | Estado / descripción |
|---|---|
| `01-saltos.png` | Referencia grupal actual de Daniella; copia individual en `evidencias/Daniella_Fernandez/01-saltos.png`. Las de Cristian y Patricio se añaden en sus subcarpetas. Es un render de salidas reales, no una captura literal de pantalla. |
| `01-saltos.txt` | Transcripción UTF-8 de las salidas CLI; copia en `evidencias/Daniella_Fernandez/01-saltos.txt`. |
| `02-ficha.json` | Agent Card pública de Daniella; copia individual en `evidencias/Daniella_Fernandez/02-ficha.json`. Cada integrante agrega su propia ficha en su subcarpeta. |
| `respuesta-a2a.json` | Respuesta `message/send` pública; copia individual en `evidencias/Daniella_Fernandez/respuesta-a2a.json`. El SDK devuelve `result.kind=message` y el texto en `result.parts[0].text`. |
| `03-tunel.png` | Verificación HTTPS generada de la ficha; copia individual en `evidencias/Daniella_Fernandez/03-tunel.png`. Falta la captura real de cloudflared y de la ficha vista desde otro dispositivo. |
| `04-catalogo.png` | Evidencia grupal pendiente: captura del coordinador con agentes que corren en otros computadores. |
| `05-ronda.png` | Evidencia grupal pendiente: captura/resumen de las tres preguntas por integrante; guardar además cada ronda en la subcarpeta de su autor. |

Subcarpetas individuales: `Daniella_Fernandez/`, `Cristian_Meza/` y `Patricio_Vergara/`. La raíz mantiene los nombres `01`–`05` pedidos por la pauta; los README de cada subcarpeta indican qué debe agregar cada integrante.

Para generar `compañeros.md`, copia `companeros.json.example` a `companeros.json`, completa autor y URL por cada agente ajeno y ejecuta `python scripts/generar_companeros.py`.

**Nota de codificación:** PowerShell mostró algunos acentos como `Ã…`; se verificó que la respuesta A2A guardada como JSON UTF-8 contiene los acentos correctos. El problema era de visualización de la consola.

## Ronda

La pauta pide tres preguntas por integrante: una de la propia skill, una de la skill de un compañero y una que ningún agente del catálogo pueda responder. La ronda debe ejecutarse desde el coordinador después de configurar las URLs de los compañeros.

### Daniella Fernández

| # | Pregunta | A quién debería ir | Resultado / pendiente |
|---|---|---|---|
| 1 | Voy cinco días a Punta Arenas en julio, ¿qué debería llevar? | Agente de Maleta de Dani; debe llamar `lista_equipaje`. | Probada directamente con `--saltos` y por A2A; falta documentar el enrutamiento desde el coordinador. |
| 2 | Pendiente: pregunta real para la skill de un compañero. | Agente del compañero, por su URL pública. | Pendiente hasta que Cristian o Patricio tenga agente y URL. |
| 3 | ¿Quién ganó el mundial de fútbol de 1962? | Ninguno; el supervisor debe responder que no hay agente adecuado. | Se observó que el agente Dani no llama a su herramienta; falta repetirlo dentro de la ronda del coordinador. |

**Observación de la prueba:** una respuesta a una pregunta sobre VPN rechazó el tema, pero dijo que correspondía al agente de viajes. La prueba de derivación incluida en `01-saltos.png` usa una pregunta de vuelos, que sí pertenece al agente de viajes.

### Cristian Meza

Completar sus tres preguntas: propia skill, skill de un compañero y tema fuera del catálogo. Registrar pregunta, agente elegido, motivo, resultado y observaciones.

### Patricio Vergara

Completar sus tres preguntas: propia skill, skill de un compañero y tema fuera del catálogo. Registrar pregunta, agente elegido, motivo, resultado y observaciones.

---

**Estado del documento:** borrador parcial para trabajo grupal; no representa aún la entrega final del ZIP. Antes de entregar, completar los blueprints restantes, `compañeros.md`, las capturas reales `03`, `04` y `05`, y validar el proyecto desde el ZIP limpio sin incluir `.env`, `.venv` ni claves.
