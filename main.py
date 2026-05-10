"""
Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas.

Demostración de POO + manejo avanzado de excepciones SIN base de datos.
Ejecuta al menos 10 operaciones (válidas e inválidas) y mantiene la app estable.
"""
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    SoftwareFJError,
)
from entidades import (
    Asesoria,
    AlquilerEquipo,
    GestorSoftwareFJ,
    ReservaSala,
)
from logger import get_logger

log = get_logger("main")


def banner(texto: str) -> None:
    print(f"\n--- {texto} ---")


def main() -> None:
    log.info("===== INICIO DE EJECUCIÓN =====")
    g = GestorSoftwareFJ()

    # ---------------- 1-3. Registro de clientes (válidos e inválidos) ----------
    banner("1) Cliente válido")
    ana = g.registrar_cliente(nombre="Ana Gómez", documento="CC12345",
                              email="ana@example.com", telefono="3001112233")
    print(ana)

    banner("2) Cliente válido")
    luis = g.registrar_cliente(nombre="Luis Pérez", documento="CC98765",
                               email="luis@example.com", telefono="3014445566")
    print(luis)

    banner("3) Cliente INVÁLIDO (email mal formado)")
    invalido = g.registrar_cliente(nombre="Pepe", documento="CC11111",
                                   email="correo-malo", telefono="3000000000")
    print("Resultado:", invalido)

    # ---------------- 4-5. Servicios (válidos e inválidos) --------------------
    banner("4) Servicios válidos")
    sala = g.registrar_servicio(ReservaSala("Sala Ejecutiva", precio_hora=50_000, capacidad=10))
    equipo = g.registrar_servicio(AlquilerEquipo("Proyector 4K", precio_dia=80_000, deposito=100_000))
    asesoria = g.registrar_servicio(Asesoria("Consultoría Cloud", precio_hora=120_000,
                                             especialidad="AWS", recargo=0.20))
    for s in (sala, equipo, asesoria):
        print(s.describir())

    banner("5) Servicio INVÁLIDO (precio negativo)")
    try:
        ReservaSala("Sala Mala", precio_hora=-10, capacidad=5)
    except SoftwareFJError as e:
        log.warning("Servicio rechazado: %s", e)
        print(f"[OK] Excepción capturada: {e}")

    # ---------------- 6. Reserva exitosa --------------------------------------
    banner("6) Reserva válida (sala, 3h, 8 asistentes)")
    r1 = g.crear_reserva(ana, sala, horas=3, asistentes=8)
    if r1:
        r1.confirmar()
        print(f"Costo procesado: ${r1.procesar():,.2f}")

    # ---------------- 7. Reserva con descuento ---------------------------------
    banner("7) Reserva válida (asesoría, 5h, 10% desc)")
    r2 = g.crear_reserva(luis, asesoria, horas=5, descuento=0.10)
    if r2:
        r2.confirmar()
        print(f"Costo procesado: ${r2.procesar():,.2f}")

    # ---------------- 8. Reserva FALLIDA: parámetros inválidos -----------------
    banner("8) Reserva inválida (asistentes > capacidad)")
    r3 = g.crear_reserva(ana, sala, horas=2, asistentes=99)
    print("Resultado:", r3)

    # ---------------- 9. Reserva FALLIDA: servicio no disponible ---------------
    banner("9) Reserva con servicio NO disponible")
    equipo.disponible = False
    r4 = g.crear_reserva(luis, equipo, dias=2)
    print("Resultado:", r4)
    equipo.disponible = True  # se restaura

    # ---------------- 10. Operación NO permitida (cancelar dos veces) ----------
    banner("10) Reserva, cancelar y volver a cancelar")
    r5 = g.crear_reserva(ana, equipo, dias=4)
    if r5:
        r5.cancelar()
        try:
            r5.cancelar()  # ya cancelada
        except OperacionNoPermitidaError as e:
            log.warning("Operación rechazada: %s", e)
            print(f"[OK] Excepción capturada: {e}")

    # ---------------- 11. Cálculo inconsistente (descuento > 1) ----------------
    banner("11) Cálculo inconsistente capturado")
    try:
        sala.calcular_costo(horas=2, asistentes=4, descuento=1.5)
    except CalculoInconsistenteError as e:
        log.error("Cálculo inválido: %s", e)
        print(f"[OK] Excepción capturada: {e}")

    # ---------------- 12. Sobrecarga: cálculo sin IVA --------------------------
    banner("12) Sobrecarga de cálculo (sin IVA)")
    subtotal = asesoria.precio_base * 2 * (1 + asesoria.recargo)
    total_sin_iva = asesoria.aplicar_impuestos_descuentos(subtotal, descuento=0.05, incluir_iva=False)
    print(f"Asesoría 2h con 5% desc, SIN IVA: ${total_sin_iva:,.2f}")

    # ---------------- Resumen final --------------------------------------------
    print(g.resumen())
    log.info("===== FIN DE EJECUCIÓN =====")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # red de seguridad: la app nunca se cae sin loguear
        log.critical("Excepción no controlada: %s", e, exc_info=True)
        print(f"[FATAL] {e} (revisar eventos.log)")