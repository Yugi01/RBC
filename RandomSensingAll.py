import chess.engine
import random
from reconchess import *
from reconchess.utilities import moves_without_opponent_pieces 
from reconchess.utilities import is_illegal_castle
from reconchess.utilities import is_psuedo_legal_castle
from reconchess.utilities import without_opponent_pieces
import chess
from collections import Counter


class RandomSensing(Player):
    def __init__(self):
        self.board = None
        self.all_possible_fens = None
        self.color = None
        self.my_piece_captured_square = None
        self.turn = None
        #local
        self.engine = chess.engine.SimpleEngine.popen_uci('./stockfish', setpgrp=True)
        #marking
        # self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)
                
    def handle_game_start(self, color, board, opponent_name):
        self.board = board.copy()
        self.all_possible_fens = set()
        self.all_possible_fens.add(self.board.fen())
        self.color = color
        self.turn = 0

    def handle_opponent_move_result(self, captured_my_piece, capture_square):
        if self.color == chess.WHITE and self.turn == 0:
            return
        
        new_possible_fens = set()

        if captured_my_piece:    
            for fen in self.all_possible_fens:
                board = chess.Board(fen)
                attacks = attacking_squares(board, chess.square_name(capture_square),self.color)
                for attack in attacks:
                    move = chess.Move.from_uci(attack)
                    board_copy = board.copy()
                    if move.uci() in get_moves(board):
                        board_copy.push(move)
                        new_possible_fens.add(board_copy.fen())
                        
        else:
            for fen in self.all_possible_fens:
                board = chess.Board(fen)
                board.turn = not self.color
                # print("PL MOVES",get_moves(board))
                non_capture_moves = [chess.Move.from_uci(m) for m in get_moves(board) if not board.is_capture(chess.Move.from_uci(m))]
                fens = get_all_possible_future_from_move(board, non_capture_moves)
                new_possible_fens.update(fens)
                # new_possible_boards.append(chess.Board(fen))
        
        fens_reduced = list(new_possible_fens)
        # print("reduced",len(fens_reduced))
        if len(fens_reduced) > 9000:
            fens_reduced = random.sample(fens_reduced,9000)
        # if new_possible_fens:
        self.all_possible_fens = set(fens_reduced)
        # print("ALL ",len(self.all_possible_fens))

    def choose_sense(self, sense_actions, move_actions, seconds_left):

        row = random.randint(1, 6)
        col = random.randint(1, 6)
        scan_square = chess.square(row,col)
        return scan_square

    def handle_sense_result(self, sense_result):
        new_boards = reconsile_sensor(self.all_possible_fens,sense_result)
        if not new_boards:
            return
        self.all_possible_fens = new_boards
        # print("all len",len(self.all_possible_fens))

    def choose_move(self, move_actions, seconds_left):
        self.turn = self.turn +1
        self.board.turn = self.color
        return best_move(self.all_possible_fens, self.engine, move_actions, self.color)

    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
        # print("REQ",requested_move)
        # print("TAKEN",taken_move)
        if taken_move is not None:
            self.board.push(taken_move)
            filtered = filter_my_move(self.all_possible_fens, taken_move,self.color)
            print("Random: ",len(filtered))
            if len(filtered)>0:
                filter_reduced = list(filtered)
                if(len(filter_reduced)>=8000):
                    filter_reduced = random.sample(filter_reduced,8000)
                self.all_possible_fens = set(filter_reduced)
            else:
                self.all_possible_fens = set(self.board)
        else:
            self.board.push(chess.Move.null())
        # else:
        #     print("ILLEGAL STUFF")
        #     illegal_fens = set()
        #     for fen in self.all_possible_fens:
        #         board = chess.Board(fen)
        #         if requested_move.uci() not in get_moves(board):
        #             illegal_fens.add(fen)
        #     print("THE FENS: ",illegal_fens)
        #     if illegal_fens:
        #         self.all_possible_fens =  self.all_possible_fens - illegal_fens
        #     print("OUTTT: ",self.all_possible_fens)

    def handle_game_end(self, winner_color, win_reason, game_history):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass
        
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
    
    
def attacking_squares(board,square,color):
    moves_to_exec = []
    opp_colour = not color
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
    # print("FEN LEN",len(fens))
    # print(fens)
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
                continue

            matching = False
            break
        if matching:
            working_boards.add(board.fen())
        # matching = True
    # working_boards.sort()
    if len(working_boards)>8000:
        working_boards = set(random.sample(list(working_boards), 8000))
    # print("WORKING BOARDS LEN",len(working_boards))
    return working_boards

def filter_my_move(fens, my_move,color):
    filtered = set()
    if(len(fens)==0):
        return
    for fen in fens:
        board = chess.Board(fen)
        board.turn = color
        if my_move.uci() in get_moves(board):
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
            board.turn = color
            board.clear_stack()
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
    # print("MOVE LENGTH: ",len(fen_list))
    for fen in fen_list:
        board = chess.Board(fen)
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
        # print("falling back random.")
        return random.choice(move_actions) if move_actions else None

    move_counts = Counter(best_moves)
    most_common_move = move_counts.most_common(1)[0][0]
    
    return most_common_move
