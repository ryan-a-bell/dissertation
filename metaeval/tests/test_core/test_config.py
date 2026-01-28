"""Tests for configuration system."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from metaeval.core.config import (
    Config,
    JudgeConfig,
    StatsConfig,
    OllamaConfig,
    PathsConfig,
    get_config,
    set_config,
    reset_config,
    get_config_path,
    generate_default_config,
)


class TestJudgeConfig:
    """Tests for JudgeConfig."""

    def test_defaults(self):
        """Test default values."""
        config = JudgeConfig()
        assert config.temperature == 0.0
        assert config.max_tokens == 2048
        assert config.timeout == 300
        assert config.default_prompt == "multi_dimensional"
        assert config.default_provider == "ollama"

    def test_custom_values(self):
        """Test custom values."""
        config = JudgeConfig(
            temperature=0.7,
            max_tokens=4096,
            default_provider="openai",
        )
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.default_provider == "openai"


class TestStatsConfig:
    """Tests for StatsConfig."""

    def test_defaults(self):
        """Test default values."""
        config = StatsConfig()
        assert config.alpha == 0.05
        assert config.bootstrap_iterations == 10000
        assert config.confidence_level == 0.95
        assert config.random_seed == 42

    def test_effect_size_thresholds(self):
        """Test effect size thresholds."""
        config = StatsConfig()
        assert "small" in config.effect_size_thresholds
        assert "medium" in config.effect_size_thresholds
        assert "large" in config.effect_size_thresholds


class TestOllamaConfig:
    """Tests for OllamaConfig."""

    def test_defaults(self):
        """Test default values."""
        config = OllamaConfig()
        assert config.host == "localhost"
        assert config.port == 11434
        assert config.default_model == "llama3.1:8b"
        assert config.auto_pull is True


class TestConfig:
    """Tests for main Config class."""

    def test_defaults(self):
        """Test default configuration."""
        config = Config()
        assert isinstance(config.judge, JudgeConfig)
        assert isinstance(config.stats, StatsConfig)
        assert isinstance(config.ollama, OllamaConfig)
        assert isinstance(config.paths, PathsConfig)

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "judge": {"temperature": 0.5, "max_tokens": 1024},
            "stats": {"alpha": 0.01},
            "ollama": {"host": "192.168.1.100", "port": 8080},
        }
        config = Config.from_dict(data)
        assert config.judge.temperature == 0.5
        assert config.judge.max_tokens == 1024
        assert config.stats.alpha == 0.01
        assert config.ollama.host == "192.168.1.100"
        assert config.ollama.port == 8080

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        data = config.to_dict()

        assert "judge" in data
        assert "stats" in data
        assert "ollama" in data
        assert "paths" in data
        assert data["judge"]["temperature"] == 0.0
        assert data["stats"]["alpha"] == 0.05

    def test_from_yaml(self):
        """Test loading config from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({
                "judge": {"temperature": 0.3},
                "stats": {"bootstrap_iterations": 5000},
            }, f)
            f.flush()

            config = Config.from_yaml(f.name)

            assert config.judge.temperature == 0.3
            assert config.stats.bootstrap_iterations == 5000

            os.unlink(f.name)

    def test_to_yaml(self):
        """Test saving config to YAML file."""
        config = Config()
        config.judge.temperature = 0.8

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config.to_yaml(f.name)

            with open(f.name) as rf:
                data = yaml.safe_load(rf)

            assert data["judge"]["temperature"] == 0.8
            os.unlink(f.name)

    def test_backward_compatibility_properties(self):
        """Test output_dir and cache_dir properties."""
        config = Config()
        assert config.output_dir == config.paths.output_dir
        assert config.cache_dir == config.paths.cache_dir


class TestGlobalConfig:
    """Tests for global config functions."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def test_get_config_returns_config(self):
        """Test get_config returns Config instance."""
        config = get_config()
        assert isinstance(config, Config)

    def test_set_config(self):
        """Test setting global config."""
        custom_config = Config()
        custom_config.judge.temperature = 0.9

        set_config(custom_config)
        retrieved = get_config()

        assert retrieved.judge.temperature == 0.9

    def test_reset_config(self):
        """Test resetting global config."""
        custom_config = Config()
        custom_config.judge.temperature = 0.9
        set_config(custom_config)

        reset_config()
        new_config = get_config()

        # Should be default again
        assert new_config.judge.temperature == 0.0


class TestConfigHelpers:
    """Tests for config helper functions."""

    def test_get_config_path(self):
        """Test get_config_path returns correct path."""
        path = get_config_path()
        assert isinstance(path, Path)
        assert path.name == "config.yaml"
        assert ".metaeval" in str(path)

    def test_generate_default_config(self):
        """Test generate_default_config returns valid YAML."""
        config_str = generate_default_config()
        assert isinstance(config_str, str)
        assert "judge:" in config_str
        assert "stats:" in config_str
        assert "ollama:" in config_str

        # Should be valid YAML
        data = yaml.safe_load(config_str)
        assert "judge" in data
        assert "stats" in data
