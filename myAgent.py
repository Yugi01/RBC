import chess.engine
import random
from reconchess import *
import os
from main import *

class MyAgent(Player):
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
            if my_move in move_actions:
                return chess.Move.from_uci(my_move)
            print("Stockfish returned:", my_move)
        except Exception as e:
            print("ERROR calling stockfish_move:", e)
            return None
        # my_move = stockfish_move(self.board,self.engine)
        print(my_move)
        return(chess.Move.from_uci(my_move))
        
    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
        print("requst",requested_move)
        print("taken",taken_move)
        if taken_move is not None:
            filtered = filter_my_move(self.all_possible_boards, taken_move)

            if filtered:
                self.all_possible_boards = filtered
                self.board = filtered[0]  # Already has move applied
            else:
                print(f"WARNING: No boards matched taken move {taken_move}. Resetting.")
                # Fallback: apply move to our current board only if it's legal
                if taken_move in self.board.legal_moves:
                    self.board.push(taken_move)
                else:
                    print(f"ERROR: Cannot push move {taken_move}, not legal on fallback board.")
                self.all_possible_boards = [self.board.copy()]
        else:
            print("No move taken. Pushing null move.")
            self.board.push(chess.Move.null())
            self.all_possible_boards = [self.board.copy()]

    def handle_game_end(self, winner_color, win_reason, game_history):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass