import os
import pytest
from unittest.mock import patch, MagicMock
from clearinghouse.dependencies import SchwabService, EnvSettings
from clearinghouse.services.orders_service import (
    fetch_positions,
    fetch_orders,
    fetch_quote,
    fetch_quotes,
    fetch_transactions,
    fetch_transaction_details,
)