# Cosci - Google Co-Scientist Python SDK

Python SDK for Google's Co-Scientist Discovery Engine, enabling AI-powered research ideation and scientific discovery through a simple, production-ready interface.

## Installation

```bash
pip install py-cosci
```

## Quick Setup

### 1. Get Google Cloud Credentials

You'll need a Google Cloud project with the Co-Scientist Discovery Engine API enabled:

1. Create a service account in your Google Cloud Console
2. Download the JSON credentials file
3. Save it somewhere secure (e.g., `credentials/service-account.json`)

### 2. Create Configuration File

Create a `config.yaml` file in your project directory:

```yaml
google_cloud:
  project_id: "your-project-id"
  engine: "your-engine-id"
  credentials_path: "credentials/service-account.json"

logging:
  level: "INFO"

settings:
  timeout: 300
  min_ideas: 1
```

### 3. Start Generating Ideas

```python
from cosci import CoScientist

# Initialize the client (automatically uses config.yaml)
client = CoScientist.from_config()

# Generate research ideas
ideas = client.generate_ideas(
    "Novel approaches to reduce hospital readmission rates using AI"
)

# Display results
for idea in ideas:
    print(f"💡 {idea.title}")
    print(f"   {idea.description}\n")
```

## Research Workflow

The Co-Scientist API operates through several stages to generate high-quality research ideas:

### Typical Research Stages

1. **CREATING** - Session initialization
2. **GENERATING_FOCUS_AREAS** - Identifying key research domains
3. **PREPOPULATING_IDEAS** - Initial idea generation
4. **GENERATING_SCORING_GUIDELINES** - Creating evaluation criteria
5. **RUNNING_INITIAL_REVIEW** - First-pass idea evaluation
6. **REVIEWING_IDEAS** - Detailed review process
7. **RUNNING_TOURNAMENT** - Competitive ranking of ideas
8. **SUCCEEDED** - Research complete with ranked ideas

⏱️ **Expected Duration**: 30-60 minutes for a complete research session

> **Note:** For complex or multifaceted goals, the research process might take a few hours to ensure thorough exploration and evaluation.

## Examples

### Example 1: Start a Research Session

```python
from cosci import CoScientist

client = CoScientist.from_config()
ideas = client.generate_ideas(
    "Suggest novel algorithms for re-ranking retrieved documents in "
    "Retrieval-Augmented Generation (RAG) systems at scale"
)
```

**Output:**
```
✅ Research started!
Session ID: 8610558248018890900
Goal: Suggest novel algorithms for re-ranking retrieved documents in Retrieval-Augmented Generation (RAG) systems at scale...

Save this ID to check progress (typically takes 30-60 minutes)
```

### Example 2: Monitor Progress

```python
from cosci import CoScientist

client = CoScientist.from_config()
session_info = client.session_manager.get_session_info("8610558248018890900")

print(f"Session: {session_info.get('name')}")
print(f"State: {session_info.get('state')}")
print(f"Ideas: {len(session_info.get('ideas', []))}")
```

**Sample Progress Output:**
```
Session: 8610558248018890900
State: GENERATING_FOCUS_AREAS
Ideas: 27
⚠️  Transition state: GENERATING_FOCUS_AREAS

# Later...
Session: 8610558248018890900
State: PREPOPULATING_IDEAS
Ideas: 35
⚠️  Transition state: PREPOPULATING_IDEAS

# Later...
Session: 8610558248018890900
State: RUNNING_TOURNAMENT
Ideas: 88
⚠️  Transition state: RUNNING_TOURNAMENT

# Finally...
Session: 8610558248018890900
State: SUCCEEDED
Ideas: 88
✅ Complete! Run 03_get_ideas.py to retrieve results
```

### Example 3: Retrieve Completed Ideas

```python
from cosci import CoScientist

client = CoScientist.from_config()
ideas = client.get_session_ideas("8610558248018890900")

print(f"✅ Found {len(ideas)} ideas\n")

# Display top ideas
for i, idea in enumerate(ideas[:3], 1):
    print(f"💡 Idea {i}: {idea.title}")
    print(f"   {idea.description[:200]}...")
    if hasattr(idea, 'elo_rating'):
        print(f"   [Elo: {idea.elo_rating}]")
    print()
```

**Output:**
```
✅ Found 88 ideas

💡 Idea 1: Adaptive Synergistic Beam Re-ranker (ASBR) for Optimal Document Set Selection in RAG Systems
   The Adaptive Synergistic Beam Re-ranker (ASBR) is a novel algorithm designed to overcome limitations in RAG by optimizing for an *optimal set* of documents for an LLM's context window...
   [Elo: 1645.476]

💡 Idea 2: Policy-Learned Generative Relevance (PLGR) Agent with Adaptive Feedback & Hierarchical Optimization for RAG Re-ranking
   The Policy-Learned Generative Relevance (PLGR) Agent introduces a novel re-ranking strategy that treats context selection as a sequential decision-making process...
   [Elo: 1556.5459]

💡 Idea 3: The Cognitive Graph Orchestrator (CGO) Reranking Algorithm
   The Cognitive Graph Orchestrator (CGO) Reranking Algorithm introduces a multi-stage, adaptive pipeline to transform RAG context preparation for LLMs...
   [Elo: 1539.115]
```

