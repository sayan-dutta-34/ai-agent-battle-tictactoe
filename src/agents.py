"""
AI Agent definitions for the Tic-Tac-Toe battle.

This module defines the Agent class and the two named agents:
- NEXUS: Uses H1 (Aggressive) heuristic
- TITAN: Uses H2 (Defensive) heuristic

Both agents use Minimax with Alpha-Beta pruning and configurable search depth.
"""

from typing import Tuple, Optional

from src.game import TicTacToe
from src.heuristic import Heuristic, AggressiveHeuristic, DefensiveHeuristic
from src.minimax import SearchStats, find_best_move


class Agent:
    """
    An AI agent that plays Tic-Tac-Toe using Minimax + Alpha-Beta pruning.

    Each agent has a unique name, a heuristic evaluation function, and a
    configurable search depth. The agent tracks its own search statistics
    (nodes evaluated and pruned) for experimental analysis.

    Attributes:
        name (str): The agent's name (e.g., 'NEXUS', 'TITAN').
        heuristic (Heuristic): The heuristic evaluation function used.
        depth (int): The search depth for Minimax.
        stats (SearchStats): Tracks nodes evaluated and pruned per move.
        total_nodes_evaluated (int): Cumulative nodes evaluated in a game.
        total_nodes_pruned (int): Cumulative nodes pruned in a game.
    """

    def __init__(self, name: str, heuristic: Heuristic, depth: int) -> None:
        """
        Initialize an AI agent.

        Args:
            name: The agent's display name.
            heuristic: The heuristic evaluation function to use.
            depth: The search depth for Minimax (must be >= 1).

        Raises:
            ValueError: If depth is less than 1.
        """
        if depth < 1:
            raise ValueError(f"Search depth must be >= 1, got {depth}")

        self.name: str = name
        self.heuristic: Heuristic = heuristic
        self.depth: int = depth
        self.stats: SearchStats = SearchStats()
        self.total_nodes_evaluated: int = 0
        self.total_nodes_pruned: int = 0

    def choose_move(self, game: TicTacToe, player: str) -> Optional[Tuple[int, int]]:
        """
        Choose the best move for the given player using Minimax + Alpha-Beta.

        The agent resets its per-move search statistics before each move,
        then accumulates them into the game-level totals.

        Args:
            game: The current game state.
            player: The player symbol ('X' or 'O') the agent is playing as.

        Returns:
            The (row, col) tuple of the chosen move, or None if no moves exist.
        """
        self.stats.reset()

        best_move = find_best_move(
            game=game,
            depth=self.depth,
            maximizing_player=player,
            heuristic=self.heuristic,
            stats=self.stats,
        )

        # Accumulate per-move stats into game-level totals
        self.total_nodes_evaluated += self.stats.nodes_evaluated
        self.total_nodes_pruned += self.stats.nodes_pruned

        return best_move

    def reset_game_stats(self) -> None:
        """Reset game-level cumulative statistics for a new game."""
        self.total_nodes_evaluated = 0
        self.total_nodes_pruned = 0
        self.stats.reset()

    def __repr__(self) -> str:
        return (
            f"Agent(name='{self.name}', heuristic='{self.heuristic.name}', "
            f"depth={self.depth})"
        )


def create_nexus(depth: int = 3) -> Agent:
    """
    Create the NEXUS agent with H1 (Aggressive) heuristic.

    Args:
        depth: The search depth for Minimax (default: 3).

    Returns:
        An Agent instance configured as NEXUS.
    """
    return Agent(
        name="NEXUS",
        heuristic=AggressiveHeuristic(),
        depth=depth,
    )


def create_titan(depth: int = 3) -> Agent:
    """
    Create the TITAN agent with H2 (Defensive) heuristic.

    Args:
        depth: The search depth for Minimax (default: 3).

    Returns:
        An Agent instance configured as TITAN.
    """
    return Agent(
        name="TITAN",
        heuristic=DefensiveHeuristic(),
        depth=depth,
    )
