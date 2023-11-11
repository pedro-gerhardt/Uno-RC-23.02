from enum import Enum

CVERM = '\033[91m'
CVERD = '\033[92m'
CAMAR = '\033[93m'
CAZUL = '\033[94m'
CFIM = '\033[0m'

class Color(Enum):
    VERM = 0
    VERD = 1
    AMAR = 2
    AZUL = 3 
    PRET = 4

class Carta:
    def __init__(self, cor, simbolo):
        self.cor = cor
        self.simbolo = simbolo

    def __str__(self):
        if self.cor == Color.VERM:
            return f"{CVERM + self.simbolo + CFIM}"
        if self.cor == Color.VERD:
            return f"{CVERD + self.simbolo + CFIM}"
        if self.cor == Color.AMAR:
            return f"{CAMAR + self.simbolo + CFIM}"
        if self.cor == Color.AZUL:
            return f"{CAZUL + self.simbolo + CFIM}"
        if self.cor == Color.PRET:
            return f"{self.simbolo}"

# cartas = []

# for _ in range(2):
#     for c in range(4):
#         for n in range(10):
#             cartas.append(Carta(Color(c), str(n)))
#         cartas.append(Carta(Color(c), '⇆'))
#         cartas.append(Carta(Color(c), 'Ø'))
#         cartas.append(Carta(Color(c), '+2'))

# for _ in range(4):
#     cartas.append(Carta(Color(4), '⊕'))
#     cartas.append(Carta(Color(4), '+4'))


# for c in cartas:
#     print(c)