"""
Quick start example for Cosci SDK.
"""

from cosci import CoScientist

# Initialize client
client = CoScientist(
    project_id="your-project-id",
    engine="your-engine-id",
    credentials_path="path/to/credentials.json",
)

# Generate ideas
ideas = client.generate_ideas(
    "Novel approaches to reduce hospital readmission rates using AI"
)

# Display results
for idea in ideas:
    print(f"Idea: {idea.title}")
    print(f"Description: {idea.description}")
    print("-" * 40)
