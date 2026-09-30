from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.game import TicTacToe

class Heuristic(ABC):
    """Abstract base class for board evaluation heuristics."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this heuristic."""
        pass
    
    @abstractmethod
    def evaluate(self, game: 'TicTacToe', maximizing_player: str) -> int:
        """Evaluate the board position for the maximizing player."""
        pass


def _get_all_lines(board_state: List[List[str]]) -> List[List[str]]:
    """Helper function to extract all rows, columns, and diagonals from the board."""
    lines = []
    # Rows
    for r in range(3):
        lines.append(board_state[r])
    # Columns
    for c in range(3):
        lines.append([board_state[r][c] for r in range(3)])
    # Diagonals
    lines.append([board_state[i][i] for i in range(3)])
    lines.append([board_state[i][2-i] for i in range(3)])
    return lines


class AggressiveHeuristic(Heuristic):
    """
    H1 (Aggressive) Heuristic.
    Values own threats higher relative to opponent threats.
    """
    
    @property
    def name(self) -> str:
        return 'H1 (Aggressive)'
        
    def evaluate(self, game: 'TicTacToe', maximizing_player: str) -> int:
        winner = game.check_winner()
        if winner == maximizing_player:
            return 100
        elif winner is not None:
            return -100
        elif game.is_draw():
            return 0
            
        opponent_player = 'O' if maximizing_player == 'X' else 'X'
        score = 0
        
        lines = _get_all_lines(game.board)
        
        for line in lines:
            max_count = line.count(maximizing_player)
            opp_count = line.count(opponent_player)
            empty_count = line.count('')
            
            if max_count == 2 and empty_count == 1:
                score += 10
            elif max_count == 1 and empty_count == 2:
                score += 1
            elif opp_count == 2 and empty_count == 1:
                score -= 8
            elif opp_count == 1 and empty_count == 2:
                score -= 1
                
        # Center bonus
        center = game.board[1][1]
        if center == maximizing_player:
            score += 3
        elif center == opponent_player:
            score -= 3
            
        return score


class DefensiveHeuristic(Heuristic):
    """
    H2 (Defensive) Heuristic.
    Values blocking opponent threats higher and considers positional control via corners.
    """
    
    @property
    def name(self) -> str:
        return 'H2 (Defensive)'
        
    def evaluate(self, game: 'TicTacToe', maximizing_player: str) -> int:
        winner = game.check_winner()
        if winner == maximizing_player:
            return 100
        elif winner is not None:
            return -100
        elif game.is_draw():
            return 0
            
        opponent_player = 'O' if maximizing_player == 'X' else 'X'
        score = 0
        
        lines = _get_all_lines(game.board)
        
        for line in lines:
            max_count = line.count(maximizing_player)
            opp_count = line.count(opponent_player)
            empty_count = line.count('')
            
            if max_count == 2 and empty_count == 1:
                score += 10
            elif max_count == 1 and empty_count == 2:
                score += 1
            elif opp_count == 2 and empty_count == 1:
                score -= 12
            elif opp_count == 1 and empty_count == 2:
                score -= 2
                
        # Center bonus
        center = game.board[1][1]
        if center == maximizing_player:
            score += 3
        elif center == opponent_player:
            score -= 3
            
        # Corner bonus
        corners = [
            game.board[0][0], game.board[0][2],
            game.board[2][0], game.board[2][2]
        ]
        max_corners = corners.count(maximizing_player)
        opp_corners = corners.count(opponent_player)
        score += 2 * max_corners
        score -= 2 * opp_corners
        
        return score
