"""Tests for new judge prompt templates."""

import pytest

from metaeval.prompts import get_prompt, list_prompts


class TestComparativePrompt:
    """Tests for the comparative prompt template."""

    def test_prompt_exists(self):
        """Test that comparative prompt is registered."""
        prompt = get_prompt("comparative", "judge")
        assert prompt is not None

    def test_prompt_metadata(self):
        """Test prompt metadata."""
        prompt = get_prompt("comparative", "judge")
        assert prompt.name == "comparative"
        assert prompt.category == "judge"
        assert prompt.version is not None

    def test_prompt_variables(self):
        """Test that required variables are defined."""
        prompt = get_prompt("comparative", "judge")

        # Comparative prompt needs two responses
        assert "question" in prompt.variables
        assert "expected_answer" in prompt.variables
        assert "response_a" in prompt.variables
        assert "response_b" in prompt.variables
        assert "rubric" in prompt.variables

    def test_prompt_template_content(self):
        """Test that template contains key instructions."""
        prompt = get_prompt("comparative", "judge")
        template = prompt.template.lower()

        # Should mention comparison
        assert "compare" in template or "comparison" in template

        # Should have placeholders
        assert "{question}" in prompt.template
        assert "{response_a}" in prompt.template
        assert "{response_b}" in prompt.template

    def test_prompt_format(self):
        """Test that prompt can be formatted."""
        prompt = get_prompt("comparative", "judge")

        formatted = prompt.format(
            question="What is systems engineering?",
            expected_answer="A discipline that...",
            response_a="SE is about systems",
            response_b="SE is a methodology",
            rubric="Full credit for mentioning lifecycle",
        )

        assert "What is systems engineering?" in formatted
        assert "SE is about systems" in formatted
        assert "SE is a methodology" in formatted


class TestDomainExpertPrompt:
    """Tests for the domain_expert prompt template."""

    def test_prompt_exists(self):
        """Test that domain_expert prompt is registered."""
        prompt = get_prompt("domain_expert", "judge")
        assert prompt is not None

    def test_prompt_metadata(self):
        """Test prompt metadata."""
        prompt = get_prompt("domain_expert", "judge")
        assert prompt.name == "domain_expert"
        assert prompt.category == "judge"
        assert prompt.version is not None

    def test_prompt_variables(self):
        """Test that required variables are defined."""
        prompt = get_prompt("domain_expert", "judge")

        assert "question" in prompt.variables
        assert "expected_answer" in prompt.variables
        assert "response" in prompt.variables
        assert "rubric" in prompt.variables

    def test_prompt_has_persona(self):
        """Test that prompt establishes an expert persona."""
        prompt = get_prompt("domain_expert", "judge")
        template = prompt.template.lower()

        # Should mention expert role
        assert "engineer" in template or "expert" in template

        # Should mention systems engineering context
        assert "systems" in template

    def test_prompt_scoring_dimensions(self):
        """Test that prompt defines scoring dimensions."""
        prompt = get_prompt("domain_expert", "judge")
        template = prompt.template.lower()

        # Should have scoring dimensions
        assert "technical" in template
        assert "practical" in template or "application" in template

    def test_prompt_format(self):
        """Test that prompt can be formatted."""
        prompt = get_prompt("domain_expert", "judge")

        formatted = prompt.format(
            question="Explain the V-model.",
            expected_answer="The V-model is...",
            response="V-model shows verification and validation",
            rubric="Mention left and right sides",
        )

        assert "Explain the V-model" in formatted
        assert "V-model shows verification" in formatted

    def test_prompt_json_output_format(self):
        """Test that prompt requests JSON output."""
        prompt = get_prompt("domain_expert", "judge")

        # Should request JSON format
        assert "json" in prompt.template.lower()


class TestPromptDiscovery:
    """Tests for prompt discovery."""

    def test_new_prompts_in_list(self):
        """Test that new prompts appear in list."""
        prompts = list_prompts("judge")

        prompt_names = [p for p in prompts]
        assert "comparative" in prompt_names
        assert "domain_expert" in prompt_names

    def test_prompt_count_increased(self):
        """Test that we have at least 6 judge prompts now."""
        prompts = list_prompts("judge")

        # Original 4 + 2 new = at least 6
        assert len(prompts) >= 6


class TestPromptCompatibility:
    """Tests for backward compatibility with existing prompts."""

    def test_original_prompts_still_work(self):
        """Test that original prompts are still accessible."""
        original_prompts = [
            "binary",
            "rubric",
            "multi_dimensional",
            "chain_of_thought",
        ]

        for name in original_prompts:
            prompt = get_prompt(name, "judge")
            assert prompt is not None
            assert prompt.name == name

    def test_original_prompts_unchanged(self):
        """Test that original prompts have expected variables."""
        # Multi-dimensional should have standard variables
        prompt = get_prompt("multi_dimensional", "judge")
        assert "question" in prompt.variables
        assert "expected_answer" in prompt.variables
        assert "response" in prompt.variables
        assert "rubric" in prompt.variables
