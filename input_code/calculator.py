#input_code/calculator.py
class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, a, b):
        """Adds two numbers and returns the result."""
        return a + b

    def subtract(self, a, b):
        """Subtracts b from a and returns the result."""
        return a - b

    def multiply(self, a, b):
        """Multiplies two numbers and returns the result."""
        return a * b

    def divide(self, a, b):
        """Divides a by b and returns the result. Returns None if division by zero."""
        if b == 0:
            return None
        return a / b

def greet_user(name):
    """Greets the user with a personalized message."""
    return f"Hello, {name}! Welcome to the smart calculator."
