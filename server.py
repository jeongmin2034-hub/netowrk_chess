import socket
import chess  # 체스 규칙을 판정해 주는 python-chess 라이브러리를 불러온다

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 5000))
server.listen()

players = []
for i in range(2):
    conn, addr = server.accept()
    players.append(
        (conn, conn.makefile("r", encoding="utf-8"))
    )  # 받는 글자를 UTF-8로 읽어 한글이 와도 깨지거나 죽지 않게 한다

board = (
    chess.Board()
)  # 체스판을 처음 배치 상태로 만든다. 규칙 판정은 모두 이 객체가 한다

players[0][0].sendall(b"START|WHITE\n")
players[1][0].sendall(b"START|BLACK\n")

first = (
    "BOARD|-|" + board.fen() + "\n"
).encode()  # 시작 보드 메시지. 둔 수가 없으므로 수 자리에 "-"를 넣는다
for conn, f in players:  # 두 플레이어 모두에게
    conn.sendall(first)  # 시작 보드를 보낸다

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
    msg = (
        "BOARD|" + parts[1] + "|" + board.fen() + "\n"
    ).encode()  # "BOARD|수|FEN" 메시지를 만든다. 4단계의 OK와 MOVE를 이것 하나로 대체한다
    conn.sendall(msg)  # 수를 둔 사람에게 보낸다. 이 메시지가 곧 성공 응답이다
    other.sendall(msg)  # 상대에게도 똑같은 메시지를 보낸다
    turn = 1 - turn

for conn, f in players:
    conn.close()
