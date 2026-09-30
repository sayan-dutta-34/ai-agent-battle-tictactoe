# AI Agent Battle: Tic-Tac-Toe

**Assignment X_02 | AI/ML Laboratory | B.Tech. 5th Semester**

This project builds two named AI agents and makes them compete in automated Tic-Tac-Toe games. The experiments investigate how search depth, heuristic design, and Alpha-Beta pruning affect decisions and computational cost.

## Requirements

- Python 3.8 or newer
- No third-party packages are required

## Assignment Requirements Covered

- 3x3 Tic-Tac-Toe game engine
- Minimax search with Alpha-Beta pruning
- Configurable search depth
- Two named AI agents with different heuristics
- Automated AI-vs-AI games
- Search-depth experiment
- Alternating starting player
- Node, pruning, move-count, and execution-time statistics
- CSV result files
- Analysis and conclusion in this README

## Project Structure

```text
ai-agent-battle-tictactoe/
├── README.md
├── src/
│   ├── __init__.py
│   ├── agents.py
│   ├── experiment.py
│   ├── game.py
│   ├── heuristic.py
│   ├── main.py
│   ├── minimax.py
│   └── utils/
│       ├── __init__.py
│       └── errors.py
└── results/
    ├── depth_results.csv
    └── results.csv
```

## How to Run

Open a terminal in the project root, the directory containing `README.md`, and run:

```bash
# Run both experiments
python -m src.main

# Run only the 10-game AI battle
python -m src.main --battle

# Run only the search-depth experiment
python -m src.main --depth

# Suppress per-move board output
python -m src.main --quiet

# Make random tie-breaking reproducible
python -m src.main --seed 42
```

Useful battle options:

```bash
python -m src.main --battle --nexus-depth 3 --titan-depth 3 --num-games 10 --seed 42
```

The program writes output files to `results/`:

- `results/results.csv`: one row for every battle game
- `results/depth_results.csv`: one row for every tested search depth

The program uses random tie-breaking when multiple moves have the same Minimax score. Use `--seed` when a repeatable run is needed. Execution times can vary by computer and should be regenerated rather than treated as fixed benchmarks.

## Implementation

### Game Engine

`src/game.py` contains the `TicTacToe` class. The board is a 3x3 list of lists, with `''` representing an empty cell and `X` and `O` representing the players. The class provides methods to display the board, make and undo moves, return valid moves, detect a winner, and detect a draw or terminal position.

### Minimax and Alpha-Beta

`src/minimax.py` implements Minimax with configurable remaining search depth. MAX maximizes the score for the selected agent and MIN minimizes it for the opponent.

Terminal positions use these scores:

| Position   | Score |
| ---------- | ----: |
| Agent win  |  +100 |
| Draw       |     0 |
| Agent loss |  -100 |

At the depth limit, a heuristic evaluates non-terminal positions. Alpha-Beta pruning skips branches that cannot change the final Minimax decision. The implementation records both evaluated nodes and pruned nodes.

### Heuristics

Both heuristics inspect the eight possible winning lines and the center square. H2 also inspects the four corners.

#### H1: Aggressive

Used by NEXUS.

| Feature                               | Score |
| ------------------------------------- | ----: |
| Two agent marks and one empty cell    |   +10 |
| One agent mark and two empty cells    |    +1 |
| Two opponent marks and one empty cell |    -8 |
| One opponent mark and two empty cells |    -1 |
| Agent controls the center             |    +3 |
| Opponent controls the center          |    -3 |

H1 gives relatively strong weight to creating offensive threats.

#### H2: Defensive

Used by TITAN. H2 uses the same line and center scores, but changes the defensive and corner weights:

| Feature                               | Score |
| ------------------------------------- | ----: |
| Two opponent marks and one empty cell |   -12 |
| One opponent mark and two empty cells |    -2 |
| Each agent-controlled corner          |    +2 |
| Each opponent-controlled corner       |    -2 |

H2 prioritizes blocking threats and controlling corners. Neither agent is random-only or deliberately weakened.

## Agent Configurations

| Agent | Algorithm            | Heuristic       | Default depth |
| ----- | -------------------- | --------------- | ------------: |
| NEXUS | Minimax + Alpha-Beta | H1 (Aggressive) |             3 |
| TITAN | Minimax + Alpha-Beta | H2 (Defensive)  |             3 |

## Experiment 1: Search Depth

The depth experiment keeps the game, algorithm, and heuristic fixed. Both agents use H1, five games are played at each depth, and the starting agent alternates. Only the depth changes.

