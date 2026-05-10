"""Entidades del dominio: Entidad (abstracta), Cliente, Servicios y Reserva."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import datetime
from itertools import count
from typing import List, Optional

from excepciones import (
    CalculoInconsistenteError,
    ClienteInvalidoError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from logger import get_logger

log = get_logger("entidades")


# Clase abstracta base
# ---------------------------------------------------------------------------
class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad gestionable."""

    _contador = count(1)

    def __init__(self) -> None:
        self._id: int = next(Entidad._contador)
        self._creado_en: datetime = datetime.now()

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Cada entidad debe describirse a sí misma."""


# Cliente
# ---------------------------------------------------------------------------
class Cliente(Entidad):
    """Cliente con encapsulación y validación robusta."""

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, nombre: str, documento: str, email: str, telefono: str) -> None:
        super().__init__()
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono
        log.info("Cliente creado: %s", self)

    # ---------- Propiedades con validación (encapsulación) ----------
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.isalnum() or len(valor) < 5:
            raise ClienteInvalidoError("Documento inválido (alfanumérico, mín. 5).")
        self._documento = valor

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        if not isinstance(valor, str) or not self.EMAIL_RE.match(valor):
            raise ClienteInvalidoError(f"Email inválido: {valor!r}")
        self._email = valor.lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        digitos = re.sub(r"\D", "", valor or "")
        if len(digitos) < 7:
            raise ClienteInvalidoError("Teléfono inválido (mín. 7 dígitos).")
        self._telefono = digitos

    def describir(self) -> str:
        return f"Cliente#{self.id} {self.nombre} <{self.email}>"

    def __repr__(self) -> str:
        return self.describir()


# Servicio (abstracto) y especializados
# ---------------------------------------------------------------------------
class Servicio(Entidad):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""

    IVA = 0.19

    def __init__(self, nombre: str, precio_base: float, disponible: bool = True) -> None:
        super().__init__()
        if not nombre or not isinstance(nombre, str):
            raise ServicioInvalidoError("El nombre del servicio es obligatorio.")
        if not isinstance(precio_base, (int, float)) or precio_base <= 0:
            raise ServicioInvalidoError("El precio base debe ser numérico y > 0.")
        self._nombre = nombre.strip()
        self._precio_base = float(precio_base)
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        """Cada servicio implementa su propio cálculo (sobrescrito y sobrecargado)."""

    @abstractmethod
    def validar_parametros(self, **kwargs) -> None:
        """Cada servicio valida sus propios parámetros antes de reservar."""

    def describir(self) -> str:
        estado = "disponible" if self.disponible else "NO disponible"
        return f"{type(self).__name__}#{self.id} '{self.nombre}' base=${self.precio_base:.2f} ({estado})"

    def aplicar_impuestos_descuentos(
        self,
        subtotal: float,
        descuento: float = 0.0,
        incluir_iva: bool = True,
    ) -> float:
        """Variante del cálculo con impuestos y descuentos opcionales."""
        if subtotal < 0:
            raise CalculoInconsistenteError("Subtotal negativo.")
        if not 0 <= descuento <= 1:
            raise CalculoInconsistenteError("Descuento debe estar entre 0 y 1.")
        total = subtotal * (1 - descuento)
        if incluir_iva:
            total *= 1 + self.IVA
        return round(total, 2)


class ReservaSala(Servicio):
    """Reserva de una sala por horas."""

    def __init__(self, nombre: str, precio_hora: float, capacidad: int) -> None:
        super().__init__(nombre, precio_hora)
        if capacidad <= 0:
            raise ServicioInvalidoError("La capacidad debe ser positiva.")
        self.capacidad = capacidad

    def validar_parametros(self, *, horas: int = 1, asistentes: int = 1, **_) -> None:
        if horas <= 0:
            raise ServicioInvalidoError("Las horas deben ser > 0.")
        if asistentes <= 0:
            raise ServicioInvalidoError("Los asistentes deben ser > 0.")
        if asistentes > self.capacidad:
            raise ServicioInvalidoError(
                f"Asistentes ({asistentes}) supera capacidad ({self.capacidad})."
            )

    def calcular_costo(self, horas: int = 1, asistentes: int = 1, descuento: float = 0.0) -> float:
        self.validar_parametros(horas=horas, asistentes=asistentes)
        subtotal = self.precio_base * horas
        return self.aplicar_impuestos_descuentos(subtotal, descuento=descuento)


class AlquilerEquipo(Servicio):
    """Alquiler de equipos por días, con depósito de garantía."""

    def __init__(self, nombre: str, precio_dia: float, deposito: float) -> None:
        super().__init__(nombre, precio_dia)
        if deposito < 0:
            raise ServicioInvalidoError("Depósito no puede ser negativo.")
        self.deposito = deposito

    def validar_parametros(self, *, dias: int = 1, **_) -> None:
        if dias <= 0:
            raise ServicioInvalidoError("Los días deben ser > 0.")

    def calcular_costo(self, dias: int = 1, descuento: float = 0.0) -> float:
        self.validar_parametros(dias=dias)
        subtotal = self.precio_base * dias + self.deposito
        return self.aplicar_impuestos_descuentos(subtotal, descuento=descuento)


class Asesoria(Servicio):
    """Asesoría especializada cobrada por hora con recargo por especialidad."""

    def __init__(self, nombre: str, precio_hora: float, especialidad: str, recargo: float = 0.15) -> None:
        super().__init__(nombre, precio_hora)
        if not especialidad:
            raise ServicioInvalidoError("Especialidad requerida.")
        self.especialidad = especialidad
        self.recargo = recargo

    def validar_parametros(self, *, horas: int = 1, **_) -> None:
        if horas <= 0:
            raise ServicioInvalidoError("Las horas deben ser > 0.")

    def calcular_costo(self, horas: int = 1, descuento: float = 0.0) -> float:
        self.validar_parametros(horas=horas)
        subtotal = self.precio_base * horas * (1 + self.recargo)
        return self.aplicar_impuestos_descuentos(subtotal, descuento=descuento)


# Reserva
# ---------------------------------------------------------------------------
class Reserva(Entidad):
    """Integra cliente y servicio con estado y procesamiento."""

    ESTADOS = {"pendiente", "confirmada", "cancelada", "procesada"}

    def __init__(self, cliente: Cliente, servicio: Servicio, **parametros) -> None:
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Cliente inválido para la reserva.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Servicio inválido para la reserva.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"Servicio {servicio.nombre} no disponible.")
        try:
            servicio.validar_parametros(**parametros)
        except ServicioInvalidoError as e:
            # Encadenamiento de excepciones
            raise ReservaInvalidaError("Parámetros inválidos para la reserva.") from e

        self.cliente = cliente
        self.servicio = servicio
        self.parametros = parametros
        self._estado = "pendiente"
        self._costo: Optional[float] = None
        log.info("Reserva creada: %s", self.describir())

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo(self) -> Optional[float]:
        return self._costo

    def confirmar(self) -> None:
        if self._estado != "pendiente":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar reserva en estado '{self._estado}'."
            )
        self._estado = "confirmada"
        log.info("Reserva #%s confirmada.", self.id)

    def cancelar(self) -> None:
        if self._estado in {"cancelada", "procesada"}:
            raise OperacionNoPermitidaError(
                f"No se puede cancelar reserva en estado '{self._estado}'."
            )
        self._estado = "cancelada"
        log.info("Reserva #%s cancelada.", self.id)

    def procesar(self) -> float:
        """Procesa la reserva calculando el costo. Demuestra try/except/else/finally."""
        if self._estado != "confirmada":
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas confirmadas (actual: {self._estado})."
            )
        try:
            costo = self.servicio.calcular_costo(**self.parametros)
        except CalculoInconsistenteError:
            log.exception("Cálculo inconsistente en reserva #%s", self.id)
            raise
        except ServicioInvalidoError as e:
            raise ReservaInvalidaError("Fallo al calcular costo.") from e
        else:
            self._costo = costo
            self._estado = "procesada"
            log.info("Reserva #%s procesada. Costo=$%.2f", self.id, costo)
            return costo
        finally:
            log.debug("Fin de procesamiento de reserva #%s (estado=%s)", self.id, self._estado)

    def describir(self) -> str:
        return (
            f"Reserva#{self.id} [{self._estado}] "
            f"{self.cliente.nombre} -> {self.servicio.nombre} {self.parametros}"
        )


# Gestor del sistema
# ---------------------------------------------------------------------------
class GestorSoftwareFJ:
    """Mantiene listas internas de clientes, servicios y reservas."""

    def __init__(self) -> None:
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []

    def registrar_cliente(self, **kwargs) -> Optional[Cliente]:
        try:
            cli = Cliente(**kwargs)
        except ClienteInvalidoError as e:
            log.error("Cliente NO registrado: %s | datos=%s", e, kwargs)
            return None
        else:
            self.clientes.append(cli)
            return cli

    def registrar_servicio(self, servicio: Servicio) -> Optional[Servicio]:
        try:
            if not isinstance(servicio, Servicio):
                raise ServicioInvalidoError("Objeto no es un Servicio.")
        except ServicioInvalidoError as e:
            log.error("Servicio NO registrado: %s", e)
            return None
        else:
            self.servicios.append(servicio)
            return servicio

    def crear_reserva(self, cliente: Cliente, servicio: Servicio, **params) -> Optional[Reserva]:
        try:
            reserva = Reserva(cliente, servicio, **params)
        except (ReservaInvalidaError, ServicioNoDisponibleError) as e:
            causa = f" (causa: {e.__cause__})" if e.__cause__ else ""
            log.error("Reserva NO creada: %s%s", e, causa)
            return None
        else:
            self.reservas.append(reserva)
            return reserva

    def resumen(self) -> str:
        lineas = ["", "=" * 60, "RESUMEN SOFTWARE FJ", "=" * 60]
        lineas.append(f"Clientes:  {len(self.clientes)}")
        lineas.append(f"Servicios: {len(self.servicios)}")
        lineas.append(f"Reservas:  {len(self.reservas)}")
        lineas.append("-" * 60)
        for r in self.reservas:
            costo = f"${r.costo:.2f}" if r.costo is not None else "—"
            lineas.append(f"  {r.describir()}  costo={costo}")
        lineas.append("=" * 60)
        return "\n".join(lineas)