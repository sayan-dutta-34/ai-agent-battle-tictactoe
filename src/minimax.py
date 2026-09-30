"""
Minimax algorithm with Alpha-Beta pruning for Tic-Tac-Toe.

This module implements the core search algorithm used by the AI agents.
It supports configurable search depth, pluggable heuristic evaluation,
and tracks search statistics (nodes evaluated, nodes pruned).
"""

import math
from typing import Tuple, Optional

from src.game import TicTacToe
from src.heuristic import Heuristic


class SearchStats:
    """
    Tracks statistics during a Minimax search.

    Attributes:
        nodes_evaluated (int): Total number of nodes evaluated during search.
        nodes_pruned (int): Total number of branches pruned by Alpha-Beta.
    """

    def __init__(self) -> None:
        self.nodes_evaluated: int = 0
        self.nodes_pruned: int = 0

    def reset(self) -> None:
        """Reset all counters to zero."""
        self.nodes_evaluated = 0
        self.nodes_pruned = 0


def minimax_alpha_beta(
    game: TicTacToe,
    depth: int,
    alpha: float,
    beta: float,
    is_maximizing: bool,
    maximizing_player: str,
    heuristic: Heuristic,
    stats: SearchStats,
) -> float:
    """
    Minimax search with Alpha-Beta pruning.

    Recursively evaluates game positions to determine the optimal score.
    MAX tries to maximize the score; MIN tries to minimize the score.

    Terminal states are scored as:
        - Win for maximizing_player:  +100
        - Loss for maximizing_player: -100
        - Draw:                          0

    When the maximum search depth is reached without reaching a terminal
    state, the heuristic function is used to estimate the position's value.

    Args:
        game: The current game state.
        depth: Remaining search depth (0 = evaluate with heuristic).
        alpha: Best score the maximizer can guarantee (starts at -inf).
        beta: Best score the minimizer can guarantee (starts at +inf).
        is_maximizing: True if the current player is MAX.
        maximizing_player: The player symbol ('X' or 'O') that MAX is playing as.
        heuristic: The heuristic evaluation function to use.
        stats: SearchStats object to track nodes evaluated and pruned.

    Returns:
        The minimax score for the current position.
    """
    stats.nodes_evaluated += 1

    # --- Terminal state check ---
    winner = game.check_winner()
    if winner is not None:
        if winner == maximizing_player:
            return 100
        else:
            return -100

    if game.is_draw():
        return 0

    # --- Depth limit reached: use heuristic ---
    if depth == 0:
        return heuristic.evaluate(game, maximizing_player)

    valid_moves = game.get_valid_moves()

    if is_maximizing:
        max_eval = -math.inf
        for row, col in valid_moves:
            # Apply move temporarily
            game.make_move(row, col, maximizing_player)
            eval_score = minimax_alpha_beta(
                game, depth - 1, alpha, beta,
                False, maximizing_player, heuristic, stats,
            )
            # Undo move
            game.undo_move(row, col)

            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)

            # Alpha-Beta pruning: beta cutoff
            if beta <= alpha:
                # Count remaining unexplored moves as pruned
                remaining = len(valid_moves) - (valid_moves.index((row, col)) + 1)
                stats.nodes_pruned += remaining
                break

        return max_eval
    else:
        min_eval = math.inf
        minimizing_player = TicTacToe.get_opponent(maximizing_player)
        for row, col in valid_moves:
            # Apply move temporarily
            game.make_move(row, col, minimizing_player)
            eval_score = minimax_alpha_beta(
                game, depth - 1, alpha, beta,
                True, maximizing_player, heuristic, stats,
            )
            # Undo move
            game.undo_move(row, col)

            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)

            # Alpha-Beta pruning: alpha cutoff
            if beta <= alpha:
                remaining = len(valid_moves) - (valid_moves.index((row, col)) + 1)
                stats.nodes_pruned += remaining
                break

        return min_eval


def find_best_move(
    game: TicTacToe,
    depth: int,
    maximizing_player: str,
    heuristic: Heuristic,
    stats: SearchStats,
) -> Optional[Tuple[int, int]]:
    """
    Find the best move for the given player using Minimax + Alpha-Beta.

    Evaluates all valid moves and returns the one with the highest minimax
    score. When multiple moves share the same best score, one is chosen
    randomly to allow variation across games without weakening the agent.

    Args:
        game: The current game state.
        depth: The search depth to use.
        maximizing_player: The player symbol ('X' or 'O') to find the best move for.
        heuristic: The heuristic evaluation function to use.
        stats: SearchStats object to track search statistics.

    Returns:
        The (row, col) tuple of the best move, or None if no moves are available.
    """
    import random

    valid_moves = game.get_valid_moves()
    if not valid_moves:
        return None

    best_score = -math.inf
    best_moves = []

    for row, col in valid_moves:
        # Apply move temporarily
        game.make_move(row, col, maximizing_player)
        # Evaluate with Minimax (opponent's turn = minimizing)
        score = minimax_alpha_beta(
            game, depth - 1, -math.inf, math.inf,
            False, maximizing_player, heuristic, stats,
        )
        # Undo move
        game.undo_move(row, col)

        if score > best_score:
            best_score = score
            best_moves = [(row, col)]
        elif score == best_score:
            best_moves.append((row, col))

    # Random tie-breaking among equally optimal moves
    return random.choice(best_moves)
