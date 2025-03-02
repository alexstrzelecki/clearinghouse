
class ForbiddenException(Exception):
    """Raised when accessing a write endpoint in read-only mode"""
    pass
