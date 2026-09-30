"""
Tic-Tac-Toe game engine implementation.
"""

import copy
from typing import List, Tuple, Optional

from src.utils.errors import InvalidMoveError, InvalidPlayerError


class TicTacToe:
    """
    Represents the Tic-Tac-Toe game state and logic.
    """

    def __init__(self) -> None:
        """
        Initializes an empty 3x3 game board.
        Empty cells are represented by empty strings ''.
        """
        self.board: List[List[str]] = [['' for _ in range(3)] for _ in range(3)]

    def display(self) -> str:
        """
        Returns a string representation of the board in a nice format.

        Returns:
            str: The formatted board.
        """
        rows = []
        for i, row in enumerate(self.board):
            formatted_row = " | ".join([cell if cell else " " for cell in row])
            rows.append(f" {formatted_row} ")
            if i < 2:
                rows.append("---+---+---")
        return "\n".join(rows)

    def make_move(self, row: int, col: int, player: str) -> bool:
        """
        Makes a move on the board for the given player.

        Args:
            row (int): The row index (0-2).
            col (int): The column index (0-2).
            player (str): The player making the move ('X' or 'O').

        Returns:
            bool: True if the move was successfully made.

        Raises:
            InvalidPlayerError: If the player symbol is invalid.
            InvalidMoveError: If the move is out of bounds or the cell is occupied.
        """
        if player not in ('X', 'O'):
            raise InvalidPlayerError(f"Invalid player '{player}'. Must be 'X' or 'O'.")

        if not (0 <= row < 3 and 0 <= col < 3):
            raise InvalidMoveError(f"Move out of bounds: ({row}, {col}). Must be between 0 and 2.")

        if self.board[row][col] != '':
            raise InvalidMoveError(f"Cell at ({row}, {col}) is already occupied.")

        self.board[row][col] = player
        return True

    def undo_move(self, row: int, col: int) -> None:
        """
        Undoes a move by clearing the specified cell.

        Args:
            row (int): The row index (0-2).
            col (int): The column index (0-2).
        """
        if 0 <= row < 3 and 0 <= col < 3:
            self.board[row][col] = ''

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """
        Returns a list of all valid (empty) moves on the board.

        Returns:
            List[Tuple[int, int]]: A list of (row, col) tuples.
        """
        moves = []
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == '':
                    moves.append((r, c))
        return moves

    def check_winner(self) -> Optional[str]:
        """
        Checks if there is a winner on the board.

        Returns:
            Optional[str]: 'X' or 'O' if there is a winner, otherwise None.
        """
        # Check rows and columns
        for i in range(3):
            # Check row
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != '':
                return self.board[i][0]
            # Check column
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != '':
                return self.board[0][i]

        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]

        return None

    def is_draw(self) -> bool:
        """
        Checks if the game is a draw (board is full and no winner).

        Returns:
            bool: True if the game is a draw, False otherwise.
        """
        return self.check_winner() is None and len(self.get_valid_moves()) == 0

    def is_terminal(self) -> bool:
        """
        Checks if the game has ended (either a winner exists or it's a draw).

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.check_winner() is not None or len(self.get_valid_moves()) == 0

    def copy(self) -> 'TicTacToe':
        """
        Creates a deep copy of the current game state.

        Returns:
            TicTacToe: A new TicTacToe instance with the copied board.
        """
        new_game = TicTacToe()
        new_game.board = copy.deepcopy(self.board)
        return new_game

    @staticmethod
    def get_opponent(player: str) -> str:
        """
        Returns the opponent of the given player.

        Args:
            player (str): The current player ('X' or 'O').

        Returns:
            str: The opponent player ('O' or 'X').

        Raises:
            InvalidPlayerError: If the player symbol is invalid.
        """
        if player == 'X':
            return 'O'
        elif player == 'O':
            return 'X'
        else:
            raise InvalidPlayerError(f"Invalid player '{player}'. Must be 'X' or 'O'.")
