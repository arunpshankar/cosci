"""List all research sessions with their states."""

from datetime import datetime

import pandas as pd

from cosci import CoScientist

client = CoScientist.from_config()

print("=" * 60)
print("All Research Sessions")
print("=" * 60)

sessions = client.list_sessions()
print(f"\nTotal sessions: {len(sessions)}")

if not sessions:
    print("No sessions found")
    client.close()
    exit(0)

# Process all sessions and get their states
sessions_with_status = []
# Dynamically capture states as we encounter them
state_counts = {}

print("\nFetching session states...")
for i, session in enumerate(sessions, 1):
    session_id = session["name"].split("/")[-1]

    # Default state
    session_state = "NO_INSTANCE"
    status = None

    # Check if instance exists
    if "ideaForgeInstance" in session:
        try:
            status = client.session_manager.get_session_status(session_id)
            session_state = status.get("state", "NO_INSTANCE")

            # Progress indicator every 10 sessions
            if i % 10 == 0:
                print(f"  Processed {i}/{len(sessions)} sessions...")

        except Exception:
            # If there's an error getting status, mark as NO_INSTANCE
            session_state = "NO_INSTANCE"

    # Dynamically count states
    if session_state not in state_counts:
        state_counts[session_state] = 0
    state_counts[session_state] += 1

    sessions_with_status.append(
        {
            "session": session,
            "session_id": session_id,
            "state": session_state,
            "status": status,
        }
    )

print(f"  Completed processing {len(sessions)} sessions")

# Display summary
print("\n" + "-" * 40)
print("State Summary")
print("-" * 40)
for state, count in sorted(state_counts.items()):
    if count > 0:
        # Add emoji indicators for different states
        emoji = ""
        if state == "SUCCEEDED":
            emoji = "✅"
        elif state in ["PROCESSING", "ACTIVE"]:
            emoji = "⏳"
        elif state == "FAILED":
            emoji = "❌"
        elif state == "NO_INSTANCE":
            emoji = "⚪"
        else:
            emoji = "ℹ️"

        print(f"{emoji} {state}: {count} sessions")

# Prepare data for DataFrame
print("\n" + "=" * 60)
print("Session Table")
print("=" * 60)

table_data = []
for item in sessions_with_status:
    session_id = item["session_id"]
    state = item["state"]
    status = item["status"]
    session = item["session"]

    # Extract relevant fields
    ideas_count = status.get("ideas_count", 0) if status else 0

    # Get full goal (no truncation)
    goal = ""
    if status and status.get("config", {}).get("goal"):
        goal = status["config"]["goal"]

    # Get timestamp if available
    start_time = ""
    if "startTime" in session:
        try:
            dt = datetime.fromisoformat(session["startTime"].replace("Z", "+00:00"))
            start_time = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError, AttributeError):
            start_time = "N/A"

    table_data.append(
        {
            "Session ID": session_id,
            "State": state,
            "Ideas": ideas_count,
            "Started": start_time,
            "Goal": goal,
        }
    )

# Create DataFrame
df = pd.DataFrame(table_data)

# Sort by state and ideas count - dynamically create priority map
state_priority = {
    "SUCCEEDED": 0,
    "PROCESSING": 1,
    "ACTIVE": 2,
    "FAILED": 3,
    "NO_INSTANCE": 4,
}
# Add any other states we encountered that aren't in our priority map
other_states = [s for s in state_counts.keys() if s not in state_priority]
for idx, state in enumerate(sorted(other_states)):
    state_priority[state] = 5 + idx

df["state_priority"] = df["State"].map(state_priority)
df = df.sort_values(["state_priority", "Ideas"], ascending=[True, False])
df = df.drop("state_priority", axis=1)

# Configure pandas display options for better output
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)  # Show full content, no truncation

# Show different views
print("\nTop 10 Sessions by Ideas Count:")
print("-" * 40)
top_ideas_df = df[df["Ideas"] > 0].head(10)[["Session ID", "State", "Ideas", "Goal"]]
if not top_ideas_df.empty:
    print(top_ideas_df.to_string(index=False))
else:
    print("No sessions with ideas found")

print("\n\nAll Sessions Summary (Top 20):")
print("-" * 40)
summary_df = df[["Session ID", "State", "Ideas", "Started"]].head(20)
print(summary_df.to_string(index=False))

# Export to CSV
csv_filename = f"sessions_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(csv_filename, index=False)
print(f"\n📁 Full data exported to: {csv_filename}")

# Actionable summary
print("\n" + "=" * 50)
print("Actions Available")
print("-" * 50)

# Get examples from DataFrame
succeeded_df = df[df["State"] == "SUCCEEDED"]
if not succeeded_df.empty:
    print("\n✅ Export ideas from completed sessions:")
    best_session = succeeded_df.iloc[0]
    print(f"   Best session: {best_session['Session ID']}")
    print(f"   Ideas count: {best_session['Ideas']}")
    print("   Command: python export_ideas.py  # Update SESSION_ID in file")

active_df = df[df["State"].isin(["PROCESSING", "ACTIVE"])]
if not active_df.empty:
    print("\n⏳ Monitor in-progress sessions:")
    active_session = active_df.iloc[0]
    print(f"   Active session: {active_session['Session ID']}")
    print("   Command: python check_progress.py  # Update SESSION_ID in file")

# Statistics
print("\n" + "-" * 40)
print("Statistics")
print("-" * 40)
print(f"Total sessions: {len(df)}")
print(f"Sessions with ideas: {len(df[df['Ideas'] > 0])}")
print(f"Total ideas across all sessions: {df['Ideas'].sum()}")
if df["Ideas"].sum() > 0:
    print(
        f"Average ideas per successful session: {df[df['Ideas'] > 0]['Ideas'].mean():.1f}"
    )

# Additional insights
if len(df) > 0:
    print("\n" + "-" * 40)
    print("Additional Insights")
    print("-" * 40)

    # State distribution as percentages
    print("\nState Distribution:")
    for state, count in state_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {state}: {percentage:.1f}%")

    # Most productive sessions
    if len(df[df["Ideas"] > 0]) > 0:
        print("\nMost Productive Session:")
        most_productive = df.loc[df["Ideas"].idxmax()]
        print(f"  ID: {most_productive['Session ID']}")
        print(f"  Ideas: {most_productive['Ideas']}")
        if most_productive["Goal"]:
            print(
                f"  Goal: {most_productive['Goal'][:100]}{'...' if len(most_productive['Goal']) > 100 else ''}"
            )

client.close()
