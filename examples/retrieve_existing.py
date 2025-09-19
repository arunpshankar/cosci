"""
Example: Retrieve and examine an existing session.
"""

from cosci import CoScientist

# Use a known session ID (replace with your own)
SESSION_ID = "3545070705744965267"
INSTANCE_ID = "15726307298804155910"

print(f"Retrieving session: {SESSION_ID}")
print(f"Retrieving instance: {INSTANCE_ID}\n")

client = CoScientist.from_config()

# Get session information
session_info = client.session_manager.get_session_info(SESSION_ID)

print("Session Details:")
print(f"  State: {session_info.get('state', 'unknown')}")
print(f"  Created: {session_info.get('startTime', 'unknown')}")

# Check for research queries
turns = session_info.get("turns", [])
if turns:
    print(f"  Research Queries: {len(turns)}")
    for turn in turns[:2]:
        query = turn.get("query", {}).get("text", "")
        if query:
            print(f"    - {query[:60]}...")

# Get instance details if available
if INSTANCE_ID:
    print("\nInstance Details:")
    instance_info = client.api_client.get(
        f"sessions/{SESSION_ID}/ideaForgeInstances/{INSTANCE_ID}"
    )

    state = instance_info.get("state", "unknown")
    print(f"  State: {state}")

    # Show configuration
    config_data = instance_info.get("config", {})
    if config_data:
        goal = config_data.get("goal", "N/A")
        print(f"  Goal: {goal[:100]}...")

    # Count ideas
    ideas = instance_info.get("ideas", [])
    idea_previews = instance_info.get("idea_previews", [])

    if ideas or idea_previews:
        print(f"  Ideas Generated: {len(ideas or idea_previews)}")

client.close()
