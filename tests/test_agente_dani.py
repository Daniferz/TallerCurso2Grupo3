from src.agente_dani.tools import lista_equipaje


def test_lista_equipaje_con_guia_estatica_y_cantidades():
    resultado = lista_equipaje.invoke(
        {"destino": "Punta Arenas", "dias": 5, "temporada": "julio"}
    )

    assert "Ropa:" in resultado
    assert "6 × ropa interior" in resultado
    assert "Documentos:" in resultado
    assert "Tecnología:" in resultado
    assert "Botiquín:" in resultado
    assert "No te olvides:" in resultado


def test_destino_o_temporada_sin_guia_no_inventa():
    resultado = lista_equipaje.invoke(
        {"destino": "Tokio", "dias": 4, "temporada": "otoño"}
    )

    assert resultado == (
        "No tengo una guía estática para ese destino y temporada; "
        "no puedo armar una lista fiable."
    )


def test_dias_invalidos_se_informan_en_una_linea():
    resultado = lista_equipaje.invoke(
        {"destino": "Punta Arenas", "dias": 0, "temporada": "invierno"}
    )

    assert resultado == "La cantidad de días debe estar entre 1 y 30."


def test_grafo_dani_se_compila_sin_invocar_gemini(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.agente_dani.graph import graph

    nodos = set(graph.get_graph().nodes)
    assert {"__start__", "model", "tools", "__end__"}.issubset(nodos)


def test_ficha_a2a_de_dani_tiene_nombre_url_y_skill(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("URL_PUBLICA", "")
    from src.agente_dani.server import tarjeta

    assert tarjeta.name == "Agente de Maleta de Dani"
    assert tarjeta.supported_interfaces[0].url.endswith(":8003")
    assert [skill.id for skill in tarjeta.skills] == ["lista_equipaje"]


def _turno(respuesta_final):
    """Simula un turno con llamada y respuesta de lista_equipaje."""
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

    salida = lista_equipaje.invoke(
        {"destino": "Pucón", "dias": 3, "temporada": "invierno"}
    )
    return salida, [
        HumanMessage(content="¿Qué llevo en la maleta para Pucón 3 días en invierno?"),
        AIMessage(
            content="",
            tool_calls=[{"name": "lista_equipaje", "args": {}, "id": "1"}],
        ),
        ToolMessage(content=salida, name="lista_equipaje", tool_call_id="1"),
        AIMessage(content=respuesta_final),
    ]


def test_respuesta_sin_lista_se_completa_con_la_salida_de_la_herramienta(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.agente_dani.graph import completar_respuesta

    intro = "Aquí tienes tu lista para Pucón, 3 días en invierno."
    salida, mensajes = _turno(intro)
    final = completar_respuesta(mensajes)
    assert final.startswith(intro)
    assert salida in final
    assert "4 × ropa interior" in final
    assert "No te olvides:" in final


def test_respuesta_que_pierde_una_categoria_se_completa(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.agente_dani.graph import completar_respuesta

    parcial = (
        "Para Pucón, 3 días en invierno:\n\n"
        "Ropa:\n- 4 × ropa interior\n- 4 × calcetines\n- polar o suéter abrigado"
    )
    salida, mensajes = _turno(parcial)
    final = completar_respuesta(mensajes)
    assert final.startswith(parcial)
    assert salida in final
    assert "Documentos:" in final and "Botiquín:" in final


def test_respuesta_completa_con_otro_formato_no_se_duplica(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from langchain_core.messages import AIMessage
    from src.agente_dani.graph import completar_respuesta

    salida, mensajes = _turno("")
    completa = salida.replace("\n- ", "\n* ").replace("×", "x")
    mensajes[-1] = AIMessage(content=completa)
    assert completar_respuesta(mensajes) == completa


def test_sin_herramienta_en_el_turno_no_se_agrega_nada(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from langchain_core.messages import AIMessage, HumanMessage
    from src.agente_dani.graph import completar_respuesta

    _, anterior = _turno("Aquí tienes tu lista.")
    mensajes = anterior + [
        HumanMessage(content="¿Y si son 5 días?"),
        AIMessage(content="Para 5 días te sugiero sumar una prenda más de abrigo."),
    ]
    assert completar_respuesta(mensajes) == (
        "Para 5 días te sugiero sumar una prenda más de abrigo."
    )


def test_pedir_datos_faltantes_no_agrega_lista_basada_en_supuestos(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.agente_dani.graph import completar_respuesta

    pregunta = "¿Cuántos días viajarás y en qué temporada?"
    _, mensajes = _turno(pregunta)
    assert completar_respuesta(mensajes) == pregunta


def test_prompt_pide_datos_clave_y_no_inventa_memoria():
    from src.agente_dani.prompts import SYSTEM_PROMPT

    assert (
        "si falta el destino, los días o la temporada, no entregues una lista ni supongas esos datos"
        in SYSTEM_PROMPT
    )
    assert "invierno, verano o un mes del calendario chileno" in SYSTEM_PROMPT
    assert "entre 1 y 30" in SYSTEM_PROMPT
    assert "llama la herramienta solo cuando tengas los tres datos" in SYSTEM_PROMPT
    assert "Solo di que recuerdas algo" in SYSTEM_PROMPT
    assert "No la resumas en una frase" in SYSTEM_PROMPT
