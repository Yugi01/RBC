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
    temp = []
    castle_moves = get_pseudo_legal_castling(without_opponent_pieces(board))
    for move in castle_moves:
        if not is_illegal_castle(board, chess.Move.from_uci(move)):
            temp.append(move)
    return temp

def exec_move(board,move):
    board.push(chess.Move.from_uci(move))

def remove_dups(list_moves):
    seen = []
    for move in list_moves:
        if move in seen:
            continue
        seen.append(move)
    return seen

def get_moves(board):
    null_move = ["0000"]
    pl_moves = [str(move) for move in board.pseudo_legal_moves]
    pl_castle = get_pl_castle_moves(board)
    all_moves = null_move + pl_castle + pl_moves
    all_moves.sort()
    return remove_dups(all_moves)

def get_all_possible_future_from_move(board,moves):
    copy_board = board
    all_out = []
    for move in moves:
        exec_move(copy_board,move)
        all_out.append(copy_board.fen())
        copy_board.pop()
    all_out.sort()
    return all_out
    
def attacking_squares(square):
    moves_to_exec = []
    opp_colour = board.turn
    attackers = board.attackers(opp_colour,chess.parse_square(square))
    for move in [chess.square_name(sq) for sq in attackers]:
        moves_to_exec.append(move+square)
    return moves_to_exec

square = input()
# all possible future states
for state in get_all_possible_future_from_move(board,attacking_squares(square)):
    print(state)
