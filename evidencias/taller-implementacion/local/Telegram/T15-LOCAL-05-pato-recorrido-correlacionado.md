# T15 · LOCAL · Recorrido correlacionado de una solicitud (Entrenamiento)

| Dato | Registro |
|---|---|
| Entorno y fecha | LOCAL · 2026-11-23 19:45 |
| Solicitud | En Telegram (@ag3nticUai_bot, bot de prueba): "arma una rutina de pecho para fuerza. 5 días por semana" |
| Resultado esperado | El bot llama a POST /chat del coordinador con su clave; el supervisor elige a Entrenamiento; el coordinador le pregunta por A2A con CLAVE_PATO; la respuesta llega al mismo chat con la rutina completa y la etiqueta [Agente de Entrenamiento de Pato] |
| Resultado obtenido | Igual a lo esperado. Captura: `T15-LOCAL-05-pato-recorrido-correlacionado.jpg`. Los cuatro registros de abajo son de la misma solicitud (mismo conversacion_id y horas consecutivas) |
| Observaciones | El ID de Telegram se reemplazó por <ID-de-Patricio>. La rutina declara el nivel supuesto (principiante) porque no se indicó. Tiempo total ~30 s (Gemini en el coordinador y en el agente). Datos de rutinas: estáticos en tools.py |

## Registros de la misma solicitud

```
# Coordinador (recibe la solicitud del bot)
[acceso 2026-11-23 19:45:45] Coordinador POST /chat desde 127.0.0.1: PERMITIDO
# Coordinador (agente elegido)
[chat] conversación <ID-de-Patricio> -> agente: Agente de Entrenamiento de Pato
# Agente de Pato (llamada A2A del coordinador)
[acceso 2026-11-23 19:45:49] Agente de Entrenamiento de Pato POST / desde 127.0.0.1: PERMITIDO
# Bot (respuesta entregada en el chat)
[telegram 2026-11-23 19:46:15] chat <ID-de-Patricio> · usuario <ID-de-Patricio> · agente: Agente de Entrenamiento de Pato · respuesta: [Agente de Entrenamiento de Pato] Para armar tu rutina usé un nivel principiante (supuse ese nivel) y 5 días por semana ...
```
