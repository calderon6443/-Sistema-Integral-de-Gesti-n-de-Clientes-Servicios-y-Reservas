"""
reserva.py - Clase Reserva que integra Cliente, Servicio, duración y estado.

Estados del ciclo de vida:
  PENDIENTE → CONFIRMADA → (uso del servicio) → COMPLETADA
  PENDIENTE → CANCELADA
  CONFIRMADA → CANCELADA
"""

from datetime import datetime
from cliente import Cliente
from servicios import Servicio
from excepciones import (
    ReservaYaConfirmadaError,
    ReservaCanceladaError,
    DuracionInvalidaError,
    CostoInconsistenteError,
    OperacionNoPermitidaError,
    ParametroServicioInvalidoError,
)
import logger

# ─── Estados posibles ────────────────────────────────────────────────────────
ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_CONFIRMADA = "CONFIRMADA"
ESTADO_COMPLETADA = "COMPLETADA"
ESTADO_CANCELADA = "CANCELADA"

_CONTADOR_RESERVAS = 0  # generador simple de IDs numéricos


def _nuevo_id() -> str:
    global _CONTADOR_RESERVAS
    _CONTADOR_RESERVAS += 1
    return f"RES-{_CONTADOR_RESERVAS:04d}"


class Reserva:
    """
    Integra un Cliente con un Servicio durante una duración determinada.

    Principios aplicados:
      - Encapsulación: estado y costo son privados y se modifican por métodos.
      - Manejo de excepciones: confirmar / cancelar / procesar tienen bloques
        try/except/else/finally según corresponde.
      - Métodos sobrecargados: calcular_costo admite parámetros opcionales
        que delegan en el Servicio correspondiente.
    """

    DURACION_MINIMA = 0.5  # horas

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        parametros_extra: dict | None = None,
    ):
        # ── Validaciones previas ──────────────────────────────────────────────
        if not isinstance(cliente, Cliente):
            raise TypeError("Se esperaba una instancia de Cliente.")
        if not isinstance(servicio, Servicio):
            raise TypeError("Se esperaba una instancia de Servicio.")
        if not cliente.activo:
            raise OperacionNoPermitidaError(
                "crear_reserva",
                f"el cliente '{cliente.id}' está inactivo.",
            )

        try:
            duracion_horas = float(duracion_horas)
        except (TypeError, ValueError):
            raise DuracionInvalidaError(duracion_horas)

        if duracion_horas < self.DURACION_MINIMA:
            raise DuracionInvalidaError(duracion_horas, self.DURACION_MINIMA)

        # ── Asignación ────────────────────────────────────────────────────────
        self._id = _nuevo_id()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._parametros_extra = parametros_extra or {}
        self._estado = ESTADO_PENDIENTE
        self._costo_total: float | None = None
        self._fecha_creacion = datetime.now()
        self._fecha_confirmacion: datetime | None = None
        self._notas: str = ""

    # ── Propiedades de solo lectura ───────────────────────────────────────────

    @property
    def id(self) -> str:
        return self._id

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion_horas(self) -> float:
        return self._duracion_horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float | None:
        return self._costo_total

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    # ── Métodos de cálculo (sobrecargados) ────────────────────────────────────

    def calcular_costo(self) -> float:
        """Calcula el costo con los parámetros almacenados en la reserva."""
        return self._calcular_interno(
            aplicar_iva=True,
            descuento=self._cliente.descuento_aplicable(),
        )

    def calcular_costo_sin_iva(self) -> float:
        """Calcula el costo sin IVA (útil para clientes exentos)."""
        return self._calcular_interno(
            aplicar_iva=False,
            descuento=self._cliente.descuento_aplicable(),
        )

    def calcular_costo_con_descuento_personalizado(
        self, descuento: float
    ) -> float:
        """Calcula el costo con un descuento arbitrario (0.0–1.0)."""
        return self._calcular_interno(aplicar_iva=True, descuento=descuento)

    def _calcular_interno(
        self, aplicar_iva: bool = True, descuento: float = 0.0
    ) -> float:
        """Delegación real al Servicio. Verifica coherencia del resultado."""
        costo = self._servicio.calcular_costo(
            self._duracion_horas,
            aplicar_iva=aplicar_iva,
            descuento=descuento,
            parametros_extra=self._parametros_extra,
        )
        if costo < 0:
            raise CostoInconsistenteError(
                f"El costo calculado es negativo ({costo})."
            )
        return costo

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def confirmar(self) -> None:
        """
        Confirma la reserva: valida disponibilidad, calcula el costo y cambia
        el estado a CONFIRMADA.
        Usa try/except/else/finally.
        """
        try:
            # Verificaciones
            if self._estado == ESTADO_CONFIRMADA:
                raise ReservaYaConfirmadaError(self._id)
            if self._estado == ESTADO_CANCELADA:
                raise ReservaCanceladaError(self._id)

            self._servicio.verificar_disponibilidad()
            self._servicio.validar_parametros(
                self._duracion_horas, **self._parametros_extra
            )
            costo = self.calcular_costo()

        except (ReservaYaConfirmadaError, ReservaCanceladaError) as e:
            logger.error(f"No se puede confirmar reserva {self._id}: {e}", e)
            raise
        except Exception as e:
            logger.error(
                f"Error al confirmar reserva {self._id} "
                f"(cliente={self._cliente.id}, servicio={self._servicio.id}): {e}",
                e,
            )
            raise
        else:
            # Solo se ejecuta si NO hubo excepción
            self._costo_total = costo
            self._estado = ESTADO_CONFIRMADA
            self._fecha_confirmacion = datetime.now()
            logger.evento(
                "RESERVA_CONFIRMADA",
                f"{self._id} | Cliente: {self._cliente.id} | "
                f"Servicio: {self._servicio.id} | "
                f"Duración: {self._duracion_horas}h | "
                f"Costo: ${costo:,.2f} COP",
            )
        finally:
            # Siempre se ejecuta
            logger.info(
                f"Intento de confirmación de reserva {self._id} procesado."
            )

    def cancelar(self, motivo: str = "Sin motivo especificado") -> None:
        """
        Cancela la reserva. No se puede cancelar una reserva ya completada.
        Usa try/except/finally.
        """
        try:
            if self._estado == ESTADO_COMPLETADA:
                raise OperacionNoPermitidaError(
                    "cancelar_reserva",
                    f"la reserva {self._id} ya fue completada.",
                )
            if self._estado == ESTADO_CANCELADA:
                raise OperacionNoPermitidaError(
                    "cancelar_reserva",
                    f"la reserva {self._id} ya estaba cancelada.",
                )
            self._estado = ESTADO_CANCELADA
            self._notas = motivo
            logger.evento(
                "RESERVA_CANCELADA",
                f"{self._id} | Motivo: {motivo}",
            )
        except OperacionNoPermitidaError as e:
            logger.error(f"Cancelación rechazada para {self._id}: {e}", e)
            raise
        finally:
            logger.info(f"Intento de cancelación de reserva {self._id} procesado.")

    def procesar(self) -> None:
        """
        Marca la reserva como COMPLETADA.
        Solo puede procesarse si está CONFIRMADA.
        Usa try/except.
        """
        try:
            if self._estado != ESTADO_CONFIRMADA:
                raise OperacionNoPermitidaError(
                    "procesar_reserva",
                    f"la reserva {self._id} debe estar CONFIRMADA para procesarse "
                    f"(estado actual: {self._estado}).",
                )
            self._estado = ESTADO_COMPLETADA
            logger.evento("RESERVA_COMPLETADA", f"{self._id}")
        except OperacionNoPermitidaError as e:
            logger.error(f"No se puede procesar reserva {self._id}: {e}", e)
            raise

    # ── Representación ────────────────────────────────────────────────────────

    def describir(self) -> str:
        costo_str = (
            f"${self._costo_total:,.2f} COP"
            if self._costo_total is not None
            else "No calculado aún"
        )
        return (
            f"Reserva {self._id}\n"
            f"  Estado   : {self._estado}\n"
            f"  Cliente  : {self._cliente.nombre} ({self._cliente.id})\n"
            f"  Servicio : {self._servicio.nombre} ({self._servicio.id})\n"
            f"  Duración : {self._duracion_horas} hora(s)\n"
            f"  Costo    : {costo_str}\n"
            f"  Creada   : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def __str__(self) -> str:
        return self.describir()

    def __repr__(self) -> str:
        return f"Reserva(id={self._id!r}, estado={self._estado!r})"
