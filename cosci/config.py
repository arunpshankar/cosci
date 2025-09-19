"""
Configuration management for Cosci SDK.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from cosci.exceptions import CosciError


@dataclass
class Config:
    """
    Configuration for Cosci SDK.
    """

    # Google Cloud settings
    project_id: str
    engine: str
    credentials_path: str
    location: str = "global"
    collection: str = "default_collection"

    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Operation settings
    timeout: int = 300
    min_ideas: int = 1
    poll_interval: int = 5

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "Config":
        """
        Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            Config object

        Raises:
            CosciError: If config file is invalid or missing
        """
        config_path = Path(path)

        if not config_path.exists():
            raise CosciError(
                f"Configuration file not found: {path}\n"
                "Please create config.yaml from config.example.yaml"
            )

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise CosciError(f"Invalid YAML in config file: {e}")

        # Validate required fields
        if not data.get("google_cloud"):
            raise CosciError("Missing 'google_cloud' section in config")

        gc = data["google_cloud"]
        if not gc.get("project_id"):
            raise CosciError("Missing 'project_id' in config")
        if not gc.get("engine"):
            raise CosciError("Missing 'engine' in config")
        if not gc.get("credentials_path"):
            raise CosciError("Missing 'credentials_path' in config")

        # Create config object
        return cls(
            project_id=gc["project_id"],
            engine=gc["engine"],
            credentials_path=gc["credentials_path"],
            location=gc.get("location", "global"),
            collection=gc.get("collection", "default_collection"),
            log_level=data.get("logging", {}).get("level", "INFO"),
            log_file=data.get("logging", {}).get("file"),
            timeout=data.get("settings", {}).get("timeout", 300),
            min_ideas=data.get("settings", {}).get("min_ideas", 1),
            poll_interval=data.get("settings", {}).get("poll_interval", 5),
        )

    def validate(self):
        """
        Validate configuration values.

        Raises:
            CosciError: If configuration is invalid
        """
        # Check credentials file exists
        if not Path(self.credentials_path).exists():
            raise CosciError(
                f"Credentials file not found: {self.credentials_path}\n"
                "Please ensure the service account JSON file exists"
            )

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise CosciError(
                f"Invalid log level: {self.log_level}\n"
                f"Must be one of: {', '.join(valid_levels)}"
            )

        # Validate numeric values
        if self.timeout <= 0:
            raise CosciError("Timeout must be positive")
        if self.min_ideas <= 0:
            raise CosciError("min_ideas must be positive")
        if self.poll_interval <= 0:
            raise CosciError("poll_interval must be positive")
