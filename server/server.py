import socket, json, threading, time, sys, random, pickle
sys.path.append('../')
from config import MSG_SIZE, TIMEOUT, QTD_CARTAS_INICIAIS
from card import Carta
from enums import Color, TipoMsg
from msg import Msg, Jogador

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

def embaralhaBaralho(baralho):
    for carta in baralho:
        if carta.simbolo == '+4' or carta.simbolo == '⊕':
            carta.cor = Color(4)
    random.shuffle(baralho)

def pescaDoBaralho():
    global cartasAJogar, cartasJogadas
    if len(cartasAJogar) < 1 and len(cartasJogadas) > 0:
        cartasAJogar = cartasJogadas[:-1]
        cartasJogadas = cartasJogadas[-1]
        embaralhaBaralho(cartasAJogar)
    return cartasAJogar.pop()
        
def sorteaEnviaMaosParaJogadores():
    global cartasAJogar, clientes
    for c in clientes:
        mao = []
        for _ in range(QTD_CARTAS_INICIAIS):
            mao.append(pescaDoBaralho())   
        c.conn.send(pickle.dumps([Msg(TipoMsg.MAODECARTAS, mao)]))

def jogouCarta(jogadorDaRodada, carta):
    global clientes, cartasJogadas, sentidoJogo
    print("Jogador", jogadorDaRodada, "jogou a carta", carta)
    cartasJogadas.append(carta)
    if carta.simbolo == '⇆':
        if len(clientes) == 2:
            validarJogadorDaRodada()
        else:
            sentidoJogo = not sentidoJogo
    elif carta.simbolo == 'Ø':
        validarJogadorDaRodada()
    elif carta.simbolo == '+2':
        validarJogadorDaRodada()
        for _ in range(2):
            comprouCarta()
    elif carta.simbolo == '+4':
        validarJogadorDaRodada()
        for _ in range(4):
            comprouCarta()

def comprouCarta():
    print("Jogador", jogadorDaRodada, "comprou uma carta")
    clientes[jogadorDaRodada - 1].conn.send(pickle.dumps(Msg(TipoMsg.COMPRARCARTA, pescaDoBaralho())))

def validarJogadorDaRodada():
    global clientes, sentidoJogo, jogadorDaRodada
    if sentidoJogo:
        jogadorDaRodada = 1 if jogadorDaRodada >= len(clientes) else jogadorDaRodada + 1
    else:
        jogadorDaRodada = len(clientes) if jogadorDaRodada == 1 else jogadorDaRodada - 1

def handle_client(jogador):
    global clientes, clientes_prontos, jogo
    falhas = 0
    conn = jogador.conn
    while jogo.ativo == False:
        try:
            listMsg = [Msg(TipoMsg.PRONTO, "Você está pronto?"),
                       Msg(TipoMsg.IDJOGADOR, len(clientes))]
            conn.send(pickle.dumps(listMsg))
            conn.settimeout(TIMEOUT)
            data = conn.recv(MSG_SIZE)
            msg = pickle.loads(data)
            if msg:
                if msg.tipo == TipoMsg.PRONTO and type(msg.conteudo) == type(True) and msg.conteudo == True:
                    clientes_prontos.append(jogador)
                    wait_for_game_start(conn)
        except socket.timeout:
            falhas += 1
            print("Conexão com o cliente {} expirou ({}/4)".format(conn.getpeername(), falhas))
            if falhas == 4:
                print("Jogador caiu")
                if jogador in clientes:
                    clientes.remove(jogador)
                if jogador in clientes_prontos:
                    clientes_prontos.remove(jogador)
                conn.close()
                break
        except ConnectionResetError:
            print("Um dos jogadores desconectou")
            if jogador in clientes:
                clientes.remove(jogador)
            if jogador in clientes_prontos:
                clientes_prontos.remove(jogador)
            break

