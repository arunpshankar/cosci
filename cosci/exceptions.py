"""
Custom exceptions for the Cosci SDK.
"""

from typing import Optional


class CosciError(Exception):
    """
    Base exception for all Cosci errors.
    """

    pass


class AuthenticationError(CosciError):
    """
    Authentication-related errors.
    """

    pass


class APIError(CosciError):
    """
    API request errors.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class SessionError(CosciError):
    """
    Session management errors.
    """

    pass


class TimeoutError(CosciError):
    """
    Timeout errors for long-running operations.
    """

    pass


class PollingError(CosciError):
    """
    Errors during polling operations.
    """

    pass
