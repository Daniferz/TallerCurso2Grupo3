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

### 2026-11-18 · Patricio Vergara · Tareas sin dueño fijo y T03 lista (afecta a todos)
- **Todas las tareas pendientes de `plan.json` están "por asignar".** Para tomar una: pon tu
  nombre en `responsable`, márcala `en_curso` y **sube ese cambio antes de programar** (el primero
  que lo sube se la queda). Detalle en `SPEC.md`, "Cómo trabajamos".
- **T02 y T03 ya están en `taller-sistema-agentes`.** Antes de trabajar: `git pull` en esa rama.
- Con T03 el coordinador usa **solo** `URLS_AGENTES` (Maleta, Entrenamiento y Sitios turísticos).
  Si un agente está apagado, responde "La parte de [agente] no está disponible en este momento..."
  y lo vuelve a intentar cada 60 s, sin reiniciar el coordinador.
- **Qué hacer:** en tu `.env`, pon en `URLS_AGENTES` las URLs de los 3 agentes y en `CLAVES_AGENTES`
  sus claves en el mismo orden. `REINTENTO_AGENTES_SEG` es opcional (60 por defecto).
- Ya desbloqueadas: T04, T05, T07, T08 y T13.

### 2026-11-18 · Patricio Vergara · T08: bot de Telegram en local (afecta a todos)
- El coordinador tiene `POST /chat` (exige `CLAVE_COORDINADOR`) y hay un bot por polling:
  `python -m src.canal.telegram`, con el coordinador y los agentes levantados. Se detiene con Ctrl+C.
- **Qué hacer para probarlo:** crea **tu propio bot de prueba** con @BotFather y agrega a tu `.env`
  `TELEGRAM_TOKEN` y `TELEGRAM_USUARIOS_PERMITIDOS` (tu ID numérico, te lo da @userinfobot).
  El token nunca va al repo ni a capturas. En las evidencias, reemplaza tu ID por `<ID-de-nombre>`.
- Ya desbloqueada: T09 (webhook para Heroku).

### 2026-11-18 · Patricio Vergara · Sitios turísticos no tiene Valparaíso (para Cristian)
- Con T03 el coordinador ya envía "Qué sitios turísticos puedo visitar en Valparaíso" al agente de
  Cristian, pero el agente responde "No tengo sitios turísticos registrados para Valparaíso".
- **Qué hacer (Cristian):** sumar las ciudades que faltan a los datos de `src/agente_cristian` y
  decir en su ficha qué ciudades cubre, para que el supervisor no lo elija para ciudades sin datos.
