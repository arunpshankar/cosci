"""Example: Monitor API performance and statistics."""

from cosci import CoScientist

client = CoScientist.from_config()

print("API Performance Monitoring")
print("=" * 60)

# Make some API calls
print("\nPerforming API operations...")

# List sessions
sessions = client.list_sessions()
print(f"  Listed {len(sessions)} sessions")

# Create a test session
research_goal = "Test research for monitoring API performance"
session = client.session_manager.create_session(research_goal)
print(f"  Created session: {session.session_id[:8]}...")

# Get session info
info = client.session_manager.get_session_info(session.session_id)
print("  Retrieved session info")

# Get API statistics
print("\nAPI Statistics:")
print("-" * 40)

if client.api_client:
    stats = client.api_client.get_stats()

    print(f"Total Requests: {stats.get('total_requests', 0)}")
    print(f"Successful: {stats.get('successful_requests', 0)}")
    print(f"Failed: {stats.get('failed_requests', 0)}")
    print(f"Success Rate: {stats.get('success_rate', 0):.1%}")
    print(f"Avg Response Time: {stats.get('avg_request_time', 0):.2f}s")

    # Status code distribution
    status_codes = stats.get("status_codes", {})
    if status_codes:
        print("\nStatus Code Distribution:")
        for code, count in sorted(status_codes.items()):
            print(f"  {code}: {count}")

client.close()
