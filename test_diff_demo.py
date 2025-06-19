#!/usr/bin/env python3
"""Demo script to test the diff visualization feature."""


def hello_world() -> str:
    """Print a greeting message."""
    print("Hello, World!")
    return "success"


def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    result = a + b
    print(f"The sum of {a} and {b} is {result}")
    return result


if __name__ == "__main__":
    hello_world()
    calculate_sum(5, 3)
