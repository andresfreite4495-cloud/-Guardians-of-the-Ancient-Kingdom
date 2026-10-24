"""Guardians of the Ancient Kingdom - definición de las clases del sistema.

Este módulo solo define clases: no ejecuta nada al importarse.
"""

from abc import ABC, abstractmethod


class AtaqueInvalidoError(ValueError):
    """Se lanza cuando un ataque no cumple las reglas del combate."""


class Personaje(ABC):
    """Clase abstracta con lo que comparten todos los guardianes."""

    VIDA_MAXIMA = 100

    def __init__(self, nombre, vida, ataque, defensa):
        # Se usan los setters para que el constructor valide igual que ellos.
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa

    # ---------- helpers de validación ----------
    @staticmethod
    def _es_entero(valor):
        # bool es subclase de int en Python; se rechaza explícitamente.
        return isinstance(valor, int) and not isinstance(valor, bool)

    # ---------- nombre ----------
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str):
            raise TypeError("El nombre debe ser un texto.")
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    # ---------- vida ----------
    @property
    def vida(self):
        return self._vida

    @vida.setter
    def vida(self, valor):
        if not self._es_entero(valor):
            raise TypeError("La vida debe ser un entero.")
        if not 0 <= valor <= self.VIDA_MAXIMA:
            raise ValueError(
                f"La vida debe estar entre 0 y {self.VIDA_MAXIMA}."
            )
        self._vida = valor

    # ---------- ataque ----------
    @property
    def ataque(self):
        return self._ataque

    @ataque.setter
    def ataque(self, valor):
        if not self._es_entero(valor):
            raise TypeError("El ataque debe ser un entero.")
        if valor <= 0:
            raise ValueError("El ataque debe ser un entero positivo.")
        self._ataque = valor

    # ---------- defensa ----------
    @property
    def defensa(self):
        return self._defensa

    @defensa.setter
    def defensa(self, valor):
        if not self._es_entero(valor):
            raise TypeError("La defensa debe ser un entero.")
        if valor < 0:
            raise ValueError("La defensa no puede ser negativa.")
        self._defensa = valor

    # ---------- comportamientos comunes ----------
    def recibir_danio(self, cantidad):
        """Resta vida y devuelve el daño efectivamente recibido.

        El daño llega ya calculado: aquí NO se vuelve a restar la defensa.
        """
        if not self._es_entero(cantidad):
            raise TypeError("El daño debe ser un entero.")
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo.")
        efectivo = min(cantidad, self._vida)
        self._vida -= efectivo
        return efectivo

    def esta_vivo(self):
        return self._vida > 0

    def mostrar_estado(self):
        return (
            f"{self.nombre} ({type(self).__name__}) | "
            f"Vida: {self.vida} | Ataque: {self.ataque} | "
            f"Defensa: {self.defensa}"
        )

    def _validar_ataque(self, objetivo):
        """Validaciones comunes a todos los tipos de ataque."""
        if not isinstance(objetivo, Personaje):
            raise TypeError("El objetivo debe ser un Personaje.")
        if objetivo is self:
            raise AtaqueInvalidoError("Un personaje no puede atacarse a sí mismo.")
        if not self.esta_vivo():
            raise AtaqueInvalidoError(
                f"{self.nombre} está derrotado y no puede atacar."
            )
        if not objetivo.esta_vivo():
            raise AtaqueInvalidoError(
                f"{objetivo.nombre} ya está derrotado."
            )

    @abstractmethod
    def atacar(self, objetivo):
        """Ataca al objetivo y devuelve el daño efectivo causado."""

    def __str__(self):
        return self.mostrar_estado()


class Guerrero(Personaje):
    """Golpe poderoso: ataque +20 % antes de descontar la defensa."""

    def calcular_danio(self, objetivo):
        # Aritmética entera para evitar errores de coma flotante.
        potenciado = (self.ataque * 120) // 100  # redondeo hacia abajo
        return max(0, potenciado - objetivo.defensa)

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.calcular_danio(objetivo))


