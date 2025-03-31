import math

def calculate_rmse(value1: float, value2: float) -> float:
    """
    Calculate the Root Mean Squared Error (RMSE) between two float values.

    Args:
        value1 (float): The first value.
        value2 (float): The second value.

    Returns:
        float: The RMSE between the two values.
    """
    rmse = math.sqrt((value1 - value2) ** 2)
    return rmse
