import socket

sock = socket.create_connection(("127.0.0.1", 5000))
f = sock.makefile("r")

color = f.readline().strip().split("|")[1]
print("내 색:", color)

my_turn = color == "WHITE"
while True:
    if my_turn:
        move = input("내 수: ")
        sock.sendall(("MOVE|" + move + "\n").encode())
    else:
        line = f.readline()
        if not line:
            break
        print("상대 수:", line.strip())
    my_turn = not my_turn
