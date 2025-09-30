"""
High-level client for the Cosci SDK.
"""

from typing import Any, Dict, List, Optional

from cosci.api_client import APIClient
from cosci.auth import Authenticator
from cosci.config import Config
from cosci.exceptions import CosciError
from cosci.logger import LogIcons, LogLevel, get_logger
from cosci.models import Idea, ResearchSession
from cosci.session import SessionManager


class CoScientist:
    """
    High-level client for Google Co-Scientist Discovery Engine.

    Example:
        # Using config file
        client = CoScientist.from_config("config.yaml")
        ideas = client.generate_ideas("Your research question")

        # Or with auto-discovery
        client = CoScientist.from_config()  # Looks for config.yaml
        ideas = client.generate_ideas("Your research question")
    """

    def __init__(self, config: Config, auto_initialize: bool = True):
        """
        Initialize the Co-Scientist client with a Config object.

        Args:
            config: Configuration object
            auto_initialize: Whether to initialize immediately
        """
        self.config = config

        # Validate configuration
        config.validate()

        # Set up logger
        log_level = LogLevel[config.log_level.upper()]
        self.logger = get_logger("CoScientist", log_level, file_output=config.log_file)

        self.logger.section("Co-Scientist SDK Initialization", "=", 60)

        # Components
        self.authenticator = None
        self.api_client = None
        self.session_manager = None

        if auto_initialize:
            self._initialize()

    @classmethod
    def from_config(cls, config_path: str = "config.yaml") -> "CoScientist":
        """
        Create client from YAML config file.

        Args:
            config_path: Path to config YAML file

        Returns:
            Configured CoScientist client
        """
        config = Config.from_yaml(config_path)
        return cls(config)

    def _initialize(self):
        """Initialize authentication and API clients."""
        try:
            # Authenticate
            self.authenticator = Authenticator(
                service_account_path=self.config.credentials_path,
                project_id=self.config.project_id,
                logger_name="Auth",
                log_level=LogLevel[self.config.log_level.upper()],
            )
            self.authenticator.authenticate()

            # Create API client
            self.api_client = APIClient(
                authenticator=self.authenticator,
                project_id=self.config.project_id,
                engine=self.config.engine,
                location=self.config.location,
                collection=self.config.collection,
                logger_name="API",
                log_level=LogLevel[self.config.log_level.upper()],
                timeout=self.config.timeout,
            )

            # Create session manager
            self.session_manager = SessionManager(
                api_client=self.api_client,
                logger=get_logger(
                    "SessionManager", LogLevel[self.config.log_level.upper()]
                ),
            )

            self.logger.success("Co-Scientist client ready", LogIcons.ROCKET)

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", LogIcons.ERROR)
            raise CosciError(f"Failed to initialize client: {e}")

    def generate_ideas(
        self,
        research_goal: str,
        wait_timeout: Optional[int] = None,
        min_ideas: Optional[int] = None,
    ) -> List[Idea]:
        """
        Generate research ideas for a given goal.

        Args:
            research_goal: The research question or goal
            wait_timeout: Override timeout from config
            min_ideas: Override min_ideas from config

        Returns:
            List of generated ideas
        """
        # Use config defaults if not specified
        wait_timeout = wait_timeout or self.config.timeout
        min_ideas = min_ideas or self.config.min_ideas

        self.logger.section("Research Ideation", "=", 60)
        self.logger.info(f"Goal: {research_goal[:200]}...", LogIcons.IDEA)
        self.logger.info(f"Timeout: {wait_timeout}s, Min ideas: {min_ideas}")

        try:
            # Create session
            session = self.session_manager.create_session(research_goal)

            # Wait for instance
            instance = self.session_manager.wait_for_instance(
                session,
                timeout=min(60, wait_timeout),
                poll_interval=self.config.poll_interval,
            )

            # Poll for ideas
            ideas = self.session_manager.poll_for_ideas(
                instance,
                timeout=wait_timeout,
                poll_interval=self.config.poll_interval,
                min_ideas=min_ideas,
            )

            self.logger.success(f"Generated {len(ideas)} ideas", LogIcons.SUCCESS)
            return ideas

        except Exception as e:
            self.logger.error(f"Failed to generate ideas: {e}", LogIcons.ERROR)
            raise CosciError(f"Idea generation failed: {e}")

    def get_session(self, session_id: str) -> ResearchSession:
        """
        Get information about an existing session.
        """
        return self.session_manager.get_session(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions.
        """
        response = self.api_client.get("sessions")
        return response.get("sessions", [])

    def close(self):
        """
        Close the client and clean up resources.
        """
        if self.api_client:
            self.api_client.close()
        self.logger.success("Client closed", LogIcons.SUCCESS)

    def __enter__(self):
        """
        Context manager entry.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        self.close()
