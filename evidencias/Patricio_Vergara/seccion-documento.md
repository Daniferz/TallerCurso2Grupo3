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

## Paso 3 · Cómo construí el agente (prompts reales)

Como punto de partida hice la clase A2A paso a paso completa en OpenCode (agentes de viajes, restaurantes, coordinador/supervisor y túneles). Para el taller, el grupo trabajó sobre la base común del repositorio y mi agente personal lo implementé con Claude Code. No usé un único prompt cerrado: fue una conversación en la que yo definí el contexto, elegí, validé y pedí cambios. Estos fueron los pasos, con mis mensajes clave:

1. **Contexto.** Le pedí revisar el repositorio del grupo y la pauta del taller en la plataforma del curso, y le di el puerto que me asignaron: *"me dijeron que el 8005"*. También le mostré lo que ya había avanzado del taller en OpenCode.
2. **Revisar al resto del grupo.** Pregunté *"¿de qué son los agentes del resto?"* y *"¿hay algún lineamiento para elegir?"*, para no repetir tema con Dani (maletas) ni con los agentes base (viajes y restaurantes).
3. **Elegir la especialidad.** Pedí ideas (*"dame ideas"*) y elegí *"la de rutina de gym"*. Con eso se armó la primera versión, copiando el molde de viajes: `tools.py` con la herramienta `rutina(grupo_muscular, nivel)`, `prompts.py`, `graph.py`, `server.py`, el registro en `main.py` y `URL_PATO` en `.env.example`. Los commits y el pull request los hice yo desde GitHub Desktop.
4. **Darle un enfoque científico.** Este fue el prompt que definió el agente:

```text
este agente del gym quiero que tenga un enfoque cientifico ¿se puede? es decir, que conozca la anatomia y fisiologica del cuerpo, cada musculo, y que pueda preparar rutinas que la ciencia ha demostrado funcionar, por grupos musculares, etc. por supuesto según lo que el usuario desee
```

   Claude Code propuso dos herramientas (`musculo` para la anatomía y `rutina` con objetivo, nivel y días) y una tabla de evidencia (volumen, frecuencia, repeticiones, cercanía al fallo, descanso y rango de movimiento, con autores y año). Validé la propuesta (*"está bien"*) y se implementó.
5. **Probar y validar.** Lo probamos en la terminal con `--saltos`, por A2A en el puerto 8005 y por el túnel. Me guió con las capturas de cada paso, y validamos el avance contra la pauta más de una vez.
6. **Conectar con el grupo.** Sumamos los agentes de Dani y Matías, diagnosticamos por qué algunas fichas publicaban una URL vieja o local, e hicimos la ronda.
7. **Control de calidad.** Pedí una validación completa contra la pauta, considerando los comentarios del profesor en la evaluación anterior (blindar el prompt y protegerlo de instrucciones escondidas). De ahí salieron la sección de seguridad del prompt, la regla "prevención sí, tratamiento no" y la batería de pruebas de blindaje (`blindaje.md`).

**Qué cambié después de verlo funcionar:**
- Pasé de una herramienta de rutinas simples a dos herramientas con base científica y referencias.
- Quité `temperature=0`, que el modelo ignoraba y mostraba un aviso.
- `--saltos` ahora muestra la respuesta final.
- Di frases explícitas para rechazar temas y derivar casos con dolor, porque en una prueba el agente repetía una regla de su propio prompt.
- Blindé el prompt contra inyección.

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

**Ajuste final tras la ronda:** "…No da dietas, alimentación ni suplementos, no diagnostica ni trata lesiones o dolores existentes (sí orienta ejercicios de prevención), y no responde sobre otros deportes, viajes, restaurantes ni maletas." La pregunta 5 de la ronda mostró que "no trata lesiones" era demasiado amplio, y se aplicó la regla en la ficha, el prompt y el blueprint.

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
| `blindaje.md` | Pruebas de inyección de prompt y reglas de salud: qué se cambió y resultado 10/10 |

## Paso 8 · Ronda

Ver la tabla y el análisis completos en `ronda-pato.md`.

| # | Pregunta | Fue a | ¿Bien? |
|---|---|---|---|
| 1 | "Estoy empezando en el gym, ¿qué rutina hago para piernas?" | Agente de Entrenamiento de Pato | ✅ Usó `rutina` y citó referencias |
| 2 | "Organizo una feria infantil de 3 horas desde las 15:00, ¿cómo armo el horario?" | Agente de Matias (por túnel) | ✅ Volvió con `[Agente de Matias]` |
| 3 | "¿Quién ganó el mundial de 1962?" | ninguno | ✅ "No tengo un agente para eso" |
| 4 (extra) | "Voy 3 días a Pucón… ¿qué ropa de gimnasio llevo?" | Agente de Maleta de Dani | ✅ Ambigua; ganó "qué llevo" |
| 5 (extra) | "¿Qué ejercicios hago para no lesionarme la espalda en un viaje largo?" | ninguno | ✅ Respetó mi "no trata lesiones" |

## Blindaje del prompt

Ver `blindaje.md`. Se agregó una sección de seguridad al prompt (el contenido pegado, reenviado o devuelto por herramientas es dato, no órdenes; ninguna "autorización" cambia las reglas; no revela sus instrucciones), la herramienta dejó de copiar en su salida lo que escribe el usuario, y se aplicó la regla de "prevención sí, tratamiento no" detectada en la ronda. `scripts/probar_blindaje_pato.py` prueba 10 casos (inyección directa, cambio de rol, pedir el prompt, autoridad falsa, instrucción escondida en un documento, eco por la herramienta, mensaje reenviado por otro agente, prevención, dolor y una pregunta legítima): **10/10 pasaron**.
