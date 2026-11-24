# T15 · HEROKU · Logs del agente de Entrenamiento (Pato)

Logs copiados del dashboard de Heroku (app `agente-pato-grupo3`, **More → View logs**). Hora en UTC
(Chile = UTC-3). Anonimizados: la IP de la prueba es `<IP-de-prueba>`, la IP de Heroku que lee la ficha
es `<IP-coordinador-Heroku>` y se quitó la línea de sesión del dashboard, que mostraba un correo personal.

| Dato | Registro |
|---|---|
| Entorno y fecha | HEROKU · 2026-11-23 23:09-23:10 UTC (20:09-20:10 en Chile) |
| Solicitud | Desde fuera de Heroku: `POST /` (A2A) sin `X-API-Key` y luego con `CLAVE_PATO`: "Arma una rutina de piernas para fuerza, 3 días por semana" |
| Resultado esperado | Sin clave: 401 y `RECHAZADO` en el log. Con clave: `PERMITIDO` y 200 con la rutina real |
| Resultado obtenido | Igual a lo esperado: 401 `RECHAZADO (Falta el encabezado X-API-Key.)`; luego `PERMITIDO` y 200 tras ~21 s (`service=20769ms`: Gemini). Respuesta recibida: rutina de piernas para fuerza, nivel principiante, que declara el nivel supuesto |
| Observaciones | A las 21:46 UTC se ve a una IP de AWS (Heroku) leyendo la ficha `/.well-known/agent-card.json`: es el coordinador del grupo descubriendo el agente al arrancar. Las claves no aparecen en ningún log. La conversación por el bot del grupo con Entrenamiento está en `Telegram/T15-HEROKU-02-entrenamiento.*` |

```
2026-11-23T21:46:15.010421+00:00 heroku[router]: at=info method=GET path="/.well-known/agent-card.json" host=agente-pato-grupo3-8c9b06247efd.herokuapp.com request_id=4f1ade39-6e15-13a4-5d85-08fb243a2b93 fwd="<IP-coordinador-Heroku>" dyno=web.1 connect=0ms service=1ms status=200 bytes=1418 protocol=http1.1 tls=true tls_version=tls1.3
2026-11-23T21:46:15.068288+00:00 app[web.1]: INFO:     <IP-coordinador-Heroku>:0 - "GET /.well-known/agent-card.json HTTP/1.1" 200 OK
2026-11-23T21:46:15.068584+00:00 heroku[router]: at=info method=GET path="/.well-known/agent-card.json" host=agente-pato-grupo3-8c9b06247efd.herokuapp.com request_id=ccb06d8c-3362-e938-ae9b-0ce8703722ee fwd="<IP-coordinador-Heroku>" dyno=web.1 connect=0ms service=1ms status=200 bytes=1418 protocol=http1.1 tls=true tls_version=tls1.3
2026-11-23T23:09:57.067086+00:00 app[web.1]: [acceso 2026-11-23 23:09:57] Agente de Entrenamiento de Pato POST / desde <IP-de-prueba>: RECHAZADO (Falta el encabezado X-API-Key.)
2026-11-23T23:09:57.067264+00:00 app[web.1]: INFO:     <IP-de-prueba>:0 - "POST / HTTP/1.1" 401 Unauthorized
2026-11-23T23:09:57.067676+00:00 heroku[router]: at=info method=POST path="/" host=agente-pato-grupo3-8c9b06247efd.herokuapp.com request_id=56001029-41cc-3eb3-8582-29e295f0c3ae fwd="<IP-de-prueba>" dyno=web.1 connect=0ms service=1ms status=401 bytes=43 protocol=http1.1 tls=true tls_version=tls1.3
2026-11-23T23:09:57.187180+00:00 app[web.1]: [acceso 2026-11-23 23:09:57] Agente de Entrenamiento de Pato POST / desde <IP-de-prueba>: PERMITIDO
2026-11-23T23:10:17.955732+00:00 app[web.1]: INFO:     <IP-de-prueba>:0 - "POST / HTTP/1.1" 200 OK
2026-11-23T23:10:17.956280+00:00 heroku[router]: at=info method=POST path="/" host=agente-pato-grupo3-8c9b06247efd.herokuapp.com request_id=8384fcd0-7a8b-e652-0c2f-99cc95db709d fwd="<IP-de-prueba>" dyno=web.1 connect=0ms service=20769ms status=200 bytes=1459 protocol=http1.1 tls=true tls_version=tls1.3
```
