# Documento de entrega · Taller A2A

**Grupo 3 · integración de Pato y Dani**
Esta versión integra los agentes personales de Patricio y Daniella, sus blueprints y las evidencias de las rondas disponibles. Cristian se incorporará en una etapa posterior. Este Markdown es la fuente editable; `documento-entrega.pdf` debe mantenerse sincronizado con esta versión.

## Integrantes

| Integrante | Agente / especialidad | Estado |
|---|---|---|
| Daniella Fernández | Agente de Maleta · listas de equipaje | Integrado; blueprint y evidencias individuales disponibles |
| Patricio Vergara | Agente de Entrenamiento · anatomía y rutinas | Integrado; blueprint, ronda y evidencias disponibles |
| Cristian Meza | Agente de lugares turísticos | Pendiente para la siguiente integración; hay una ficha externa documentada en `evidencias/Daniella_Fernandez/compañeros.md` |

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
| Dirección pública | `https://absent-offerings-realized-envelope.trycloudflare.com` (URL temporal registrada en `blueprint-DANI.md`; puede cambiar). |

La Agent Card guardada en `evidencias/Daniella_Fernandez/02-ficha.json` conserva la URL del túnel anterior (`starting-pics-infrastructure-persian.trycloudflare.com`); las URL rápidas cambian al reiniciar Cloudflare Tunnel.

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

### Patricio Vergara · Agente de Entrenamiento

Archivo individual: `blueprint-PATO.md`.

| Qué definir | Mi agente |
|---|---|
| Quién soy | Pato · entrenador de gimnasio con enfoque científico; conozco la anatomía y función de los músculos y armo rutinas basadas en evidencia. |
| Hace | Explica origen, inserción y función de músculos principales, y arma rutinas por grupo muscular, objetivo, nivel y días por semana, citando los estudios que respaldan los parámetros. |
| No hace | No da dietas, planes de alimentación ni suplementos; no diagnostica ni trata lesiones o dolores; no responde sobre viajes, restaurantes ni maletas. |
| Herramientas | `musculo(nombre)`: anatomía, función y ejercicios. `rutina(grupo_muscular, objetivo, nivel, dias_por_semana)`: ejercicios, series, repeticiones, cercanía al fallo, descanso, frecuencia y referencias. Usa datos estáticos en `src/agente_pato/tools.py`. |
| Decide solo | Deduce grupo, objetivo, nivel y días; si faltan datos, usa hipertrofia, principiante y 3 días, y lo explicita. |
| Nunca sin persona | Si se mencionan dolor, lesión, embarazo o una condición médica, no propone rutina y recomienda consultar a un profesional de salud. |
| Deriva a otro | Dietas, suplementos, lesiones, viajes, restaurantes o maletas: indica el límite y no responde esa parte. |
| Dónde se ejecuta | `http://127.0.0.1:8005` · `src/agente_pato/` · `python main.py pato "pregunta"`. |
| Dirección pública | `https://greatly-available-hide-mud.trycloudflare.com` (URL temporal registrada el 9 de noviembre de 2026; puede cambiar). |

### Cristian Meza · siguiente integración

El manifiesto de Dani contiene una Agent Card externa de Cristian para lugares turísticos. En esta rama todavía no se incorporan su código, blueprint ni ronda; se agregarán en la siguiente integración.

| Qué definir | Completar |
|---|---|
| Quién soy | Cristian · agente de lugares turísticos, según la ficha externa registrada. |
| Hace / No hace | Recomienda lugares, horarios, precios referenciales e imágenes; no responde sobre vuelos, hoteles, reservas, clima, visas, equipaje ni restricciones de sitios. |
| Herramientas y datos | Skills externas `listado_sitios_turisticos` y `consultar_horarios`; consultar `evidencias/Daniella_Fernandez/compañeros.md`. |
| Decide solo / Nunca sin persona | Pendiente de validar con el blueprint y la implementación de Cristian. |
| Deriva a otro | Temas de viaje y equipaje quedan fuera de su ficha. |
| Dónde se ejecuta / Dirección pública | La ficha registrada apunta a `http://127.0.0.1:8004`; la URL pública del manifiesto es temporal. Aún no está integrado como código en esta rama. |

## Evidencias

La raíz de `evidencias/` conserva los nombres canónicos de Pato. Las evidencias individuales de Dani están en `evidencias/Daniella_Fernandez/`; no se sustituyen entre integrantes.

