import socket, sys, pickle
sys.path.append('../')
from config import MSG_SIZE
from msg import Msg
from enums import TipoMsg
from card import Carta

mao = []
cartaTopo = None
idJogador = -1

def printaMao():
    global mao
    for c in mao: 
        print(c, end=" ")
    print("\n")


def start():
    global mao
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((socket.gethostbyname(socket.gethostname()), 5050))
    pronto = False

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
                printaMao()
            elif msg.tipo == TipoMsg.CARTATOPO:
                cartaTopo = msg.conteudo
                print("Carta no topo:", cartaTopo)
            elif msg.tipo == TipoMsg.JOGADORVEZ:
                if msg.conteudo != idJogador:
                    print("Vez do jogador", str(msg.conteudo))
                else:
                    opcao = input("Você quer jogar (J) ou comprar (C)?")
                    if opcao == "J":
                        idx = int(input("Qual carta quer jogar? (Índice)"))
                        server_socket.send(pickle.dumps(Msg(TipoMsg.JOGARCARTA, mao[idx])))
                        mao.pop(idx)
                    elif opcao == "C":
                        server_socket.send(pickle.dumps(Msg(TipoMsg.COMPRARCARTA, None)))
                        data2 = server_socket.recv(MSG_SIZE)
                        msg2 = pickle.loads(data2)
                        mao.append(msg2.conteudo)
                        printaMao()
                        opcao = input("Você quer jogar (J) ou pular (P)?")
                        if opcao == "J":
                            idx2 = int(input("Qual carta quer jogar? (Índice)"))
                            server_socket.send(pickle.dumps(Msg(TipoMsg.JOGARCARTA, mao[idx2])))
                            mao.pop(idx2)
                        elif opcao == "P":
                            server_socket.send(pickle.dumps(Msg(TipoMsg.PULARVEZ, None)))

start()