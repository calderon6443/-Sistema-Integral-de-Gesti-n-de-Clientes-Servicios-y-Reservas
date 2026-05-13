"""
entidades.py - Clase abstracta base del sistema Software FJ

Define el contrato mínimo que cualquier entidad del sistema debe cumplir:
identificador único, descripción y representación en texto.
"""

from abc import ABC, abstractmethod


class EntidadBase(ABC):
    """
    Clase abstracta raíz de todas las entidades del sistema.

    Principios aplicados:
      - Abstracción: define comportamiento sin implementarlo.
      - Encapsulación: el ID se protege contra modificación externa.
    """

    def __init__(self, entidad_id: str):
        if not entidad_id or not isinstance(entidad_id, str):
            raise ValueError("El ID de entidad no puede ser vacío o nulo.")
        self._id: str = entidad_id.strip().upper()

    # ── Propiedad de solo lectura ─────────────────────────────────────────────
    @property
    def id(self) -> str:
        """Identificador único de la entidad (inmutable tras la creación)."""
        return self._id

    # ── Métodos abstractos ────────────────────────────────────────────────────
    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""

    @abstractmethod
    def validar(self) -> bool:
        """
        Verifica que los datos internos de la entidad son coherentes.
        Retorna True si son válidos, False en caso contrario.
        """

    # ── Métodos concretos comunes ─────────────────────────────────────────────
    def __str__(self) -> str:
        return self.describir()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntidadBase):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
