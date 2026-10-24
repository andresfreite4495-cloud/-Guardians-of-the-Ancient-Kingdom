import pytest

from personajes import (
    Arquero,
    AtaqueInvalidoError,
    Combate,
    Guerrero,
    Mago,
    Personaje,
)


# ---------- creación ----------
@pytest.mark.parametrize(
    "clase", [Guerrero, Mago, Arquero], ids=lambda c: c.__name__
)
def test_creacion_valida(clase):
    p = clase("Hero", 100, 30, 10)
    assert (p.nombre, p.vida, p.ataque, p.defensa) == ("Hero", 100, 30, 10)
    assert p.esta_vivo()


def test_personaje_es_abstracto():
    with pytest.raises(TypeError):
        Personaje("X", 10, 10, 10)


@pytest.mark.parametrize("vida", [101, 150, -1, -50])
def test_vida_fuera_de_rango(vida):
    with pytest.raises(ValueError):
        Guerrero("X", vida, 10, 5)


@pytest.mark.parametrize("nombre", ["", "   "])
def test_nombre_vacio(nombre):
    with pytest.raises(ValueError):
        Mago(nombre, 50, 10, 5)


@pytest.mark.parametrize("ataque,defensa", [(0, 5), (-3, 5), (10, -1)])
def test_ataque_o_defensa_invalidos(ataque, defensa):
    with pytest.raises(ValueError):
        Arquero("X", 50, ataque, defensa)


def test_tipos_invalidos():
    with pytest.raises(TypeError):
        Guerrero("X", "50", 10, 5)
    with pytest.raises(TypeError):
        Guerrero("X", 50, 10.5, 5)


def test_setters_validan():
    p = Guerrero("X", 50, 10, 5)
    with pytest.raises(ValueError):
        p.vida = 101
    with pytest.raises(ValueError):
        p.ataque = 0
    p.defensa = 0
    assert p.defensa == 0


# ---------- daño de cada clase ----------
def test_dano_guerrero():
    assert Guerrero("G", 100, 30, 5).atacar(Mago("M", 100, 5, 10)) == 26


def test_dano_guerrero_redondea_hacia_abajo_y_no_negativo():
    # 33 * 1.2 = 39.6 -> 39; 39 - 10 = 29
    assert Guerrero("G", 100, 33, 5).atacar(Mago("M", 100, 5, 10)) == 29
    assert Guerrero("G", 100, 10, 5).atacar(Mago("M", 100, 5, 50)) == 0


def test_dano_mago_ignora_defensa():
    assert Mago("M", 100, 40, 5).atacar(Guerrero("G", 100, 5, 20)) == 40


def test_dano_arquero_critico():
    assert Arquero("A", 100, 35, 5).atacar(Guerrero("G", 100, 5, 15)) == 40


def test_arquero_sin_dano_si_no_supera_defensa():
    assert Arquero("A", 100, 15, 5).atacar(Guerrero("G", 100, 5, 15)) == 0
    assert Arquero("A", 100, 10, 5).atacar(Guerrero("G", 100, 5, 15)) == 0


# ---------- vida y estado ----------
def test_vida_nunca_negativa():
    p = Guerrero("G", 20, 10, 5)
    assert p.recibir_danio(50) == 20
    assert p.vida == 0
    assert not p.esta_vivo()


def test_recibir_danio_no_aplica_defensa_de_nuevo():
    p = Guerrero("G", 100, 10, 50)
    assert p.recibir_danio(10) == 10
    assert p.vida == 90


def test_danio_negativo_rechazado():
    with pytest.raises(ValueError):
        Guerrero("G", 100, 10, 5).recibir_danio(-1)


# ---------- ataques inválidos ----------
def test_derrotado_no_puede_atacar():
    muerto = Mago("M", 10, 10, 5)
    muerto.recibir_danio(10)
    with pytest.raises(AtaqueInvalidoError):
        muerto.atacar(Guerrero("G", 100, 10, 5))


def test_no_se_puede_atacar_a_un_derrotado():
    muerto = Guerrero("G", 10, 10, 5)
    muerto.recibir_danio(10)
    with pytest.raises(AtaqueInvalidoError):
        Mago("M", 100, 10, 5).atacar(muerto)


def test_objetivo_invalido():
    with pytest.raises(TypeError):
        Mago("M", 100, 10, 5).atacar("nadie")


# ---------- combate ----------
def test_combate_ejemplo_del_enunciado():
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    c = Combate(arthas, gandalf, verbose=False)
    c.iniciar()
    assert c.ganador is gandalf
    assert c.estado == "victoria"
    assert arthas.vida == 0
    assert gandalf.vida == 2


def test_empate_tecnico():
    c = Combate(
        Guerrero("A", 100, 5, 30), Guerrero("B", 100, 5, 30), verbose=False
    )
    c.iniciar()
    assert c.estado == "empate_tecnico"
    assert c.ganador is None
    assert c.rondas == 1


def test_empate_por_limite_de_rondas():
    # Dos magos con ataque 1: cada turno causa 1 de daño, así que tras
    # 50 rondas cada uno conserva 50 de vida y nadie gana.
    a = Mago("A", 100, 1, 5)
    b = Mago("B", 100, 1, 5)
    c = Combate(a, b, verbose=False)
    c.iniciar()
    assert c.estado == "empate_limite"
    assert c.ganador is None
    assert c.rondas == Combate.MAX_RONDAS
    assert a.vida == 50 and b.vida == 50


def test_combate_valida_participantes():
    g = Guerrero("G", 100, 10, 5)
    with pytest.raises(TypeError):
        Combate(g, "no soy personaje")
    with pytest.raises(ValueError):
        Combate(g, g)


def test_combate_no_se_ejecuta_dos_veces():
    c = Combate(
        Guerrero("A", 100, 30, 5), Mago("B", 50, 10, 5), verbose=False
    )
    c.iniciar()
    with pytest.raises(RuntimeError):
        c.iniciar()
