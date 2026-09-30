"""
AI Agent Battle -- Tic-Tac-Toe
Main entry point for the application.

Assignment X_02 | AI/ML Laboratory | B.Tech. 5th Semester

Usage:
    python -m src.main              Run all experiments (depth + battle)
    python -m src.main --battle     Run only the 10-game AI Agent Battle
    python -m src.main --depth      Run only the Search-Depth Experiment
    python -m src.main --quiet      Run with minimal output (no per-move details)
"""

import argparse
import sys
import random

from src.agents import create_nexus, create_titan
from src.experiment import Experiment, DepthExperiment


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Agent Battle -- Tic-Tac-Toe | Minimax + Alpha-Beta Pruning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m src.main              Run all experiments\n"
            "  python -m src.main --battle     Run only the 10-game battle\n"
            "  python -m src.main --depth      Run only the depth experiment\n"
            "  python -m src.main --quiet      Run with minimal per-move output\n"
            "  python -m src.main --seed 42    Set random seed for reproducibility\n"
        ),
    )

    parser.add_argument(
        "--battle", action="store_true",
        help="Run only the 10-game AI Agent Battle (Experiment 2)",
    )
    parser.add_argument(
        "--depth", action="store_true",
        help="Run only the Search-Depth Experiment (Experiment 1)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-move game output (show only summaries)",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility (default: None = non-deterministic)",
    )
    parser.add_argument(
        "--nexus-depth", type=int, default=3,
        help="Search depth for NEXUS agent in battle (default: 3)",
    )
    parser.add_argument(
        "--titan-depth", type=int, default=3,
        help="Search depth for TITAN agent in battle (default: 3)",
    )
    parser.add_argument(
        "--num-games", type=int, default=10,
        help="Number of games in the battle (default: 10)",
    )

    return parser.parse_args()


def run_depth_experiment(verbose: bool = True) -> None:
    """
    Run Experiment 1: Search-Depth Analysis.

    Tests depths 1-4 with both agents using the same heuristic (H1)
    to isolate the effect of search depth on game performance and
    computational cost.
    """
    print("\n" + "#" * 60)
    print("  EXPERIMENT 1: DOES DEEPER THINKING HELP?")
    print("#" * 60)

    results = DepthExperiment.run(
        depths=[1, 2, 3, 4],
        num_games_per_depth=5,
        verbose=verbose,
    )

    DepthExperiment.save_results(results)


def run_battle(
    nexus_depth: int = 3,
    titan_depth: int = 3,
    num_games: int = 10,
    verbose: bool = True,
) -> None:
    """
    Run Experiment 2: AI Agent Battle.

    NEXUS (H1 Aggressive) vs TITAN (H2 Defensive).
    Alternating starting players across 10 games.
    """
    print("\n" + "#" * 60)
    print("  EXPERIMENT 2: AI AGENT BATTLE")
    print("#" * 60)

    nexus = create_nexus(depth=nexus_depth)
    titan = create_titan(depth=titan_depth)

    print(f"\n  Agent Configurations:")
    print(f"    {nexus}")
    print(f"    {titan}")

    experiment = Experiment(agent1=nexus, agent2=titan)
    results = experiment.run_battle(num_games=num_games, verbose=verbose)

    # Print and save summary
    Experiment.print_summary(results, nexus.name, titan.name)
    Experiment.save_battle_results(results, nexus.name, titan.name)


def main() -> None:
    """Main entry point for the AI Agent Battle program."""
    args = parse_args()

    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print(f"\n  Random seed set to: {args.seed}")

    verbose = not args.quiet

    print("\n" + "=" * 60)
    print("    +-------------------------------------------+")
    print("    |     AI AGENT BATTLE -- TIC-TAC-TOE        |")
    print("    |     Minimax + Alpha-Beta Pruning          |")
    print("    +-------------------------------------------+")
    print("=" * 60)

    # Determine what to run
    run_all = not args.battle and not args.depth

    if run_all or args.depth:
        run_depth_experiment(verbose=verbose)

    if run_all or args.battle:
        run_battle(
            nexus_depth=args.nexus_depth,
            titan_depth=args.titan_depth,
            num_games=args.num_games,
            verbose=verbose,
        )

    print("\n" + "=" * 60)
    print("  All experiments completed successfully!")
    print("  Check the results/ directory for CSV output files.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
