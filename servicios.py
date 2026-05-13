"""
servicios.py - Clase abstracta Servicio y tres clases derivadas especializadas.

Servicios disponibles en Software FJ:
  1. ReservaSala      → reserva de salas de reuniones / conferencias.
  2. AlquilerEquipo   → alquiler de equipos tecnológicos.
  3. AsesoriaEspecializada → sesiones de consultoría con un experto.

Principios aplicados:
  - Abstracción: Servicio es una ABC.
  - Herencia: las tres clases heredan de Servicio.
  - Polimorfismo: cada clase sobreescribe calcular_costo() y describir().
  - Encapsulación: precio base y disponibilidad son atributos privados.
  - Sobrecarga simulada: calcular_costo acepta parámetros opcionales.
"""

from abc import abstractmethod
from entidades import EntidadBase
from excepciones import (
    ServicioNoDisponibleError,
    ParametroServicioInvalidoError,
    CostoInconsistenteError,
)


# ─── Clase abstracta base ─────────────────────────────────────────────────────

class Servicio(EntidadBase):
    """
    Clase abstracta que representa cualquier servicio ofrecido por Software FJ.
    Define el contrato que deben cumplir todos los servicios concretos.
    """

    IVA_DEFAULT = 0.19  # 19 % de IVA (Colombia)

    def __init__(self, servicio_id: str, nombre: str, precio_hora: float):
        super().__init__(servicio_id)
        self.nombre = nombre
        self.precio_hora = precio_hora          # validado por el setter
        self._disponible: bool = True

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ParametroServicioInvalidoError(
                "nombre", "debe tener al menos 3 caracteres."
            )
        self._nombre = valor.strip()

    @property
    def precio_hora(self) -> float:
        return self._precio_hora

    @precio_hora.setter
    def precio_hora(self, valor: float) -> None:
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ParametroServicioInvalidoError(
                "precio_hora", "debe ser un número positivo."
            )
        if valor <= 0:
            raise ParametroServicioInvalidoError(
                "precio_hora", f"debe ser mayor que 0, se recibió {valor}."
            )
        self._precio_hora = valor

    @property
    def disponible(self) -> bool:
        return self._disponible

    # ── Métodos concretos comunes ─────────────────────────────────────────────

    def activar(self) -> None:
        self._disponible = True

    def desactivar(self) -> None:
        self._disponible = False

    def verificar_disponibilidad(self) -> None:
        """Lanza ServicioNoDisponibleError si el servicio está inactivo."""
        if not self._disponible:
            raise ServicioNoDisponibleError(self.id)

    def validar(self) -> bool:
        return bool(self._nombre) and self._precio_hora > 0

    # ── Métodos abstractos ────────────────────────────────────────────────────

    @abstractmethod
    def calcular_costo(
        self,
        horas: float,
        aplicar_iva: bool = True,
        descuento: float = 0.0,
        *,
        parametros_extra: dict | None = None,
    ) -> float:
        """
        Calcula el costo total del servicio.

        Parámetros
        ----------
        horas           : Duración en horas (>= 0.5).
        aplicar_iva     : Si True aplica IVA del 19 %.
        descuento       : Porcentaje de descuento (0.0–1.0).
        parametros_extra: Diccionario con opciones específicas del servicio.
        """

    @abstractmethod
    def describir(self) -> str:
        """Descripción completa y específica del servicio."""

    @abstractmethod
    def validar_parametros(self, horas: float, **kwargs) -> None:
        """Valida los parámetros específicos antes de calcular costos."""

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _validar_horas(self, horas: float, minimo: float = 0.5) -> float:
        """Valida y convierte la duración; lanza excepción si es inválida."""
        try:
            horas = float(horas)
        except (TypeError, ValueError):
            raise ParametroServicioInvalidoError(
                "horas", f"debe ser numérico, se recibió '{horas}'."
            )
        if horas < minimo:
            raise ParametroServicioInvalidoError(
                "horas",
                f"mínimo {minimo} hora(s) para este servicio, se recibió {horas}.",
            )
        return horas

    def _aplicar_descuento_e_iva(
        self, subtotal: float, aplicar_iva: bool, descuento: float
    ) -> float:
        """Aplica descuento e IVA al subtotal y verifica coherencia."""
        if not (0.0 <= descuento <= 1.0):
            raise CostoInconsistenteError(
                f"El descuento debe estar entre 0 y 1, se recibió {descuento}."
            )
        total = subtotal * (1 - descuento)
        if aplicar_iva:
            total *= 1 + self.IVA_DEFAULT
        if total < 0:
            raise CostoInconsistenteError(
                f"El costo resultante es negativo ({total:.2f}), verifique descuentos."
            )
        return round(total, 2)


