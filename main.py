"""Guardians of the Ancient Kingdom - creación de objetos y casos de prueba.

Ejecutar:  python main.py
Pruebas automatizadas:  pytest -v   (ver test_personajes.py)
"""

from personajes import (
    Arquero,
    AtaqueInvalidoError,
    Combate,
    Guerrero,
    Mago,
    Personaje,
)


def titulo(texto):
    print(f"\n{'=' * 60}\n{texto}\n{'=' * 60}")


def debe_fallar(descripcion, funcion, excepcion=(ValueError, TypeError)):
    """Comprueba que la función lance la excepción esperada."""
    try:
        funcion()
    except excepcion as e:
        print(f"[OK] {descripcion} -> {type(e).__name__}: {e}")
    else:
        print(f"[FALLO] {descripcion}: no lanzó excepción")


def main():
    titulo("1. Creación correcta de los tres tipos de personajes")
    guerrero = Guerrero("Arthas", 100, 30, 20)
    mago = Mago("Gandalf", 80, 40, 10)
    arquero = Arquero("Legolas", 90, 35, 15)
    for p in (guerrero, mago, arquero):
        print(p.mostrar_estado())

    titulo("2. Rechazo de vida superior a 100 o negativa")
    debe_fallar("Vida 150", lambda: Guerrero("X", 150, 10, 5))
    debe_fallar("Vida -5", lambda: Mago("X", -5, 10, 5))

    titulo("3. Rechazo de nombres vacíos")
    debe_fallar("Nombre vacío", lambda: Arquero("", 50, 10, 5))
    debe_fallar("Nombre solo espacios", lambda: Arquero("   ", 50, 10, 5))

    titulo("4. Rechazo de ataques y defensas inválidos")
    debe_fallar("Ataque 0", lambda: Guerrero("X", 50, 0, 5))
    debe_fallar("Ataque negativo", lambda: Guerrero("X", 50, -3, 5))
    debe_fallar("Defensa negativa", lambda: Mago("X", 50, 10, -1))
    debe_fallar("Ataque no entero", lambda: Mago("X", 50, "fuerte", 1))

    titulo("5. Habilidad del Guerrero (30 de ataque vs 10 de defensa)")
    objetivo = Mago("Dummy", 100, 10, 10)
    danio = Guerrero("Tester", 100, 30, 5).atacar(objetivo)
    print(f"Daño causado: {danio} (esperado 26) | vida objetivo: {objetivo.vida}")

    titulo("6. Ataque del Mago ignorando defensa (40 vs defensa 20)")
    objetivo = Guerrero("Dummy", 100, 10, 20)
    danio = Mago("Tester", 100, 40, 5).atacar(objetivo)
    print(f"Daño causado: {danio} (esperado 40) | vida objetivo: {objetivo.vida}")

    titulo("7. Disparo crítico del Arquero (35 vs defensa 15)")
    objetivo = Guerrero("Dummy", 100, 10, 15)
    danio = Arquero("Tester", 100, 35, 5).atacar(objetivo)
    print(f"Daño causado: {danio} (esperado 40) | vida objetivo: {objetivo.vida}")
    objetivo = Guerrero("Roca", 100, 10, 50)
    danio = Arquero("Tester", 100, 35, 5).atacar(objetivo)
    print(f"Ataque no supera defensa -> daño {danio} (esperado 0)")

    titulo("8. Imposibilidad de tener vida negativa")
    victima = Guerrero("Frágil", 20, 10, 5)
    recibido = victima.recibir_danio(50)
    print(f"Daño recibido efectivo: {recibido} (esperado 20) | vida: {victima.vida}")
    debe_fallar("Daño negativo", lambda: victima.recibir_danio(-10))
    debe_fallar("Setter con vida -1", lambda: setattr(victima, "vida", -1))

    titulo("9. Imposibilidad de atacar estando derrotado")
    enemigo = Mago("Enemigo", 100, 10, 5)
    debe_fallar(
        "Derrotado ataca",
        lambda: victima.atacar(enemigo),
        AtaqueInvalidoError,
    )
    debe_fallar(
        "Atacar a un derrotado",
        lambda: enemigo.atacar(victima),
        AtaqueInvalidoError,
    )
    debe_fallar("Objetivo inválido", lambda: enemigo.atacar("no soy personaje"))

    titulo("10 y 11. Combate completo e identificación del ganador")
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf)
    combate.iniciar()
    ok = combate.ganador is gandalf
    print(f"\n[{'OK' if ok else 'FALLO'}] El ganador esperado era Gandalf")

    titulo("12. Empate técnico (combate sin daño)")
    g1 = Guerrero("Muro A", 100, 5, 30)
    g2 = Guerrero("Muro B", 100, 5, 30)
    combate = Combate(g1, g2)
    combate.iniciar()
    ok = combate.estado == "empate_tecnico" and combate.ganador is None
    print(f"\n[{'OK' if ok else 'FALLO'}] Estado: {combate.estado}")

    titulo("Extra: polimorfismo con una lista de Personaje")
    for p in (guerrero, mago, arquero):
        rival = Guerrero("Saco", 100, 10, 12)
        print(f"{p.nombre} -> daño {p.atacar(rival)}")

    titulo("Extra: Personaje es abstracta")
    debe_fallar("Instanciar Personaje", lambda: Personaje("X", 10, 10, 10), TypeError)


if __name__ == "__main__":
    main()
