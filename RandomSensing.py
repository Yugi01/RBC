import chess.engine
import random
from reconchess import *
import os
from main import *

class RandomSensing(Player):
    def __init__(self):
        self.board = None
        self.all_possible_boards = None
        self.color = None
        self.my_piece_captured_square = None

        #local
        self.engine = chess.engine.SimpleEngine.popen_uci('./stockfish', setpgrp=True)
        #marking
        # self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)
                
    def handle_game_start(self, color, board, opponent_name):
        self.board = board.copy()
        self.all_possible_boards = [self.board]
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece, capture_square):
    # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions, move_actions, seconds_left):
        # write code here to select a sensing move
        return random.choice(sense_actions)

    def handle_sense_result(self, sense_result):
        # This is where the sensing result returns feedback
        for square, piece in sense_result:
            if piece is None:
                self.board.remove_piece_at(square)
            else:
                self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions, seconds_left):

        try:
            self.board.turn = self.color
            my_move = stockfish_move(self.board, self.engine)
            if my_move in str(move_actions):
                return(chess.Move.from_uci(my_move))
        except Exception as e:
            return None
        
    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):

        if taken_move is not None:
            filtered = filter_my_move(self.all_possible_boards, taken_move)

            if not filtered:
                self.all_possible_boards = filtered
                self.board = filtered[0]  # Already has move applied
                return

            if taken_move in self.board.legal_moves:
                self.board.push(taken_move)
            else:
                self.board.push(chess.Move.null())

    def handle_game_end(self, winner_color, win_reason, game_history):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass