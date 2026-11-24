# T15 · LOCAL · Comparación repetida: agente de Pato directo vs. coordinador

| Dato | Registro |
|---|---|
| Entorno y fecha | LOCAL · 2026-11-23 19:34 |
| Solicitud | `python scripts/comparar_directo_coordinador.py pato "..."` con dos preguntas, incluida la que falló el 23-11 a las 09:27 por la saturación de Gemini (503 UNAVAILABLE, "high demand") en `T15-LOCAL-comparaciones-y-acceso-parcial.txt` |
| Resultado esperado | Mismas cifras directo y vía coordinador; el coordinador solo agrega la etiqueta y el motivo |
| Resultado obtenido | Las dos comparaciones PASAN (cifras idénticas) |
| Observaciones | El 503 anterior fue una saturación temporal del proveedor, no una falla del agente; el sistema la informó como error y no como respuesta |

```
### Agente de Entrenamiento de Pato · LOCAL · 2026-11-23 19:34
Pregunta: Estoy empezando en el gimnasio; ¿qué rutina de piernas hago?

**Directo al agente:**

Como no especificaste el objetivo, el nivel ni los días, usé los valores por defecto: hipertrofia, principiante y 3 días por semana. Ante cualquier dolor debes consultar a un profesional.

Rutina de piernas · objetivo hipertrofia · nivel principiante · 3 día(s) disponibles
Músculos trabajados: cuádriceps, isquiotibiales, glúteos y pantorrillas.
Volumen: 10 series semanales para piernas, repartidas en 2 sesión(es) por semana (5 series por sesión).
Ejercicios por sesión:
1. Sentadilla (con barra o goblet): 3 × 8-12
2. Peso muerto rumano: 2 × 8-12
Intensidad: terminar a 2-3 repeticiones del fallo.
Descanso entre series: 2 minutos (1-1,5 en aislamiento).
Progresión: cuando completes todas las series en el tope del rango, sube un poco el peso.
Por qué funciona:
- Más series semanales por músculo producen más hipertrofia (relación dosis-respuesta) — Schoenfeld, Ogborn y Krieger, 2017, J Sports Sci.
- Entrenar cada músculo al menos 2 veces por semana supera a 1 vez; con el mismo volumen semanal la diferencia es pequeña — Schoenfeld, Ogborn y Krieger, 2016, Sports Med; Schoenfeld, Grgic y Krieger, 2019, J Sports Sci.
- Terminar las series a pocas repeticiones del fallo favorece la hipertrofia; llegar siempre al fallo no es necesario — Refalo et al., 2023, Sports Med.
- Sobrecarga progresiva y variables según objetivo y nivel — ACSM, 2009, Progression Models in Resistance Training for Healthy Adults, Med Sci Sports Exerc.

**Vía coordinador:**

[Agente de Entrenamiento de Pato] Como no especificaste los días por semana ni el objetivo, supuse 3 días por semana, nivel principiante y objetivo de hipertrofia. Te recuerdo que ante cualquier dolor debes consultar a un profesional.

Rutina de piernas · objetivo hipertrofia · nivel principiante · 3 día(s) disponibles
Músculos trabajados: cuádriceps, isquiotibiales, glúteos y pantorrillas.
Volumen: 10 series semanales para piernas, repartidas en 2 sesión(es) por semana (5 series por sesión).
Ejercicios por sesión:
1. Sentadilla (con barra o goblet): 3 × 8-12
2. Peso muerto rumano: 2 × 8-12
Intensidad: terminar a 2-3 repeticiones del fallo.
Descanso entre series: 2 minutos (1-1,5 en aislamiento).
Progresión: cuando completes todas las series en el tope del rango, sube un poco el peso.
Por qué funciona:
- Más series semanales por músculo producen más hipertrofia (relación dosis-respuesta) — Schoenfeld, Ogborn y Krieger, 2017, J Sports Sci.
- Entrenar cada músculo al menos 2 veces por semana supera a 1 vez; con el mismo volumen semanal la diferencia es pequeña — Schoenfeld, Ogborn y Krieger, 2016, Sports Med; Schoenfeld, Grgic y Krieger, 2019, J Sports Sci.
- Terminar las series a pocas repeticiones del fallo favorece la hipertrofia; llegar siempre al fallo no es necesario — Refalo et al., 2023, Sports Med.
- Sobrecarga progresiva y variables según objetivo y nivel — ACSM, 2009, Progression Models in Resistance Training for Healthy Adults, Med Sci Sports Exerc.
Motivo de selección: La pregunta trata sobre una rutina de gimnasio para piernas y nivel principiante, lo cual corresponde al Agente de Entrenamiento de Pato.

- Etiqueta [Agente de Entrenamiento de Pato] al inicio: sí
- Cifras directo: 3, 10, 2, 5, 1, 8-12, 2-3, 1-1,5, 2017, 2016, 2019, 2023, 2009
- Cifras vía coordinador: 3, 10, 2, 5, 1, 8-12, 2-3, 1-1,5, 2017, 2016, 2019, 2023, 2009
- Resultado: PASA (mismas cifras, solo cambia la etiqueta)

### Agente de Entrenamiento de Pato · LOCAL · 2026-11-23 19:34
Pregunta: Arma una rutina de pecho para fuerza, 5 días por semana

**Directo al agente:**

Como me pediste una rutina de pecho para fuerza y 5 días por semana, he usado el nivel principiante por defecto. Recuerda que ante cualquier dolor debes consultar a un profesional. Aquí tienes la rutina:

Rutina de pecho · objetivo fuerza · nivel principiante · 5 día(s) disponibles
Músculos trabajados: pectoral mayor, deltoides anterior y tríceps.
Volumen: 12 series semanales para pecho, repartidas en 3 sesión(es) por semana (4 series por sesión).
Ejercicios por sesión:
1. Press de banca (barra o mancuernas): 2 × 5-8
2. Press inclinado con mancuernas: 2 × 5-8
Intensidad: dejar 2-3 repeticiones en reserva y priorizar la técnica.
Descanso entre series: 2-3 minutos.
Progresión: cuando completes todas las series en el tope del rango, sube un poco el peso.
Por qué funciona:
- Cargas altas y bajas dan hipertrofia similar si las series terminan cerca del fallo; las cargas altas ganan en fuerza máxima — Schoenfeld, Grgic, Ogborn y Krieger, 2017, J Strength Cond Res.
- Entrenar cada músculo al menos 2 veces por semana supera a 1 vez; con el mismo volumen semanal la diferencia es pequeña — Schoenfeld, Ogborn y Krieger, 2016, Sports Med; Schoenfeld, Grgic y Krieger, 2019, J Sports Sci.
- Sobrecarga progresiva y variables según objetivo y nivel — ACSM, 2009, Progression Models in Resistance Training for Healthy Adults, Med Sci Sports Exerc.

**Vía coordinador:**

[Agente de Entrenamiento de Pato] Aquí tienes tu rutina basada en evidencia:

Rutina de pecho · objetivo fuerza · nivel principiante · 5 día(s) disponibles
Músculos trabajados: pectoral mayor, deltoides anterior y tríceps.
Volumen: 12 series semanales para pecho, repartidas en 3 sesión(es) por semana (4 series por sesión).
Ejercicios por sesión:
1. Press de banca (barra o mancuernas): 2 × 5-8
2. Press inclinado con mancuernas: 2 × 5-8
Intensidad: dejar 2-3 repeticiones en reserva y priorizar la técnica.
Descanso entre series: 2-3 minutos.
Progresión: cuando completes todas las series en el tope del rango, sube un poco el peso.
Por qué funciona:
- Cargas altas y bajas dan hipertrofia similar si las series terminan cerca del fallo; las cargas altas ganan en fuerza máxima — Schoenfeld, Grgic, Ogborn y Krieger, 2017, J Strength Cond Res.
- Entrenar cada músculo al menos 2 veces por semana supera a 1 vez; con el mismo volumen semanal la diferencia es pequeña — Schoenfeld, Ogborn y Krieger, 2016, Sports Med; Schoenfeld, Grgic y Krieger, 2019, J Sports Sci.
- Sobrecarga progresiva y variables según objetivo y nivel — ACSM, 2009, Progression Models in Resistance Training for Healthy Adults, Med Sci Sports Exerc.

*(Nota: Para el nivel principiante y objetivo de fuerza, los 5 días disponibles se han organizado en 3 sesiones específicas para este grupo muscular, permitiendo el descanso y la recuperación óptimos).* Ante cualquier dolor, te recomiendo consultar a un profesional.
Motivo de selección: La pregunta solicita una rutina de gimnasio basada en objetivos y frecuencia semanal, lo cual corresponde al Agente de Entrenamiento de Pato.

- Etiqueta [Agente de Entrenamiento de Pato] al inicio: sí
- Cifras directo: 5, 12, 3, 4, 1, 2, 5-8, 2-3, 2017, 2016, 2019, 2009
- Cifras vía coordinador: 5, 12, 3, 4, 1, 2, 5-8, 2-3, 2017, 2016, 2019, 2009
- Resultado: PASA (mismas cifras, solo cambia la etiqueta)

```
