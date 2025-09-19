"""Session management for the Cosci SDK."""

import time
from typing import Dict, Optional, List, Any

from cosci.models import ResearchSession, Instance, Idea, SessionState, InstanceState
from cosci.api_client import APIClient
from cosci.logger import get_logger, LogIcons
from cosci.exceptions import SessionError, TimeoutError


class SessionManager:
    """Manages research sessions and their lifecycle."""
    
    def __init__(self, api_client: APIClient, logger=None):
        """Initialize the session manager."""
        self.api_client = api_client
        self.logger = logger or get_logger("SessionManager")
        self._sessions: Dict[str, ResearchSession] = {}
    
    def create_session(self, research_goal: str) -> ResearchSession:
        """Create a new research session."""
        self.logger.info(f"Creating session for: {research_goal[:100]}...", LogIcons.ROCKET)
        
        response = self._query_assistant(research_goal)
        
        session_id = self._extract_session_id(response)
        if not session_id:
            raise SessionError("Failed to extract session ID from response")
        
        session = ResearchSession(
            session_id=session_id,
            research_goal=research_goal,
            state=SessionState.CREATED
        )
        
        self._sessions[session_id] = session
        self.logger.success(f"Session created: {session_id}", LogIcons.SUCCESS)
        
        return session
    
    def wait_for_instance(
        self,
        session: ResearchSession,
        timeout: int = 60,
        poll_interval: int = 2
    ) -> Instance:
        """Wait for an instance to be created for the session."""
        self.logger.info(f"Waiting for instance (timeout={timeout}s)...", LogIcons.WAIT)
        
        start_time = time.time()
        attempts = 0
        
        while time.time() - start_time < timeout:
            attempts += 1
            
            try:
                session_info = self.get_session_info(session.session_id)
                
                instance_path = session_info.get('ideaForgeInstance', '')
                if instance_path:
                    instance_id = instance_path.split('/')[-1]
                    
                    instance = Instance(
                        instance_id=instance_id,
                        session_id=session.session_id,
                        state=InstanceState.CREATING
                    )
                    
                    session.instance = instance
                    self.logger.success(f"Instance created: {instance_id}", LogIcons.SUCCESS)
                    return instance
                
                elapsed = time.time() - start_time
                self.logger.debug(f"Attempt {attempts}: No instance yet ({elapsed:.1f}s elapsed)")
                
            except Exception as e:
                self.logger.debug(f"Error checking session: {e}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Instance not created within {timeout} seconds")
    
    def poll_for_ideas(
        self,
        instance: Instance,
        timeout: int = 300,
        poll_interval: int = 5,
        min_ideas: int = 1
    ) -> List[Idea]:
        """Poll for ideas to be generated."""
        self.logger.info(f"Polling for ideas (timeout={timeout}s)...", LogIcons.IDEA)
        
        start_time = time.time()
        attempts = 0
        
        while time.time() - start_time < timeout:
            attempts += 1
            
            try:
                instance_info = self._get_instance_info(
                    instance.session_id,
                    instance.instance_id
                )
                
                state_str = instance_info.get('state', 'UNKNOWN')
                if state_str in [s.value for s in InstanceState]:
                    instance.state = InstanceState(state_str)
                
                ideas_data = instance_info.get('ideas', [])
                idea_previews = instance_info.get('idea_previews', [])
                
                if ideas_data or (instance.state == InstanceState.SUCCEEDED and idea_previews):
                    ideas = self._parse_ideas(ideas_data or idea_previews)
                    
                    if len(ideas) >= min_ideas:
                        instance.ideas = ideas
                        self.logger.success(f"Generated {len(ideas)} ideas", LogIcons.SUCCESS)
                        return ideas
                
                elapsed = time.time() - start_time
                self.logger.progress(
                    int(elapsed), timeout,
                    f"Waiting for ideas (attempt {attempts}, state: {instance.state.value})"
                )
                
            except Exception as e:
                self.logger.debug(f"Error polling instance: {e}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Ideas not generated within {timeout} seconds")
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information from API."""
        endpoint = f"sessions/{session_id}"
        return self.api_client.get(endpoint)
    
    def get_idea_details(
        self,
        session_id: str,
        instance_id: str,
        idea_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific idea."""
        endpoint = f"sessions/{session_id}/ideaForgeInstances/{instance_id}/ideaForgeIdeas/{idea_id}"
        return self.api_client.get(endpoint)
    
    def _query_assistant(self, query: str) -> Any:
        """Query the assistant."""
        endpoint = f"assistants/{self.api_client.assistant}:streamAssist"
        data = {
            "query": {"text": query},
            "answer_generation_mode": "IDEA_FORGE"
        }
        return self.api_client.post(endpoint, data)
    
    def _get_instance_info(self, session_id: str, instance_id: str) -> Dict[str, Any]:
        """Get instance information from API."""
        endpoint = f"sessions/{session_id}/ideaForgeInstances/{instance_id}"
        return self.api_client.get(endpoint)
    
    def _extract_session_id(self, response: Any) -> Optional[str]:
        """Extract session ID from assistant response."""
        if isinstance(response, list):
            for item in response:
                if isinstance(item, dict):
                    session_id = self._extract_from_dict(item)
                    if session_id:
                        return session_id
        elif isinstance(response, dict):
            return self._extract_from_dict(response)
        return None
    
    def _extract_from_dict(self, data: Dict) -> Optional[str]:
        """Extract session ID from dictionary."""
        if 'sessionInfo' in data and 'session' in data['sessionInfo']:
            session_name = data['sessionInfo']['session']
            return session_name.split('/')[-1]
        if 'session' in data and isinstance(data['session'], str):
            return data['session'].split('/')[-1]
        return None
    
    def _parse_ideas(self, ideas_data: List[Dict]) -> List[Idea]:
        """Parse ideas from API response."""
        ideas = []
        
        for data in ideas_data:
            try:
                if 'ideaForgeIdea' in data:
                    idea_path = data['ideaForgeIdea']
                    idea_id = idea_path.split('/')[-1]
                    idea = Idea(idea_id=idea_id)
                elif 'name' in data:
                    idea_id = data['name'].split('/')[-1]
                    idea = Idea(
                        idea_id=idea_id,
                        title=data.get('title'),
                        description=data.get('description'),
                        content=data.get('content', {}),
                        attributes=data.get('attributes', {})
                    )
                else:
                    continue
                
                ideas.append(idea)
                
            except Exception as e:
                self.logger.debug(f"Failed to parse idea: {e}")
        
        return ideas