"""Excepciones personalizadas del sistema Software FJ."""

class SoftwareFJError(Exception):
    """Excepción base del sistema."""


class DatosInvalidosError(SoftwareFJError):
    """Se lanza cuando los datos de entrada no son válidos."""


class ClienteInvalidoError(DatosInvalidosError):
    """Error en la creación o validación de un cliente."""


class ServicioInvalidoError(DatosInvalidosError):
    """Error en la creación o validación de un servicio."""


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio solicitado no está disponible."""


class ReservaInvalidaError(SoftwareFJError):
    """Error al crear o procesar una reserva."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se intentó una operación no permitida (ej. cancelar reserva ya cancelada)."""


class CalculoInconsistenteError(SoftwareFJError):
    """Error en el cálculo de costos o totales."""
