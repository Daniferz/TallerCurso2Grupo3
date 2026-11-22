"""Bot de Telegram: usuarios permitidos, mensajes sin texto, fallas y token fuera del log."""

import asyncio

import pytest

from src.canal import telegram


TOKEN = "123456:TOKEN-SECRETO-DE-PRUEBA"
PERMITIDO = 111
OTRO = 999


@pytest.fixture
def bot(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", TOKEN)
    monkeypatch.setenv("TELEGRAM_USUARIOS_PERMITIDOS", f"{PERMITIDO}, abc,")
    enviados, consultas = [], []

    async def enviar_mensaje(http, chat_id, texto):
        enviados.append((chat_id, texto))

    async def llamar_telegram(http, metodo, datos, espera=0):
        return True

    async def preguntar_coordinador(http, texto, conversacion_id):
        consultas.append((texto, conversacion_id))
        return {"respuesta": f"[Agente de prueba] {texto}", "agente": "Agente de prueba"}

    monkeypatch.setattr(telegram, "enviar_mensaje", enviar_mensaje)
    monkeypatch.setattr(telegram, "llamar_telegram", llamar_telegram)
    monkeypatch.setattr(telegram, "preguntar_coordinador", preguntar_coordinador)
    return enviados, consultas


def _update(usuario, chat=500, **mensaje):
    return {"update_id": 1, "message": {"chat": {"id": chat}, "from": {"id": usuario}, **mensaje}}


def test_lee_usuarios_permitidos_ignorando_basura(bot):
    assert telegram.usuarios_permitidos() == {PERMITIDO}


def test_usuario_permitido_recibe_la_respuesta_con_chat_id_como_conversacion(bot, capsys):
    enviados, consultas = bot
    asyncio.run(telegram.atender(None, _update(PERMITIDO, text="rutina de pecho")))
    assert consultas == [("rutina de pecho", "500")]
    assert enviados == [(500, "[Agente de prueba] rutina de pecho")]
    log = capsys.readouterr().out
    assert "chat 500" in log and "agente: Agente de prueba" in log
    assert TOKEN not in log


def test_usuario_no_permitido_ve_su_id_y_no_se_llama_al_coordinador(bot, capsys):
    enviados, consultas = bot
    asyncio.run(telegram.atender(None, _update(OTRO, text="hola")))
    assert consultas == []
    assert len(enviados) == 1
    assert "No tienes acceso" in enviados[0][1]
    assert f"Tu ID es {OTRO}" in enviados[0][1]
    assert "RECHAZADO" in capsys.readouterr().out


def test_foto_o_sticker_recibe_no_puedo_leer(bot):
    enviados, consultas = bot
    asyncio.run(telegram.atender(None, _update(PERMITIDO, photo=[{"file_id": "x"}])))
    asyncio.run(telegram.atender(None, _update(PERMITIDO, sticker={"file_id": "y"})))
    assert consultas == []
    assert [texto for _, texto in enviados] == [telegram.MENSAJE_NO_TEXTO] * 2
    assert telegram.MENSAJE_NO_TEXTO.startswith("No puedo leer ese tipo de mensaje")


def test_coordinador_caido_da_mensaje_claro_sin_detalles(bot, monkeypatch, capsys):
    enviados, _ = bot

    async def preguntar_coordinador(http, texto, conversacion_id):
        raise telegram.ErrorCoordinador("no se pudo conectar con el coordinador en http://127.0.0.1:8002/chat")

    monkeypatch.setattr(telegram, "preguntar_coordinador", preguntar_coordinador)
    asyncio.run(telegram.atender(None, _update(PERMITIDO, text="hola")))
    assert enviados == [(500, telegram.MENSAJE_FALLA)]
    assert "127.0.0.1" not in telegram.MENSAJE_FALLA
    assert "no se pudo conectar" in capsys.readouterr().out


def test_start_da_bienvenida_sin_llamar_al_coordinador(bot):
    enviados, consultas = bot
    asyncio.run(telegram.atender(None, _update(PERMITIDO, text="/start")))
    assert consultas == []
    assert enviados == [(500, telegram.MENSAJE_BIENVENIDA)]


def test_el_token_nunca_aparece_en_el_log(bot, capsys):
    telegram.registrar(f"error en https://api.telegram.org/bot{TOKEN}/getUpdates")
    salida = capsys.readouterr().out
    assert TOKEN not in salida
    assert "<token>" in salida


def test_mensajes_largos_se_parten(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", TOKEN)
    trozos = []

    async def llamar_telegram(http, metodo, datos, espera=0):
        trozos.append(datos["text"])

    monkeypatch.setattr(telegram, "llamar_telegram", llamar_telegram)
    asyncio.run(telegram.enviar_mensaje(None, 1, "a" * 9000))
    assert [len(t) for t in trozos] == [4000, 4000, 1000]


def test_aviso_al_chat_se_envia_una_vez_por_conversacion(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", TOKEN)
    monkeypatch.setenv("TELEGRAM_CHAT_AVISO", "-100123")
    monkeypatch.setenv("AVISO_MINUTOS", "10")
    telegram._ultimo_aviso.clear()
    envios = []

    async def llamar(http, metodo, datos, espera=0):
        envios.append((metodo, datos))
        return True

    monkeypatch.setattr(telegram, "llamar_telegram", llamar)
    assert asyncio.run(telegram.avisar_chat("¿Quién ganó?", "hilo-1"))
    assert not asyncio.run(telegram.avisar_chat("¿Y ahora?", "hilo-1"))
    assert asyncio.run(telegram.avisar_chat("¿Quién ganó?", "hilo-2"))
    assert len(envios) == 2
    assert envios[0][0] == "sendMessage"
    assert "hilo-1" in envios[0][1]["text"]
