import socket, json, threading, time, sys, random, pickle
sys.path.append('../')
from config import MSG_SIZE, TIMEOUT, QTD_CARTAS_INICIAIS
from card import Carta
from enums import Color, TipoMsg
from msg import Msg

class Jogo:
    def __init__(self):
        self.ativo = False



def criaBaralho():
    for _ in range(2):
        for c in range(4):
            for n in range(10):
                cartasAJogar.append(Carta(Color(c), str(n)))
            cartasAJogar.append(Carta(Color(c), '⇆'))
            cartasAJogar.append(Carta(Color(c), 'Ø'))
            cartasAJogar.append(Carta(Color(c), '+2'))

    for _ in range(4):
        cartasAJogar.append(Carta(Color(4), '⊕'))
        cartasAJogar.append(Carta(Color(4), '+4'))

def embaralhaBaralho():
    random.shuffle(cartasAJogar)

def sorteaCartasParaJogadores(num_clientes):
    global maosClientes, cartasAJogar
    maosClientes.clear()
    for i in range(num_clientes):
        maosClientes.append([])
        for _ in range(QTD_CARTAS_INICIAIS):
            # fazer validacao se cartasAJogar não está vazia; se estiver, chamar processo de reembaralhar pilha
            maosClientes[i].append(cartasAJogar.pop())

def enviaMaosParaJogadores():
    global clientes
    for c in range(len(clientes)):
        print("Enviando mãos aos jogadores...")
        pick = pickle.dumps(Msg(TipoMsg.CARTAS, maosClientes[c]))
        print(clientes[c].send(pick))
        # clientes[c].send(pickle.dumps(maosClientes[c]))
        # clientes[c].send(json.dumps(vars(maosClientes[c])).encode())
        

def handle_client(conn):
    global clientes, clientes_prontos, jogo
    falhas = 0
    while jogo.ativo == False:
        try:
            # conn.send("Você está pronto?".encode())
            conn.send(pickle.dumps(Msg(TipoMsg.PRONTO, "Você está pronto?")))
            conn.settimeout(TIMEOUT)
            data = conn.recv(MSG_SIZE)
            msg = pickle.loads(data)
            if msg:
                if msg.tipo == TipoMsg.PRONTO and type(msg.conteudo) == type(True) and msg.conteudo == True:
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
        conn.send(pickle.dumps(Msg(TipoMsg.MSGSIMPLES, "Aguardando jogadores ficarem prontos: {}/{}".format(len(clientes_prontos), len(clientes)))))
        # conn.send("Aguardando jogadores ficarem prontos: {}/{}".format(len(clientes_prontos), len(clientes)).encode())
        if(len(clientes) < 2):
            conn.send(pickle.dumps(Msg(TipoMsg.MSGSIMPLES, "Aguardando mais jogadores (mínimo 2)")))
            # conn.send("Aguardando mais jogadores (mínimo 2)".encode())
        time.sleep(5)
    conn.send(pickle.dumps(Msg(TipoMsg.MSGSIMPLES , "Jogo iniciando...")))
    # conn.send("Jogo iniciando...".encode())
    jogo.ativo = True

def start_game():
    global clientes, jogo
    print("Jogo iniciado")
    criaBaralho()
    print("Tamanho do baralho: ", len(cartasAJogar))
    embaralhaBaralho()
    sorteaCartasParaJogadores(len(clientes))
    cartasJogadas.append(cartasAJogar.pop())
    enviaMaosParaJogadores()
    # while jogo.ativo:
    #     for cliente in clientes:
    #         print("Enviando mensagem para", cliente.getpeername())
    #         cliente.send("Aguardando lógica do jogo ser implementada...".encode())
    #     time.sleep(5)

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
cartasAJogar = []
cartasJogadas = []
maosClientes = []

start()