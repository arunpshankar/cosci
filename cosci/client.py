"""
High-level client for the Cosci SDK.

This is the main interface users interact with.
"""

from typing import List, Dict, Any

from cosci.api_client import APIClient
from cosci.auth import Authenticator
from cosci.session import SessionManager
from cosci.models import ResearchSession, Idea
from cosci.logger import get_logger, LogLevel, LogIcons
from cosci.exceptions import CosciError


class CoScientist:
    """
    High-level client for Google Co-Scientist Discovery Engine.
    
    This is the main entry point for interacting with the Co-Scientist API.
    It provides a simple, intuitive interface for research ideation.
    
    Example:
        >>> from cosci import CoScientist
        >>> client = CoScientist(
        ...     project_id="my-project",
        ...     engine="my-engine",
        ...     credentials_path="path/to/credentials.json"
        ... )
        >>> ideas = client.generate_ideas("Novel approaches to cancer treatment")
        >>> for idea in ideas:
        ...     print(idea.title)
    """
    
    def __init__(
        self,
        project_id: str,
        engine: str,
        credentials_path: str,
        location: str = "global",
        collection: str = "default_collection",
        log_level: LogLevel = LogLevel.INFO,
        auto_authenticate: bool = True
    ):
        """Initialize the Co-Scientist client."""
        self.logger = get_logger("CoScientist", log_level)
        
        self.logger.section("Co-Scientist SDK Initialization", "=", 60)
        
        self.project_id = project_id
        self.engine = engine
        self.location = location
        self.collection = collection
        
        self.authenticator = None
        self.api_client = None
        self.session_manager = None
        
        if auto_authenticate:
            self._initialize(credentials_path, log_level)
    
    def _initialize(self, credentials_path: str, log_level: LogLevel):
        """I
        nitialize authentication and clients.
        """
        try:
            self.authenticator = Authenticator(
                service_account_path=credentials_path,
                project_id=self.project_id,
                logger_name="Auth",
                log_level=log_level
            )
            self.authenticator.authenticate()
            
            self.api_client = APIClient(
                authenticator=self.authenticator,
                project_id=self.project_id,
                engine=self.engine,
                location=self.location,
                collection=self.collection,
                logger_name="API",
                log_level=log_level
            )
            
            self.session_manager = SessionManager(
                api_client=self.api_client,
                logger=get_logger("SessionManager", log_level)
            )
            
            self.logger.success("Co-Scientist client ready", LogIcons.ROCKET)
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", LogIcons.ERROR)
            raise CosciError(f"Failed to initialize client: {e}")
    
    def generate_ideas(
        self,
        research_goal: str,
        wait_timeout: int = 300,
        min_ideas: int = 1
    ) -> List[Idea]:
        """
        Generate research ideas for a given goal.
        
        This is the main method users will call. It handles the entire
        workflow: session creation, instance creation, and idea generation.
        
        Args:
            research_goal: The research question or goal
            wait_timeout: Maximum time to wait for ideas (seconds)
            min_ideas: Minimum number of ideas to generate
            
        Returns:
            List of generated ideas
            
        Example:
            >>> ideas = client.generate_ideas(
            ...     "Novel approaches to reduce hospital readmissions",
            ...     wait_timeout=180
            ... )
        """
        self.logger.section("Research Ideation", "=", 60)
        self.logger.info(f"Goal: {research_goal[:200]}...", LogIcons.IDEA)
        
        try:
            session = self.session_manager.create_session(research_goal)
            
            instance = self.session_manager.wait_for_instance(
                session,
                timeout=min(60, wait_timeout)
            )
            
            ideas = self.session_manager.poll_for_ideas(
                instance,
                timeout=wait_timeout,
                min_ideas=min_ideas
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
        info = self.session_manager.get_session_info(session_id)
        
        # Parse state
        state_str = info.get('state', 'CREATED')
        state = SessionState.CREATED
        for s in SessionState:
            if s.value == state_str:
                state = s
                break
        
        return ResearchSession(
            session_id=session_id,
            state=state,
            metadata=info
        )
    
    def get_instance_info(self, session_id: str, instance_id: str) -> Dict[str, Any]:
        """
        Get instance information.
        """
        endpoint = f"sessions/{session_id}/ideaForgeInstances/{instance_id}"
        return self.api_client.get(endpoint)
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information.
        """
        return self.session_manager.get_session_info(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions.
        """
        response = self.api_client.get("sessions")
        return response.get('sessions', [])
    
    def close(self):
        """
        Close the client and clean up resources.
        """
        if self.api_client:
            self.api_client.close()
        self.logger.success("Client closed", LogIcons.SUCCESS)