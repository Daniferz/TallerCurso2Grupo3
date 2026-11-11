# Patricio Vergara · Agente de Entrenamiento de Pato

Sección lista para pegar en `documento-entrega.md`. Puerto 8005 · `src/agente_pato/` · `python main.py pato "pregunta"`.

## Blueprint

Ver `blueprint-PATO.md` en la raíz del proyecto.

| Qué definir | Mi agente |
|---|---|
| Quién soy | Pato · entrenador de gimnasio con enfoque científico: conozco la anatomía y función de los músculos y armo rutinas basadas en evidencia. |
| Hace | Explica origen, inserción y función de cada músculo principal, y arma rutinas por grupo muscular según objetivo (hipertrofia, fuerza o resistencia), nivel y días por semana, citando los estudios que respaldan cada parámetro. |
| No hace | No da dietas, alimentación ni suplementos, no diagnostica ni trata lesiones o dolores, y no responde sobre vuelos, hoteles, restaurantes ni maletas. |
| Herramientas | `musculo(nombre)` y `rutina(grupo_muscular, objetivo, nivel, dias_por_semana)`, con datos estáticos en `tools.py`. |
| Decide solo | Deduce grupo, objetivo, nivel y días; si falta alguno usa hipertrofia, principiante y 3 días, y lo dice. |
| Nunca sin persona | No arma rutinas si la persona menciona dolor, lesión, embarazo o una condición médica: la deriva a un profesional de la salud. |
| Deriva a otro | Dietas, suplementos, lesiones, viajes, restaurantes o maletas → lo dice en una frase y no responde. |
| Dónde se ejecuta | `http://127.0.0.1:8005` · `src/agente_pato/` |
| Dirección pública | `https://greatly-available-hide-mud.trycloudflare.com` (túnel temporal del 9 de noviembre) |

## Paso 3 · Prompt 1 usado

Como punto de partida hice la clase A2A paso a paso completa en OpenCode (agentes de viajes, restaurantes, coordinador/supervisor y túneles). Para el taller, el grupo trabajó sobre la base común del repositorio y mi agente personal lo implementé con Claude Code, siguiendo el molde del agente de viajes y la plantilla del prompt 1 de la pauta:

```text
Quiero crear un agente nuevo que represente lo que yo sé hacer. Mi nombre es Pato y mi especialidad es armar rutinas de gimnasio. Hazlo copiando el molde del agente de viajes, en src/agente_pato/ con los mismos cuatro archivos y siguiendo AGENTS.md:

1) tools.py. Una herramienta con @tool, rutina(grupo_muscular, nivel), con datos inventados pero creíbles dentro del archivo: ejercicios con series × repeticiones, descanso y un consejo para pecho, espalda, piernas, hombros, brazos, core y cuerpo completo, en nivel principiante o intermedio. Si piden algo que no está en los datos, la herramienta lo dice en una línea, nunca lanza un error.

2) prompts.py. Un SYSTEM_PROMPT que diga: eres Pato, entrenador de gimnasio. Responde solo sobre rutinas, en español y corto, usando la herramienta antes de contestar y sin inventar datos. Si mencionan dolor o una lesión, deriva a un profesional de la salud. Si te preguntan algo que no es de tu tema (dietas, suplementos, viajes, restaurantes, maletas), dilo en una frase y no intentes responderlo. Si te preguntan quién eres, di tu nombre y tu especialidad.

3) graph.py. Igual que el de viajes: create_agent con el modelo de Gemini, mi herramienta, el SYSTEM_PROMPT y MemorySaver, con las tres funciones responder, saltos y diagrama. Conéctalo a main.py para que funcionen python main.py pato "pregunta", --saltos y --diagrama.

4) server.py. La ficha con crear_tarjeta: nombre "Agente de Gimnasio de Pato", una descripción de dos frases (qué sé y qué no hago) y una skill por herramienta con una pregunta de ejemplo. Lee URL_PATO del .env (agrégala al .env y al .env.example apuntando a http://127.0.0.1:8005) y arma app = crear_app(tarjeta, responder).

No lo levantes tú. Dime cómo probarlo sin servidor y después el comando: uvicorn src.agente_pato.server:app --port 8005 --reload.
```

