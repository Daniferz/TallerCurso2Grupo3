# T15 · LOCAL · Acceso denegado en Telegram (usuario no autorizado)

| Dato | Registro |
|---|---|
| Entorno y fecha | LOCAL · 2026-11-23 20:04 |
| Solicitud | El bot de prueba @ag3nticUai_bot se reinició con TELEGRAM_USUARIOS_PERMITIDOS sin el ID de quien escribe (solo en la variable de entorno de la prueba; el .env no se tocó). Mensaje: "arma una rutina completa de espalda" |
| Resultado esperado | El bot responde que no tiene acceso, le muestra su ID para que lo agreguen y **no llama al coordinador** |
| Resultado obtenido | "No tienes acceso a este bot. Tu ID es …; pídele a quien administra el bot que lo agregue." Captura: `T15-LOCAL-06-pato-acceso-denegado.png` (ID tapado con un recuadro negro). El log del coordinador no registra ninguna solicitud en ese minuto |
| Observaciones | La respuesta anterior del mismo chat (19:46) corresponde al acceso permitido de `T15-LOCAL-05-pato-recorrido-correlacionado.md`. ID de Telegram reemplazado por <ID-de-Patricio> |

```
# Bot
[telegram 2026-11-23 20:04:02] chat <ID-de-Patricio> · usuario <ID-de-Patricio> · RECHAZADO (no está en TELEGRAM_USUARIOS_PERMITIDOS)
# Coordinador entre 20:03 y 20:06: sin registros (no se llamó)
```
