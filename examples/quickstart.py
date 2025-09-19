"""Quick start example for Cosci SDK using config file."""

from cosci import CoScientist

# Load client from config.yaml
client = CoScientist.from_config()

# Generate ideas
ideas = client.generate_ideas(
    "Novel approaches to reduce hospital readmission rates using AI"
)

# Display results
print(f"\nGenerated {len(ideas)} ideas:\n")
print("=" * 60)

for i, idea in enumerate(ideas, 1):
    print(f"\nIdea {i}: {idea.title}")
    if idea.description:
        print(f"Description: {idea.description}")
    print("-" * 40)

# Clean up
client.close()
