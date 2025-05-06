import chess

fen_input = input()

board = chess.Board(fen_input)

def exec_move(move):
    board.push(chess.Move.from_uci(move))

def get_moves(fen):
    null_move = ["0000"]
    pl_moves = [str(move) for move in board.pseudo_legal_moves]
    pl_moves.sort()
    all_moves = null_move + pl_moves
    return all_moves


# print(board)
# move = input()
# exec_move(move)
# print(board.fen())
print(get_moves(board.fen()))
