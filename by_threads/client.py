import socket
import threading

def send(msg):
    client.send(str(len(msg)).encode('utf-8').ljust(64))
    client.send(msg.encode('utf-8'))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostbyname(socket.gethostname()), 5050))

send("Hello world!")