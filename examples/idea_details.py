"""
Example: Get detailed information about generated ideas.
"""

from cosci import CoScientist

client = CoScientist.from_config()

# Generate ideas
print("Generating research ideas...")
ideas = client.generate_ideas(
    "Novel approaches for early detection of Alzheimer's disease"
)

print(f"Generated {len(ideas)} ideas\n")

# Get detailed information for each idea
for i, idea in enumerate(ideas[:3], 1):  # First 3 ideas
    print(f"Idea {i}: {idea.title}")
    print("-" * 60)

    if idea.description:
        print(f"Description: {idea.description}")

    if idea.attributes:
        print("Attributes:")
        for key, value in idea.attributes.items():
            print(f"  {key}: {value}")

    if idea.content:
        print("Content Preview:")
        content_str = str(idea.content)[:200]
        print(f"  {content_str}...")

    print()

client.close()