### Recorded Results

These values are read from `results/depth_results.csv`.

| Depth | Result                     | Average nodes evaluated | Average nodes pruned | Average time (s) |
| ----: | -------------------------- | ----------------------: | -------------------: | ---------------: |
|     1 | TITAN dominates (3W/2L/0D) |                    39.0 |                  0.0 |         0.000350 |
|     2 | All draws                  |                   285.0 |                  0.0 |         0.002101 |
|     3 | All draws                  |                   932.6 |                572.4 |         0.005917 |
|     4 | All draws                  |                 3,357.2 |              1,296.4 |         0.020376 |

### Depth Analysis

1. Increasing depth changed the decisions and outcomes at depth 1. From depth 2 onward, the agents avoided losses and all games were draws.
2. Average execution time increased at every depth. Depth 4 took substantially longer than depth 1.
3. Average evaluated nodes increased from 39.0 at depth 1 to 3,357.2 at depth 4, showing the growing cost of exploring more future positions.
4. No pruning was recorded at depths 1 and 2 in this run. At depths 3 and 4, Alpha-Beta pruned 572.4 and 1,296.4 nodes on average.
5. Deeper search improved decision quality in this experiment, but depth 3 and depth 4 produced the same game outcome while depth 4 required more work.

## Experiment 2: 10-Game AI Battle

The main battle uses NEXUS and TITAN at their default depth of 3. The starting agent alternates to reduce first-player bias:

- Odd-numbered games: NEXUS starts
- Even-numbered games: TITAN starts

### Recorded Results

These values are read from `results/results.csv`.

| Game | First | Winner | Moves | NEXUS nodes | TITAN nodes | NEXUS pruned | TITAN pruned | Time (s) |
| ---: | ----- | ------ | ----: | ----------: | ----------: | -----------: | -----------: | -------: |
|    1 | NEXUS | DRAW   |     9 |         557 |         347 |          374 |          227 | 0.007866 |
|    2 | TITAN | DRAW   |     9 |         354 |         560 |          220 |          371 | 0.005970 |
|    3 | NEXUS | DRAW   |     9 |         586 |         391 |          345 |          183 | 0.006506 |
|    4 | TITAN | DRAW   |     9 |         367 |         571 |          207 |          360 | 0.006078 |
|    5 | NEXUS | DRAW   |     9 |         557 |         347 |          374 |          227 | 0.005767 |
|    6 | TITAN | DRAW   |     9 |         355 |         610 |          219 |          333 | 0.006237 |
|    7 | NEXUS | DRAW   |     9 |         571 |         384 |          360 |          190 | 0.006108 |
|    8 | TITAN | DRAW   |     9 |         384 |         568 |          190 |          375 | 0.006310 |
|    9 | NEXUS | DRAW   |     9 |         574 |         376 |          357 |          198 | 0.006068 |
|   10 | TITAN | DRAW   |     9 |         383 |         611 |          191 |          332 | 0.006422 |

### Battle Summary

| Metric                        |    Value |
| ----------------------------- | -------: |
| NEXUS wins                    |        0 |
| TITAN wins                    |        0 |
| Draws                         |       10 |
| First-player wins             |   0 / 10 |
| Average moves                 |      9.0 |
| Average NEXUS nodes evaluated |    468.8 |
| Average TITAN nodes evaluated |    476.5 |
| Average NEXUS nodes pruned    |    283.7 |
| Average TITAN nodes pruned    |    279.6 |
| Average execution time        | 0.0063 s |

## Observations

- The agents made different choices because H1 and H2 assign different values to threats, defensive positions, and corners.
- At depth 3, both agents were strong enough to prevent the other from winning, so all ten games ended in draws.
- The experiment did not show a first-player advantage: no first player won.
- The agent that moved first generally evaluated more nodes because more legal moves were available early in its search. This was a computational pattern, not a winning advantage.
- Neither agent can be called the overall winner from this battle. The result shows that both heuristic strategies produced competitive play at depth 3.

## Conclusion

The project demonstrates that deeper Minimax search can improve decisions, but the improvement has a computational cost. Alpha-Beta pruning reduces the work without changing the Minimax objective. The two heuristics produce different playing preferences, yet both agents reach the same draw-heavy result when given enough search depth. In this Tic-Tac-Toe experiment, the most important finding is the trade-off between decision quality and computation rather than which named agent wins more games.

## Results Files

- [results/results.csv](results/results.csv) contains the 10 battle games.
- [results/depth_results.csv](results/depth_results.csv) contains the depth comparison.
