"""
Advanced example with context manager and custom settings.
"""

from cosci import CoScientist
from cosci.config import Config

# Load and customize config
config = Config.from_yaml()
config.log_level = "DEBUG"  # Override for debugging
config.timeout = 1800  # set to 30+ minutes (1800+ seconds) for complex queries

# Use context manager for automatic cleanup
with CoScientist(config) as client:
    # Generate ideas with custom parameters
    ideas = client.generate_ideas(
        research_goal="Innovative methods for early cancer detection using biomarkers",
        min_ideas=5,  # Wait for at least 5 ideas
    )

    # Process ideas
    for idea in ideas:
        print(f"\nID: {idea.idea_id}")
        print(f"Title: {idea.title}")
        if idea.description:
            print(f"Description: {idea.description}")
        if idea.attributes:
            print("Attributes:")
            for key, value in idea.attributes.items():
                print(f"  - {key}: {value}")

    # List recent sessions
    sessions = client.list_sessions()
    print(f"\nTotal sessions: {len(sessions)}")
