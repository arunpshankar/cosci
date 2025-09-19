"""
Advanced usage example for Cosci SDK.
"""

from cosci import CoScientist, LogLevel

# Initialize with debug logging
client = CoScientist(
    project_id="your-project-id",
    engine="your-engine-id",
    credentials_path="credentials.json",
    log_level=LogLevel.DEBUG
)

# Generate ideas with custom parameters
ideas = client.generate_ideas(
    research_goal="Innovative methods for early cancer detection using biomarkers",
    wait_timeout=300,  # 5 minutes
    min_ideas=5        # Wait for at least 5 ideas
)

# Access detailed information
for idea in ideas:
    print(f"ID: {idea.idea_id}")
    print(f"Title: {idea.title}")
    print(f"Description: {idea.description}")
    if idea.attributes:
        print("Attributes:")
        for key, value in idea.attributes.items():
            print(f"  {key}: {value}")
    print("=" * 60)

# Get session information
sessions = client.list_sessions()
print(f"\nTotal sessions: {len(sessions)}")

# Clean up
client.close()