from typing import List, Tuple
import math

def calculate_rmse(pairs: List[Tuple[float,float]]) -> float:
    """
    Calculate the Root Mean Squared Error (RMSE) between two float values.

    Args:
        pairs: List of tuples of float values. (target, actual)

    Returns:
        float: The RMSE between the two values.
    """
    squares = sum([(t - v) ** 2 for t,v in pairs])
    return math.sqrt(squares/len(pairs))
