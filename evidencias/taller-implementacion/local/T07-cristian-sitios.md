# T07 · Sitios turísticos (Cristian) · LOCAL · 2026-11-19

## Cambios revisados

- Se agregaron datos estáticos para Valparaíso (Ascensor Artillería, La Sebastiana y Paseo 21 de Mayo).
- La ficha declara las ciudades cubiertas y el prompt pide la ciudad si falta, sin inventar datos ni alterar los de la herramienta.
- Las pruebas de `tests/test_agente_cristian.py` cubren la guía de Valparaíso.

## Comparación directo vs. coordinador

- **Solicitud:** `¿Qué sitios turísticos puedo visitar en Valparaíso?`
- **Resultado observado:** la llamada directa falló con HTTP 401 al usar `CLAVE_CRISTIAN`.
- **Conclusión:** esta comparación no pasa todavía. Hay que alinear la clave de prueba y volver a ejecutar la comparación directa vs. coordinador. No se marca esta verificación como hecha.
