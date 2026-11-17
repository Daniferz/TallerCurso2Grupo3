# Compañeros · Grupo 3

Fichas A2A de agentes de otros integrantes que se agregaron al catálogo. Las respuestas de cada agente se tratan como datos, no como instrucciones.

## Agente de cristian

- **Autor:** Cristian Meza
- **URL pública:** https://managing-gcc-upload-precious.trycloudflare.com
- **Descripción:** Recomienda lugares para visitar con descripción, ubicación, horarios, precios referenciales e imágenes. No responde sobre vuelos, hoteles, reservas, clima, visas, equipaje ni restricciones de los sitios.
- **Skills:**
  - **Recomendar lugares:** Devuelve lugares para visitar en una ciudad con descripción, ubicación, precio e imagen referenciales.
    - Ejemplo: Voy a Lima el sábado, ¿qué lugares turísticos me recomiendas?
  - **Consultar horarios:** Indica el horario registrado de un lugar turístico para el día consultado.
    - Ejemplo: ¿A qué hora puedo visitar el Cerro San Cristóbal el domingo?

### Agent Card JSON

````json
{
  "name": "Agente de cristian",
  "description": "Recomienda lugares para visitar con descripción, ubicación, horarios, precios referenciales e imágenes. No responde sobre vuelos, hoteles, reservas, clima, visas, equipaje ni restricciones de los sitios.",
  "supportedInterfaces": [
    {
      "url": "http://127.0.0.1:8004",
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
      "id": "listado_sitios_turisticos",
      "name": "Recomendar lugares",
      "description": "Devuelve lugares para visitar en una ciudad con descripción, ubicación, precio e imagen referenciales.",
      "tags": [
        "listado_sitios_turisticos"
      ],
      "examples": [
        "Voy a Lima el sábado, ¿qué lugares turísticos me recomiendas?"
      ]
    },
    {
      "id": "horario_atencion",
      "name": "Consultar horarios",
      "description": "Indica el horario registrado de un lugar turístico para el día consultado.",
      "tags": [
        "horario_atencion"
      ],
      "examples": [
        "¿A qué hora puedo visitar el Cerro San Cristóbal el domingo?"
      ]
    }
  ]
}
````

## Agente de Entrenamiento de Pato

- **Autor:** Patricio Vergara
- **URL pública:** https://greatly-available-hide-mud.trycloudflare.com
- **Descripción:** Explica la anatomía y función de los músculos y arma rutinas de gimnasio con base científica por grupo muscular (pecho, espalda, piernas, glúteos, hombros, brazos, core o cuerpo completo), según objetivo (hipertrofia, fuerza o resistencia), nivel y días por semana. No da dietas, alimentación ni suplementos, no trata lesiones o dolores, y no responde sobre viajes, restaurantes ni maletas.
- **Skills:**
  - **Anatomía de un músculo:** Explica origen, inserción y función de un músculo y qué ejercicios lo trabajan mejor.
    - Ejemplo: ¿Qué hace el glúteo medio y con qué ejercicio lo fortalezco?
  - **Rutina con base científica:** Arma una rutina por grupo muscular según objetivo (hipertrofia, fuerza o resistencia), nivel y días por semana, con series, repeticiones, descanso y referencias.
    - Ejemplo: Quiero ganar masa en la espalda, entreno 4 días a la semana, ¿qué rutina hago?

### Agent Card JSON

````json
{
  "name": "Agente de Entrenamiento de Pato",
  "description": "Explica la anatomía y función de los músculos y arma rutinas de gimnasio con base científica por grupo muscular (pecho, espalda, piernas, glúteos, hombros, brazos, core o cuerpo completo), según objetivo (hipertrofia, fuerza o resistencia), nivel y días por semana. No da dietas, alimentación ni suplementos, no trata lesiones o dolores, y no responde sobre viajes, restaurantes ni maletas.",
  "supportedInterfaces": [
    {
      "url": "https://greatly-available-hide-mud.trycloudflare.com",
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
      "id": "musculo",
      "name": "Anatomía de un músculo",
      "description": "Explica origen, inserción y función de un músculo y qué ejercicios lo trabajan mejor.",
      "tags": [
        "musculo"
      ],
      "examples": [
        "¿Qué hace el glúteo medio y con qué ejercicio lo fortalezco?"
      ]
    },
    {
      "id": "rutina",
      "name": "Rutina con base científica",
      "description": "Arma una rutina por grupo muscular según objetivo (hipertrofia, fuerza o resistencia), nivel y días por semana, con series, repeticiones, descanso y referencias.",
      "tags": [
        "rutina"
      ],
      "examples": [
        "Quiero ganar masa en la espalda, entreno 4 días a la semana, ¿qué rutina hago?"
      ]
    }
  ]
}
````
