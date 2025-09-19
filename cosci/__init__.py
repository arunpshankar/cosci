"""
Cosci - Python SDK for Google Co-Scientist Discovery Engine

A production-ready SDK for interacting with Google's Co-Scientist API,
providing research ideation and scientific discovery capabilities.
"""

from cosci.__version__ import __version__, __author__, __email__, __license__
from cosci.client import CoScientist
from cosci.models import ResearchSession, Instance, Idea, SessionState, InstanceState
from cosci.session import SessionManager
from cosci.api_client import APIClient
from cosci.auth import Authenticator, authenticate
from cosci.logger import Logger, LogLevel, LogIcons, get_logger
from cosci.exceptions import (
    CosciError,
    AuthenticationError,
    APIError,
    SessionError,
    TimeoutError,
    PollingError
)

__all__ = [
    # Main client
    "CoScientist",
    
    # Models
    "ResearchSession",
    "Instance", 
    "Idea",
    "SessionState",
    "InstanceState",
    
    # Session management
    "SessionManager",
    
    # Low-level
    "APIClient",
    "Authenticator",
    "authenticate",
    
    # Logging
    "Logger",
    "LogLevel",
    "LogIcons",
    "get_logger",
    
    # Exceptions
    "CosciError",
    "AuthenticationError",
    "APIError",
    "SessionError",
    "TimeoutError",
    "PollingError",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]