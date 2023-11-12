import socket
import threading
import time
from config import MSG_SIZE, TIMEOUT

class Jogo:
    def __init__(self):
        self.ativo = False

def handle_client(conn):
    global clientes, clientes_prontos, jogo
    falhas = 0
    while jogo.ativo == False:
        try:
            conn.send("Você está pronto?".encode())
            conn.settimeout(TIMEOUT)
            msg = conn.recv(MSG_SIZE)
            if msg:
                if msg.decode() == "pronto":
                    clientes_prontos.append(conn)
                    wait_for_game_start(conn)
        except socket.timeout:
            falhas += 1
            print("Conexão com o cliente {} expirou ({}/4)".format(conn.getpeername(), falhas))
            if falhas == 4:
                print("Jogador caiu")
                if conn in clientes:
                    clientes.remove(conn)
                if conn in clientes_prontos:
                    clientes_prontos.remove(conn)
                conn.close()
                break
        except ConnectionResetError:
            print("Um dos jogadores desconectou")
            if conn in clientes:
                clientes.remove(conn)
            if conn in clientes_prontos:
                clientes_prontos.remove(conn)
            break

def wait_for_game_start(conn):
    global clientes, clientes_prontos, jogo
    while len(clientes_prontos) < len(clientes) or len(clientes) < 2 and len(clientes) > 0:
        conn.send("Aguardando jogadores ficarem prontos: {}/{}".format(len(clientes_prontos), len(clientes)).encode())
        if(len(clientes) < 2):
            conn.send("Aguardando mais jogadores (mínimo 2)".encode())
        time.sleep(5)
    conn.send("Jogo iniciando...".encode())
    jogo.ativo = True

def start_game():
    global clientes, jogo
    print("Jogo iniciado")
    while jogo.ativo:
        for cliente in clientes:
            print("Enviando mensagem para", cliente.getpeername())
            cliente.send("Aguardando lógica do jogo ser implementada...".encode())
        time.sleep(5)


def start():
    print("Servidor iniciado")
    global clientes, clientes_prontos, jogo
    jogo = Jogo()
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((socket.gethostbyname(socket.gethostname()), 5050))
    print("Servidor vinculado à porta 5050")
    servidor.listen()
    servidor.settimeout(TIMEOUT) 
    while jogo.ativo == False:
        print("Aguardando...")
        try:
            conn, addr = servidor.accept()
            print("Conectado a", addr)
            clientes.append(conn)
            print("Clientes:", len(clientes))
            thread = threading.Thread(target=handle_client, args=(conn,))
            thread.start()
        except socket.timeout:
            if jogo.ativo == False:
                print("Nenhuma nova conexão, tentando novamente...")
    start_game()
    
clientes = []
clientes_prontos = []
jogo = None

start()