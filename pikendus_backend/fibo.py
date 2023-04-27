# -*- coding: utf-8 -*-
"""Module that performs fibonacci-related computations

"""
import math


__all__ = ["fibonacci"]


def fibonacci(n: int) -> int:
    """Computes the fibonacci sequence

    Args:
        n: The 0-based index of the fibonacci term

    Returns:
        The n-th fibonacci term

    Examples:
        >>> fibonacci(2)
        2

    """
    phi = (1 + math.sqrt(5)) / 2
    fres = math.pow(phi, (n + 1)) / math.sqrt(5)
    return int(round(fres, 0))
