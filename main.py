import chess
from reconchess.utilities import moves_without_opponent_pieces 
from reconchess.utilities import is_illegal_castle
from reconchess.utilities import is_psuedo_legal_castle
from reconchess.utilities import without_opponent_pieces
import chess.engine
from collections import Counter
import random
import time

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
    board.push(move)

def remove_dups(list_moves):
    seen = []
    for move in list_moves:
        if move in seen:
            continue
        seen.append(move)
    return seen

def get_moves(board):
    board_copy = board.copy()
    null_move = ["0000"]
    pl_moves = [str(move) for move in board_copy.pseudo_legal_moves]
    pl_castle = get_pl_castle_moves(board_copy)
    all_moves = null_move + pl_castle + pl_moves
    # all_moves.sort()
    return set(all_moves)

def get_all_possible_future_from_move(board,moves):
    all_out = set()
    for move in moves:
        copy_board = board.copy()
        copy_board.push(move)
        all_out.add(copy_board.fen())
    # all_out.sort()
    return all_out
    
    
def attacking_squares(board,square):
    moves_to_exec = []
    opp_colour = not board.turn
    body_copy = board.copy()
    attackers = body_copy.attackers(opp_colour,chess.parse_square(square))
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

def reconsile_sensor(fens,sensor):
    working_boards = set()
    print("FEN LEN GEN:",len(fens))
    print(fens)
    for fen in fens:
        matching = True
        board = chess.Board(fen)
        for square,piece in sensor:
            
            actual = board.piece_at(square)

            if actual is None and piece is None:
                continue
            elif actual is not None and piece is not None and \
                actual.piece_type == piece.piece_type and \
                actual.color == piece.color:
                print("FEN: ",fen)
                print("SENSOR: ", [(chess.square_name(s),p) for s,p in sensor] )
                continue

            matching = False
            break
        if matching:
            working_boards.add(board.fen())
        # matching = True
    # working_boards.sort()
    print("WORKING BOARDS LEN",len(working_boards))
    return working_boards

def filter_my_move(fens, my_move,color):
    filtered = set()
    if(len(fens)==0):
        raise ValueError("FENS ARE empty")
    for fen in fens:
        board = chess.Board(fen)
        board.turn = color
        if my_move in board.legal_moves:
            board.push(my_move)
            filtered.add(board.fen())
            
    if not filtered:
        return fens
    
    if len(filtered)>8000:
        filtered = set(random.sample(list(filtered), 8000))
    return filtered

#TROUTBOT CHOOSE_MOVE        
def stockfish_move(board,engine,time_per_board,color):

        # if we might be able to take the king, try to
        enemy_king_square = board.king(not board.turn)
        if enemy_king_square:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = board.attackers(board.turn, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)

        # otherwise, try to move with the stockfish chess engine
        try:
            board.clear_stack()
            board.turn = color
            result = engine.play(board, chess.engine.Limit(time=time_per_board))
            return result.move
        except chess.engine.EngineTerminatedError:
            print('Stockfish Engine died')
        except chess.engine.EngineError:
            print('Stockfish Engine bad state at "{}"'.format(board.fen()))

        # if all else fails, pass
        return None


def best_move(fens, engine, move_actions, color):
    fen_list = list(fens)
    N = len(fen_list)

    # Cap the belief set at 8000 boards
    if N > 8000:
        fen_list = random.sample(fen_list, 8000)
        N = 8000
    
    time_per_board = 8/N if N>0 else 8

    best_moves = []

    for fen in fen_list:
        board = chess.Board(fen)
        # print(fen)
        # board_copy = board.copy()
        # board.turn = color  # ensure correct turn
        move = stockfish_move(board,engine,time_per_board,color)
        if move:
            for legal in move_actions:
                # print("LEGAL",legal)
                # print()
                # print(move == str(legal))
                # print(move," ",legal)
                # print(move_actions)
                if move == legal:
                    # print("here")
                    best_moves.append(move)
                    break

    if not best_moves:
        print("[WARN] No valid moves from Stockfish — falling back randomly.")
        return random.choice(move_actions) if move_actions else None

    # Use Counter for majority voting
    move_counts = Counter(best_moves)
    most_common_move = move_counts.most_common(1)[0][0]

    print(f"[CHOOSE_MOVE] Majority voted move: {most_common_move.uci()} (votes: {move_counts[most_common_move]})")
    return most_common_move
