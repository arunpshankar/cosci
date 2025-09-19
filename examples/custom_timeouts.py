"""
Example: Using custom timeouts and configurations.
"""

from cosci import CoScientist
from cosci.config import Config

# Load config and customize settings
config = Config.from_yaml()
config.timeout = 600  # 10 minutes for complex research
config.poll_interval = 10  # Check every 10 seconds
config.min_ideas = 5  # Wait for at least 5 ideas

print("Custom Configuration Example")
print("=" * 60)
print(f"Timeout: {config.timeout}s")
print(f"Poll Interval: {config.poll_interval}s")
print(f"Minimum Ideas: {config.min_ideas}")
print()

# Create client with custom config
client = CoScientist(config)

# Complex research goal
research_goal = """
Develop a comprehensive framework for using artificial intelligence
and machine learning to predict and prevent hospital-acquired infections,
incorporating real-time patient monitoring, environmental sensors,
and historical infection patterns.
"""

print("Research Goal:")
print(research_goal)
print("\nGenerating ideas (this may take a while)...")

# Generate ideas with custom settings
ideas = client.generate_ideas(research_goal)

print(f"\nGenerated {len(ideas)} ideas:")
for i, idea in enumerate(ideas, 1):
    print(f"\n{i}. {idea.title}")
    if idea.description:
        print(f"   {idea.description[:150]}...")

client.close()
