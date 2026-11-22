# T06 · Saludo y memoria del coordinador · LOCAL · 2026-11-22

## Saludo

- `tests/test_supervisor.py::test_nodo_saludo_lista_los_tres_agentes_y_que_sabe_cada_uno` recorre el grafo con la entrada `¡Hola!` y un catálogo de prueba.
- Verifica que el saludo liste Maleta, Entrenamiento y Sitios turísticos, con una frase por agente, sin llamar al modelo supervisor.
- `python main.py coordinador --diagrama` muestra el nodo `saludo`.

## Memoria al elegir agente

- `tests/test_supervisor.py::test_memoria_de_seguimiento_se_aísla_por_conversacion_id` simula el supervisor y A2A, sin red ni Gemini.
- Con el mismo `conversacion_id`, `maleta para Pucón 3 días en invierno` seguido de `¿y si son 5 días?` conserva la primera pregunta en el contexto y deriva ambas a Maleta.
- Con otro `conversacion_id`, la segunda pregunta no recibe el historial anterior y no deriva a Maleta por contexto heredado.

## Pruebas

- `pytest tests/test_supervisor.py`: 14 pasaron.
- `pytest`: 71 pasaron (2 avisos deprecados de FastAPI).
