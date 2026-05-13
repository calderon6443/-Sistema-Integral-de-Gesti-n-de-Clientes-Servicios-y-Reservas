"""
main.py - Punto de entrada del sistema Software FJ
=====================================================
Simula más de 10 operaciones completas (válidas e inválidas) demostrando:
  • Creación correcta e incorrecta de clientes
  • Creación correcta e incorrecta de servicios
  • Reservas exitosas y fallidas
  • Manejo avanzado de excepciones
  • Encadenamiento de excepciones
  • El sistema NUNCA se detiene ante errores
"""

import sys
import os

# Asegurar que Python encuentra los módulos del proyecto
sys.path.insert(0, os.path.dirname(__file__))

import logger
from gestor import GestorSistema
from cliente import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from excepciones import (
    SistemaFJError,
    DatosClienteInvalidosError,
    ParametroServicioInvalidoError,
    ServicioNoDisponibleError,
    ClienteYaExisteError,
    ClienteNoEncontradoError,
)


# ─── Utilidades de presentación ───────────────────────────────────────────────

def seccion(titulo: str) -> None:
    print(f"\n{'━' * 60}")
    print(f"  {titulo}")
    print(f"{'━' * 60}")


def subseccion(titulo: str) -> None:
    print(f"\n  ▶ {titulo}")


# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def main() -> None:
    logger.iniciar_sesion()
    print("\n" + "═" * 60)
    print("   SISTEMA SOFTWARE FJ — Demostración de Operaciones")
    print("═" * 60)

    gestor = GestorSistema()

    # ══════════════════════════════════════════════════════════════
    # BLOQUE 1 — Registro de Clientes (válidos e inválidos)
    # ══════════════════════════════════════════════════════════════
    seccion("BLOQUE 1: REGISTRO DE CLIENTES")

    # ── Operación 1: Registro VÁLIDO ──────────────────────────────
    subseccion("Op.1 — Registrar cliente válido (Ana Gómez, premium)")
    try:
        c1 = Cliente("CLI001", "Ana Gómez", "ana.gomez@correo.com", "+57 310-555-1234", "premium")
        gestor.registrar_cliente(c1)
    except SistemaFJError as e:
        logger.error(f"Op.1 falló inesperadamente: {e}", e)
        print(f"  ✘ Error inesperado: {e}")

    # ── Operación 2: Registro VÁLIDO ──────────────────────────────
    subseccion("Op.2 — Registrar cliente válido (Carlos Ruiz, corporativo)")
    try:
        c2 = Cliente("CLI002", "Carlos Ruiz", "c.ruiz@empresa.co", "3201234567", "corporativo")
        gestor.registrar_cliente(c2)
    except SistemaFJError as e:
        logger.error(f"Op.2 falló inesperadamente: {e}", e)
        print(f"  ✘ Error inesperado: {e}")

    # ── Operación 3: Registro INVÁLIDO — email malformado ─────────
    subseccion("Op.3 — Intentar cliente con email inválido (ERROR ESPERADO)")
    try:
        c_malo = Cliente("CLI003", "Pedro Pérez", "correo-sin-arroba", "3009876543", "regular")
        gestor.registrar_cliente(c_malo)
    except DatosClienteInvalidosError as e:
        logger.error(f"Op.3 — Dato inválido capturado: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")
    except SistemaFJError as e:
        logger.error(f"Op.3 — Error de sistema: {e}", e)
        print(f"  ✘ Error de sistema: {e}")

    # ── Operación 4: Registro INVÁLIDO — nombre con números ───────
    subseccion("Op.4 — Intentar cliente con nombre inválido (ERROR ESPERADO)")
    try:
        c_malo2 = Cliente("CLI004", "Juan123", "juan@ok.com", "3111234567", "regular")
        gestor.registrar_cliente(c_malo2)
    except DatosClienteInvalidosError as e:
        logger.error(f"Op.4 — Dato inválido capturado: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")

    # ── Operación 5: Registro DUPLICADO ───────────────────────────
    subseccion("Op.5 — Registrar cliente duplicado (ERROR ESPERADO)")
    try:
        c_dup = Cliente("CLI001", "Ana Gómez Copia", "otra@correo.com", "3000000001", "regular")
        gestor.registrar_cliente(c_dup)
    except ClienteYaExisteError as e:
        logger.error(f"Op.5 — Duplicado capturado: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")

    # Registrar un tercer cliente para las reservas
    try:
        c3 = Cliente("CLI005", "Lucía Herrera", "lucia.h@firma.com", "3157654321", "regular")
        gestor.registrar_cliente(c3)
    except SistemaFJError:
        pass

    # ══════════════════════════════════════════════════════════════
    # BLOQUE 2 — Creación de Servicios (válidos e inválidos)
    # ══════════════════════════════════════════════════════════════
    seccion("BLOQUE 2: CREACIÓN DE SERVICIOS")

    # ── Operación 6: Servicios VÁLIDOS ────────────────────────────
    subseccion("Op.6 — Agregar servicios válidos al catálogo")
    try:
        sala_a = ReservaSala("SAL001", "Sala Amazonas", 80_000, aforo=12)
        gestor.agregar_servicio(sala_a)

        sala_b = ReservaSala("SAL002", "Sala Orinoco (Gran Formato)", 150_000, aforo=40)
        gestor.agregar_servicio(sala_b)

        equipo_laptop = AlquilerEquipo(
            "EQP001", "Portátiles HP ProBook", 25_000, stock=10, tipo_equipo="Laptop"
        )
        gestor.agregar_servicio(equipo_laptop)

        asesoria_ti = AsesoriaEspecializada(
            "ASE001", "Consultoría en Ciberseguridad", 200_000, area="Tecnología"
        )
        gestor.agregar_servicio(asesoria_ti)

        asesoria_legal = AsesoriaEspecializada(
            "ASE002", "Asesoría Legal Empresarial", 180_000, area="Legal"
        )
        gestor.agregar_servicio(asesoria_legal)

    except SistemaFJError as e:
        logger.error(f"Op.6 — Error creando servicios: {e}", e)
        print(f"  ✘ {e}")

    # ── Operación 7: Servicio INVÁLIDO — precio negativo ──────────
    subseccion("Op.7 — Servicio con precio negativo (ERROR ESPERADO)")
    try:
        s_malo = ReservaSala("SAL999", "Sala Inválida", -5000, aforo=5)
        gestor.agregar_servicio(s_malo)
    except ParametroServicioInvalidoError as e:
        logger.error(f"Op.7 — Parámetro inválido: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")

    # ── Operación 8: Servicio desactivado ─────────────────────────
    subseccion("Op.8 — Desactivar servicio (simulación de mantenimiento)")
    try:
        sala_b.desactivar()
        logger.advertencia(f"Servicio {sala_b.id} marcado como no disponible.")
        print(f"  ⚠ Servicio '{sala_b.nombre}' desactivado temporalmente.")
    except Exception as e:
        logger.error(f"Op.8 — Error al desactivar: {e}", e)

    # ══════════════════════════════════════════════════════════════
    # BLOQUE 3 — Creación y gestión de Reservas
    # ══════════════════════════════════════════════════════════════
    seccion("BLOQUE 3: RESERVAS")

    # ── Operación 9: Reserva EXITOSA con confirmación ─────────────
    subseccion("Op.9 — Crear y confirmar reserva válida (Ana → Sala Amazonas, 3h)")
    try:
        r1 = gestor.crear_reserva(
            "CLI001", "SAL001", 3.0,
            parametros_extra={"capacidad": 8, "proyector": True}
        )
        gestor.confirmar_reserva(r1)
        # Mostrar variantes de cálculo (métodos sobrecargados)
        print(f"    Costo sin IVA             : ${r1.calcular_costo_sin_iva():,.2f} COP")
        print(f"    Costo con descuento 50%   : ${r1.calcular_costo_con_descuento_personalizado(0.5):,.2f} COP")
    except SistemaFJError as e:
        logger.error(f"Op.9 falló: {e}", e)
        print(f"  ✘ {e}")

    # ── Operación 10: Reserva sobre servicio NO disponible ─────────
    subseccion("Op.10 — Intentar reservar sala desactivada (ERROR ESPERADO)")
    try:
        r2 = gestor.crear_reserva("CLI002", "SAL002", 2.0)
        gestor.confirmar_reserva(r2)
    except ServicioNoDisponibleError as e:
        logger.error(f"Op.10 — Servicio no disponible: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")
    except SistemaFJError as e:
        logger.error(f"Op.10 — Error: {e}", e)
        print(f"  ✘ {e}")

    # ── Operación 11: Reserva con duración inválida ────────────────
    subseccion("Op.11 — Reserva con duración inválida (ERROR ESPERADO)")
    try:
        r3 = gestor.crear_reserva("CLI001", "SAL001", 0.1)
        gestor.confirmar_reserva(r3)
    except SistemaFJError as e:
        logger.error(f"Op.11 — Duración inválida: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")

    # ── Operación 12: Reserva de equipo con asesoría ───────────────
    subseccion("Op.12 — Reserva de equipo (Carlos → Portátiles HP, 4h, 3 unidades)")
    try:
        r4 = gestor.crear_reserva(
            "CLI002", "EQP001", 4.0,
            parametros_extra={"cantidad": 3, "seguro": True}
        )
        gestor.confirmar_reserva(r4)
        print(f"    Detalle:\n{r4.describir()}")
    except SistemaFJError as e:
        logger.error(f"Op.12 falló: {e}", e)
        print(f"  ✘ {e}")

    # ── Operación 13: Asesoría con nivel senior ────────────────────
    subseccion("Op.13 — Asesoría ciberseguridad, nivel senior, con informe")
    try:
        r5 = gestor.crear_reserva(
            "CLI005", "ASE001", 2.0,
            parametros_extra={"nivel_experto": "senior", "informe": True}
        )
        gestor.confirmar_reserva(r5)
        print(f"    Detalle:\n{r5.describir()}")
    except SistemaFJError as e:
        logger.error(f"Op.13 falló: {e}", e)
        print(f"  ✘ {e}")

    # ── Operación 14: Cancelar una reserva confirmada ──────────────
    subseccion("Op.14 — Cancelar reserva ya confirmada (r4)")
    try:
        gestor.cancelar_reserva(r4, "El cliente reprogramó la reunión.")
    except SistemaFJError as e:
        logger.error(f"Op.14 — Error al cancelar: {e}", e)
        print(f"  ✘ {e}")

    # ── Operación 15: Confirmar reserva ya confirmada ──────────────
    subseccion("Op.15 — Reconfirmar reserva ya confirmada (ERROR ESPERADO)")
    try:
        gestor.confirmar_reserva(r1)   # r1 ya fue confirmada en Op.9
    except SistemaFJError as e:
        logger.error(f"Op.15 — Reconfirmación rechazada: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")

    # ── Operación 16: Cliente inexistente ──────────────────────────
    subseccion("Op.16 — Reserva para cliente inexistente (ERROR ESPERADO)")
    try:
        r6 = gestor.crear_reserva("FANTASMA99", "ASE002", 1.5)
    except ClienteNoEncontradoError as e:
        logger.error(f"Op.16 — Cliente no encontrado: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")

    # ── Operación 17: Encadenamiento de excepciones ────────────────
    subseccion("Op.17 — Encadenamiento de excepciones (try/except/raise from)")
    try:
        try:
            valor_externo = "abc"   # valor no numérico simulando entrada de usuario
            horas = float(valor_externo)
        except ValueError as e_original:
            from excepciones import DuracionInvalidaError
            raise DuracionInvalidaError(valor_externo) from e_original
    except SistemaFJError as e:
        causa = e.__cause__
        logger.error(
            f"Op.17 — Excepción encadenada: {e} | Causa original: {causa}", e
        )
        print(f"  ✘ Excepción de dominio: {e}")
        print(f"     Causada por         : {causa}")

    # ── Operación 18: Asesoría con nivel inválido ──────────────────
    subseccion("Op.18 — Asesoría con nivel de experto inexistente (ERROR ESPERADO)")
    try:
        r7 = gestor.crear_reserva(
            "CLI001", "ASE002", 1.0,
            parametros_extra={"nivel_experto": "dios", "informe": False}
        )
        gestor.confirmar_reserva(r7)
    except SistemaFJError as e:
        logger.error(f"Op.18 — Nivel inválido: {e}", e)
        print(f"  ✘ Capturado correctamente: {e}")

    # ══════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ══════════════════════════════════════════════════════════════
    seccion("LISTADO FINAL DE CLIENTES")
    gestor.listar_clientes()

    seccion("LISTADO FINAL DE SERVICIOS")
    gestor.listar_servicios()

    seccion("LISTADO FINAL DE RESERVAS")
    gestor.listar_reservas()

    gestor.resumen()

    print(f"\n  📄 Log de eventos guardado en: softwarefj_eventos.log")
    print("  Sistema finalizado correctamente sin interrupciones.\n")
    logger.info("Ejecución de main.py finalizada correctamente.")


# ─── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
