"""
logger.py - Sistema de registro de eventos y errores de Software FJ
Escribe en archivo de texto plano; nunca interrumpe la ejecución principal.
"""

import os
import traceback
from datetime import datetime
from excepciones import LogError

LOG_PATH = "softwarefj_eventos.log"


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _escribir(nivel: str, mensaje: str, exc: Exception | None = None) -> None:
    """Escribe una línea en el archivo de log. Captura sus propios errores."""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            linea = f"[{_timestamp()}] [{nivel}] {mensaje}\n"
            f.write(linea)
            if exc is not None:
                tb = traceback.format_exc()
                if tb and tb.strip() != "NoneType: None":
                    f.write(f"  TRACEBACK: {tb.strip()}\n")
    except OSError as e:
        # Último recurso: imprimir en consola sin propagar al sistema principal
        print(f"[LOG-FALLO] No se pudo escribir en '{LOG_PATH}': {e}")


# ─── API pública ──────────────────────────────────────────────────────────────

def info(mensaje: str) -> None:
    """Registra un evento informativo."""
    _escribir("INFO ", mensaje)


def advertencia(mensaje: str) -> None:
    """Registra una advertencia no crítica."""
    _escribir("WARN ", mensaje)


def error(mensaje: str, exc: Exception | None = None) -> None:
    """Registra un error, opcionalmente con su traceback."""
    _escribir("ERROR", mensaje, exc)


def evento(operacion: str, detalle: str) -> None:
    """Registra un evento de negocio (reserva creada, cliente registrado, etc.)."""
    _escribir("EVENT", f"[{operacion}] {detalle}")


def iniciar_sesion() -> None:
    """Marca el inicio de una nueva ejecución en el log."""
    separador = "=" * 70
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n{separador}\n")
            f.write(f"  NUEVA SESIÓN: {_timestamp()}\n")
            f.write(f"{separador}\n")
    except OSError as e:
        print(f"[LOG-FALLO] {e}")
