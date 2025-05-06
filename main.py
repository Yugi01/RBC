import chess

fen_input = input()

board = chess.Board(fen_input)

def exec_move(move):
    board.push(chess.Move.from_uci(move))


# print(board)
move = input()
exec_move(move)
print(board.fen())
