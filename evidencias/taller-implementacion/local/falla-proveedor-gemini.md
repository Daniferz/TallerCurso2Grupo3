# Falla del proveedor (Gemini) · LOCAL · 2026-11-21

Pauta: "las fallas del proveedor ... producen mensajes claros; no deben presentarse como operaciones
exitosas". Se simula la falla con una `GOOGLE_API_KEY` inválida **solo en la variable de entorno de
la prueba**; el `.env` no se tocó.

## Caso 1: agente por terminal

| Dato | Registro |
|---|---|
| Entorno y fecha | LOCAL · 2026-11-21 12:59 |
| Solicitud | `GOOGLE_API_KEY=clave-invalida python main.py pato "Arma una rutina de pecho"` |
| Resultado esperado | Error en una línea, sin stack trace, y código de salida distinto de 0 |
| Resultado obtenido | `No se pudo completar la consulta: la clave de Gemini no es válida o no tiene permiso para este modelo.` · código de salida 1 |
| Observaciones | Ninguna respuesta inventada. |

## Caso 2: vía coordinador (`POST /chat`)

| Dato | Registro |
|---|---|
| Entorno y fecha | LOCAL · 2026-11-21 13:00 |
| Solicitud | `POST /chat` con `CLAVE_COORDINADOR`: "Arma una rutina de pecho para fuerza". El agente de Pato corre con la clave de Gemini inválida. |
| Resultado esperado | Error claro y HTTP distinto de 200 (nunca éxito falso) |
| Resultado obtenido | HTTP **502** · `{"detail":"El coordinador no pudo responder: Agente de Entrenamiento de Pato no pudo responder: No se pudo responder: la clave de Gemini no es válida o no tiene permiso para este modelo."}` |
| Observaciones | Log del agente: `[error] No se pudo responder: la clave de Gemini no es válida o no tiene permiso para este modelo.` La primera ejecución mostró además el stack trace de `a2a-sdk`; se corrigió en `src/comun/servidor.py` (filtro `_SinStackTrace`) y en la segunda ejecución el log quedó sin stack trace. |

## Caso 3: lo que ve la persona en Telegram

| Dato | Registro |
|---|---|
| Entorno y fecha | LOCAL · 2026-11-21 |
| Solicitud | Cualquier pregunta por Telegram cuando `/chat` responde error |
| Resultado esperado | Mensaje claro en el chat, sin detalles técnicos |
| Resultado obtenido | "No pude responder en este momento: el asistente no está disponible. Intenta de nuevo en unos minutos." (el detalle técnico queda solo en el log del bot) |
| Observaciones | Mismo mensaje que con el coordinador apagado (T08). Falta la captura en Telegram (T15). |

Pendiente para T15: captura de pantalla del caso 3 en Telegram.
