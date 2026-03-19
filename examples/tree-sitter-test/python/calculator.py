"""A simple calculator module."""


class Calculator:
    """Basic arithmetic calculator."""

    def __init__(self):
        self.history = []

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def clear_history(self):
        """Clear calculation history."""
        self.history = []
