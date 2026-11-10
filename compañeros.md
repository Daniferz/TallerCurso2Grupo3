# Compañeros sumados al coordinador de Pato

Agentes de otros computadores agregados a `URLS_AGENTES` (paso 7, 9 de noviembre de 2026). Las URLs son temporales: cambian cada vez que se reinicia el túnel.

## Agente de Matias

- **Autor:** Matías
- **Skill:** Programa y horarios de ferias
- **URL:** https://prepaid-portable-jaguar-increased.trycloudflare.com

```json
{
  "name": "Agente de Matias",
  "description": "Arma el programa de actividades y el horario de ferias tecnológicas, gastronómicas, culturales o infantiles de 30 minutos a 8 horas, para público familiar, adulto o estudiantes. No responde sobre lugares ni capacidad, comida ni costos, y no reserva ni confirma el programa definitivo: entrega solo propuestas.",
  "supportedInterfaces": [
    {
      "url": "https://prepaid-portable-jaguar-increased.trycloudflare.com",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "version": "1.0.0",
  "capabilities": {
    "streaming": false
  },
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain"
  ],
  "skills": [
    {
      "id": "armar_programa",
      "name": "Armar programa de feria",
      "description": "Propone las actividades que caben en el tiempo disponible, con su hora de inicio y término, según tipo de evento, público y hora de inicio.",
      "tags": [
        "armar_programa"
      ],
      "examples": [
        "Necesito armar el programa de una feria infantil de 3 horas que parta a las 15:00."
      ],
      "inputModes": [
        "text/plain"
      ],
      "outputModes": [
        "text/plain"
      ]
    }
  ]
}
```

## Agente de Maleta de Dani

- **Autor:** Dani
- **Skill:** Experta en maletas: qué llevar según destino, días y temporada
- **URL:** https://absent-offerings-realized-envelope.trycloudflare.com

```json
{
  "name": "Agente de Maleta de Dani",
  "description": "Prepara listas de equipaje con ropa, documentos, tecnología y botiquín para Punta Arenas, Pucón e Iquique, según los días y la temporada. No busca ni compara vuelos, hoteles o precios, ni informa clima, visas o políticas de equipaje de aerolíneas.",
  "supportedInterfaces": [
    {
      "url": "https://starting-pics-infrastructure-persian.trycloudflare.com",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "version": "1.0.0",
  "capabilities": {
    "streaming": false
  },
  "defaultInputModes": [
    "text/plain"
  ],
  "defaultOutputModes": [
    "text/plain"
  ],
  "skills": [
    {
      "id": "lista_equipaje",
      "name": "Lista de equipaje",
      "description": "Arma una lista por categorías para Punta Arenas, Pucón o Iquique, según los días y la temporada, usando guías estáticas.",
      "tags": [
        "lista_equipaje"
      ],
      "examples": [
        "Voy cinco días a Punta Arenas en julio, ¿qué debería llevar?"
      ]
    }
  ]
}
```
