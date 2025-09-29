"""
Check the status of an ongoing research session.
"""

from cosci import CoScientist

# Replace with your session ID from start_research.py
SESSION_ID = "8681664624681458482"

client = CoScientist.from_config()

print(f"\nSession: {SESSION_ID}")

try:
    status = client.session_manager.get_session_status(SESSION_ID)

    # Core status
    print(f"State: {status['state']}")
    print(f"Ideas: {status['ideas_count']}")

    # Goal if available
    if status.get("config", {}).get("goal"):
        print(f"Goal: {status['config']['goal']}")

    # Progress bar if max_ideas is set
    if status.get("config", {}).get("max_ideas"):
        max_ideas = status["config"]["max_ideas"]
        current = status["ideas_count"]
        progress = (current / max_ideas) * 100

        bar_length = 20
        filled = int(bar_length * current // max_ideas)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\nProgress: [{bar}] {current}/{max_ideas} ({progress:.0f}%)")

    # Status-specific message
    print()
    if status["state"] == "SUCCEEDED":
        print("✅ Complete! Run 03_get_ideas.py to retrieve results")
    elif status["state"] in ["PROCESSING", "ACTIVE"]:
        print("⏳ Processing... check again in a few minutes")
    elif status["state"] == "FAILED":
        print("❌ Failed - check logs or start new session")
    elif not status["has_instance"]:
        print("🔄 Initializing... check back in a minute")
    else:
        print(f"⚠️  Unexpected state: {status['state']}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"Verify session ID: {SESSION_ID}")

client.close()
