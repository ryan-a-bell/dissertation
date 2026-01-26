"""Configuration management for metaeval."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
class InferenceConfig:
    """Configuration for model inference."""

    temperature: float = 0.0
    max_tokens: int = 2048
    timeout: int = 300
    retries: int = 3
    batch_size: int = 10


@dataclass
class AnalysisConfig:
    """Configuration for statistical analysis."""

    alpha: float = 0.05
    bootstrap_iterations: int = 10000
    random_seed: int = 42


@dataclass
class Config:
    """Main configuration class for metaeval."""

    api: APIConfig = field(default_factory=APIConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output_dir: Path = field(default_factory=lambda: Path("output"))
    cache_dir: Path = field(default_factory=lambda: Path(".cache"))

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(api=APIConfig.from_env())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create configuration from a dictionary."""
        api_data = data.get("api", {})
        inference_data = data.get("inference", {})
        analysis_data = data.get("analysis", {})

        return cls(
            api=APIConfig(**api_data) if api_data else APIConfig(),
            inference=InferenceConfig(**inference_data) if inference_data else InferenceConfig(),
            analysis=AnalysisConfig(**analysis_data) if analysis_data else AnalysisConfig(),
            output_dir=Path(data.get("output_dir", "output")),
            cache_dir=Path(data.get("cache_dir", ".cache")),
        )

    def ensure_dirs(self) -> None:
        """Ensure output and cache directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
