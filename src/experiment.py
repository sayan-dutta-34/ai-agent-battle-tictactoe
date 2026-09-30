"""
Experiment runner for the AI Agent Battle.

This module handles:
1. Running individual AI-vs-AI games
2. The Search-Depth Experiment (Experiment 1)
3. The 10-game AI Agent Battle (Experiment 2)
4. Saving results to CSV files
5. Printing summary statistics
"""

import csv
import os
import time
from typing import List, Dict, Any, Optional

from src.game import TicTacToe
from src.agents import Agent, create_nexus, create_titan
from src.heuristic import AggressiveHeuristic


# ----------------------------------------------------------
#  Constants
# ----------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")


# ----------------------------------------------------------
#  Single Game Runner
# ----------------------------------------------------------

class GameResult:
    """
    Stores the result of a single AI-vs-AI game.

    Attributes:
        game_number (int): The game number in the series.
        first_player_name (str): Name of the agent who played first.
        winner (str): Name of the winning agent, or 'DRAW'.
        num_moves (int): Total number of moves played.
        agent1_nodes (int): Nodes evaluated by agent 1.
        agent2_nodes (int): Nodes evaluated by agent 2.
        agent1_pruned (int): Nodes pruned by agent 1.
        agent2_pruned (int): Nodes pruned by agent 2.
        execution_time (float): Total game execution time in seconds.
    """

    def __init__(
        self,
        game_number: int,
        first_player_name: str,
        winner: str,
        num_moves: int,
        agent1_nodes: int,
        agent2_nodes: int,
        agent1_pruned: int,
        agent2_pruned: int,
        execution_time: float,
    ) -> None:
        self.game_number = game_number
        self.first_player_name = first_player_name
        self.winner = winner
        self.num_moves = num_moves
        self.agent1_nodes = agent1_nodes
        self.agent2_nodes = agent2_nodes
        self.agent1_pruned = agent1_pruned
        self.agent2_pruned = agent2_pruned
        self.execution_time = execution_time


def run_single_game(
    agent1: Agent,
    agent2: Agent,
    game_number: int = 1,
    first_agent: Optional[Agent] = None,
    verbose: bool = True,
) -> GameResult:
    """
    Run a single AI-vs-AI Tic-Tac-Toe game.

    The first agent plays 'X' and the second plays 'O'.
    X always moves first in Tic-Tac-Toe.

    Args:
        agent1: The first agent (e.g., NEXUS).
        agent2: The second agent (e.g., TITAN).
        game_number: The game number for display and recording.
        first_agent: Which agent goes first. If None, agent1 goes first.
        verbose: If True, print game progress.

    Returns:
        A GameResult containing the game outcome and statistics.
    """
    game = TicTacToe()

    # Determine who plays X (first) and who plays O
    if first_agent is None or first_agent.name == agent1.name:
        x_agent = agent1
        o_agent = agent2
    else:
        x_agent = agent2
        o_agent = agent1

    # Reset game-level stats
    x_agent.reset_game_stats()
    o_agent.reset_game_stats()

    # Map player symbols to agents
    agents = {'X': x_agent, 'O': o_agent}
    current_player = 'X'
    move_count = 0

    if verbose:
        print(f"\n{'='*50}")
        print(f"  Game {game_number}: {x_agent.name} (X) vs {o_agent.name} (O)")
        print(f"  {x_agent.name} goes first")
        print(f"{'='*50}")

    start_time = time.time()

    while not game.is_terminal():
        current_agent = agents[current_player]
        move = current_agent.choose_move(game, current_player)

        if move is None:
            break  # Safety: no valid moves (should not happen in normal game)

        row, col = move
        game.make_move(row, col, current_player)
        move_count += 1

        if verbose:
            print(f"\n  Move {move_count}: {current_agent.name} ({current_player}) -> ({row}, {col})")
            print(game.display())

        # Switch player
        current_player = TicTacToe.get_opponent(current_player)

    execution_time = time.time() - start_time

    # Determine winner
    winner_symbol = game.check_winner()
    if winner_symbol is not None:
        winner_name = agents[winner_symbol].name
    else:
        winner_name = "DRAW"

    if verbose:
        print(f"\n  Result: {winner_name}")
        print(f"  Moves: {move_count}")
        print(f"  {agent1.name} - Nodes evaluated: {agent1.total_nodes_evaluated}, Pruned: {agent1.total_nodes_pruned}")
        print(f"  {agent2.name} - Nodes evaluated: {agent2.total_nodes_evaluated}, Pruned: {agent2.total_nodes_pruned}")
        print(f"  Execution time: {execution_time:.4f}s")

    return GameResult(
        game_number=game_number,
        first_player_name=x_agent.name,
        winner=winner_name,
        num_moves=move_count,
        agent1_nodes=agent1.total_nodes_evaluated,
        agent2_nodes=agent2.total_nodes_evaluated,
        agent1_pruned=agent1.total_nodes_pruned,
        agent2_pruned=agent2.total_nodes_pruned,
        execution_time=execution_time,
    )


