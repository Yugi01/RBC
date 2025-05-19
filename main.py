import chess
from reconchess.utilities import moves_without_opponent_pieces 
from reconchess.utilities import is_illegal_castle
from reconchess.utilities import is_psuedo_legal_castle
from reconchess.utilities import without_opponent_pieces
import chess.engine

#local
# engine = chess.engine.SimpleEngine.popen_uci('./stockfish', setpgrp=True)
#marking
# engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)

def get_pseudo_legal_castling(board):
    castle_moves = []
    if(board.turn == chess.WHITE):
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
    all_out = []
    for move in moves:
        copy_board = board.copy()
        exec_move(copy_board,move)
        all_out.append(copy_board.fen())
    all_out.sort()
    return all_out
    
def attacking_squares(board,square):
    moves_to_exec = []
    opp_colour = board.turn
    attackers = board.attackers(opp_colour,chess.parse_square(square))
    for move in [chess.square_name(sq) for sq in attackers]:
        moves_to_exec.append(move+square)
    return moves_to_exec

def useable_sensor_out(sensor):
    temp = sensor.split(";")
    sensor_out = []
    for info in temp:
        square,piece = info.split(":")
        piece = "None" if piece == '?' else piece
        sensor_out.append({square:piece})
    return sensor_out

def reconsile_sensor(boards,sensor):
    working_boards = []
    matching = True
    for board in boards:
        for sen in sensor:
            for square,piece in sen.items():
                if str(board.piece_at(chess.parse_square(square))) == piece:
                    continue
                matching = False
        if matching:
            working_boards.append(board.fen())
        matching = True
    working_boards.sort()
    return working_boards

def filter_my_move(boards, my_move):
    filtered = []
    for board in boards:
        if my_move in board.legal_moves:
            board_copy = board.copy()
            board_copy.push(my_move)
            filtered.append(board_copy)
    return filtered

#TROUTBOT CHOOSE_MOVE        
def stockfish_move(board,engine):

        # if we might be able to take the king, try to
        enemy_king_square = board.king(not board.turn)
        if enemy_king_square:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = board.attackers(board.turn, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square).uci()

        # otherwise, try to move with the stockfish chess engine
        try:
            board.clear_stack()
            result = engine.play(board, chess.engine.Limit(time=0.1))
            return result.move.uci()
        except chess.engine.EngineTerminatedError:
            print('Stockfish Engine died')
        except chess.engine.EngineError:
            print('Stockfish Engine bad state at "{}"'.format(board.fen()))

        # if all else fails, pass
        return None

def best_move(boards, engine):
    best_moves = []

    for board in boards:
        if board.turn == chess.WHITE:  # or self.color
            move = stockfish_move(board, engine)
            if move:
                best_moves.append(move)

    if not best_moves:
        return None

    # print(best_moves)
    return max(set(best_moves), key=best_moves.count)


# num_inputs = int(input())
# boards = []
# for i in range(num_inputs):
#     fen_input = input()
#     boards.append(chess.Board(fen_input))
# print(best_move(boards))
# sensor_raw = input()

# useful_board = reconsile_sensor(boards,useable_sensor_out(sensor_raw))

# for board in useful_board:
#     print(board)

# square = input()
# all possible future states
# for state in get_all_possible_future_from_move(board,attacking_squares(square)):
#     print(state)
# engine.quit()