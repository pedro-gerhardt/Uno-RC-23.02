import socket, sys, pickle
sys.path.append('../')
from config import MSG_SIZE
from msg import Msg
from enums import TipoMsg
from card import Carta

mao = []
server_socket = None

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
    idx = int(input("Qual carta quer jogar? (Índice) "))
    # fazer validacao se index correto;
    # fazer validacao se carta preta, pedir uma cor, enviar junto e tratar no servidor
    server_socket.send(pickle.dumps(Msg(TipoMsg.JOGARCARTA, mao[idx])))
    print("Você jogou a carta", mao.pop(idx))

def compraCarta():
    global server_socket, mao
    server_socket.send(pickle.dumps(Msg(TipoMsg.COMPRARCARTA, None)))
    msg2 = pickle.loads(server_socket.recv(MSG_SIZE))
    mao.append(msg2.conteudo)
    printaMao()
    opcao = input("Você quer jogar (J) ou pular (P)?")
    if opcao == "J":
        jogaCarta()
    elif opcao == "P":
        pulaVez()

def start():
    global mao, server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((socket.gethostbyname(socket.gethostname()), 5050))
    pronto = False; cartaTopo = None; idJogador = -1
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