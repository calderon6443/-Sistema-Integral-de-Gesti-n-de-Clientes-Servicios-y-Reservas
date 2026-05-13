"""
gestor.py - Gestor central del sistema Software FJ.

Administra las listas de clientes, servicios y reservas en memoria.
Aplica validaciones de negocio y delega el logging a logger.py.
"""

from cliente import Cliente
from servicios import Servicio
from reserva import Reserva
from excepciones import (
    ClienteYaExisteError,
    ClienteNoEncontradoError,
    ServicioNoEncontradoError,
    OperacionNoPermitidaError,
)
import logger


class GestorSistema:
    """
    Controlador principal del sistema Software FJ.

    Mantiene en memoria:
      - _clientes  : dict[id → Cliente]
      - _servicios : dict[id → Servicio]
      - _reservas  : list[Reserva]
    """

    def __init__(self):
        self._clientes: dict[str, Cliente] = {}
        self._servicios: dict[str, Servicio] = {}
        self._reservas: list[Reserva] = []
        logger.info("GestorSistema inicializado.")

    # ─── Gestión de Clientes ─────────────────────────────────────────────────

    def registrar_cliente(self, cliente: Cliente) -> None:
        """Agrega un cliente al sistema. Rechaza duplicados."""
        try:
            if cliente.id in self._clientes:
                raise ClienteYaExisteError(cliente.id)
            if not cliente.validar():
                raise OperacionNoPermitidaError(
                    "registrar_cliente",
                    f"el cliente {cliente.id} no pasó validación interna.",
                )
            self._clientes[cliente.id] = cliente
            logger.evento(
                "CLIENTE_REGISTRADO",
                f"{cliente.id} | {cliente.nombre} | {cliente.tipo}",
            )
            print(f"  ✔ Cliente registrado: {cliente.nombre} [{cliente.id}]")
        except ClienteYaExisteError as e:
            logger.error(str(e), e)
            print(f"  ✘ {e}")
            raise

    def obtener_cliente(self, cliente_id: str) -> Cliente:
        """Busca y retorna un cliente por su ID."""
        cid = cliente_id.strip().upper()
        if cid not in self._clientes:
            raise ClienteNoEncontradoError(cid)
        return self._clientes[cid]

    def listar_clientes(self) -> None:
        """Imprime todos los clientes registrados."""
        if not self._clientes:
            print("  (No hay clientes registrados)")
            return
        for c in self._clientes.values():
            print(f"  • {c.describir()}")

    # ─── Gestión de Servicios ────────────────────────────────────────────────

    def agregar_servicio(self, servicio: Servicio) -> None:
        """Agrega un servicio al catálogo."""
        try:
            if servicio.id in self._servicios:
                raise OperacionNoPermitidaError(
                    "agregar_servicio",
                    f"ya existe un servicio con ID '{servicio.id}'.",
                )
            self._servicios[servicio.id] = servicio
            logger.evento(
                "SERVICIO_AGREGADO",
                f"{servicio.id} | {servicio.nombre}",
            )
            print(f"  ✔ Servicio agregado: {servicio.nombre} [{servicio.id}]")
        except OperacionNoPermitidaError as e:
            logger.error(str(e), e)
            print(f"  ✘ {e}")
            raise

    def obtener_servicio(self, servicio_id: str) -> Servicio:
        """Busca y retorna un servicio por su ID."""
        sid = servicio_id.strip().upper()
        if sid not in self._servicios:
            raise ServicioNoEncontradoError(sid)
        return self._servicios[sid]

    def listar_servicios(self) -> None:
        """Imprime todos los servicios del catálogo."""
        if not self._servicios:
            print("  (No hay servicios en el catálogo)")
            return
        for s in self._servicios.values():
            print(f"  • {s.describir()}")

    # ─── Gestión de Reservas ─────────────────────────────────────────────────

    def crear_reserva(
        self,
        cliente_id: str,
        servicio_id: str,
        duracion_horas: float,
        parametros_extra: dict | None = None,
    ) -> Reserva:
        """
        Crea una reserva en estado PENDIENTE.
        Usa try/except/else para separar el intento del éxito.
        """
        reserva = None
        try:
            cliente = self.obtener_cliente(cliente_id)
            servicio = self.obtener_servicio(servicio_id)
            reserva = Reserva(cliente, servicio, duracion_horas, parametros_extra)
        except (ClienteNoEncontradoError, ServicioNoEncontradoError) as e:
            logger.error(f"No se pudo crear reserva: {e}", e)
            print(f"  ✘ {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado creando reserva: {e}", e)
            print(f"  ✘ Error al crear reserva: {e}")
            raise
        else:
            self._reservas.append(reserva)
            logger.evento(
                "RESERVA_CREADA",
                f"{reserva.id} | Cliente: {cliente_id} | Servicio: {servicio_id}",
            )
            print(f"  ✔ Reserva creada: {reserva.id} (estado: PENDIENTE)")
        return reserva

    def confirmar_reserva(self, reserva: Reserva) -> None:
        """Delega la confirmación a la reserva y captura errores."""
        try:
            reserva.confirmar()
            print(
                f"  ✔ Reserva {reserva.id} CONFIRMADA | "
                f"Costo: ${reserva.costo_total:,.2f} COP"
            )
        except Exception as e:
            print(f"  ✘ No se pudo confirmar {reserva.id}: {e}")
            raise

    def cancelar_reserva(self, reserva: Reserva, motivo: str = "") -> None:
        """Cancela una reserva con motivo opcional."""
        try:
            reserva.cancelar(motivo or "Cancelación solicitada por gestor.")
            print(f"  ✔ Reserva {reserva.id} CANCELADA.")
        except Exception as e:
            print(f"  ✘ No se pudo cancelar {reserva.id}: {e}")
            raise

    def listar_reservas(self) -> None:
        """Imprime un resumen de todas las reservas."""
        if not self._reservas:
            print("  (No hay reservas registradas)")
            return
        for r in self._reservas:
            costo = (
                f"${r.costo_total:,.2f}" if r.costo_total is not None else "N/A"
            )
            print(
                f"  • [{r.estado}] {r.id} | "
                f"Cliente: {r.cliente.nombre} | "
                f"Servicio: {r.servicio.nombre} | "
                f"{r.duracion_horas}h | Costo: {costo}"
            )

    # ─── Estadísticas ─────────────────────────────────────────────────────────

    def resumen(self) -> None:
        """Imprime estadísticas generales del sistema."""
        total_confirmadas = sum(
            1 for r in self._reservas if r.estado == "CONFIRMADA"
        )
        total_canceladas = sum(
            1 for r in self._reservas if r.estado == "CANCELADA"
        )
        ingresos = sum(
            r.costo_total
            for r in self._reservas
            if r.costo_total is not None and r.estado != "CANCELADA"
        )
        print("\n" + "=" * 55)
        print("  RESUMEN DEL SISTEMA — Software FJ")
        print("=" * 55)
        print(f"  Clientes registrados : {len(self._clientes)}")
        print(f"  Servicios en catálogo: {len(self._servicios)}")
        print(f"  Reservas totales     : {len(self._reservas)}")
        print(f"  Confirmadas          : {total_confirmadas}")
        print(f"  Canceladas           : {total_canceladas}")
        print(f"  Ingresos estimados   : ${ingresos:,.2f} COP")
        print("=" * 55)
