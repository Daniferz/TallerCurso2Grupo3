# T09 · Webhook de Telegram · LOCAL · 2026-11-19

- `POST /telegram` valida `X-Telegram-Bot-Api-Secret-Token`; la lógica reutiliza la atención del bot local.
- `scripts/registrar_webhook.py` incluye registrar, consultar y borrar el webhook; las llamadas usan timeout explícito y no imprimen token ni secreto.
- En una prueba local, `setWebhook` registró un endpoint HTTPS temporal, `getWebhookInfo` mostró cero actualizaciones pendientes, `/start` respondió y, tras `deleteWebhook`, el polling local volvió a responder.
- El endpoint temporal se retiró al terminar la prueba. El despliegue de entrega no depende de túneles; la URL final del coordinador corresponde a T12.
- Las pruebas automatizadas de T09/T10 pasaban en la rama fuente. En la rama limpia se volverá a ejecutar la suite completa.
