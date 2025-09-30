"""
Co-Scientist SDK Logger Module
==============================
Professional logging system with colored output and multiple log levels.
"""

import json
import logging
from enum import Enum
from typing import Dict, Optional

# Use try-except for colorama to make it optional
try:
    from colorama import init

    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

    # Define dummy values if colorama not available
    class DummyColor:
        def __getattr__(self, name):
            return ""

    Fore = DummyColor()
    Back = DummyColor()
    Style = DummyColor()


class LogLevel(Enum):
    """
    Enumeration of available log levels.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    SUCCESS = 25  # Custom level between INFO and WARNING


class LogIcons:
    """
    Unicode icons for different log types.
    """

    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "📌"
    DEBUG = "🔧"
    API = "🌐"
    AUTH = "🔐"
    DATA = "📊"
    PROCESS = "🏃"
    TIME = "⏱️"
    SEARCH = "🔍"
    DOCUMENT = "📄"
    IDEA = "💡"
    ROCKET = "🚀"
    WAIT = "⏳"
    ARROW = "➜"


class Logger:
    """
    Main logger class for Co-Scientist SDK.
    """

    def __init__(
        self,
        name: str = "Cosci",
        level: LogLevel = LogLevel.INFO,
        console_output: bool = True,
        file_output: Optional[str] = None,
        include_timestamp: bool = True,
    ):
        """Initialize the logger."""
        self.name = name
        self.logger = logging.getLogger(name)

        # Register custom SUCCESS level
        logging.addLevelName(25, "SUCCESS")

        # Set base level
        self.logger.setLevel(level.value)
        self.logger.propagate = False
        self.logger.handlers = []

        # Console handler
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level.value)

            if include_timestamp:
                fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            else:
                fmt = "%(name)s - %(levelname)s - %(message)s"

            formatter = logging.Formatter(fmt, datefmt="%H:%M:%S")
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File handler
        if file_output:
            file_handler = logging.FileHandler(file_output, mode="a", encoding="utf-8")
            file_handler.setLevel(level.value)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self._indent_level = 0

    def debug(self, message: str, icon: str = ""):
        """
        Log a debug message.
        """
        self.logger.debug(f"{icon} {message}" if icon else message)

    def info(self, message: str, icon: str = ""):
        """
        Log an info message.
        """
        self.logger.info(f"{icon} {message}" if icon else message)

    def warning(self, message: str, icon: str = ""):
        """
        Log a warning message.
        """
        self.logger.warning(f"{icon} {message}" if icon else message)

    def error(self, message: str, icon: str = ""):
        """
        Log an error message.
        """
        self.logger.error(f"{icon} {message}" if icon else message)

    def critical(self, message: str, icon: str = ""):
        """
        Log a critical message.
        """
        self.logger.critical(f"{icon} {message}" if icon else message)

    def success(self, message: str, icon: str = ""):
        """
        Log a success message.
        """
        self.logger.log(25, f"{icon} {message}" if icon else message)

    def indent(self):
        """
        Increase indentation level.
        """
        self._indent_level += 1

    def dedent(self):
        """
        Decrease indentation level.
        """
        self._indent_level = max(0, self._indent_level - 1)

    def section(self, title: str, separator: str = "=", width: int = 60):
        """
        Log a section header.
        """
        sep_line = separator * width
        self.info("")
        self.info(sep_line)
        self.info(title.center(width))
        self.info(sep_line)

    def subsection(self, title: str):
        """
        Log a subsection header.
        """
        self.info(f"\n=> {title}")
        self.indent()

    def end_subsection(self):
        """
        End a subsection.
        """
        self.dedent()

    def json(
        self, data: Dict, message: str = "Data:", level: LogLevel = LogLevel.DEBUG
    ):
        """
        Log JSON data.
        """
        self.logger.log(level.value, f"{message}\n{json.dumps(data, indent=2)}")

    def list(
        self, items: list, message: str = "Items:", level: LogLevel = LogLevel.INFO
    ):
        """
        Log a list.
        """
        self.logger.log(level.value, message)
        for item in items:
            self.logger.log(level.value, f"  - {item}")

    def progress(self, current: int, total: int, message: str = "Progress"):
        """
        Log progress information.
        """
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 20
        filled_length = int(bar_length * current // total) if total > 0 else 0
        bar = "#" * filled_length + "-" * (bar_length - filled_length)
        self.info(f"{message}: [{bar}] {percentage:.1f}% ({current}/{total})")

    def process_start(self, process_name: str):
        """
        Log the start of a process.
        """
        self.info(f"Starting: {process_name}", LogIcons.PROCESS)
        self.indent()

    def process_complete(self, process_name: str):
        """
        Log the completion of a process.
        """
        self.dedent()
        self.success(f"Completed: {process_name}", LogIcons.SUCCESS)

    def process_failed(self, process_name: str, error: Optional[str] = None):
        """
        Log a process failure.
        """
        self.dedent()
        message = f"Failed: {process_name}"
        if error:
            message += f" - {error}"
        self.error(message, LogIcons.ERROR)


def get_logger(
    name: str = "Cosci", level: LogLevel = LogLevel.INFO, **kwargs
) -> Logger:
    """
    Get or create a logger instance.
    """
    return Logger(name, level, **kwargs)
