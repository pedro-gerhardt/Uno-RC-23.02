from enums import Color

CVERM = '\033[91m'
CVERD = '\033[92m'
CAMAR = '\033[93m'
CAZUL = '\033[94m'
CFIM = '\033[0m'

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
