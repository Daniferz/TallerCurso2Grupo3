# T15 · LOCAL · Sitios, saludo e inicio de memoria

- **Fecha:** 2026-11-23
- **Solicitudes visibles:** sitios turísticos en Valparaíso; “Hola”; inicio de consulta de Maleta para Pucón en invierno.
- **Esperado:** derivar Valparaíso a Sitios, listar las especialidades ante el saludo e iniciar un hilo de Maleta.
- **Obtenido:** la respuesta nombra al Agente de Sitios, el saludo enumera las especialidades y Maleta responde a la consulta inicial.
- **Observaciones:** captura recortada para ocultar contactos; el seguimiento del mismo hilo está en `T15-LOCAL-03-memoria-seguimiento.jpg`.
- **Corrección (revisión final, 2026-11-23):** en esta captura el saludo rotula al Agente de Sitios como "Maleta" (aparece "Maleta" dos veces). La causa era que el saludo buscaba "equipaje" en toda la ficha, y la de Sitios dice que *no* responde sobre equipaje. Se corrigió en `_nombre_para_saludo` (`src/coordinador/graph.py`): ahora usa el nombre del agente y solo la primera frase de la ficha. Verificado en local: el saludo lista Entrenamiento, Maleta y Sitios turísticos una vez cada uno.
- **Captura:** `T15-LOCAL-04-sitios-saludo-memoria.jpg`
