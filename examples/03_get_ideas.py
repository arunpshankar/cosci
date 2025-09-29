"""Retrieve and export ideas from a completed session."""

from cosci import CoScientist
from cosci.utils import IdeaProcessor

# Replace with your completed session ID
SESSION_ID = "16373935967978322018"

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
print("\n" + "-" * 40)
print("Ideas Overview")
print("-" * 40)

for i, idea in enumerate(ideas, 1):
    print(f"\n💡 Idea {i}: {idea.title}")

    if idea.description:
        # Clean description display
        description = idea.description[:200]
        if len(idea.description) > 200:
            description += "..."
        print(f"   Description: {description}")

    # Display attributes if available
    if idea.attributes:
        if idea.attributes.get("eloRating"):
            print(f"   Elo Rating: {idea.attributes['eloRating']}")
        if idea.attributes.get("category"):
            print(f"   Category: {idea.attributes['category']}")
        if idea.attributes.get("tags"):
            print(f"   Tags: {', '.join(idea.attributes['tags'])}")

# Export to JSON
print("\n" + "-" * 40)
print("Exporting Data")
print("-" * 40)

try:
    output_file = client.session_manager.export_session_ideas(
        SESSION_ID, output_dir="./data/ideas", format="json"
    )
    print(f"\n✅ JSON exported to: {output_file}")
except Exception as e:
    print(f"\n❌ Error exporting JSON: {e}")

# Export top ideas as markdown
try:
    processor = IdeaProcessor()

    # Rank and get top ideas
    ranked_ideas = processor.rank_ideas(ideas)
    top_count = min(3, len(ranked_ideas))  # Get top 3 or fewer if less available
    top_ideas = ranked_ideas[:top_count]

    # Export to markdown
    md_file = f"./data/ideas/top_ideas_{SESSION_ID[:8]}.md"
    processor.export_to_markdown(top_ideas, md_file)
    print(f"✅ Top {top_count} ideas exported to: {md_file}")

    # Display top ideas summary
    print("\n" + "-" * 40)
    print(f"Top {top_count} Ideas (by ranking)")
    print("-" * 40)
    for idx, idea in enumerate(top_ideas, 1):
        print(f"{idx}. {idea.title}")
        if idea.attributes.get("eloRating"):
            print(f"   Elo: {idea.attributes['eloRating']}")

except Exception as e:
    print(f"\n❌ Error exporting markdown: {e}")

# Summary statistics
print("\n" + "=" * 40)
print("Export Summary")
print("=" * 40)
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
    print("Elo Rating Statistics:")
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

print("\n✅ Export complete!")
print("\nNext steps:")
print("  1. Review the JSON file for complete idea details")
print("  2. Check the markdown file for formatted top ideas")
print("  3. Use the session ID to track this research session")

client.close()
