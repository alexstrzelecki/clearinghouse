from fastapi import HTTPException

class ForbiddenException(HTTPException):
    """Raised when accessing a write endpoint in read-only mode"""
    def __init__(self):
        super().__init__(status_code=403, detail="Clearinghouse is in read-only mode.")
