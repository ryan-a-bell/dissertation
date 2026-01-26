"""Tests for prompt registry."""

import tempfile
from pathlib import Path

import pytest
import yaml

from metaeval.prompts.registry import (
    PromptTemplate,
    PromptRegistry,
    get_registry,
    get_prompt,
    add_prompt_path,
)


class TestPromptTemplate:
    """Tests for PromptTemplate dataclass."""

    def test_creation(self):
        """Test creating a prompt template."""
        template = PromptTemplate(
            name="test_prompt",
            category="judge",
            template="Hello {name}!",
            description="A test prompt",
            version="1.0",
            variables=["name"],
        )
        assert template.name == "test_prompt"
        assert template.category == "judge"
        assert "{name}" in template.template

    def test_format(self):
        """Test formatting a template."""
        template = PromptTemplate(
            name="test",
            category="judge",
            template="Question: {question}\nAnswer: {answer}",
            variables=["question", "answer"],
        )
        result = template.format(question="What is 2+2?", answer="4")
        assert "What is 2+2?" in result
        assert "4" in result

    def test_format_missing_variable(self):
        """Test format with missing variable raises error."""
        template = PromptTemplate(
            name="test",
            category="judge",
            template="Hello {name}!",
            variables=["name"],
        )
        with pytest.raises(KeyError):
            template.format()

    def test_from_yaml_dict(self):
        """Test creating template from YAML dict."""
        data = {
            "name": "test_prompt",
            "category": "convert",
            "template": "Convert this: {input}",
            "description": "Conversion prompt",
            "version": "2.0",
            "variables": ["input"],
        }
        template = PromptTemplate.from_yaml_dict(data)
        assert template.name == "test_prompt"
        assert template.version == "2.0"


class TestPromptRegistry:
    """Tests for PromptRegistry."""

    def test_singleton(self):
        """Test registry is singleton."""
        reg1 = get_registry()
        reg2 = get_registry()
        assert reg1 is reg2

    def test_list_all(self):
        """Test listing all prompts."""
        registry = get_registry()
        prompts = registry.list()
        assert isinstance(prompts, list)
        # Should have built-in prompts
        assert len(prompts) > 0

    def test_list_by_category(self):
        """Test listing prompts by category."""
        registry = get_registry()

        judge_prompts = registry.list("judge")
        convert_prompts = registry.list("convert")

        for p in judge_prompts:
            assert p.category == "judge"

        for p in convert_prompts:
            assert p.category == "convert"

    def test_get_existing_prompt(self):
        """Test getting an existing prompt."""
        registry = get_registry()
        prompts = registry.list("judge")

        if prompts:
            name = prompts[0].name
            prompt = registry.get(name, "judge")
            assert prompt is not None
            assert prompt.name == name

    def test_get_nonexistent_prompt(self):
        """Test getting a nonexistent prompt returns None."""
        registry = get_registry()
        prompt = registry.get("nonexistent_prompt_xyz", "judge")
        assert prompt is None

    def test_add_search_path(self):
        """Test adding custom search path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a custom prompt file
            prompt_dir = Path(tmpdir) / "custom"
            prompt_dir.mkdir()

            prompt_data = {
                "name": "custom_test",
                "category": "judge",
                "template": "Custom: {input}",
                "version": "1.0",
                "variables": ["input"],
            }

            with open(prompt_dir / "custom_test.yaml", "w") as f:
                yaml.dump(prompt_data, f)

            registry = get_registry()
            registry.add_search_path(prompt_dir)

            # Should find the custom prompt
            prompt = registry.get("custom_test", "judge")
            assert prompt is not None
            assert prompt.name == "custom_test"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_prompt(self):
        """Test get_prompt function."""
        registry = get_registry()
        prompts = registry.list("judge")

        if prompts:
            prompt = get_prompt(prompts[0].name, "judge")
            assert prompt is not None

    def test_add_prompt_path(self):
        """Test add_prompt_path function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            add_prompt_path(Path(tmpdir))
            # Should not raise error


class TestBuiltInPrompts:
    """Tests for built-in prompts."""

    def test_judge_prompts_exist(self):
        """Test that judge prompts exist."""
        registry = get_registry()
        judge_prompts = registry.list("judge")
        names = [p.name for p in judge_prompts]

        # Check for expected prompts
        assert "multi_dimensional" in names or len(names) > 0

    def test_convert_prompts_exist(self):
        """Test that convert prompts exist."""
        registry = get_registry()
        convert_prompts = registry.list("convert")
        names = [p.name for p in convert_prompts]

        # Check for expected prompts
        assert "standard" in names or len(names) > 0

    def test_prompts_have_required_fields(self):
        """Test that all prompts have required fields."""
        registry = get_registry()
        prompts = registry.list()

        for prompt in prompts:
            assert prompt.name is not None
            assert prompt.category is not None
            assert prompt.template is not None
            assert len(prompt.template) > 0
