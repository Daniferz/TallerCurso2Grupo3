# SPEC · Sistema de agentes del Grupo 3 (taller de implementación)

Pauta: `taller_implementacion_agentes.pdf` (Agentic AI, Curso 2). Plan de tareas: `plan.json`.

## Qué resuelve
Un asistente en **Telegram** para preparar un viaje por Chile. El coordinador recibe cada
pregunta y se la pasa por A2A al especialista que corresponde:

| Agente | Dueño | Qué sabe | Paquete |
|---|---|---|---|
| Maleta | Daniella Fernández | Listas de equipaje por destino, días y temporada | `src/agente_dani` |
| Entrenamiento | Patricio Vergara | Anatomía y rutinas de gimnasio con base científica | `src/agente_pato` |
| Sitios turísticos | Cristian Meza | Sitios con ubicación, horarios y precios | `src/agente_cristian` |
| Coordinador | Grupo | Elige el agente, conserva la respuesta tal cual y la etiqueta `[Nombre]` | `src/coordinador` |

Los agentes de ejemplo de viajes y restaurantes salen del catálogo del coordinador.

## Decisiones tomadas
- **Canal (opción 2 del PDF):** Telegram.
  - **Local (entrega obligatoria):** el bot lee mensajes por *polling* con `TELEGRAM_TOKEN`. No
    necesita túnel ni URL pública: el evaluador crea su bot con BotFather, pone el token en `.env`
    y corre un comando.
  - **Heroku (+1):** webhook `POST /telegram` en el coordinador, protegido con el secreto del webhook.
- **Nube (+1):** Heroku, una app por agente y una para el coordinador, todas desde este repo
  (`Procfile` con `$APP_MODULO`).
  Heroku ya está pagado por el grupo, probablemente con el plan **Eco** (confirmar en *Resources*
  de cada app). Eco duerme las apps tras 30 min sin uso y tardan 10-20 s en despertar: por eso en
  Heroku se usa `TIEMPO_FICHA_A2A=30` y antes de capturar evidencias se despiertan las apps (T03, T15).
- **Extra:** cuando ningún agente puede responder, el coordinador avisa a un chat del grupo
  (`TELEGRAM_CHAT_AVISO`). Si el aviso falla, la persona igual recibe su respuesta.
- **Rama de trabajo:** `taller-sistema-agentes`. `main` solo recibe trabajo revisado por PR.

## Seguridad
| Dónde | Cómo se protege | Variable |
|---|---|---|
| Mensajes A2A a cada agente (`POST /`) | Cabecera `X-API-Key`; **cada agente tiene su propia clave** y rechaza la de los otros | `CLAVE_PATO`, `CLAVE_DANI`, `CLAVE_CRISTIAN` |
| Coordinador → agentes | Envía la clave de cada agente | `CLAVES_AGENTES` (mismo orden que `URLS_AGENTES`) |
| `POST /chat` del coordinador | Cabecera `X-API-Key` | `CLAVE_COORDINADOR` |
| `POST /telegram` (Heroku) | Cabecera `X-Telegram-Bot-Api-Secret-Token` | `TELEGRAM_SECRETO_WEBHOOK` |
| Bot de Telegram | Solo responde a usuarios autorizados; al resto le dice que no tiene acceso | `TELEGRAM_USUARIOS_PERMITIDOS` |
| Ficha A2A y `/salud` | Públicas (la spec A2A pide fichas descubribles) | — |

Las claves viven solo en `.env` (local) o en las variables de Heroku. Nunca en el repo, el ZIP,
los logs ni las capturas. `.env.example` lleva todas las variables con valores ficticios.

## Qué es real y qué es simulado
- **Real:** Gemini, la comunicación A2A, el control de acceso y los mensajes de Telegram.
- **Simulado (datos estáticos en `tools.py`):** guías de equipaje, músculos y rutinas, sitios
  turísticos. Se declara en el README y en las evidencias.
- **No se conserva:** la memoria (`MemorySaver`) y las tareas A2A viven en RAM; se pierden al
  reiniciar o cuando Heroku reinicia la app.

## Requisitos de la pauta que este plan cubre
1. Recorrido completo real: Telegram → coordinador → agente → respuesta en el mismo chat.
2. La respuesta final conserva cifras, unidades y condiciones; se piden los datos faltantes.
3. Entradas inválidas, fallas del proveedor y agentes caídos dan mensajes claros, nunca éxito falso.
4. Acceso permitido y rechazado demostrados sin mostrar claves.
5. Acciones con efectos reales (mensajes y avisos de Telegram): solo cuentas y chats de prueba;
   README explica cómo detener el bot y evitar envíos accidentales.
6. Evidencias con LOCAL o HEROKU y fecha, solicitud, resultado esperado, obtenido y observaciones.
7. README reproducible: integrantes y aportes, opción elegida, preparación manual (BotFather,
   Gemini, Heroku), instalación, comandos para iniciar, probar y detener, límites conocidos.
8. +1: despliegue que funciona con los computadores de los integrantes apagados, sin túnel.

## Cómo trabajamos
1. Cada integrante toma **una tarea a la vez** de `plan.json`, de las que tienen su nombre o
   "por asignar" (al tomarla, pone su nombre).
2. Crea una rama desde `taller-sistema-agentes` (ej.: `t05-prompt-supervisor`), la marca
   `en_curso`, la implementa con `@implementador` y abre un PR hacia `taller-sistema-agentes`.
3. Antes de empezar: `git pull`. Las tareas que tocan el mismo archivo están encadenadas en
   `depende_de` para no chocar.
4. `@spec` agrega o ajusta tareas cuando cambie el alcance; nadie marca `hecho` sin evidencia.

## Preguntas abiertas
1. Los "12 resultados" y sus porcentajes que mencionó el grupo: ¿de qué documento salen? El PDF
   no los numera. Hay que listarlos en `plan.json` (tarea de evidencias) para no olvidar ninguno.
2. ¿Se borra el código de los agentes de ejemplo (viajes y restaurantes) o solo sale del catálogo?
3. ¿Sacamos `grupo-3-taller-a2a.zip` del repo? Pesa 2,7 MB y es de la entrega anterior.
4. ¿Se entrega el link de GitHub (el repo es público) o un ZIP generado con `git archive`?
