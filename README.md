Software FJ

Sistema en Python orientado a objetos, que gestiona clientes, 
servicios (reserva de salas, alquiler de equipos, asesorías) y
reservas para la empresa **Software FJ**.

Conceptos aplicados

- **Abstracción**: `Entidad` y `Servicio` son `ABC` con métodos abstractos.
- **Herencia**: `Cliente`, `Servicio` heredan de `Entidad`; `ReservaSala`,
  `AlquilerEquipo`, `Asesoria` heredan de `Servicio`.
- **Polimorfismo**: `calcular_costo` y `validar_parametros` se sobrescriben
  en cada servicio.
- **Encapsulación**: `Cliente` usa `@property` con validación estricta.
- **Sobrecarga**: `aplicar_impuestos_descuentos(subtotal, descuento, incluir_iva)`
  y variantes de `calcular_costo` con parámetros opcionales.
- **Excepciones**: jerarquía propia + `try/except`, `try/except/else`,
  `try/except/finally`, **encadenamiento** con `raise ... from ...`.
- **Logs**: todos los errores y eventos relevantes quedan en `eventos.log`.
- **Estabilidad**: el `main` ejecuta operaciones válidas e inválidas y nunca
  se interrumpe.
