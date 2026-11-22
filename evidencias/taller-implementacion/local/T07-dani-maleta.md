# T07 · Maleta (Dani) · LOCAL · 2026-11-22

## Datos faltantes

- **Solicitud:** `maleta para Pucón`
- **Esperado:** pedir días y temporada antes de entregar una lista.
- **Obtenido:** “Para poder darte tu lista de equipaje, ¿podrías indicarme cuántos días durará tu viaje (entre 1 y 30) y en qué temporada irás (invierno, verano o un mes del calendario chileno)?”
- **Resultado:** PASA. No entregó una lista usando datos supuestos.

## Respuesta directa del agente

- **Solicitud:** `¿Qué llevo en la maleta para Pucón 3 días en invierno?`
- **Obtenido:** respuesta real del Agente de Maleta de Dani con las categorías Ropa, Documentos, Tecnología, Botiquín y No te olvides. Incluyó, entre otras cantidades, `4 × ropa interior`, `4 × calcetines` y `3 × primera capa térmica`.
- **Resultado:** respuesta directa completa.

## Comparación directo vs. coordinador

- **Comando:** `python scripts/comparar_directo_coordinador.py dani "¿Qué llevo en la maleta para Pucón 3 días en invierno?"`
- **Problema inicial:** el coordinador no pudo conectar porque la ficha de Dani anunciaba una URL pública antigua en vez de su URL local.
- **Ajuste local:** se dejó `URL_PUBLICA` vacía en `.env`, se reiniciaron los servicios y la ficha pasó a anunciar `http://127.0.0.1:8003`.
- **Resultado final:** PASA. Dani respondió directamente y vía coordinador con las mismas categorías y cantidades (`4 × ropa interior`, `4 × calcetines`, `3 × primera capa térmica`); el coordinador solo agregó `[Agente de Maleta de Dani]` y el motivo de selección. Salida de `scripts/comparar_directo_coordinador.py` del 2026-11-22 13:30.

## Pruebas automatizadas

- `tests/test_agente_dani.py`: 11 pasaron.
- `pytest` completo: 73 pasaron (2 avisos deprecados de FastAPI).
- Ejecutadas con Python 3.12.10 en un entorno virtual temporal, porque el `.venv` del proyecto no tenía una instalación utilizable de pytest.