### Example 4: View Recent Sessions

```python
from cosci import CoScientist

client = CoScientist.from_config()
sessions = client.list_sessions(days=7)

print(f"Found {len(sessions)} sessions in last 7 days")
for session in sessions[:5]:
    print(f"  {session.id}: {session.state} ({session.idea_count} ideas)")
```

**Output:**
```
Found 13 sessions in last 7 days

State Distribution:
  CREATING: 7
  IN_PROGRESS: 5
  SUCCEEDED: 1
```

### Example 5: Export Ideas

```python
from cosci import CoScientist

client = CoScientist.from_config()
client.export_ideas(
    session_id="8610558248018890900",
    output_path="out/ideas/",
    format="json"
)
```

**Output:**
```
Exporting session: 8610558248018890900
✅ Full export: out/ideas/ideas_86105582_20250930_113128.json
✅ Simple export: out/ideas/ideas_simple_86105582_20250930_113128.json

Exported 88 ideas
Average Elo: 1379.32
Top idea: Adaptive Synergistic Beam Re-ranker (ASBR) for Optimal Document Set Selection in RAG Systems
```

## More Examples

Check out the `examples/` directory for complete working examples:

- `01_quick_start.py` - Start a research session
- `02_monitor_progress.py` - Monitor session progress through all stages
- `03_get_ideas.py` - Retrieve and display completed ideas with Elo ratings
- `04_recent_sessions.py` - View recent sessions with statistics
- `05_all_sessions.py` - Comprehensive session management
- `07_export_ideas.py` - Export ideas to JSON format

Run any example:
```bash
python examples/01_quick_start.py
```

## Features

- 🚀 **Simple Interface** - One method to generate ideas: `generate_ideas()`
- ⚙️ **Configurable** - YAML-based configuration for easy setup
- 📊 **Rich Logging** - Detailed logs showing research stages
- 🔄 **Automatic Retries** - Built-in retry logic with exponential backoff
- 📈 **Performance Monitoring** - Track research progress through multiple stages
- 🎯 **Type Safe** - Full type hints for better IDE support
- 🏆 **Elo Rankings** - Ideas ranked by competitive tournament scoring

## Understanding Elo Ratings

Ideas generated by Co-Scientist are ranked using an Elo rating system:

- **1600+**: Exceptional ideas (top tier)
- **1500-1599**: Strong ideas with high potential
- **1400-1499**: Solid ideas worth exploring
- **1300-1399**: Viable ideas with specific applications
- **Below 1300**: May require refinement

The average Elo across all ideas provides a quality benchmark for the session.

## Configuration Options

The `config.yaml` file supports these options:

```yaml
google_cloud:
  project_id: "your-project-id"       # Required
  engine: "your-engine-id"             # Required
  credentials_path: "path/to/creds"    # Required
  location: "global"                   # Optional (default: "global")
  collection: "default_collection"     # Optional

logging:
  level: "INFO"    # DEBUG, INFO, WARNING, ERROR
  file: null       # Set to path for file logging

settings:
  timeout: 3600         # Max seconds to wait (increase for complex queries)
  min_ideas: 1          # Minimum ideas to generate
  poll_interval: 30     # Seconds between status checks during research
```

## Requirements

- Python 3.8+
- Google Cloud Project with Co-Scientist API access
- Service account credentials with appropriate permissions

## Troubleshooting

### Long Wait Times
Research sessions typically take 30-60 minutes. For complex queries:

```python
# Increase timeout for complex research questions
client = CoScientist.from_config()
ideas = client.generate_ideas(
    "Complex multi-faceted research question",
    wait_timeout=3600  # 60 minutes
)
```

### Monitoring Progress
Use the monitoring script to check intermediate states:

```bash
python examples/02_monitor_progress.py
```

This shows the current stage (GENERATING_FOCUS_AREAS, PREPOPULATING_IDEAS, etc.) and idea count.

### Debug Mode
```python
from cosci.config import Config

config = Config.from_yaml()
config.log_level = "DEBUG"
client = CoScientist(config)
```

## Support

- **Documentation**: [GitHub Wiki](https://github.com/arunpshankar/cosci)
- **Issues**: [GitHub Issues](https://github.com/arunpshankar/cosci/issues)
- **Examples**: [Example Scripts](https://github.com/arunpshankar/cosci/tree/main/examples)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## Citation

If you use Cosci in your research, please cite:

```bibtex
@software{cosci2025,
  title = {Cosci: Python SDK for Google Co-Scientist},
  year = {2025},
  url = {https://github.com/yourusername/cosci}
}
```