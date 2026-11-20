import socket


def show(fen):  # 새로 추가: FEN 문자열을 8x8 글자 보드로 출력하는 함수
    rows = fen.split()[0].split(
        "/"
    )  # FEN의 첫 덩어리(말 배치)를 "/" 기준으로 8줄로 나눈다
    for i, row in enumerate(rows):  # 8번째 줄부터 한 줄씩 꺼낸다 (i는 0부터 7까지)
        line = ""  # 이 줄을 글자로 만들 빈 문자열
        for ch in row:  # 줄의 글자를 하나씩 본다
            line += (
                "." * int(ch) if ch.isdigit() else ch
            )  # 숫자면 그 개수만큼 빈칸(.), 글자면 말 그대로 붙인다
        print(8 - i, " ".join(line))  # 줄 번호와 함께, 칸 사이를 띄워서 출력한다
    print("  a b c d e f g h")  # 아래쪽에 열 이름을 출력한다


sock = socket.create_connection(("127.0.0.1", 5000))
f = sock.makefile("r", encoding="utf-8")

color = f.readline().strip().split("|")[1]
print("내 색:", color)
show(f.readline().strip().split("|")[2])  # 서버가 보낸 시작 보드를 읽어서 출력한다

my_turn = color == "WHITE"
while True:
    if my_turn:
        move = input("내 수: ")
        sock.sendall(("MOVE|" + move + "\n").encode())
        reply = f.readline().strip()
        if not reply:  # 빈 값이면 서버와 연결이 끊긴 것이다
            break
        if reply.startswith("ERROR"):
            print("잘못된 수:", reply)
            continue
    else:
        reply = (
            f.readline().strip()
        )  # 상대가 둔 뒤 서버가 보내는 BOARD 메시지를 기다린다
        if not reply:
            break
        print("상대 수:", reply.split("|")[1])  # BOARD|수|FEN에서 수 부분만 출력한다
    show(
        reply.split("|")[2]
    )  # 내 차례였든 아니든, 받은 메시지의 FEN으로 새 보드를 출력한다
    my_turn = not my_turn