| Archivo | Estado / descripción |
|---|---|
| `01-saltos.png` | Salidas CLI del agente de Pato. Dani tiene su propia captura en `evidencias/Daniella_Fernandez/01-saltos.png`. |
| `02-ficha.json` | Agent Card pública de Pato; la ficha de Dani está en `evidencias/Daniella_Fernandez/02-ficha.json`. |
| `mensaje-a2a.json` / `respuesta-a2a.json` | Respuesta A2A de Pato y respuesta A2A de Dani, respectivamente; el SDK devuelve `result.kind=message` y el texto en `result.parts[0].text`. |
| `03-tunel-terminal.png`, `03-tunel-celular.png` | Evidencia del túnel de Pato desde terminal y celular. Dani conserva su verificación HTTPS en `evidencias/Daniella_Fernandez/03-tunel.png`. |
| `04-catalogo.png` | Captura del coordinador de Pato. La copia de Dani está en `evidencias/Daniella_Fernandez/04-catalogo.png`; ambas deben leerse junto a las notas de disponibilidad de cada prueba. |
| `05-ronda.png` | Captura de la ronda de Pato; la de Dani está en `evidencias/Daniella_Fernandez/05-ronda.png`. El detalle escrito de Pato está en `evidencias/ronda-pato.md`. |

Subcarpetas individuales previstas: `Daniella_Fernandez/`, `Cristian_Meza/` y `Patricio_Vergara/`. En esta integración las evidencias canónicas de Pato permanecen en la raíz para conservar los nombres pedidos por la pauta; las de Dani se guardan en su subcarpeta. Cristian añadirá las suyas al integrarse.

Para generar `compañeros.md`, copia `companeros.json.example` a `companeros.json`, completa autor y URL por cada agente ajeno y ejecuta `python scripts/generar_companeros.py`.

**Nota de codificación:** PowerShell mostró algunos acentos como `Ã…`; se verificó que la respuesta A2A guardada como JSON UTF-8 contiene los acentos correctos. El problema era de visualización de la consola.

## Ronda

La pauta pide tres preguntas por integrante: una de la propia skill, una de la skill de un compañero y una que ningún agente del catálogo pueda responder. La ronda debe ejecutarse desde el coordinador después de configurar las URLs de los compañeros.

### Daniella Fernández

| # | Pregunta | A quién debería ir | Resultado / pendiente |
|---|---|---|---|
| 1 | Quiero ganar masa en la espalda, entreno 4 días a la semana, ¿qué rutina hago? | Agente de Entrenamiento de Pato. | El coordinador lo eligió y la respuesta incluyó la rutina y sus referencias. |
| 2 | Voy a Lima el sábado, ¿qué lugares turísticos me recomiendas? | Agente de Cristian, según la ficha externa. | La captura registra la selección, pero anota que no se pudo conectar al agente; es un límite de disponibilidad, no una respuesta exitosa. |
| 3 | ¿Cuál es la capital de Tokio? | Ninguno. | El coordinador eligió `ninguno` y explicó que el tema no corresponde a las skills del catálogo. |

**Evidencia de la skill propia:** la consulta “Voy cinco días a Punta Arenas en julio, ¿qué debería llevar?” aparece en `01-saltos.png` y `respuesta-a2a.json`; recorrió `model → tools → model`. La captura `05-ronda.png` documenta el enrutamiento desde el coordinador hacia Pato, Cristian y `ninguno`, no una segunda ejecución de la skill propia desde el coordinador. Una respuesta a una pregunta sobre VPN rechazó el tema, pero lo atribuyó al agente de viajes; la prueba de derivación incluida en `01-saltos.png` usa una pregunta de vuelos, que sí pertenece al agente de viajes.

### Cristian Meza

Su ronda y evidencias se incorporan junto con el código en la siguiente integración.

### Patricio Vergara

| # | Pregunta | A quién debería ir | Resultado |
|---|---|---|---|
| 1 | Estoy empezando en el gym, ¿qué rutina hago para piernas? | Agente de Entrenamiento de Pato. | Usó `rutina`, asumió hipertrofia/principiante/3 días al faltar datos y citó referencias. |
| 2 | Organizo una feria infantil de 3 horas desde las 15:00, ¿cómo armo el horario? | Agente de Matías, por túnel. | Respondió con un programa de 15:00 a 17:25; quedaron 35 minutos sin actividades. |
| 3 | ¿Quién ganó el mundial de 1962? | Ninguno. | El supervisor indicó que el catálogo no cubre historia del fútbol. |

Análisis y motivos completos: `evidencias/ronda-pato.md`. La ronda detectó como posible solapamiento equipaje para entrenar; las fichas delimitan explícitamente ambos dominios.

---

**Estado del documento:** integración Pato + Dani lista para revisión; Cristian queda expresamente fuera de esta etapa. Antes de la entrega final del grupo, integrar su código y blueprint, completar su ronda, verificar la disponibilidad de su URL y validar el ZIP limpio sin `.env`, `.venv` ni claves.
