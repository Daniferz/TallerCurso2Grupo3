# T07 · Sitios turísticos (Cristian) · LOCAL · 2026-11-22

## Cambios revisados

- Se agregaron datos estáticos para Valparaíso (Ascensor Artillería, La Sebastiana y Paseo 21 de Mayo).
- La ficha declara las ciudades cubiertas y el prompt pide la ciudad si falta, sin inventar datos ni alterar los de la herramienta.
- Las pruebas de `tests/test_agente_cristian.py` cubren la guía de Valparaíso.

## Datos faltantes

- **Solicitud:** `¿Qué sitios turísticos puedo visitar?`
- **Obtenido:** `¿A qué ciudad deseas viajar?`
- **Resultado:** PASA. Cristian pregunta la ciudad antes de recomendar lugares.

## Comparación directo vs. coordinador

- **Comando:** `python scripts/comparar_directo_coordinador.py cristian "¿Qué sitios turísticos puedo visitar en Valparaíso?"`
- **Solicitud:** `¿Qué sitios turísticos puedo visitar en Valparaíso?`
- **Resultado:** PASA. La respuesta directa y la del coordinador contienen los mismos sitios y cifras (horarios y precios); el coordinador agrega `[Agente de cristian]` y el motivo de selección.
- **Cifras comparadas:** `08:00`, `20:00`, `500`, `10:00`, `18:00`, `9.500`, `21`.
