import chess
from reconchess.utilities import moves_without_opponent_pieces 
from reconchess.utilities import is_illegal_castle
from reconchess.utilities import is_psuedo_legal_castle
from reconchess.utilities import without_opponent_pieces

fen_input = input()

board = chess.Board(fen_input)


def get_pseudo_legal_castling(board):
    castle_moves = []
    if(chess.WHITE):
        if bool(board.castling_rights & chess.BB_H1):
            castle_moves.append("e1g1")
        if bool(board.castling_rights & chess.BB_A1):
            castle_moves.append("e1c1")
    else:
        if bool(board.castling_rights & chess.BB_H8):
            castle_moves.append("e8g8")
        if bool(board.castling_rights & chess.BB_A8):
            castle_moves.append("e8c8")
    return castle_moves

def get_pl_castle_moves(board):
    castle_moves = get_pseudo_legal_castling(without_opponent_pieces(board))
    return castle_moves

def exec_move(move):
    board.push(chess.Move.from_uci(move))

def get_moves(board):
    null_move = ["0000"]
    pl_moves = [str(move) for move in board.pseudo_legal_moves]
    pl_castle = get_pl_castle_moves(board)
    all_moves = null_move + pl_castle + pl_moves
    all_moves.sort()
    return all_moves

# print(board)
# move = input()
# exec_move(move)
# print(board.fen())
all_moves = get_moves(board)

for move in all_moves:
    print(move)
