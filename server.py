import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 5000))
server.listen()

players = []
for i in range(2):
    conn, addr = server.accept()
    players.append((conn, conn.makefile("r")))

players[0][0].sendall(b"START|WHITE\n")
players[1][0].sendall(b"START|BLACK\n")

turn = 0
while True:
    conn, f = players[turn]
    line = f.readline()
    if not line:
        break
    other = players[1 - turn][0]
    other.sendall(line.encode())
    turn = 1 - turn

for conn, f in players:
    conn.close()
