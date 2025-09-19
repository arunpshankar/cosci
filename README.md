# Cosci - Google Co-Scientist Python SDK

Python SDK for Google's Co-Scientist Discovery Engine, enabling AI-powered research ideation and scientific discovery through a simple, production-ready interface.

## Installation

```bash
pip install cosci
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

## Examples

### Basic Usage
```python
from cosci import CoScientist

# Simple one-liner to get ideas
client = CoScientist.from_config()
ideas = client.generate_ideas("Your research question here")
```

### Advanced Usage with Custom Settings
```python
from cosci import CoScientist
from cosci.config import Config

# Customize configuration
config = Config.from_yaml("config.yaml")
config.timeout = 600  # 10 minutes
config.log_level = "DEBUG"  # See detailed logs

# Initialize with custom config
client = CoScientist(config)

# Generate ideas with specific requirements
ideas = client.generate_ideas(
    research_goal="Innovative cancer detection methods",
    min_ideas=5,  # Wait for at least 5 ideas
    wait_timeout=600  # Custom timeout
)

# Process results
for idea in ideas:
    print(f"Title: {idea.title}")
    if idea.attributes:
        for key, value in idea.attributes.items():
            print(f"  {key}: {value}")
```

### Working with Sessions
```python
from cosci import CoScientist

client = CoScientist.from_config()

# List existing sessions
sessions = client.list_sessions()
print(f"Found {len(sessions)} existing sessions")

# Get specific session info
session_info = client.session_manager.get_session_info("session-id-here")
print(f"Session state: {session_info.get('state')}")
```

## More Examples

Check out the `examples/` directory for more use cases:

- `quickstart.py` - Basic usage
- `advanced.py` - Advanced configuration
- `session_management.py` - Working with sessions
- `retrieve_existing.py` - Access previous results
- `api_statistics.py` - Monitor API performance

Run any example:
```bash
python examples/quickstart.py
```

## Features

- 🚀 **Simple Interface** - One method to generate ideas: `generate_ideas()`
- ⚙️ **Configurable** - YAML-based configuration for easy setup
- 📊 **Rich Logging** - Detailed logs with multiple verbosity levels
- 🔄 **Automatic Retries** - Built-in retry logic with exponential backoff
- 📈 **Performance Monitoring** - Track API statistics and performance
- 🎯 **Type Safe** - Full type hints for better IDE support

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
  timeout: 300          # Max seconds to wait for ideas
  min_ideas: 1          # Minimum ideas to generate
  poll_interval: 5      # Seconds between status checks
```

## Requirements

- Python 3.8+
- Google Cloud Project with Co-Scientist API access
- Service account credentials with appropriate permissions

## Troubleshooting

### Authentication Issues
```python
# Make sure credentials file exists
import os
if not os.path.exists("credentials/service-account.json"):
    print("Credentials file not found!")
```

### Timeout Issues
```python
# Increase timeout for complex queries
client = CoScientist.from_config()
ideas = client.generate_ideas(
    "Complex research question",
    wait_timeout=600  # 10 minutes
)
```

### Debug Mode
```python
# Enable debug logging to see what's happening
from cosci.config import Config

config = Config.from_yaml()
config.log_level = "DEBUG"
client = CoScientist(config)
```

## Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/cosci/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/cosci/issues)
- **Examples**: [Example Scripts](https://github.com/yourusername/cosci/tree/main/examples)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## Citation

If you use Cosci in your research, please cite:

```bibtex
@software{cosci2024,
  title = {Cosci: Python SDK for Google Co-Scientist},
  year = {2024},
  url = {https://github.com/yourusername/cosci}
}
```