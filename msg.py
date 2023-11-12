class Msg:
    def __init__(self, tipo, conteudo):
        self.tipo = tipo
        self.conteudo = conteudo


class Jogador:
    def __init__(self, conn, qtd_cartas):
        self.conn = conn
        self.qtd_cartas = qtd_cartas