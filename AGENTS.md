# Reglas del proyecto

Estas reglas aplican a todo lo que se genere de aquí en adelante en este proyecto.

1. Todo en español: nombres de archivos, variables, funciones, comentarios y mensajes.
2. Las funciones que usan internet son `async`.
3. Toda llamada por red tiene un timeout explícito.
4. Si algo no responde, el error se muestra en una sola línea entendible, sin stack trace.
5. Cada agente expone una función `responder(texto, context_id)` que devuelve un texto. Es el contrato que todos cumplen.
6. Cada agente se puede correr desde la terminal sin servidor, igual que en el Curso 1: `python main.py {agente} "pregunta"`. Con `--saltos` muestra por qué nodos y herramientas pasó; con `--diagrama` imprime su estructura en Mermaid sin ejecutarlo.
