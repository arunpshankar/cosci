"""
Data models for the Cosci SDK.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SessionState(Enum):
    """
    Session states.
    """

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InstanceState(Enum):
    """
    Instance states.
    """

    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class ResearchSession:
    """
    Represents a Co-Scientist research session.
    """

    def __init__(
        self,
        session_id: str,
        research_goal: Optional[str] = None,
        state: SessionState = SessionState.CREATED,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.session_id = session_id
        self.research_goal = research_goal
        self.state = state
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
        self.instance: Optional[Instance] = None

    def __repr__(self) -> str:
        return f"ResearchSession(id={self.session_id}, state={self.state.value})"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "session_id": self.session_id,
            "research_goal": self.research_goal,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "instance": self.instance.to_dict() if self.instance else None,
            "metadata": self.metadata,
        }


class Instance:
    """
    Represents a Co-Scientist instance.
    """

    def __init__(
        self,
        instance_id: str,
        session_id: str,
        state: InstanceState = InstanceState.CREATING,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.instance_id = instance_id
        self.session_id = session_id
        self.state = state
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
        self.ideas: List[Idea] = []

    def __repr__(self) -> str:
        return f"Instance(id={self.instance_id}, state={self.state.value}, ideas={len(self.ideas)})"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "instance_id": self.instance_id,
            "session_id": self.session_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "ideas": [idea.to_dict() for idea in self.ideas],
            "metadata": self.metadata,
        }


class Idea:
    """
    Represents a research idea.
    """

    def __init__(
        self,
        idea_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ):
        self.idea_id = idea_id
        self.title = title
        self.description = description
        self.content = content or {}
        self.attributes = attributes or {}
        self.created_at = created_at or datetime.now()

    def __repr__(self) -> str:
        return f"Idea(id={self.idea_id}, title={self.title})"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "idea_id": self.idea_id,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "attributes": self.attributes,
            "created_at": self.created_at.isoformat(),
        }
