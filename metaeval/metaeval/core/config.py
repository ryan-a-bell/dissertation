"""Configuration management for metaeval."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass
class APIConfig:
    """API configuration for various providers."""

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    huggingface_token: str | None = None
    runpod_api_key: str | None = None
    openrouter_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Load API configuration from environment variables."""
        load_dotenv()
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            huggingface_token=os.getenv("HF_TOKEN"),
            runpod_api_key=os.getenv("RUNPOD_API_KEY"),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        )


@dataclass
class JudgeConfig:
    """Configuration for LLM-as-a-Judge."""

    temperature: float = 0.0
    max_tokens: int = 2048
    timeout: int = 300
    default_prompt: str = "multi_dimensional"
    default_provider: str = "ollama"


@dataclass
class OllamaConfig:
    """Configuration for Ollama."""

    host: str = "localhost"
    port: int = 11434
    default_model: str = "llama3.1:8b"
    auto_pull: bool = True


@dataclass
class PathsConfig:
    """Configuration for file paths."""

    data_dir: Path = field(default_factory=lambda: Path("data"))
    cache_dir: Path = field(default_factory=lambda: Path(".cache"))
    output_dir: Path = field(default_factory=lambda: Path("output"))


@dataclass
class StatsConfig:
    """Configuration for statistical analysis."""

    alpha: float = 0.05
    bootstrap_iterations: int = 10000
    confidence_level: float = 0.95
    random_seed: int = 42
    effect_size_thresholds: dict[str, float] = field(default_factory=lambda: {
        "small": 0.1,
        "medium": 0.3,
        "large": 0.5,
    })


@dataclass
class InferenceConfig:
    """Configuration for model inference."""

    temperature: float = 0.0
    max_tokens: int = 2048
    timeout: int = 300
    retries: int = 3
    batch_size: int = 10


@dataclass
class Config:
    """Main configuration class for metaeval."""

    api: APIConfig = field(default_factory=APIConfig)
    judge: JudgeConfig = field(default_factory=JudgeConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)

    # Backward compatibility properties
    @property
    def output_dir(self) -> Path:
        return self.paths.output_dir

    @property
    def cache_dir(self) -> Path:
        return self.paths.cache_dir

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        config = cls(api=APIConfig.from_env())

        # Load additional env vars
        if os.getenv("METAEVAL_ALPHA"):
            config.stats.alpha = float(os.getenv("METAEVAL_ALPHA"))
        if os.getenv("METAEVAL_BOOTSTRAP_ITERATIONS"):
            config.stats.bootstrap_iterations = int(os.getenv("METAEVAL_BOOTSTRAP_ITERATIONS"))
        if os.getenv("OLLAMA_HOST"):
            config.ollama.host = os.getenv("OLLAMA_HOST")
        if os.getenv("OLLAMA_PORT"):
            config.ollama.port = int(os.getenv("OLLAMA_PORT"))

        return config

    @classmethod
    def from_yaml(cls, path: Path | str) -> "Config":
        """Load configuration from YAML file."""
        path = Path(path)
        if not path.exists():
            return cls.from_env()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create configuration from a dictionary."""
        api_data = data.get("api", {})
        judge_data = data.get("judge", {})
        ollama_data = data.get("ollama", {})
        stats_data = data.get("stats", {})
        inference_data = data.get("inference", {})
        paths_data = data.get("paths", {})

        # Handle paths conversion to Path objects
        if paths_data:
            for key in ["data_dir", "cache_dir", "output_dir"]:
                if key in paths_data:
                    paths_data[key] = Path(paths_data[key])

        return cls(
            api=APIConfig(**api_data) if api_data else APIConfig.from_env(),
            judge=JudgeConfig(**judge_data) if judge_data else JudgeConfig(),
            ollama=OllamaConfig(**ollama_data) if ollama_data else OllamaConfig(),
            stats=StatsConfig(**stats_data) if stats_data else StatsConfig(),
            inference=InferenceConfig(**inference_data) if inference_data else InferenceConfig(),
            paths=PathsConfig(**paths_data) if paths_data else PathsConfig(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api": {
                "openai_api_key": "***" if self.api.openai_api_key else None,
                "anthropic_api_key": "***" if self.api.anthropic_api_key else None,
                "openrouter_api_key": "***" if self.api.openrouter_api_key else None,
            },
            "judge": {
                "temperature": self.judge.temperature,
                "max_tokens": self.judge.max_tokens,
                "timeout": self.judge.timeout,
                "default_prompt": self.judge.default_prompt,
                "default_provider": self.judge.default_provider,
            },
            "ollama": {
                "host": self.ollama.host,
                "port": self.ollama.port,
                "default_model": self.ollama.default_model,
                "auto_pull": self.ollama.auto_pull,
            },
            "stats": {
                "alpha": self.stats.alpha,
                "bootstrap_iterations": self.stats.bootstrap_iterations,
                "confidence_level": self.stats.confidence_level,
                "random_seed": self.stats.random_seed,
                "effect_size_thresholds": self.stats.effect_size_thresholds,
            },
            "inference": {
                "temperature": self.inference.temperature,
                "max_tokens": self.inference.max_tokens,
                "timeout": self.inference.timeout,
                "retries": self.inference.retries,
                "batch_size": self.inference.batch_size,
            },
            "paths": {
                "data_dir": str(self.paths.data_dir),
                "cache_dir": str(self.paths.cache_dir),
                "output_dir": str(self.paths.output_dir),
            },
        }

    def to_yaml(self, path: Path | str) -> None:
        """Save configuration to YAML file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def ensure_dirs(self) -> None:
        """Ensure output and cache directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """
    Get the global configuration.

    Loads from (in order of priority):
    1. Previously set config via set_config()
    2. ~/.metaeval/config.yaml if exists
    3. Environment variables
    """
    global _config
    if _config is None:
        # Try to load from default config file
        default_path = Path.home() / ".metaeval" / "config.yaml"
        if default_path.exists():
            _config = Config.from_yaml(default_path)
        else:
            _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset global configuration to reload on next access."""
    global _config
    _config = None


def get_config_path() -> Path:
    """Get the default configuration file path."""
    return Path.home() / ".metaeval" / "config.yaml"


def generate_default_config() -> str:
    """Generate default configuration as YAML string."""
    return """# Metaeval Configuration
# This file controls default settings for the metaeval toolkit.

# LLM-as-a-Judge settings
judge:
  temperature: 0.0          # Generation temperature (0.0 = deterministic)
  max_tokens: 2048          # Maximum tokens to generate
  timeout: 300              # Request timeout in seconds
  default_prompt: multi_dimensional  # Default judge prompt style
  default_provider: ollama  # Default provider (ollama, openai, anthropic, openrouter)

# Ollama settings (for local models)
ollama:
  host: localhost           # Ollama server host
  port: 11434               # Ollama server port
  default_model: llama3.1:8b  # Default model for judging
  auto_pull: true           # Auto-pull missing models

# Statistical analysis settings
stats:
  alpha: 0.05               # Significance level for hypothesis tests
  bootstrap_iterations: 10000  # Number of bootstrap iterations
  confidence_level: 0.95    # Confidence level for intervals
  random_seed: 42           # Random seed for reproducibility
  effect_size_thresholds:   # Interpretation thresholds
    small: 0.1
    medium: 0.3
    large: 0.5

# Model inference settings
inference:
  temperature: 0.0          # Generation temperature
  max_tokens: 2048          # Maximum tokens to generate
  timeout: 300              # Request timeout in seconds
  retries: 3                # Number of retries on failure
  batch_size: 10            # Batch size for parallel inference

# File paths
paths:
  data_dir: data            # Directory for benchmark data
  cache_dir: .cache         # Directory for cached results
  output_dir: output        # Directory for analysis output

# API Keys (set via environment variables for security)
# OPENAI_API_KEY=your-key
# ANTHROPIC_API_KEY=your-key
# OPENROUTER_API_KEY=your-key
"""