# ─── Servicio 1: Reserva de Sala ─────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Servicio para reservar salas de reuniones o conferencias.

    Parámetros extra aceptados en calcular_costo():
      - capacidad  (int)  : número de personas; salas con más de 20 tienen
                            recargo del 15 %.
      - proyector  (bool) : si se requiere proyector (+$50 000 fijo).
    """

    RECARGO_GRAN_SALA = 0.15
    COSTO_PROYECTOR = 50_000.0

    def __init__(self, servicio_id: str, nombre: str, precio_hora: float, aforo: int):
        super().__init__(servicio_id, nombre, precio_hora)
        if not isinstance(aforo, int) or aforo <= 0:
            raise ParametroServicioInvalidoError(
                "aforo", "debe ser un entero positivo."
            )
        self._aforo = aforo

    @property
    def aforo(self) -> int:
        return self._aforo

    def validar_parametros(self, horas: float, **kwargs) -> None:
        self._validar_horas(horas)
        capacidad = kwargs.get("capacidad", 1)
        if capacidad > self._aforo:
            raise ParametroServicioInvalidoError(
                "capacidad",
                f"la sala tiene aforo para {self._aforo} personas, "
                f"se solicitó {capacidad}.",
            )

    def calcular_costo(
        self,
        horas: float,
        aplicar_iva: bool = True,
        descuento: float = 0.0,
        *,
        parametros_extra: dict | None = None,
    ) -> float:
        self.verificar_disponibilidad()
        horas = self._validar_horas(horas)
        extra = parametros_extra or {}
        capacidad = extra.get("capacidad", 1)
        proyector = extra.get("proyector", False)

        subtotal = self._precio_hora * horas

        # Recargo por sala grande
        if capacidad > 20:
            subtotal *= 1 + self.RECARGO_GRAN_SALA

        # Costo fijo del proyector
        if proyector:
            subtotal += self.COSTO_PROYECTOR

        return self._aplicar_descuento_e_iva(subtotal, aplicar_iva, descuento)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"[SALA] {self._nombre} (ID: {self.id}) | "
            f"Aforo: {self._aforo} personas | "
            f"Precio/hora: ${self._precio_hora:,.0f} COP | {estado}"
        )


# ─── Servicio 2: Alquiler de Equipo ──────────────────────────────────────────

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos (portátiles, proyectores, etc.).

    Parámetros extra aceptados en calcular_costo():
      - cantidad (int) : número de unidades del equipo a alquilar.
      - seguro   (bool): seguro de daños (+10 % sobre subtotal).
    """

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        precio_hora: float,
        stock: int,
        tipo_equipo: str,
    ):
        super().__init__(servicio_id, nombre, precio_hora)
        if not isinstance(stock, int) or stock < 0:
            raise ParametroServicioInvalidoError(
                "stock", "debe ser un entero no negativo."
            )
        if not tipo_equipo or not isinstance(tipo_equipo, str):
            raise ParametroServicioInvalidoError(
                "tipo_equipo", "no puede ser vacío."
            )
        self._stock = stock
        self._tipo_equipo = tipo_equipo.strip()

    @property
    def stock(self) -> int:
        return self._stock

    def validar_parametros(self, horas: float, **kwargs) -> None:
        self._validar_horas(horas)
        cantidad = kwargs.get("cantidad", 1)
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ParametroServicioInvalidoError(
                "cantidad", "debe ser un entero positivo."
            )
        if cantidad > self._stock:
            raise ParametroServicioInvalidoError(
                "cantidad",
                f"se solicitaron {cantidad} unidades pero solo hay {self._stock} "
                "en stock.",
            )

    def calcular_costo(
        self,
        horas: float,
        aplicar_iva: bool = True,
        descuento: float = 0.0,
        *,
        parametros_extra: dict | None = None,
    ) -> float:
        self.verificar_disponibilidad()
        horas = self._validar_horas(horas)
        extra = parametros_extra or {}
        cantidad = extra.get("cantidad", 1)
        seguro = extra.get("seguro", False)

        subtotal = self._precio_hora * horas * cantidad
        if seguro:
            subtotal *= 1.10  # recargo del 10 % por seguro

        return self._aplicar_descuento_e_iva(subtotal, aplicar_iva, descuento)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"[EQUIPO] {self._nombre} (ID: {self.id}) | "
            f"Tipo: {self._tipo_equipo} | Stock: {self._stock} unidades | "
            f"Precio/hora: ${self._precio_hora:,.0f} COP | {estado}"
        )


