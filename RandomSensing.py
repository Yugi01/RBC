import chess.engine
import random
from reconchess import *
import os
from main import *

class RandomSensing(Player):
    def __init__(self):
        self.board = None
        self.all_possible_fens = None
        self.color = None
        self.my_piece_captured_square = None
        #local
        self.engine = chess.engine.SimpleEngine.popen_uci('./stockfish', setpgrp=True)
        #marking
        # self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)
                
    def handle_game_start(self, color, board, opponent_name):
        self.board = board.copy()
        self.all_possible_fens = set()
        self.all_possible_fens.add(self.board.fen())
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece, capture_square):
        new_possible_fens = set()

        if captured_my_piece:    
            for fen in self.all_possible_fens:
                board = chess.Board(fen)
                attacks = attacking_squares(board, chess.square_name(capture_square))
                for attack in attacks:
                    move = chess.Move.from_uci(attack)
                    if move in board.legal_moves:
                        board.push(move)
                        new_possible_fens.add(board.fen())
        else:
            # Opponent did NOT capture — only consider non-capturing legal moves    
            for fen in self.all_possible_fens:
                board = chess.Board(fen)
                board.turn = not self.color
                non_capture_moves = [m for m in board.legal_moves if not board.is_capture(m)]
                fens = get_all_possible_future_from_move(board, non_capture_moves)
                new_possible_fens.update(fens)
                # new_possible_boards.append(chess.Board(fen))
        fens_reduced = list(new_possible_fens)
        if len(fens_reduced) > 8000:
            fens_reduced = random.sample(fens_reduced,8000)
        self.all_possible_fens = set(fens_reduced)


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
        print("len",len(self.all_possible_fens))

    def choose_move(self, move_actions, seconds_left):
        self.board.turn = self.color
        return best_move(self.all_possible_fens, self.engine, move_actions, self.color)

    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
        print("REQ",requested_move)
        print("TAKEN",taken_move)
        if taken_move is not None:
            filtered = filter_my_move(self.all_possible_fens, taken_move,self.color)
            print(f"[DEBUG] taken_move: {taken_move.uci()}, filtered size: {len(filtered)}")
            if filtered:
                filter_reduced = list(filtered)
                if(len(filter_reduced)>=8000):
                    filter_reduced = random.sample(filter_reduced,8000)
                self.all_possible_fens = set(filter_reduced)
                self.board = chess.Board(next(iter(filtered)))
            else:
                print(f"[ERROR] No boards believed move {taken_move.uci()} was legal!")
                # fallback: just push the move on current board to stay in sync
                if self.board.is_legal(taken_move):
                    self.board.push(taken_move)
                    self.all_possible_fens = {self.board.fen()} 
                else:
                    self.board.push(chess.Move.null())
        else:
            illegal_fens = set()
            for fen in self.all_possible_fens:
                board = chess.Board(fen)
                if requested_move not in board.legal_moves:
                    illegal_fens.add(fen)
                    if len(illegal_fens) > 8000:
                        break

            if illegal_fens:
                self.all_possible_fens = illegal_fens
            else:
                fallback = self.board.copy()
                fallback.push(chess.Move.null())
                self.all_possible_fens = {fallback.fen()}

    def handle_game_end(self, winner_color, win_reason, game_history):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass