# Ronda de preguntas · Pato (paso 8)

Coordinador de Pato con 3 agentes en el catálogo: Agente de Entrenamiento de Pato (local, puerto 8005), Agente de Maleta de Dani y Agente de Matias (ambos por túnel de Cloudflare, desde otros computadores). Viajes y restaurantes no estaban levantados.

| # | Pregunta | A quién debía ir | A quién fue | Motivo del supervisor | ¿Bien? |
|---|----------|------------------|-------------|-----------------------|--------|
| 1 | "Estoy empezando en el gym, ¿qué rutina hago para piernas?" | Mi agente (Pato) | Agente de Entrenamiento de Pato | "El usuario solicita una rutina de gimnasio enfocada en piernas para un nivel principiante." | ✅ Usó la herramienta `rutina` (hipertrofia, principiante, 3 días) y citó las referencias. |
| 2 | "Organizo una feria infantil de 3 horas desde las 15:00, ¿cómo armo el horario?" | Matías, por el túnel | Agente de Matias | "Crea programas y horarios para ferias infantiles y otros eventos." | ✅ Volvió con `[Agente de Matias]` y un programa de 15:00 a 17:25. |
| 3 | "¿Quién ganó el mundial de 1962?" | Ninguno | ninguno | "Ninguno de los agentes disponibles en el catálogo tiene la capacidad de responder preguntas sobre historia del fútbol." | ✅ Respondió "No tengo un agente para eso" y listó los 3 agentes. |

Las tres preguntas usaron 2 saltos: `supervisor → agente_remoto` (1 y 2) y `supervisor → sin_agente` (3).

## Análisis (borrador para el documento)

**¿Qué ficha eligió mejor el supervisor y qué decía?**
Las dos fichas que se usaron fueron elegidas sin dudar, porque las dos nombran temas concretos. La de Matías dice "programa de actividades y horario de ferias tecnológicas, gastronómicas, culturales o infantiles", y el motivo del supervisor repite casi esas mismas palabras. La mía dice "rutinas de gimnasio por grupo muscular… según objetivo, nivel y días", y el motivo también la parafrasea.

**¿Hubo alguna pregunta que dos agentes podrían responder?**
En esta ronda no. El cruce posible es entre mi agente y el de Dani: una pregunta como "voy 5 días a Pucón, ¿qué ropa llevo para entrenar?" toca maletas y gimnasio. Las dos fichas dicen qué no hacen (la mía "no responde sobre… maletas"), lo que debería ayudar al supervisor a mandarla a Dani.

**¿Algún agente "robó" la pregunta 3?**
No. Ninguna ficha promete fútbol ni historia, así que el supervisor eligió "ninguno". Mi ficha dice "gimnasio" y no "deporte" en general, y eso evitó que me llegara.

**¿Qué cambiaría de mi ficha?**
(Completar después de la ronda con lo que observes; por ejemplo, agregar "no responde sobre otros deportes ni resultados deportivos" para dejar aún más claro el límite.)

## Notas

- La ficha de Dani publicaba una URL antigua del túnel, por lo que sus respuestas no llegaban aunque su ficha sí se descargaba. Se le pidió reiniciar su agente con la URL nueva.
- A Matías al principio se le acabó el crédito de Gemini (error 402); al cambiar la clave, su agente respondió bien.
