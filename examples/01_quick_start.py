"""
Start a research session and exit immediately.
"""

from cosci import CoScientist

client = CoScientist.from_config()

# Start research (returns immediately, now with bug fix!)
research_goal = "What are the most effective algorithms and approaches for source attribution in answer engines at web \
    scale, specifically for properly crediting and citing content from web crawl data?"
session = client.session_manager.create_session(research_goal)

print("\n✅ Research started!")
print(f"Session ID: {session.session_id}")
print(f"Goal: {research_goal}")
print("\nSave this ID to check progress (typically takes 30-60 minutes)")

client.close()
