import socket, sys, pickle
sys.path.append('../')
from config import MSG_SIZE
from msg import Msg
from enums import Color, TipoMsg
from card import Carta

mao = []
server_socket = None
cartaTopo = None

def printaMao():
    global mao
    for c in mao: 
        print(c, end=" ")
    print("\n")

def pulaVez():
    global server_socket
    server_socket.send(pickle.dumps(Msg(TipoMsg.PULARVEZ, None)))
    print("Você pulou a vez")

def jogaCarta():
    global mao, server_socket
    if not validaMao():
        print("Você não pode jogar nenhuma carta! Comprando uma nova carta...")
        compraCarta()
        return None
    while True:
        idx = int(input("Qual carta quer jogar? (Índice) "))
        if validaIndex(idx):
            cartaJogada = mao[idx]
            if not validaCarta(cartaJogada):
                print("Carta seleciona não pode ser jogada!\n")
                opcao = input("Você quer tentar jogar outra carta (J) ou comprar uma nova (C)? ")
                if opcao == "J":
                    continue
                elif opcao == "C":
                    compraCarta()
                    break
                continue
            server_socket.send(pickle.dumps(Msg(TipoMsg.JOGARCARTA, mao[idx])))
            print("Você jogou a carta", mao.pop(idx))
            break
        else:
            idx = int(input("Carta seleciona está fora do range! Escolha outra: "))

def validaMao():
    global mao
    for carta in mao:
        if validaCarta(carta):
            return True
    return False

def validaCarta(carta):
    global cartaTopo
    if (carta.cor == cartaTopo.cor) or (carta.simbolo == cartaTopo.simbolo) or (carta.cor == Color(4)):
        return True
    return False

def validaIndex(index):
    global mao
    return ((index + 1 <= len(mao)) and (index > -1))

def compraCarta():
    global server_socket, mao
    server_socket.send(pickle.dumps(Msg(TipoMsg.COMPRARCARTA, None)))
    msg2 = pickle.loads(server_socket.recv(MSG_SIZE))
    mao.append(msg2.conteudo)
    printaMao()
    opcao = input("Você quer jogar (J) ou pular (P)? ")
    if opcao == "J":
        jogaCarta()
    elif opcao == "P":
        pulaVez()

def start():
    global mao, server_socket, cartaTopo
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((socket.gethostbyname(socket.gethostname()), 5050))
    pronto = False; idJogador = -1
    while True:
        data = memoryview(bytearray(MSG_SIZE))
        bc = server_socket.recv_into(data, MSG_SIZE)
        # print(bc)
        if bc == 0:
            continue
        msgs = pickle.loads(data)        
        for msg in msgs:
            if not pronto and msg.tipo == TipoMsg.PRONTO:
                confirmation = input("Está pronto para jogar? (s/n) ")
                if confirmation.lower() == "s":
                    print("Vamos jogar!")
                    server_socket.send(pickle.dumps(Msg(TipoMsg.PRONTO, True)))
                    pronto = True
                else:
                    print("Talvez na próxima")
            if msg.tipo == TipoMsg.IDJOGADOR:
                idJogador = msg.conteudo
            elif msg.tipo == TipoMsg.MSGSIMPLES:
                print(msg.conteudo)
            elif msg.tipo == TipoMsg.MAODECARTAS:
                mao = msg.conteudo
            elif msg.tipo == TipoMsg.CARTATOPO:
                cartaTopo = msg.conteudo
                print("Carta no topo:", cartaTopo)
            elif msg.tipo == TipoMsg.JOGADORVEZ:
                if msg.conteudo != idJogador:
                    print("Vez do jogador", str(msg.conteudo))
                else:
                    printaMao()
                    opcao = input("Você quer jogar (J) ou comprar (C)? ")
                    if opcao == "J":
                        jogaCarta()
                    elif opcao == "C":
                        compraCarta()

start()