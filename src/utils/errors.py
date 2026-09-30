"""
Custom exceptions for the Tic-Tac-Toe game.
"""

class GameError(Exception):
    """Base exception for all game-related errors."""
    pass


class InvalidMoveError(GameError):
    """Exception raised for invalid moves on the game board."""
    pass


class InvalidPlayerError(GameError):
    """Exception raised when an invalid player symbol is provided."""
    pass
