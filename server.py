import socket
import chess  # 체스 규칙을 판정해 주는 python-chess 라이브러리를 불러온다

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

board = (
    chess.Board()
)  # 체스판을 처음 배치 상태로 만든다. 규칙 판정은 모두 이 객체가 한다
turn = 0

while True:
    conn, f = players[turn]
    other = players[1 - turn][
        0
    ]  # 상대방의 통화선. 3단계에서는 아래쪽에 있던 줄을 위로 옮겼다
    line = f.readline()
    if not line:
        break
    parts = line.strip().split(
        "|"
    )  # 끝의 줄바꿈을 지우고 "|" 기준으로 쪼갠다 (예: ["MOVE", "e2e4"])
    if (
        parts[0] != "MOVE" or len(parts) != 2
    ):  # MOVE 메시지가 아니거나 조각 수가 맞지 않으면
        conn.sendall(b"ERROR|BAD_FORMAT\n")  # 형식이 잘못됐다고 알려준다
        continue  # 차례를 바꾸지 않고 같은 사람의 다음 입력을 기다린다
    try:  # 수 문자열을 해석하다가 오류가 날 수 있으므로 보호한다
        move = chess.Move.from_uci(
            parts[1]
        )  # "e2e4" 같은 문자열을 체스 수 객체로 바꾼다
    except ValueError:  # 해석할 수 없는 문자열이라면
        conn.sendall(b"ERROR|BAD_MOVE\n")  # 수 표기가 잘못됐다고 알려준다
        continue  # 같은 사람의 다음 입력을 기다린다
    if move not in board.legal_moves:  # 지금 판에서 둘 수 없는 수라면
        conn.sendall(b"ERROR|ILLEGAL\n")  # 규칙에 어긋난 수라고 알려준다
        continue  # 차례를 바꾸지 않고 같은 사람의 다음 입력을 기다린다
    board.push(move)  # 합법적인 수이므로 서버의 체스판에 반영한다
    conn.sendall(b"OK\n")  # 수를 둔 사람에게 성공했다고 알려준다
    other.sendall(
        ("MOVE|" + parts[1] + "\n").encode()
    )  # 받은 줄 대신, 검사를 통과한 수를 다시 조립해서 상대에게 전달한다
    turn = 1 - turn

for conn, f in players:
    conn.close()