class Mago(Personaje):
    """Hechizo penetrante: ignora por completo la defensa."""

    def calcular_danio(self, objetivo):
        return self.ataque

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.calcular_danio(objetivo))


class Arquero(Personaje):
    """Disparo crítico: duplica el daño si el ataque supera la defensa."""

    def calcular_danio(self, objetivo):
        if self.ataque > objetivo.defensa:
            return (self.ataque - objetivo.defensa) * 2
        return 0

    def atacar(self, objetivo):
        self._validar_ataque(objetivo)
        return objetivo.recibir_danio(self.calcular_danio(objetivo))


class Combate:
    """Administra el enfrentamiento por turnos entre dos personajes.

    Agregación: los personajes se crean fuera y solo se reciben aquí.
    No se consulta nunca el tipo concreto: se usa polimorfismo con atacar().
    """

    MAX_RONDAS = 50

    def __init__(self, personaje1, personaje2, verbose=True):
        for p in (personaje1, personaje2):
            if not isinstance(p, Personaje):
                raise TypeError("Los participantes deben ser Personajes.")
        if personaje1 is personaje2:
            raise ValueError("Los participantes deben ser distintos.")
        if not (personaje1.esta_vivo() and personaje2.esta_vivo()):
            raise ValueError("Ambos participantes deben estar vivos.")

        self._participantes = [personaje1, personaje2]
        self._turno = 0  # índice del personaje que ataca
        self._rondas = 0
        self._ganador = None
        self._estado = "pendiente"  # victoria | empate_tecnico | empate_limite
        self._verbose = verbose

    @property
    def ganador(self):
        return self._ganador

    @property
    def estado(self):
        return self._estado

    @property
    def rondas(self):
        return self._rondas

    def _imprimir(self, texto=""):
        if self._verbose:
            print(texto)

    def cambiar_turno(self):
        self._turno = 1 - self._turno

    def verificar_ganador(self):
        """Devuelve el vencedor, o None si aún no lo hay."""
        a, b = self._participantes
        if not a.esta_vivo() and b.esta_vivo():
            return b
        if not b.esta_vivo() and a.esta_vivo():
            return a
        return None

    def iniciar(self):
        if self._estado != "pendiente":
            raise RuntimeError("El combate ya fue ejecutado.")

        self._imprimir("=== INICIO DEL COMBATE ===")
        for p in self._participantes:
            self._imprimir(p.mostrar_estado())

        while self._rondas < self.MAX_RONDAS:
            self._rondas += 1
            self._imprimir(f"\n--- Ronda {self._rondas} ---")
            danio_ronda = 0

            for _ in range(2):
                atacante = self._participantes[self._turno]
                objetivo = self._participantes[1 - self._turno]
                danio = atacante.atacar(objetivo)
                danio_ronda += danio
                self._imprimir(
                    f"{atacante.nombre} ataca a {objetivo.nombre} "
                    f"y causa {danio} de daño."
                )
                for p in self._participantes:
                    self._imprimir("  " + p.mostrar_estado())

                self._ganador = self.verificar_ganador()
                if self._ganador is not None:
                    self._estado = "victoria"
                    return self.mostrar_resultado()
                self.cambiar_turno()

            if danio_ronda == 0:
                self._estado = "empate_tecnico"
                return self.mostrar_resultado()

        self._estado = "empate_limite"
        return self.mostrar_resultado()

    def mostrar_resultado(self):
        if self._estado == "victoria":
            texto = f"Ganador: {self._ganador.nombre}"
        elif self._estado == "empate_tecnico":
            texto = "Empate técnico: una ronda completa sin daño."
        elif self._estado == "empate_limite":
            texto = f"Empate: se alcanzaron {self.MAX_RONDAS} rondas sin ganador."
        else:
            texto = "El combate aún no ha terminado."
        self._imprimir("\n=== RESULTADO ===")
        self._imprimir(texto)
        return texto
