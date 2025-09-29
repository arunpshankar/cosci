"""
Retrieve and display ideas from a completed session.
"""

from cosci import CoScientist

# Replace with your completed session ID
SESSION_ID = "8681664624681458482"

client = CoScientist.from_config()

print("=" * 60)
print("Retrieving Ideas")
print("=" * 60)
print(f"\nSession ID: {SESSION_ID}")

# Get ideas from session
ideas = client.session_manager.get_ideas_from_session(SESSION_ID)

if not ideas:
    print("\n❌ Error: No ideas found. Session may still be processing.")
    client.close()
    exit(1)

print(f"\n✅ Found {len(ideas)} ideas")

# Display ideas
print("\n" + "-" * 60)
print("Ideas Overview")
print("-" * 60)

for i, idea in enumerate(ideas, 1):
    print(f"\n💡 Idea {i}: {idea.title}")

    # Display full description in compact format
    if idea.description:
        print(f"   {idea.description}")

    # Display attributes if available
    if idea.attributes:
        attrs = []
        if idea.attributes.get("eloRating"):
            attrs.append(f"Elo: {idea.attributes['eloRating']}")
        if idea.attributes.get("category"):
            attrs.append(f"Category: {idea.attributes['category']}")
        if idea.attributes.get("tags"):
            attrs.append(f"Tags: {', '.join(idea.attributes['tags'])}")

        if attrs:
            print(f"   [{' | '.join(attrs)}]")

# Summary statistics
print("\n" + "=" * 60)
print("Summary Statistics")
print("=" * 60)
print(f"Total ideas retrieved: {len(ideas)}")

# Calculate average Elo if available
elo_ratings = [
    idea.attributes.get("eloRating", 0)
    for idea in ideas
    if idea.attributes.get("eloRating")
]
if elo_ratings:
    avg_elo = sum(elo_ratings) / len(elo_ratings)
    max_elo = max(elo_ratings)
    min_elo = min(elo_ratings)
    print("\nElo Rating Statistics:")
    print(f"  Average: {avg_elo:.2f}")
    print(f"  Maximum: {max_elo}")
    print(f"  Minimum: {min_elo}")

# Categories breakdown if available
categories = {}
for idea in ideas:
    if idea.attributes and idea.attributes.get("category"):
        cat = idea.attributes["category"]
        categories[cat] = categories.get(cat, 0) + 1

if categories:
    print("\nIdeas by Category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")

print("\n✅ Retrieval complete!")

client.close()
