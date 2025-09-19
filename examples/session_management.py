"""Example: Working with sessions and instances directly."""

from cosci import CoScientist

# Initialize client
client = CoScientist.from_config()

# List existing sessions
print("Fetching existing sessions...")
sessions = client.list_sessions()
print(f"Found {len(sessions)} existing sessions\n")

# Display recent sessions
for i, session in enumerate(sessions[:5], 1):
    session_name = session.get("name", "")
    session_id = session_name.split("/")[-1]
    state = session.get("state", "unknown")
    print(f"{i}. Session {session_id[:8]}... - State: {state}")

# Create a new session with detailed control
print("\nCreating new research session...")
research_goal = "Innovative approaches to reduce surgical site infections"

# Use the session manager directly for more control
session = client.session_manager.create_session(research_goal)
print(f"Created session: {session.session_id}")

# Wait for instance with custom timeout
print("Waiting for instance...")
instance = client.session_manager.wait_for_instance(
    session, timeout=60, poll_interval=2
)
print(f"Instance ready: {instance.instance_id}")

# Poll for ideas with progress tracking
print("Generating ideas...")
ideas = client.session_manager.poll_for_ideas(instance, timeout=300, min_ideas=3)

print(f"\nGenerated {len(ideas)} ideas:")
for idea in ideas:
    print(f"  - {idea.title}")

client.close()