# ─── Servicio 3: Asesoría Especializada ──────────────────────────────────────

class AsesoriaEspecializada(Servicio):
    """
    Servicio de consultoría y asesoría con un experto en una temática específica.

    Parámetros extra aceptados en calcular_costo():
      - nivel_experto (str): 'junior' (sin recargo) | 'senior' (+30 %) |
                             'principal' (+60 %).
      - informe       (bool): si se incluye informe escrito (+$200 000 fijo).
    """

    NIVELES = {
        "junior": 0.0,
        "senior": 0.30,
        "principal": 0.60,
    }
    COSTO_INFORME = 200_000.0
    MIN_HORAS = 1.0  # Las asesorías son mínimo 1 hora

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        precio_hora: float,
        area: str,
    ):
        super().__init__(servicio_id, nombre, precio_hora)
        if not area or not isinstance(area, str):
            raise ParametroServicioInvalidoError("area", "no puede ser vacía.")
        self._area = area.strip()

    @property
    def area(self) -> str:
        return self._area

    def validar_parametros(self, horas: float, **kwargs) -> None:
        self._validar_horas(horas, minimo=self.MIN_HORAS)
        nivel = kwargs.get("nivel_experto", "junior")
        if nivel not in self.NIVELES:
            raise ParametroServicioInvalidoError(
                "nivel_experto",
                f"debe ser uno de {list(self.NIVELES.keys())}, se recibió '{nivel}'.",
            )

    def calcular_costo(
        self,
        horas: float,
        aplicar_iva: bool = True,
        descuento: float = 0.0,
        *,
        parametros_extra: dict | None = None,
    ) -> float:
        self.verificar_disponibilidad()
        horas = self._validar_horas(horas, minimo=self.MIN_HORAS)
        extra = parametros_extra or {}
        nivel = extra.get("nivel_experto", "junior")
        informe = extra.get("informe", False)

        if nivel not in self.NIVELES:
            raise ParametroServicioInvalidoError(
                "nivel_experto",
                f"nivel desconocido '{nivel}'. Use: {list(self.NIVELES.keys())}.",
            )

        recargo_nivel = self.NIVELES[nivel]
        subtotal = self._precio_hora * horas * (1 + recargo_nivel)

        if informe:
            subtotal += self.COSTO_INFORME

        return self._aplicar_descuento_e_iva(subtotal, aplicar_iva, descuento)

    def describir(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"[ASESORÍA] {self._nombre} (ID: {self.id}) | "
            f"Área: {self._area} | "
            f"Precio base/hora: ${self._precio_hora:,.0f} COP | {estado}"
        )
