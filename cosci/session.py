"""
Session management for the Cosci SDK.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cosci.api_client import APIClient
from cosci.exceptions import SessionError, TimeoutError
from cosci.logger import LogIcons, get_logger
from cosci.models import Idea, Instance, InstanceState, ResearchSession, SessionState


class SessionManager:
    """
    Manages research sessions and their lifecycle.
    """

    def __init__(self, api_client: APIClient, logger=None):
        """
        Initialize the session manager.
        """
        self.api_client = api_client
        self.logger = logger or get_logger("SessionManager")
        self._sessions: Dict[str, ResearchSession] = {}

    def create_session(self, research_goal: str) -> ResearchSession:
        """
        Create a new research session and start execution.
        """
        self.logger.info(
            f"Creating session for: {research_goal[:100]}...", LogIcons.ROCKET
        )

        # Step 1: Create the session
        response = self._query_assistant(research_goal)

        session_id = self._extract_session_id(response)
        if not session_id:
            raise SessionError("Failed to extract session ID from response")

        session = ResearchSession(
            session_id=session_id,
            research_goal=research_goal,
            state=SessionState.CREATED,
        )

        self._sessions[session_id] = session
        self.logger.success(f"Session created: {session_id}", LogIcons.SUCCESS)

        # Step 2: Wait for session to be fully created (takes ~30-60 seconds)
        import time

        wait_time = 45  # Wait 45 seconds for session to be ready
        self.logger.info(
            f"Waiting {wait_time}s for session to be ready...", LogIcons.WAIT
        )
        time.sleep(wait_time)

        # Step 3: Try to start execution
        self.logger.info("Starting session execution...", LogIcons.PROCESS)

        try:
            self._start_session_execution(session_id)
            session.state = SessionState.IN_PROGRESS
            self.logger.success("Session execution started", LogIcons.SUCCESS)
        except SessionError as e:
            # Starting failed - check if session auto-started
            self.logger.warning(
                f"Could not manually start session, checking if it auto-started... Error: {e}",
                LogIcons.WARNING,
            )

            time.sleep(5)  # Wait another 5 seconds

            try:
                status = self.get_session_status(session_id)
                if status["has_instance"]:
                    self.logger.success(
                        "Session auto-started successfully!", LogIcons.SUCCESS
                    )
                    session.state = SessionState.IN_PROGRESS
                else:
                    self.logger.warning(
                        f"Session created but not started. Manual start may be required.\n"
                        f"Session ID: {session_id}\n"
                        f"You can start it via the Co-Scientist UI or wait for auto-start.",
                        LogIcons.WARNING,
                    )
            except Exception:
                self.logger.warning(
                    f"Session {session_id} created but start status unclear.\n"
                    f"Check session status manually.",
                    LogIcons.WARNING,
                )

        return session

    def _start_session_execution(self, session_id: str):
        """
        Start the execution of a created session.
        This is the critical second RPC call that was missing.
        Tries multiple methods as different API versions may use different endpoints.
        """
        # Build the session path for the parent field
        session_path = f"{self.api_client.base_path}/sessions/{session_id}"

        # Method 1: Try :startInstance endpoint (from official Colab)
        self.logger.debug("Attempting to start instance with :startInstance endpoint")
        endpoint = f"sessions/{session_id}:startInstance"

        data = {"parent": session_path}

        try:
            result = self.api_client.post(endpoint, data)
            self.logger.debug(f"Session execution started via :startInstance: {result}")
            return result
        except Exception as e:
            self.logger.warning(f":startInstance endpoint failed: {e}")

            # Method 2: Try creating IdeaForge instance directly
            self.logger.debug(
                "Attempting alternative method: direct IdeaForge instance creation"
            )
            try:
                alt_endpoint = f"sessions/{session_id}/ideaForgeInstances"
                alt_data = {}  # Empty body may trigger auto-start

                result = self.api_client.post(alt_endpoint, alt_data)
                self.logger.debug(
                    f"Session execution started via alternative method: {result}"
                )
                return result
            except Exception as e2:
                self.logger.error(f"Alternative method also failed: {e2}")

                # If both methods fail, provide helpful error message
                raise SessionError(
                    f"Failed to start session execution. Tried multiple methods:\n"
                    f"1. :startInstance endpoint: {str(e)}\n"
                    f"2. Direct instance creation: {str(e2)}\n"
                    f"The session {session_id} was created but may need manual starting.\n"
                    f"Check the session status to see if it started automatically."
                )

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed status for a session.
        """
        info = self.get_session_info(session_id)
        instance_path = info.get("ideaForgeInstance", "")

        status = {
            "session_id": session_id,
            "has_instance": bool(instance_path),
            "state": "INITIALIZING",
            "ideas_count": 0,
            "instance_id": None,
        }

        if instance_path:
            instance_id = instance_path.split("/")[-1]
            status["instance_id"] = instance_id

            try:
                instance = self.api_client.get(
                    f"sessions/{session_id}/ideaForgeInstances/{instance_id}"
                )
                status["state"] = instance.get("state", "UNKNOWN")
                status["ideas_count"] = instance.get("stats", {}).get("numIdeas", 0)
                status["config"] = instance.get("config", {})
            except Exception as e:
                self.logger.debug(f"Error getting instance details: {e}")

        return status

    def get_ideas_from_session(
        self, session_id: str, fetch_details: bool = False
    ) -> List[Idea]:
        """
        Get ideas from a session without waiting.
        """
        info = self.get_session_info(session_id)
        instance_path = info.get("ideaForgeInstance", "")

        if not instance_path:
            return []

        instance_id = instance_path.split("/")[-1]
        instance = self.api_client.get(
            f"sessions/{session_id}/ideaForgeInstances/{instance_id}"
        )

        ideas_data = instance.get("ideas", [])
        idea_previews = instance.get("ideaPreviews", [])

        ideas = self._parse_ideas(ideas_data or idea_previews)

        # Optionally fetch full details for each idea
        if fetch_details and ideas:
            for idea in ideas:
                try:
                    details = self.get_idea_details(
                        session_id, instance_id, idea.idea_id
                    )
                    idea.content = details
                except Exception as e:
                    self.logger.debug(
                        f"Could not fetch details for idea {idea.idea_id}: {e}"
                    )

        return ideas

    def export_session_ideas(
        self, session_id: str, output_dir: str = "./data/ideas", format: str = "json"
    ) -> str:
        """
        Export session ideas to file.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Get session status and ideas
        status = self.get_session_status(session_id)
        ideas = self.get_ideas_from_session(session_id, fetch_details=True)

        # Prepare export data
        export_data = {
            "session_id": session_id,
            "research_goal": status.get("config", {}).get("goal", "Unknown"),
            "export_timestamp": datetime.now().isoformat(),
            "ideas_count": len(ideas),
            "ideas": [idea.to_dict() for idea in ideas],
        }

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ideas_{session_id[:8]}_{timestamp}.{format}"
        filepath = output_path / filename

        if format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

        self.logger.success(
            f"Exported {len(ideas)} ideas to {filepath}", LogIcons.SUCCESS
        )
        return str(filepath)

    def wait_for_instance(
        self, session: ResearchSession, timeout: int = 60, poll_interval: int = 2
    ) -> Instance:
        """
        Wait for an instance to be created for the session.
        """
        self.logger.info(f"Waiting for instance (timeout={timeout}s)...", LogIcons.WAIT)

        start_time = time.time()
        attempts = 0

        while time.time() - start_time < timeout:
            attempts += 1

            try:
                session_info = self.get_session_info(session.session_id)

                instance_path = session_info.get("ideaForgeInstance", "")
                if instance_path:
                    instance_id = instance_path.split("/")[-1]

                    instance = Instance(
                        instance_id=instance_id,
                        session_id=session.session_id,
                        state=InstanceState.CREATING,
                    )

                    session.instance = instance
                    self.logger.success(
                        f"Instance created: {instance_id}", LogIcons.SUCCESS
                    )
                    return instance

                elapsed = time.time() - start_time
                self.logger.debug(
                    f"Attempt {attempts}: No instance yet ({elapsed:.1f}s elapsed)"
                )

            except Exception as e:
                self.logger.debug(f"Error checking session: {e}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Instance not created within {timeout} seconds")

    def poll_for_ideas(
        self,
        instance: Instance,
        timeout: int = 300,
        poll_interval: int = 5,
        min_ideas: int = 1,
    ) -> List[Idea]:
        """
        Poll for ideas to be generated.
        """
        self.logger.info(f"Polling for ideas (timeout={timeout}s)...", LogIcons.IDEA)

        start_time = time.time()
        attempts = 0

        while time.time() - start_time < timeout:
            attempts += 1

            try:
                instance_info = self._get_instance_info(
                    instance.session_id, instance.instance_id
                )

                state_str = instance_info.get("state", "UNKNOWN")
                if state_str in [s.value for s in InstanceState]:
                    instance.state = InstanceState(state_str)

                ideas_data = instance_info.get("ideas", [])
                idea_previews = instance_info.get("ideaPreviews", [])

                if ideas_data or (
                    instance.state == InstanceState.SUCCEEDED and idea_previews
                ):
                    ideas = self._parse_ideas(ideas_data or idea_previews)

                    if len(ideas) >= min_ideas:
                        instance.ideas = ideas
                        self.logger.success(
                            f"Generated {len(ideas)} ideas", LogIcons.SUCCESS
                        )
                        return ideas

                elapsed = time.time() - start_time
                self.logger.progress(
                    int(elapsed),
                    timeout,
                    f"Waiting for ideas (attempt {attempts}, state: {instance.state.value})",
                )

            except Exception as e:
                self.logger.debug(f"Error polling instance: {e}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Ideas not generated within {timeout} seconds")

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information from API.
        """
        endpoint = f"sessions/{session_id}"
        return self.api_client.get(endpoint)

    def get_idea_details(
        self, session_id: str, instance_id: str, idea_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific idea.
        """
        endpoint = f"sessions/{session_id}/ideaForgeInstances/{instance_id}/ideaForgeIdeas/{idea_id}"
        return self.api_client.get(endpoint)

    def _query_assistant(self, query: str) -> Any:
        """
        Query the assistant to create a session.
        """
        endpoint = f"assistants/{self.api_client.assistant}:streamAssist"
        data = {"query": {"text": query}, "answer_generation_mode": "IDEA_FORGE"}
        return self.api_client.post(endpoint, data)

    def _get_instance_info(self, session_id: str, instance_id: str) -> Dict[str, Any]:
        """
        Get instance information from API.
        """
        endpoint = f"sessions/{session_id}/ideaForgeInstances/{instance_id}"
        return self.api_client.get(endpoint)

    def _extract_session_id(self, response: Any) -> Optional[str]:
        """
        Extract session ID from assistant response.
        """
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
        """
        Extract session ID from dictionary.
        """
        if "sessionInfo" in data and "session" in data["sessionInfo"]:
            session_name = data["sessionInfo"]["session"]
            return session_name.split("/")[-1]
        if "session" in data and isinstance(data["session"], str):
            return data["session"].split("/")[-1]
        return None

    def _parse_ideas(self, ideas_data: List[Dict]) -> List[Idea]:
        """
        Parse ideas from API response.
        """
        ideas = []

        for data in ideas_data:
            try:
                if "ideaForgeIdea" in data:
                    idea_path = data["ideaForgeIdea"]
                    idea_id = idea_path.split("/")[-1]
                    idea = Idea(
                        idea_id=idea_id,
                        title=data.get("title"),
                        description=data.get("summary"),
                        attributes={
                            "ranking": data.get("ranking"),
                            "eloRating": data.get("eloRating"),
                        },
                    )
                elif "name" in data:
                    idea_id = data["name"].split("/")[-1]
                    idea = Idea(
                        idea_id=idea_id,
                        title=data.get("title"),
                        description=data.get("description"),
                        content=data.get("content", {}),
                        attributes=data.get("attributes", {}),
                    )
                else:
                    continue

                ideas.append(idea)

            except Exception as e:
                self.logger.debug(f"Failed to parse idea: {e}")

        return ideas
