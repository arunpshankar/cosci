"""
List recent research sessions from the last 7 days.
"""

from datetime import datetime, timedelta, timezone

import pandas as pd

from cosci import CoScientist

client = CoScientist.from_config()

print("=" * 60)
print("Recent Research Sessions (7 Days)")
print("=" * 60)

sessions = client.list_sessions()
cutoff = datetime.now(timezone.utc) - timedelta(days=7)

recent_sessions = []
for session in sessions:
    if "startTime" in session:
        start_time = datetime.fromisoformat(session["startTime"].replace("Z", "+00:00"))
        if start_time > cutoff:
            recent_sessions.append(session)

print(f"\nFound {len(recent_sessions)} sessions in last 7 days")
print(f"Total sessions in system: {len(sessions)}")

if not recent_sessions:
    print("\nNo recent sessions found")
    client.close()
    exit(0)

# Prepare data for DataFrame
table_data = []
for session in recent_sessions:
    session_id = session["name"].split("/")[-1]
    start_time = datetime.fromisoformat(session["startTime"].replace("Z", "+00:00"))
    state = session.get("state", "UNKNOWN")

    # Default values
    ideas_count = 0
    goal = ""
    instance_status = "Not started"

    # Get detailed status if instance exists
    if "ideaForgeInstance" in session:
        instance_status = "Active"
        try:
            status = client.session_manager.get_session_status(session_id)
            ideas_count = status.get("ideas_count", 0)
            if status.get("config", {}).get("goal"):
                goal = status["config"]["goal"]
            state = status.get("state", state)
        except Exception:
            # If we can't get status, keep defaults
            pass

    table_data.append(
        {
            "Session ID": session_id,
            "Date": start_time.strftime("%Y-%m-%d"),
            "Time": start_time.strftime("%H:%M:%S"),
            "State": state,
            "Ideas": ideas_count,
            "Instance": instance_status,
            "Goal": goal,
        }
    )

# Create DataFrame
df = pd.DataFrame(table_data)

# Sort by date and time (most recent first)
df = df.sort_values(["Date", "Time"], ascending=[False, False])

# Configure pandas display options for better output
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_rows", None)

# Display summary statistics
print("\n" + "=" * 40)
print("Summary by Day")
print("=" * 40)
daily_summary = (
    df.groupby("Date")
    .agg({"Session ID": "count", "Ideas": "sum"})
    .rename(columns={"Session ID": "Sessions", "Ideas": "Total Ideas"})
)
daily_summary = daily_summary.sort_index(ascending=False)
print(daily_summary)

# Display state distribution
print("\n" + "=" * 40)
print("State Distribution")
print("=" * 40)
state_summary = df["State"].value_counts()
print(state_summary)

# Display the full DataFrame
print("\n" + "=" * 40)
print("All Recent Sessions")
print("=" * 40)
print(df.to_string(index=False))

# Statistics
print("\n" + "=" * 40)
print("Statistics")
print("=" * 40)
print(f"Total recent sessions: {len(df)}")
print(f"Sessions with ideas: {len(df[df['Ideas'] > 0])}")
print(f"Total ideas generated: {df['Ideas'].sum()}")

client.close()
