"""
Export ideas from a completed session to well-structured JSON.
"""

import json
from datetime import datetime
from pathlib import Path

from cosci import CoScientist
from cosci.utils import IdeaProcessor

# Your completed session ID
SESSION_ID = "8681664624681458482"

client = CoScientist.from_config()

print(f"\nExporting session: {SESSION_ID}")

# Get session status and ideas
status = client.session_manager.get_session_status(SESSION_ID)
ideas = client.session_manager.get_ideas_from_session(SESSION_ID, fetch_details=True)

if not ideas:
    print("❌ No ideas found to export")
    client.close()
    exit(1)

if status["state"] != "SUCCEEDED":
    print(f"⚠️  Session is {status['state']}, ideas may be incomplete")

# Process ideas
processor = IdeaProcessor()
ranked_ideas = processor.rank_ideas(ideas)
summary = processor.summarize_ideas(ideas)

# Build comprehensive JSON structure
export_data = {
    "metadata": {
        "session_id": SESSION_ID,
        "export_timestamp": datetime.now().isoformat(),
        "export_version": "1.0",
        "research_goal": status.get("config", {}).get("goal", "Unknown"),
        "session_state": status["state"],
    },
    "summary": {
        "total_ideas": summary["count"],
        "average_elo_rating": round(summary["avg_elo"], 2),
        "highest_elo_rating": round(summary["max_elo"], 2),
        "lowest_elo_rating": round(summary["min_elo"], 2),
        "ideas_with_descriptions": summary["has_descriptions"],
        "ideas_with_content": summary["has_content"],
    },
    "ideas": [
        {
            "rank": i,
            "id": idea.idea_id,
            "title": idea.title or "Untitled",
            "description": idea.description or "",
            "metrics": {
                "elo_rating": idea.attributes.get("eloRating", None),
                "original_ranking": idea.attributes.get("ranking", None),
            },
            "content": idea.content if idea.content else None,
            "timestamp": idea.created_at.isoformat() if idea.created_at else None,
        }
        for i, idea in enumerate(ranked_ideas, 1)
    ],
    "top_ideas": [
        {
            "rank": i,
            "title": idea.title,
            "elo_rating": idea.attributes.get("eloRating", 0),
        }
        for i, idea in enumerate(ranked_ideas[:3], 1)
    ],
}

# Save main export
output_dir = Path("./data/ideas")
output_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = output_dir / f"ideas_{SESSION_ID[:8]}_{timestamp}.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(export_data, f, indent=2, ensure_ascii=False)

print(f"✅ Full export: {output_file}")

# Create a simplified version for quick reading
simple_export = {
    "session": SESSION_ID,
    "goal": status.get("config", {}).get("goal", "Unknown")[:100],
    "ideas": [
        {
            "title": idea.title,
            "description": idea.description[:200] if idea.description else "",
            "elo": idea.attributes.get("eloRating", 0),
        }
        for idea in ranked_ideas
    ],
}

simple_file = output_dir / f"ideas_simple_{SESSION_ID[:8]}_{timestamp}.json"
with open(simple_file, "w", encoding="utf-8") as f:
    json.dump(simple_export, f, indent=2, ensure_ascii=False)

print(f"✅ Simple export: {simple_file}")

# Summary
print(f"\nExported {len(ideas)} ideas")
print(f"Average Elo: {summary['avg_elo']:.2f}")
if ranked_ideas:
    print(f"Top idea: {ranked_ideas[0].title}")

client.close()
