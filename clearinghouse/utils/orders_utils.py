from typing import List, Optional, Dict, Tuple
from itertools import product

from clearinghouse.models.request import (
    NumericalOrder
)
from clearinghouse.utils.math_utils import calculate_rmse

DEFAULT_INSTRUCTION_ORDER = [
    "SELL",
    "SELL_SHORT",
    "BUY_TO_COVER",
    "BUY"
]


def sort_orders(
        orders: List[NumericalOrder],
        attr: Optional[str] = "instruction",
        sort_order: Optional[List[str]] = None
) -> List[NumericalOrder]:
    """
    Util function to sort a list of NumericalOrder based on an attr (most commonly instruction type).

    :param orders: List of NumericalOrder objects to be sorted.
    :param attr: Attribute of NumericalOrder to sort by. Defaults to "instruction".
    :param sort_order: Custom order for sorting. Defaults to DEFAULT_INSTRUCTION_ORDER.
    :return: Sorted list of NumericalOrder objects.

    :raises AttributeError: If the specified attr does not exist on a NumericalOrder object.
    """
    if not sort_order:
        sort_order = DEFAULT_INSTRUCTION_ORDER

    if not orders:
        return []

    return sorted(
        orders,
        key=lambda order: sort_order.index(getattr(order, attr))
    )


def find_order_minimum_error(
        order_options: Dict[str, Tuple[float, Tuple[float, float]]],
        capital_cap: Optional[float] = float('inf'),
) -> Dict[str, int]:

    """
    Calculate permutations of options for each symbol and track the original choice by index.
    The input options are intended to be total position size.

    example:
    {
    "A": (100, (80, 130)),
    "B": (100, (100,)),
    "C": (80, (79, 140))
    }
    ->
    {"A": 0, "B": 0, "C": 1}


    :param order_options: Dictionary with symbols as keys and tuples of (target, options) as values.
    :param capital_cap: The max amount of money to spend in this transaction
    :return: List of dictionaries mapping symbols to indices of chosen options.
    """
    if not order_options:
        return {}

    # Generate all permutations of indices for the options
    # e.g. [(0, 0, 0), (0, 0, 1), (1, 0, 0), (1, 0, 1)]
    symbol_keys = list(order_options.keys())
    index_permutations = list(product(*[range(len(options)) for _, options in order_options.values()]))
    best_permutation = None
    smallest_rmse = float('inf')

    for indices in index_permutations:
        pairs = []
        capital_value = 0

        for k, idx in enumerate(indices):
            target, options = order_options[symbol_keys[k]]
            pairs.append((target, options[idx]))
            capital_value += options[idx]

        # Discard permutations that exceed the cap
        if capital_value > capital_cap:
            continue

        rmse = calculate_rmse(pairs)
        if rmse < smallest_rmse:
            smallest_rmse = rmse
            best_permutation = indices

    if not best_permutation:
        return {}

    return {symbol_keys[k]: idx for k, idx in enumerate(best_permutation)}