**Qué cambié después de verlo funcionar:** le di un enfoque científico. Agregué una segunda herramienta, `musculo(nombre)`, con la anatomía de 15 músculos, y amplié `rutina` con objetivo y días por semana, volumen semanal repartido en sesiones (mínimo 2 series por ejercicio) y referencias (Schoenfeld, Refalo, Maeo, ACSM). También quité `temperature=0` porque el modelo la ignoraba y mostraba un aviso en la terminal, hice que `--saltos` muestre la respuesta final, y di frases explícitas para rechazar temas ajenos y derivar casos con dolor, porque en una prueba el agente repetía una regla de su propio prompt.

## Paso 4 · Diagrama

Salida de `python main.py pato --diagrama` (ver `diagrama.md`):

```text
graph TD;
	__start__([<p>__start__</p>]):::first
	model(model)
	tools(tools<hr/><small><em>__tools = musculo, rutina</em></small>)
	__end__([<p>__end__</p>]):::last
	__start__ --> model;
	model -.-> __end__;
	model -.-> tools;
	tools -.-> model;
```

Respuesta del mensaje por PowerShell al puerto 8005: ver `mensaje-a2a.json` (texto dentro de `result.parts`).

## Paso 5 · Ficha antes y después del prompt 2

**Antes:** "Arma rutinas de gimnasio para pecho, espalda, piernas, hombros, brazos, core o cuerpo completo, en nivel principiante o intermedio, con series, repeticiones y descanso. No da dietas, alimentación ni suplementos, no trata lesiones o dolores, y no responde sobre viajes, restaurantes ni maletas."

**Después:** "Explica la anatomía y función de los músculos y arma rutinas de gimnasio con base científica por grupo muscular (pecho, espalda, piernas, glúteos, hombros, brazos, core o cuerpo completo), según objetivo (hipertrofia, fuerza o resistencia), nivel y días por semana. No da dietas, alimentación ni suplementos, no trata lesiones o dolores, y no responde sobre viajes, restaurantes ni maletas."

**Por qué:** al agregar la herramienta de anatomía, la ficha tenía que decirlo, o el supervisor nunca me mandaría preguntas sobre músculos. Agregué también los objetivos y los días para que el supervisor sepa qué tipo de rutina puedo armar, y mantuve la frase de "no hago" para que no me lleguen preguntas de dietas, lesiones ni de los otros agentes del grupo. Cada herramienta tiene su skill con una pregunta de ejemplo. Ficha final: `02-ficha.json`.

## Evidencias (en `evidencias/Patricio_Vergara/`)

| Archivo | Qué muestra |
|---|---|
| `01-saltos.png` | `--saltos` con una pregunta de mi tema (usa `rutina`), una con dolor (deriva a un profesional) y una de otro tema (la rechaza), con la respuesta final |
| `02-ficha.json` | Ficha final descargada por el túnel |
| `03-tunel-terminal.png` y `03-tunel-celular.png` | Terminal de cloudflared con la URL y la ficha abierta desde el celular |
| `04-catalogo.png` | Coordinador con "Supervisor con 2 agentes" de otros computadores (Dani y Matías) |
| `05-ronda.png` | Las tres preguntas de la ronda con `--saltos` |
| `05-ronda-ambigua.png` | Dos preguntas extra que dos agentes podían responder (gimnasio + maleta, ejercicios + lesión) |
| `compañeros.md` | Nombre, skill, URL y ficha JSON de los agentes ajenos sumados |

## Paso 8 · Ronda

Ver la tabla y el análisis completos en `ronda-pato.md`.

| # | Pregunta | Fue a | ¿Bien? |
|---|---|---|---|
| 1 | "Estoy empezando en el gym, ¿qué rutina hago para piernas?" | Agente de Entrenamiento de Pato | ✅ Usó `rutina` y citó referencias |
| 2 | "Organizo una feria infantil de 3 horas desde las 15:00, ¿cómo armo el horario?" | Agente de Matias (por túnel) | ✅ Volvió con `[Agente de Matias]` |
| 3 | "¿Quién ganó el mundial de 1962?" | ninguno | ✅ "No tengo un agente para eso" |
| 4 (extra) | "Voy 3 días a Pucón… ¿qué ropa de gimnasio llevo?" | Agente de Maleta de Dani | ✅ Ambigua; ganó "qué llevo" |
| 5 (extra) | "¿Qué ejercicios hago para no lesionarme la espalda en un viaje largo?" | ninguno | ✅ Respetó mi "no trata lesiones" |
