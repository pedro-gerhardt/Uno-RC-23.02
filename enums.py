from enum import Enum

class Color(Enum):
    VERM = 0
    VERD = 1
    AMAR = 2
    AZUL = 3 
    PRET = 4

class TipoMsg(Enum):
    MSGSIMPLES = 0
    PRONTO = 1
    CARTAS = 2