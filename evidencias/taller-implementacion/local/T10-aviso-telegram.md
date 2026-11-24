# T10 · Aviso cuando ningún agente corresponde · LOCAL

- El coordinador conserva la respuesta normal aunque el aviso a Telegram falle.
- Limita los avisos a uno por conversación cada `AVISO_MINUTOS` (10 por defecto).
- Evidencia manual registrada el 2026-11-19 en la rama de Cristian: tres preguntas fuera de tema en una conversación produjeron un solo aviso; con un chat de aviso inválido, la persona recibió su respuesta normal.
- Las pruebas automatizadas simulan Telegram; no envían mensajes reales.
- En la rama limpia de PR: `tests/test_supervisor.py` y `tests/test_telegram.py` pasan; suite completa: 85 passed (2 avisos deprecados de FastAPI).