# ----------------------------------------------------------
#  Experiment Class
# ----------------------------------------------------------

class Experiment:
    """
    Runs AI-vs-AI experiments and collects statistics.

    Supports:
    - Experiment 1: Search-Depth analysis
    - Experiment 2: 10-game AI Agent Battle
    """

    def __init__(self, agent1: Agent, agent2: Agent) -> None:
        """
        Initialize the experiment with two agents.

        Args:
            agent1: The first agent (e.g., NEXUS).
            agent2: The second agent (e.g., TITAN).
        """
        self.agent1 = agent1
        self.agent2 = agent2

    # ------------------------------------------------------
    #  Experiment 2: AI Agent Battle (10 games)
    # ------------------------------------------------------

    def run_battle(
        self, num_games: int = 10, verbose: bool = True
    ) -> List[GameResult]:
        """
        Run a series of AI-vs-AI games with alternating starting players.

        Game 1: agent1 starts, Game 2: agent2 starts, Game 3: agent1, ...

        Args:
            num_games: Number of games to play (default: 10).
            verbose: If True, print game-by-game details.

        Returns:
            A list of GameResult objects.
        """
        results: List[GameResult] = []

        print("\n" + "=" * 60)
        print("  AI AGENT BATTLE")
        print(f"  {self.agent1.name} (Depth={self.agent1.depth}, {self.agent1.heuristic.name})")
        print(f"       vs.")
        print(f"  {self.agent2.name} (Depth={self.agent2.depth}, {self.agent2.heuristic.name})")
        print(f"  Games: {num_games}")
        print("=" * 60)

        for game_num in range(1, num_games + 1):
            # Alternate starting player
            if game_num % 2 == 1:
                first_agent = self.agent1
            else:
                first_agent = self.agent2

            result = run_single_game(
                agent1=self.agent1,
                agent2=self.agent2,
                game_number=game_num,
                first_agent=first_agent,
                verbose=verbose,
            )
            results.append(result)

        return results

    # ------------------------------------------------------
    #  Summary Statistics
    # ------------------------------------------------------

    @staticmethod
    def print_summary(
        results: List[GameResult],
        agent1_name: str,
        agent2_name: str,
    ) -> Dict[str, Any]:
        """
        Print and return aggregate statistics for a series of games.

        Args:
            results: List of GameResult objects.
            agent1_name: Name of the first agent.
            agent2_name: Name of the second agent.

        Returns:
            A dictionary containing summary statistics.
        """
        agent1_wins = sum(1 for r in results if r.winner == agent1_name)
        agent2_wins = sum(1 for r in results if r.winner == agent2_name)
        draws = sum(1 for r in results if r.winner == "DRAW")

        avg_agent1_nodes = sum(r.agent1_nodes for r in results) / len(results)
        avg_agent2_nodes = sum(r.agent2_nodes for r in results) / len(results)
        avg_agent1_pruned = sum(r.agent1_pruned for r in results) / len(results)
        avg_agent2_pruned = sum(r.agent2_pruned for r in results) / len(results)
        avg_time = sum(r.execution_time for r in results) / len(results)
        avg_moves = sum(r.num_moves for r in results) / len(results)

        # Check first-player advantage
        first_player_wins = sum(
            1 for r in results
            if r.winner != "DRAW" and r.winner == r.first_player_name
        )

        summary = {
            "agent1_wins": agent1_wins,
            "agent2_wins": agent2_wins,
            "draws": draws,
            "avg_agent1_nodes": avg_agent1_nodes,
            "avg_agent2_nodes": avg_agent2_nodes,
            "avg_agent1_pruned": avg_agent1_pruned,
            "avg_agent2_pruned": avg_agent2_pruned,
            "avg_time": avg_time,
            "avg_moves": avg_moves,
            "first_player_wins": first_player_wins,
        }

        print("\n" + "=" * 60)
        print("  BATTLE SUMMARY")
        print("=" * 60)
        print(f"  {agent1_name} wins:  {agent1_wins}")
        print(f"  {agent2_name} wins:  {agent2_wins}")
        print(f"  Draws:            {draws}")
        print(f"  ---")
        print(f"  First-player wins: {first_player_wins} / {len(results)}")
        print(f"  Average moves:     {avg_moves:.1f}")
        print(f"  ---")
        print(f"  Avg. nodes evaluated ({agent1_name}): {avg_agent1_nodes:.1f}")
        print(f"  Avg. nodes evaluated ({agent2_name}): {avg_agent2_nodes:.1f}")
        print(f"  Avg. nodes pruned ({agent1_name}):    {avg_agent1_pruned:.1f}")
        print(f"  Avg. nodes pruned ({agent2_name}):    {avg_agent2_pruned:.1f}")
        print(f"  Avg. execution time: {avg_time:.4f}s")
        print("=" * 60)

        return summary

    # ------------------------------------------------------
    #  Save Results to CSV
    # ------------------------------------------------------

    @staticmethod
    def save_battle_results(
        results: List[GameResult],
        agent1_name: str,
        agent2_name: str,
        filepath: Optional[str] = None,
    ) -> str:
        """
        Save 10-game battle results to a CSV file.

        Args:
            results: List of GameResult objects.
            agent1_name: Name of the first agent.
            agent2_name: Name of the second agent.
            filepath: Path to the output CSV file. Defaults to results/results.csv.

        Returns:
            The path to the saved CSV file.
        """
        if filepath is None:
            filepath = os.path.join(RESULTS_DIR, "results.csv")

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Column names use agent names as specified in PDF example
        a1_lower = agent1_name.lower()
        a2_lower = agent2_name.lower()

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "game", "first", "winner", "moves",
                f"{a1_lower}_nodes", f"{a2_lower}_nodes",
                f"{a1_lower}_pruned", f"{a2_lower}_pruned",
                "execution_time",
            ])
            for r in results:
                writer.writerow([
                    r.game_number,
                    r.first_player_name,
                    r.winner,
                    r.num_moves,
                    r.agent1_nodes,
                    r.agent2_nodes,
                    r.agent1_pruned,
                    r.agent2_pruned,
                    f"{r.execution_time:.6f}",
                ])

        print(f"\n  Battle results saved to: {filepath}")
        return filepath


