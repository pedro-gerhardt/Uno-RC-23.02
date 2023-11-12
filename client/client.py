import socket, sys, pickle
sys.path.append('../')
from config import MSG_SIZE
from msg import Msg
from enums import TipoMsg
from card import Carta

mao = []

def start():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((socket.gethostbyname(socket.gethostname()), 5050))
    pronto = False

    while True:
        data = memoryview(bytearray(MSG_SIZE))
        bc = server_socket.recv_into(data, MSG_SIZE)
        if bc == 0:
            continue
        msg = pickle.loads(data)
        print(msg.tipo)
        if not pronto and msg.tipo == TipoMsg.PRONTO:
            confirmation = input("Está pronto para jogar? (s/n) ")
            if confirmation.lower() == "s":
                print("Vamos jogar!")
                server_socket.send(pickle.dumps(Msg(TipoMsg.PRONTO, True)))
                pronto = True
            else:
                print("Talvez na próxima")
        elif msg.tipo == TipoMsg.MSGSIMPLES:
            print(msg.conteudo)
        elif msg.tipo == TipoMsg.CARTAS:
            print(len(msg.conteudo))
            mao = msg.conteudo
            for c in mao: print(c)

start()