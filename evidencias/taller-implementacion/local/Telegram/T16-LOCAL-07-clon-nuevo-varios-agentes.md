# T16 · LOCAL · Prueba desde cero (clon nuevo siguiendo el README)

| Dato | Registro |
|---|---|
| Entorno y fecha | LOCAL · 2026-11-23 21:05-21:09, en una carpeta nueva fuera del repositorio de trabajo |
| Solicitud | `git clone` del repositorio, `python -m venv .venv`, `pip install -r requirements-lock.txt`, `.env` desde `.env.example`, y los comandos de "Iniciar en local" del README (3 agentes, coordinador y bot). En Telegram (bot de prueba): "hola" y "que llevo en una maleta para pucon 3 días en invierno y que sitios turísticos puedo visitar en valparaíso?" |
| Resultado esperado | Instalación sin errores, pytest pasa, "Supervisor con 3 agentes", el saludo lista las tres especialidades y la pregunta mixta la responden Maleta y Sitios, cada uno con su etiqueta |
| Resultado obtenido | Igual a lo esperado: pytest 92 passed en el clon; el coordinador llama en paralelo a Maleta y Sitios (A2A PERMITIDO en ambos a las 21:08:43) y el bot entrega la respuesta combinada. Captura: `T16-LOCAL-07-clon-nuevo-varios-agentes.png` |
| Observaciones | Sin pasos no documentados. ID de Telegram reemplazado por <ID-de-Patricio>. La parte de Sitios lista los lugares; sus horarios y precios dependen de cómo resume la respuesta el agente de Cristian |

```
# Bot
[telegram 2026-11-23 21:08:12] chat <ID-de-Patricio> · usuario <ID-de-Patricio> · agente: ninguno · respuesta: ¡Hola! Puedo ayudarte con: - Entrenamiento: Explica la anatomía y función de los músculos y arma rutinas de gimnasio con...
[telegram 2026-11-23 21:08:46] chat <ID-de-Patricio> · usuario <ID-de-Patricio> · agente: Agente de Maleta de Dani, Agente de cristian · respuesta: [Agente de Maleta de Dani] Aquí tienes la lista completa de equipaje para tu viaje a Pucón por 3 días en invierno: **Rop...
# Coordinador
[acceso 2026-11-23 21:08:12] Coordinador POST /chat desde 127.0.0.1: PERMITIDO
[chat] conversación <ID-de-Patricio> -> agente: ninguno
[acceso 2026-11-23 21:08:41] Coordinador POST /chat desde 127.0.0.1: PERMITIDO
[chat] conversación <ID-de-Patricio> -> agente: Agente de Maleta de Dani, Agente de cristian
# Agentes (A2A desde el coordinador)
[acceso 2026-11-23 21:08:43] Agente de Maleta de Dani POST / desde 127.0.0.1: PERMITIDO
[acceso 2026-11-23 21:08:43] Agente de cristian POST / desde 127.0.0.1: PERMITIDO
```
