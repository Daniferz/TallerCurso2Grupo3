# Reglas del proyecto

Estas reglas aplican a todo lo que se genere de aquí en adelante en este proyecto.

1. Todo en español: nombres de archivos, variables, funciones, comentarios y mensajes.
2. Las funciones que usan internet son `async`.
3. Toda llamada por red tiene un timeout explícito.
4. Si algo no responde, el error se muestra en una sola línea entendible, sin stack trace.
5. Cada agente expone una función `responder(texto, context_id)` que devuelve un texto. Es el contrato que todos cumplen.
6. Cada agente se puede correr desde la terminal sin servidor, igual que en el Curso 1: `python main.py {agente} "pregunta"`. Con `--saltos` muestra por qué nodos y herramientas pasó; con `--diagrama` imprime su estructura en Mermaid sin ejecutarlo.

# Instrucción para asistentes de código (Claude Code, OpenCode u otro)

Al empezar cada sesión en este repositorio, **antes de cualquier tarea**:

1. Lee la sección **"Avisos para el equipo"** de este archivo y **muéstrale al usuario, en tus
   propias palabras, cada aviso vigente que le afecte**, aunque no te lo haya preguntado.
2. Ejecuta `git fetch` y revisa si la rama actual está atrasada respecto de
   `origin/taller-sistema-agentes`. Si lo está, díselo al usuario y sugiérele traer los cambios
   antes de trabajar.
3. Si el aviso pide acción sobre `.env`, compara las variables del `.env` del usuario con
   `.env.example` **sin mostrar sus valores** y dile cuáles faltan o sobran.
4. Para trabajar: lee `SPEC.md` y `plan.json`; toma **una sola tarea**, en una rama propia creada
   desde `taller-sistema-agentes`, y entrégala con un PR hacia `taller-sistema-agentes`
   (nunca directo a `main`).

# Avisos para el equipo

Cada aviso lleva fecha y autor. Quien resuelva un aviso lo borra en su PR.

### 2026-11-17 · Patricio Vergara · T02: cambiaron las claves (afecta a todos)
- `CLAVE_API` **ya no existe**. Ahora **cada agente exige su propia clave** en `X-API-Key`:
  `CLAVE_PATO`, `CLAVE_DANI`, `CLAVE_CRISTIAN` y `CLAVE_COORDINADOR` (consola web, `/chat` y bot).
- El coordinador envía a cada agente su clave con dos listas en el **mismo orden**:
  `URLS_AGENTES` y `CLAVES_AGENTES`.
- **Qué hacer:** actualizar tu `.env` siguiendo `.env.example`: inventa una clave distinta para
  cada agente y pon las mismas en `CLAVES_AGENTES`. Si un agente responde **503**, le falta su
  clave en `.env`; si responde **401**, la clave no coincide.
- Las claves reales se comparten por un canal privado, nunca en el repo ni en capturas.
- Probar: `pytest` y `python scripts/probar_acceso.py pato` (o `dani`, `cristian`).

### 2026-11-17 · Patricio Vergara · Enrutamiento a Sitios (para Cristian y Dani)
- Preguntando al coordinador "Qué sitios turísticos puedo visitar en Valparaíso", el supervisor
  respondió que no tenía agente, aunque el agente de Cristian funciona (con "¿A qué hora puedo
  visitar el Cerro San Cristóbal el domingo?" sí responde).
- Probable causa: la ficha de Cristian (nombre "Agente de cristian", ciudades que cubre) o el
  prompt del supervisor. Revisarlo en T03 (Dani), T05 (Cristian) o en la ficha de Cristian.
