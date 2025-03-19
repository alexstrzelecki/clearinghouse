from __future__ import annotations
from clearinghouse.models.request import (
    Order,
)
from clearinghouse.models.response import (
    Quote,
)
from clearinghouse.main import safety_settings


def is_trade_within_max_dollar_trade_size(order: Order) -> bool:
    conditions = [
        order.price * order.amount <= safety_settings.max_dollar_trade_size,
        is_sell_within_max_dollar_sell_size(order),
        is_buy_within_max_dollar_buy_size(order),
    ]
    return all(conditions)


def is_sell_within_max_dollar_sell_size(order: Order) -> bool:
    if order.instruction == "sell":
        return order.price * order.amount <= safety_settings.max_dollar_sell_size
    return True


def is_buy_within_max_dollar_buy_size(order: Order) -> bool:
    if order.instruction == "buy":
        return order.price * order.amount <= safety_settings.max_dollar_buy_size
    return True


def is_short_sale_allowed(order: Order) -> bool:
    raise NotImplementedError()


def is_currency_allowed(order: Order) -> bool:
    raise NotImplementedError()


def is_security_restricted(order: Order) -> bool:
    return order.symbol in safety_settings.restricted_securities
