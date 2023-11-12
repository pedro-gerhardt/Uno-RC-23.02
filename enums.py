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
    MAODECARTAS = 2
    CARTATOPO = 3
    JOGADORVEZ = 4
    QTDCARTASJOGADORES = 5
    IDJOGADOR = 6
    JOGARCARTA = 7
    PULARVEZ = 8
    COMPRARCARTA = 9

# class AcaoRodada(Enum):
#     JOGAR = 0
#     PULAR = 1
#     COMPRAR = 2