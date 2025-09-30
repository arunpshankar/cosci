"""
Start a research session and exit immediately.
"""

from cosci import CoScientist

client = CoScientist.from_config()

# Start research (returns immediately, now with bug fix!)
research_goal = "Suggest novel algorithms for re-ranking retrieved documents in Retrieval-Augmented Generation (RAG) \
    systems at scale, to optimize relevance, coherence, and answer quality in the generation phase."
session = client.session_manager.create_session(research_goal)

print("\n✅ Research started!")
print(f"Session ID: {session.session_id}")
print(f"Goal: {research_goal}")
print("\nSave this ID to check progress (typically takes 30-60 minutes)")

client.close()