def wait_for_game_start(conn):
    global clientes, clientes_prontos, jogo
    while len(clientes_prontos) < len(clientes) or len(clientes) < 2 and len(clientes) > 0:
        conn.send(pickle.dumps([Msg(TipoMsg.MSGSIMPLES, "Aguardando jogadores ficarem prontos: {}/{}".format(len(clientes_prontos), len(clientes)))]))
        if(len(clientes) < 2):
            conn.send(pickle.dumps([Msg(TipoMsg.MSGSIMPLES, "Aguardando mais jogadores (mínimo 2)")]))
        time.sleep(5)
    conn.send(pickle.dumps([Msg(TipoMsg.MSGSIMPLES , "Jogo iniciando...")]))
    jogo.ativo = True

def start_game():
    global clientes, jogo, cartasJogadas, jogadorDaRodada
    print("Jogo iniciado")
    criaBaralho()
    embaralhaBaralho(cartasAJogar)
    sorteaEnviaMaosParaJogadores()
    cartasJogadas.append(pescaDoBaralho())
    while jogo.ativo:
        try:
            for cliente in clientes:
                print("Enviando mensagem para", cliente.conn.getpeername())
                listMsg = [Msg(TipoMsg.CARTATOPO, cartasJogadas[-1]),
                        Msg(TipoMsg.JOGADORVEZ, jogadorDaRodada)]
                cliente.conn.send(pickle.dumps(listMsg))
            data = clientes[jogadorDaRodada - 1].conn.recv(MSG_SIZE)
            msg = pickle.loads(data)
            if msg.tipo == TipoMsg.JOGARCARTA:
                jogouCarta(jogadorDaRodada, msg.conteudo)
                validarJogadorDaRodada()
            elif msg.tipo == TipoMsg.COMPRARCARTA:
                comprouCarta()
                data2 = clientes[jogadorDaRodada - 1].conn.recv(MSG_SIZE)
                msg2 = pickle.loads(data2)
                if msg2.tipo == TipoMsg.JOGARCARTA:
                    jogouCarta(jogadorDaRodada, msg2.conteudo)
                elif msg2.tipo == TipoMsg.PULARVEZ:
                    print("Jogador", jogadorDaRodada, "pulou a vez")
                validarJogadorDaRodada()
            elif msg.tipo == TipoMsg.VITORIA:
                for cliente in clientes:
                    cliente.conn.send(pickle.dumps(Msg(TipoMsg.VITORIA, "Jogador {} venceu o jogo!".format(jogadorDaRodada))))
                jogo.ativo = False
                break
        except socket.timeout:
            print("Jogador {} não respondeu a tempo, pulando a vez...".format(jogadorDaRodada))
            validarJogadorDaRodada()
        except ConnectionResetError:
            disconnected_player = None
            for i, cliente in enumerate(clientes):
                try:
                    cliente.conn.send(pickle.dumps(Msg(TipoMsg.MSGSIMPLES, "Checking connection...")))
                except ConnectionResetError:
                    disconnected_player = i + 1
                    break
            if disconnected_player is not None:
                print("Jogador {} foi desconectado.".format(disconnected_player))
                clientes.pop(disconnected_player - 1)
            if len(clientes) == 0:
                jogo.ativo = False
                print("Todos os jogadores foram desconectados. O jogo acabou.")
        time.sleep(1)

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
            jogador = Jogador(conn, QTD_CARTAS_INICIAIS)
            clientes.append(jogador)
            print("Clientes:", len(clientes))
            thread = threading.Thread(target=handle_client, args=(jogador,))
            thread.start()
        except socket.timeout:
            if jogo.ativo == False:
                print("Nenhuma nova conexão, tentando novamente...")
    start_game()
    print("Jogo terminado")
    
clientes = []
clientes_prontos = []
jogo = None
cartasAJogar = []
cartasJogadas = []
sentidoJogo = False
jogadorDaRodada = 1

start()