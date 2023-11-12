import socket
from config import MSG_SIZE


def start():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((socket.gethostbyname(socket.gethostname()), 5050))

    while True:
        msg = server_socket.recv(MSG_SIZE)
        if msg.decode() == "Você está pronto?":
            confirmation = input("Está pronto para jogar? (s/n) ")
            if confirmation.lower() == "s":
                print("Vamos jogar!")
                server_socket.send("pronto".encode())
            else:
                print("Talvez na próxima")
        else:
            print(msg.decode())


start()