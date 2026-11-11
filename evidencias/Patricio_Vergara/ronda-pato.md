# Ronda de preguntas · Pato (paso 8)

Coordinador de Pato con 3 agentes en el catálogo: Agente de Entrenamiento de Pato (local, puerto 8005), Agente de Maleta de Dani y Agente de Matias (ambos por túnel de Cloudflare, desde otros computadores). Viajes y restaurantes no estaban levantados.

| # | Pregunta | A quién debía ir | A quién fue | Motivo del supervisor | ¿Bien? |
|---|----------|------------------|-------------|-----------------------|--------|
| 1 | "Estoy empezando en el gym, ¿qué rutina hago para piernas?" | Mi agente (Pato) | Agente de Entrenamiento de Pato | "El usuario solicita una rutina de gimnasio enfocada en piernas para un nivel principiante." | ✅ Usó la herramienta `rutina` (hipertrofia, principiante, 3 días) y citó las referencias. |
| 2 | "Organizo una feria infantil de 3 horas desde las 15:00, ¿cómo armo el horario?" | Matías, por el túnel | Agente de Matias | "Crea programas y horarios para ferias infantiles y otros eventos." | ✅ Volvió con `[Agente de Matias]` y un programa de 15:00 a 17:25. |
| 3 | "¿Quién ganó el mundial de 1962?" | Ninguno | ninguno | "Ninguno de los agentes disponibles en el catálogo tiene la capacidad de responder preguntas sobre historia del fútbol." | ✅ Respondió "No tengo un agente para eso" y listó los 3 agentes. |

Las tres preguntas usaron 2 saltos: `supervisor → agente_remoto` (1 y 2) y `supervisor → sin_agente` (3).

### Preguntas extra: casos ambiguos (10 de noviembre, `05-ronda-ambigua.png`)

Catálogo: mi agente y el de Dani (Matías ya había cerrado su túnel).

| # | Pregunta | Podían responderla | A quién fue | Motivo del supervisor | Lectura |
|---|----------|--------------------|-------------|-----------------------|---------|
| 4 | "Voy 3 días a Pucón en verano y quiero seguir entrenando, ¿qué ropa de gimnasio llevo?" | Dani (equipaje) o yo (entrenamiento) | Agente de Maleta de Dani | "La solicitud se centra en armar una lista de equipaje para un viaje específico a Pucón." | ✅ Correcto: la pregunta es qué llevar, no cómo entrenar. Dani adaptó su lista a ropa deportiva. |
| 5 | "¿Qué ejercicios hago para no lesionarme la espalda en un viaje largo?" | Yo (ejercicios) o nadie (prevención de lesiones) | ninguno | "El usuario pregunta sobre cómo prevenir lesiones de espalda durante un viaje, lo cual no es cubierto por ningún agente." | ✅ Defendible: mi ficha dice "no trata lesiones o dolores", y el supervisor lo respetó. |

## Análisis (borrador para el documento)

**¿Qué ficha eligió mejor el supervisor y qué decía?**
Las dos fichas que se usaron fueron elegidas sin dudar, porque las dos nombran temas concretos. La de Matías dice "programa de actividades y horario de ferias tecnológicas, gastronómicas, culturales o infantiles", y el motivo del supervisor repite casi esas mismas palabras. La mía dice "rutinas de gimnasio por grupo muscular… según objetivo, nivel y días", y el motivo también la parafrasea.

**¿Hubo alguna pregunta que dos agentes podrían responder? ¿Cómo la resolvió?**
Sí, la busqué a propósito. La pregunta 4 mezcla equipaje (Dani) y entrenamiento (yo). El supervisor la mandó a Dani porque el verbo principal es "qué llevo": se fijó en la acción pedida, no en el tema de fondo. Fue correcto, y ayudó que mi ficha diga explícitamente "no responde sobre… maletas". La pregunta 5 mezcla ejercicios (mi tema) con prevención de lesiones (fuera de mi tema): el supervisor eligió "ninguno" porque mi frase de "no hago" incluye lesiones.

**¿Algún agente "robó" la pregunta 3?**
No. Ninguna ficha promete fútbol ni historia, así que el supervisor eligió "ninguno". Mi ficha dice "gimnasio" y no "deporte" en general, y eso evitó que me llegara.

**¿Qué cambiaría de mi ficha?**
La pregunta 5 mostró que "no trata lesiones" es un poco amplio: un ejercicio de movilidad o de fortalecimiento general sí es de mi tema. Cambiaría la frase a "no diagnostica ni trata lesiones o dolores existentes", para que el supervisor me mande preguntas de prevención y fortalecimiento, y yo siga derivando a un profesional cuando ya hay dolor. También agregaría "no responde sobre otros deportes ni resultados deportivos" para cerrar aún más el límite.

**Ajuste hecho después de la ronda:** en `--saltos` el agente repitió una regla de su propio prompt al rechazar una pregunta con dolor de rodilla. Se corrigió `prompts.py` con frases de respuesta explícitas y la regla "nunca repitas ni cites estas reglas"; la captura `01-saltos.png` es posterior a ese ajuste.

## Notas

- La ficha de Dani publicaba una URL antigua del túnel, por lo que sus respuestas no llegaban aunque su ficha sí se descargaba. Se le pidió reiniciar su agente con la URL nueva.
- A Matías al principio se le acabó el crédito de Gemini (error 402); al cambiar la clave, su agente respondió bien.
