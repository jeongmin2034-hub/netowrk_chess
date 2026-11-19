import socket

sock = socket.create_connection(("127.0.0.1", 5000))
f = sock.makefile("r", encoding="utf-8")  # 서버가 보낸 글자도 UTF-8로 읽는다

color = f.readline().strip().split("|")[1]
print("내 색:", color)

my_turn = color == "WHITE"
while True:
    if my_turn:
        move = input("내 수: ")
        sock.sendall(("MOVE|" + move + "\n").encode())
        reply = (
            f.readline().strip()
        )  # 서버의 판정 결과(OK 또는 ERROR)를 기다려서 읽는다
        if reply.startswith("ERROR"):  # 서버가 거절했다면
            print("잘못된 수:", reply)  # 거절 이유를 출력한다
            continue  # 차례를 바꾸지 않고 처음으로 돌아가 다시 입력받는다
    else:
        line = f.readline()
        if not line:
            break
        print("상대 수:", line.strip())
    my_turn = not my_turn
