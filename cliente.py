"""
cliente.py - Clase Cliente con encapsulación y validaciones robustas
"""

import re
from entidades import EntidadBase
from excepciones import DatosClienteInvalidosError


class Cliente(EntidadBase):
    """
    Representa a un cliente de Software FJ.

    Encapsula datos personales y aplica validaciones estrictas en cada
    propiedad mediante setters.

    Principios aplicados:
      - Encapsulación: atributos privados con propiedades controladas.
      - Herencia: extiende EntidadBase.
      - Abstracción: implementa describir() y validar().
    """

    # Expresión regular básica para correos electrónicos
    _RE_EMAIL = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
    # Solo dígitos, guiones y el símbolo +
    _RE_TELEFONO = re.compile(r"^\+?[\d\s\-]{7,15}$")

    def __init__(
        self,
        cliente_id: str,
        nombre: str,
        email: str,
        telefono: str,
        tipo: str = "regular",
    ):
        """
        Parámetros
        ----------
        cliente_id : str  Identificador único (p. ej. cédula o código).
        nombre     : str  Nombre completo del cliente.
        email      : str  Correo electrónico válido.
        telefono   : str  Número de contacto.
        tipo       : str  'regular' | 'premium' | 'corporativo'.
        """
        super().__init__(cliente_id)
        # Usamos los setters para validar desde la construcción
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.tipo = tipo
        self._activo: bool = True

    # ── Propiedades con validación ────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatosClienteInvalidosError(
                "nombre", valor, "debe tener al menos 3 caracteres."
            )
        if any(c.isdigit() for c in valor):
            raise DatosClienteInvalidosError(
                "nombre", valor, "no puede contener dígitos."
            )
        self._nombre = valor.strip().title()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise DatosClienteInvalidosError(
                "email", valor, "el correo no puede ser nulo o vacío."
            )
        if not self._RE_EMAIL.match(valor.strip()):
            raise DatosClienteInvalidosError(
                "email", valor, "formato de correo electrónico inválido."
            )
        self._email = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise DatosClienteInvalidosError(
                "telefono", valor, "el teléfono no puede ser nulo o vacío."
            )
        if not self._RE_TELEFONO.match(valor.strip()):
            raise DatosClienteInvalidosError(
                "telefono",
                valor,
                "debe contener entre 7 y 15 dígitos (puede incluir +, - y espacios).",
            )
        self._telefono = valor.strip()

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str) -> None:
        tipos_validos = {"regular", "premium", "corporativo"}
        if not valor or valor.lower() not in tipos_validos:
            raise DatosClienteInvalidosError(
                "tipo",
                valor,
                f"debe ser uno de: {', '.join(tipos_validos)}.",
            )
        self._tipo = valor.lower()

    @property
    def activo(self) -> bool:
        return self._activo

    # ── Métodos abstractos implementados ──────────────────────────────────────

    def describir(self) -> str:
        estado = "ACTIVO" if self._activo else "INACTIVO"
        return (
            f"Cliente [{self.id}] | {self._nombre} | {self._email} | "
            f"Tel: {self._telefono} | Tipo: {self._tipo.upper()} | {estado}"
        )

    def validar(self) -> bool:
        """Retorna True si todos los campos obligatorios están presentes."""
        return bool(self._nombre and self._email and self._telefono)

    # ── Métodos de negocio ────────────────────────────────────────────────────

    def desactivar(self) -> None:
        """Marca al cliente como inactivo (baja lógica)."""
        self._activo = False

    def descuento_aplicable(self) -> float:
        """
        Devuelve el porcentaje de descuento según el tipo de cliente.
        regular=0%, premium=10%, corporativo=20%
        """
        tabla = {"regular": 0.0, "premium": 0.10, "corporativo": 0.20}
        return tabla.get(self._tipo, 0.0)
