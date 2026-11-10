# Evidencias · Agente Cristian

## 01 · Saltos

### Pregunta del tema

Consulta: `¿Qué sitios turísticos puedo visitar en Lima el sábado?`

La ejecución muestra la herramienta `listado_sitios_turisticos`:

![Saltos de una consulta turística](evidencias/01-saltos.png)

### Pregunta fuera del tema

Consulta: `¿Qué vuelos hay de Lima a Bogotá?`

El agente rechaza la consulta porque los vuelos corresponden a otro agente y no llama ninguna herramienta turística. La misma captura muestra ambos casos.

## 02 · Diagrama

Salida de `python main.py cristian "" --diagrama`:

![Diagrama del agente Cristian](evidencias/02-diagrama.png)

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
    __start__([<p>__start__</p>]):::first
    model(model)
    tools(tools)
    __end__([<p>__end__</p>]):::last
    __start__ --> model;
    model -.-> __end__;
    model -.-> tools;
    tools --> model;
    classDef default fill:#f2f0ff,line-height:1.2
    classDef first fill-opacity:0
    classDef last fill:#bfb6fc
```
