import chess
import math
from collections import defaultdict
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.signal


def calculate_entropy(fen_list):
    total_entropy = {}
    square_counts = defaultdict(int)
    total = len(fen_list)
    if not total:
        return 3,3
    total_entropy_np = []
    convolution_np = np.full((3,3),1/9)
    
    for fen in fen_list:
        board = chess.Board(fen)
        for square in chess.SQUARES:
            if board.piece_at(square):
                square_counts[square] += 1
    
    for square in chess.SQUARES:
        count = square_counts[square]
        p = count/total if total != 0 else count
        if p == 0 or p==1:
            entropy = 0
        else:
            entropy = -p * math.log2(p) - (1-p) * math.log2(1-p)
        # print(chess.square_name(square))
        # print(square)
        total_entropy[chess.square_name(square)] = entropy
        total_entropy_np.append(entropy)
        
    total_entropy_np = np.array(total_entropy_np).reshape((8,8))
    total_entropy_np = np.flip(total_entropy_np,axis=0)
    # print(total_entropy_np.round(2))
    # print()
    new_entropy = scipy.signal.convolve2d(total_entropy_np,convolution_np,mode="same")
    print(new_entropy.round(2))
    # print(entropy)
    row,col=divmod(np.argmax(new_entropy),8)
    row = int(row)
    col = int(col)
    rank = 7-row
    if rank == 0:
        rank = 1
    if rank == 7:
        rank = 6
    if col == 0:
        col =1
    if col ==7:
        col = 6
    # rank = 7 - row
    # return new_entropy
    return col,rank
    # print(square_counts)

# def plot_entropy_heatmap(entropy_array):
#     # Create square labels from a8 to h1
#     square_labels = np.array([
#         [chess.square_name(file + 8 * rank) for file in range(8)]
#         for rank in range(8)
#     ])

#     plt.figure(figsize=(10, 8))
#     ax = sns.heatmap(
#         entropy_array,
#         annot=square_labels,
#         fmt='',
#         cmap='YlOrRd',
#         cbar_kws={'label': 'Entropy'},
#         linewidths=0.5,
#         linecolor='black'
#     )

#     # Label axes correctly
#     ax.set_xticks(np.arange(8) + 0.5)
#     ax.set_yticks(np.arange(8) + 0.5)
#     ax.set_xticklabels(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
#     ax.set_yticklabels(['8', '7', '6', '5', '4', '3', '2', '1'], rotation=0)
#     ax.set_title("Entropy Heatmap of Board Squares")

#     # Optional flip if needed
#     plt.gca()
#     plt.tight_layout()
#     plt.show()

# plot_entropy_heatmap(calculate_entropy(test_fens))