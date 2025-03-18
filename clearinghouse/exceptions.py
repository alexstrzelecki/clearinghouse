from fastapi import HTTPException

class ForbiddenException(HTTPException):
    """Raised when accessing a write endpoint in read-only mode"""
    def __init__(self):
        super().__init__(status_code=403, detail="Clearinghouse is in read-only mode.")


class NullPositionException(HTTPException):
    """Raised when there is no current position in the account."""
    def __init__(self, symbol: str = ""):
        if symbol:
            detail_message = f" No current position position for symbol: {symbol}."
        else:
            detail_message = f"No position found"
        super().__init__(status_code=403, detail=detail_message)


class FailedOrderException(HTTPException):
    """Raised when an order fails to be placed."""
    def __init__(self, symbol: str, message: str):
        detail_message = f"Failed to place order for {symbol}: {message}"
        super().__init__(status_code=502, detail=detail_message)
