"""
Utility functions for processing and analyzing ideas.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cosci.models import Idea


class IdeaProcessor:
    """
    Process and analyze research ideas.
    """

    @staticmethod
    def rank_ideas(ideas: List[Idea], metric: str = "eloRating") -> List[Idea]:
        """
        Rank ideas by specified metric.
        """
        return sorted(ideas, key=lambda x: x.attributes.get(metric, 0), reverse=True)

    @staticmethod
    def filter_ideas(
        ideas: List[Idea],
        min_elo: Optional[float] = None,
        keywords: Optional[List[str]] = None,
    ) -> List[Idea]:
        """
        Filter ideas based on criteria.
        """
        filtered = ideas

        if min_elo:
            filtered = [
                idea
                for idea in filtered
                if idea.attributes.get("eloRating", 0) >= min_elo
            ]

        if keywords:
            filtered = [
                idea
                for idea in filtered
                if any(
                    kw.lower() in (idea.title or "").lower()
                    or kw.lower() in (idea.description or "").lower()
                    for kw in keywords
                )
            ]

        return filtered

    @staticmethod
    def summarize_ideas(ideas: List[Idea]) -> Dict[str, Any]:
        """
        Generate summary statistics for ideas.
        """
        if not ideas:
            return {"count": 0}

        elo_ratings = [
            idea.attributes.get("eloRating", 0)
            for idea in ideas
            if "eloRating" in idea.attributes
        ]

        return {
            "count": len(ideas),
            "avg_elo": sum(elo_ratings) / len(elo_ratings) if elo_ratings else 0,
            "max_elo": max(elo_ratings) if elo_ratings else 0,
            "min_elo": min(elo_ratings) if elo_ratings else 0,
            "has_descriptions": sum(1 for idea in ideas if idea.description),
            "has_content": sum(1 for idea in ideas if idea.content),
        }

    @staticmethod
    def export_to_markdown(ideas: List[Idea], filepath: str):
        """
        Export ideas to markdown format.
        """
        content = "# Research Ideas\n\n"
        content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

        for i, idea in enumerate(ideas, 1):
            content += f"## Idea {i}: {idea.title or 'Untitled'}\n\n"

            if idea.description:
                content += f"{idea.description}\n\n"

            if idea.attributes:
                content += "**Metrics:**\n"
                for key, value in idea.attributes.items():
                    if value:
                        content += f"- {key}: {value}\n"
                content += "\n"

            if idea.content:
                content += "**Details:**\n"
                content += f"{idea.content}\n\n"

            content += "---\n\n"

        Path(filepath).write_text(content)
        return filepath


class SessionAnalyzer:
    """
    Analyze research sessions and their outcomes.
    """

    @staticmethod
    def load_session_data(filepath: str) -> Dict[str, Any]:
        """
        Load exported session data from JSON.
        """
        with open(filepath, "r") as f:
            return json.load(f)

    @staticmethod
    def compare_sessions(session_files: List[str]) -> Dict[str, Any]:
        """
        Compare multiple research sessions.
        """
        sessions_data = []

        for filepath in session_files:
            data = SessionAnalyzer.load_session_data(filepath)
            sessions_data.append(data)

        comparison = {
            "total_sessions": len(sessions_data),
            "total_ideas": sum(s["ideas_count"] for s in sessions_data),
            "sessions": [],
        }

        for data in sessions_data:
            session_summary = {
                "session_id": data["session_id"],
                "goal": data.get("research_goal", "Unknown")[:50],
                "ideas_count": data["ideas_count"],
                "top_idea": None,
            }

            # Get top idea by Elo rating
            ideas = data.get("ideas", [])
            if ideas:
                sorted_ideas = sorted(
                    ideas,
                    key=lambda x: x.get("attributes", {}).get("eloRating", 0),
                    reverse=True,
                )
                if sorted_ideas:
                    session_summary["top_idea"] = sorted_ideas[0].get("title")

            comparison["sessions"].append(session_summary)

        return comparison
