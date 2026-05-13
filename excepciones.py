"""
excepciones.py - Excepciones personalizadas del sistema Software FJ
Todas las excepciones del dominio del negocio se definen aquí.
"""


class SistemaFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


# ─── Excepciones de Cliente ───────────────────────────────────────────────────

class ClienteError(SistemaFJError):
    """Error relacionado con operaciones de clientes."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLIENTE")


class ClienteYaExisteError(ClienteError):
    """Se intenta registrar un cliente con ID duplicado."""
    def __init__(self, cliente_id: str):
        super().__init__(f"El cliente con ID '{cliente_id}' ya está registrado.")
        self.cliente_id = cliente_id


class ClienteNoEncontradoError(ClienteError):
    """Se busca un cliente que no existe."""
    def __init__(self, cliente_id: str):
        super().__init__(f"No se encontró ningún cliente con ID '{cliente_id}'.")
        self.cliente_id = cliente_id


class DatosClienteInvalidosError(ClienteError):
    """Los datos proporcionados para un cliente no pasan validación."""
    def __init__(self, campo: str, valor, razon: str):
        super().__init__(
            f"Dato inválido en campo '{campo}' (valor='{valor}'): {razon}"
        )
        self.campo = campo
        self.valor = valor


# ─── Excepciones de Servicio ──────────────────────────────────────────────────

class ServicioError(SistemaFJError):
    """Error relacionado con operaciones de servicios."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SERVICIO")


class ServicioNoDisponibleError(ServicioError):
    """El servicio existe pero no está disponible para reserva."""
    def __init__(self, servicio_id: str):
        super().__init__(f"El servicio '{servicio_id}' no está disponible actualmente.")
        self.servicio_id = servicio_id


class ServicioNoEncontradoError(ServicioError):
    """Se referencia un servicio que no existe en el catálogo."""
    def __init__(self, servicio_id: str):
        super().__init__(f"El servicio '{servicio_id}' no existe en el catálogo.")
        self.servicio_id = servicio_id


class ParametroServicioInvalidoError(ServicioError):
    """Un parámetro requerido por el servicio es inválido o falta."""
    def __init__(self, parametro: str, razon: str):
        super().__init__(f"Parámetro de servicio inválido '{parametro}': {razon}")
        self.parametro = parametro


# ─── Excepciones de Reserva ───────────────────────────────────────────────────

class ReservaError(SistemaFJError):
    """Error relacionado con operaciones de reservas."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RESERVA")


class ReservaYaConfirmadaError(ReservaError):
    """Se intenta confirmar una reserva que ya estaba confirmada."""
    def __init__(self, reserva_id: str):
        super().__init__(f"La reserva '{reserva_id}' ya fue confirmada previamente.")


class ReservaCanceladaError(ReservaError):
    """Se intenta operar sobre una reserva cancelada."""
    def __init__(self, reserva_id: str):
        super().__init__(f"La reserva '{reserva_id}' fue cancelada y no puede modificarse.")


class DuracionInvalidaError(ReservaError):
    """La duración especificada para una reserva no es válida."""
    def __init__(self, duracion, minimo: float = 0.5):
        super().__init__(
            f"Duración inválida '{duracion}' horas. El mínimo permitido es {minimo} hora(s)."
        )


class CostoInconsistenteError(ReservaError):
    """El cálculo de costo produjo un resultado inconsistente."""
    def __init__(self, detalle: str):
        super().__init__(f"Cálculo de costo inconsistente: {detalle}")


# ─── Excepciones de Sistema ───────────────────────────────────────────────────

class LogError(SistemaFJError):
    """Error al intentar escribir en el archivo de logs."""
    def __init__(self, detalle: str):
        super().__init__(f"No se pudo escribir en el log: {detalle}", "ERR_LOG")


class OperacionNoPermitidaError(SistemaFJError):
    """Se intenta realizar una operación que el sistema no permite."""
    def __init__(self, operacion: str, razon: str):
        super().__init__(
            f"Operación no permitida '{operacion}': {razon}", "ERR_OPERACION"
        )
