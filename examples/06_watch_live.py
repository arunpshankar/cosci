"""Watch a research session with live updates."""

import sys
import time

from cosci import CoScientist

# Replace with your session ID to watch
SESSION_ID = "11717670767947535533"
UPDATE_INTERVAL = 30  # seconds

client = CoScientist.from_config()

print(f"\nWatching session: {SESSION_ID}")
print("Press Ctrl+C to stop watching\n")

last_count = 0
spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
spin_idx = 0

try:
    while True:
        status = client.session_manager.get_session_status(SESSION_ID)

        if not status["has_instance"]:
            sys.stdout.write(f"\r{spinner[spin_idx]} Initializing...")
            spin_idx = (spin_idx + 1) % len(spinner)
            sys.stdout.flush()
            time.sleep(5)
            continue

        state = status["state"]
        num_ideas = status["ideas_count"]

        # Clear line
        sys.stdout.write("\r" + " " * 50 + "\r")

        # Alert for new ideas
        if num_ideas > last_count:
            print(f"💡 New idea! Total: {num_ideas}")
            last_count = num_ideas

        # Live status line
        sys.stdout.write(f"{state} | Ideas: {num_ideas}")
        sys.stdout.flush()

        if state == "SUCCEEDED":
            print("\n\n✅ Research complete!")
            print("Run: python export_ideas.py")
            break
        elif state == "FAILED":
            print("\n\n❌ Research failed")
            break

        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print("\n\nStopped watching. Session continues in background.")

client.close()
