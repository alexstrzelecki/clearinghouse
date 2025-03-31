from typing import List, Optional, Any
from clearinghouse.models.request import (
    NumericalOrder
)

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