# ----------------------------------------------------------
#  Experiment 1: Search-Depth Experiment
# ----------------------------------------------------------

class DepthExperiment:
    """
    Investigates the effect of search depth on AI performance.

    Keeps the game, algorithm, and heuristic fixed while varying only
    the search depth (1, 2, 3, 4). Both agents use the SAME heuristic
    for this experiment to isolate the effect of depth.
    """

    @staticmethod
    def run(
        depths: List[int] = None,
        num_games_per_depth: int = 5,
        verbose: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Run the search-depth experiment.

        For each depth, runs num_games_per_depth AI-vs-AI games where
        both agents use the same heuristic (H1) but at the given depth.
        This isolates the effect of depth on:
        - Game outcome
        - Nodes evaluated
        - Nodes pruned
        - Execution time

        Args:
            depths: List of search depths to test (default: [1, 2, 3, 4]).
            num_games_per_depth: Games per depth setting (default: 5).
            verbose: If True, print per-game details.

        Returns:
            A list of dicts with aggregated results per depth.
        """
        if depths is None:
            depths = [1, 2, 3, 4]

        all_depth_results: List[Dict[str, Any]] = []

        print("\n" + "=" * 60)
        print("  EXPERIMENT 1: SEARCH DEPTH ANALYSIS")
        print(f"  Heuristic: H1 (Aggressive) -- fixed for both agents")
        print(f"  Games per depth: {num_games_per_depth}")
        print(f"  Depths tested: {depths}")
        print("=" * 60)

        for depth in depths:
            print(f"\n{'-'*50}")
            print(f"  Testing Depth = {depth}")
            print(f"{'-'*50}")

            # Both agents use SAME heuristic (H1) to isolate depth effect
            agent_a = create_nexus(depth=depth)
            agent_b = create_titan(depth=depth)
            # Override TITAN's heuristic to H1 for this experiment
            agent_b.heuristic = AggressiveHeuristic()

            game_results: List[GameResult] = []
            total_nodes = 0
            total_pruned = 0
            total_time = 0.0
            wins_a = 0
            wins_b = 0
            draws = 0

            for g in range(1, num_games_per_depth + 1):
                # Alternate starting player
                first_agent = agent_a if g % 2 == 1 else agent_b

                result = run_single_game(
                    agent1=agent_a,
                    agent2=agent_b,
                    game_number=g,
                    first_agent=first_agent,
                    verbose=verbose,
                )
                game_results.append(result)

                total_nodes += result.agent1_nodes + result.agent2_nodes
                total_pruned += result.agent1_pruned + result.agent2_pruned
                total_time += result.execution_time

                if result.winner == agent_a.name:
                    wins_a += 1
                elif result.winner == agent_b.name:
                    wins_b += 1
                else:
                    draws += 1

            avg_nodes = total_nodes / num_games_per_depth
            avg_pruned = total_pruned / num_games_per_depth
            avg_time = total_time / num_games_per_depth

            # Summarize result pattern
            if draws == num_games_per_depth:
                result_summary = "All Draws"
            elif wins_a > wins_b:
                result_summary = f"{agent_a.name} dominates ({wins_a}W/{wins_b}L/{draws}D)"
            elif wins_b > wins_a:
                result_summary = f"{agent_b.name} dominates ({wins_b}W/{wins_a}L/{draws}D)"
            else:
                result_summary = f"Even ({wins_a}W/{wins_b}L/{draws}D)"

            depth_data = {
                "depth": depth,
                "result": result_summary,
                "avg_nodes_evaluated": round(avg_nodes, 1),
                "avg_nodes_pruned": round(avg_pruned, 1),
                "avg_time": round(avg_time, 6),
                "wins_a": wins_a,
                "wins_b": wins_b,
                "draws": draws,
                "total_nodes": total_nodes,
                "total_pruned": total_pruned,
                "total_time": round(total_time, 6),
            }
            all_depth_results.append(depth_data)

            print(f"\n  Depth {depth} Summary:")
            print(f"    Result: {result_summary}")
            print(f"    Avg. nodes evaluated: {avg_nodes:.1f}")
            print(f"    Avg. nodes pruned:    {avg_pruned:.1f}")
            print(f"    Avg. execution time:  {avg_time:.6f}s")

        # Print consolidated table
        print("\n" + "=" * 60)
        print("  SEARCH DEPTH EXPERIMENT RESULTS")
        print("=" * 60)
        print(f"  {'Depth':<8}{'Result':<30}{'Avg Nodes':<15}{'Avg Pruned':<15}{'Avg Time (s)':<15}")
        print(f"  {'-'*8}{'-'*30}{'-'*15}{'-'*15}{'-'*15}")
        for d in all_depth_results:
            print(
                f"  {d['depth']:<8}"
                f"{d['result']:<30}"
                f"{d['avg_nodes_evaluated']:<15}"
                f"{d['avg_nodes_pruned']:<15}"
                f"{d['avg_time']:<15.6f}"
            )
        print("=" * 60)

        return all_depth_results

    @staticmethod
    def save_results(
        results: List[Dict[str, Any]],
        filepath: Optional[str] = None,
    ) -> str:
        """
        Save search-depth experiment results to a CSV file.

        Args:
            results: List of depth experiment result dicts.
            filepath: Path to the output CSV file. Defaults to results/depth_results.csv.

        Returns:
            The path to the saved CSV file.
        """
        if filepath is None:
            filepath = os.path.join(RESULTS_DIR, "depth_results.csv")

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "depth", "result", "avg_nodes_evaluated",
                "avg_nodes_pruned", "avg_time",
            ])
            for d in results:
                writer.writerow([
                    d["depth"],
                    d["result"],
                    d["avg_nodes_evaluated"],
                    d["avg_nodes_pruned"],
                    d["avg_time"],
                ])

        print(f"\n  Depth experiment results saved to: {filepath}")
        return filepath
