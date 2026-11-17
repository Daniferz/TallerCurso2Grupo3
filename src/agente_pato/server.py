"""Servidor A2A del Agente de Entrenamiento de Pato."""

from src.comun.registro import CATALOGO
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .graph import responder


agente = CATALOGO["pato"]

tarjeta = crear_tarjeta(
    agente.nombre,
    agente.descripcion,
    agente.url,
    [
        (
            "musculo",
            "Anatomía de un músculo",
            "Explica origen, inserción y función de un músculo y qué ejercicios lo trabajan mejor.",
            "¿Qué hace el glúteo medio y con qué ejercicio lo fortalezco?",
        ),
        (
            "rutina",
            "Rutina con base científica",
            "Arma una rutina por grupo muscular según objetivo (hipertrofia, fuerza o resistencia), nivel y días por semana, con series, repeticiones, descanso y referencias.",
            "Quiero ganar masa en la espalda, entreno 4 días a la semana, ¿qué rutina hago?",
        ),
    ],
)

app = crear_app(tarjeta, responder)
