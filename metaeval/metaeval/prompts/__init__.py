"""
Prompt templates for metaeval.

This module provides a registry system for prompt templates that supports:
- Auto-discovery of prompts from YAML files
- Custom prompt directories
- Programmatic registration

Usage:
    from metaeval.prompts import get_prompt, list_prompts, add_prompt_path

    # List available prompts
    print(list_prompts("judge"))  # ['binary', 'rubric', 'multi_dimensional', 'chain_of_thought']

    # Get a specific prompt
    prompt = get_prompt("multi_dimensional", "judge")
    formatted = prompt.format(question="...", expected_answer="...", ...)

    # Add custom prompt directory
    add_prompt_path("/path/to/my/prompts")

Creating custom prompts:
    Create a YAML file in the prompts directory with this structure:

    ```yaml
    name: my_custom_prompt
    category: judge  # or "convert"
    version: "1.0"
    description: Description of what this prompt does
    variables:
      - question
      - expected_answer
      - response
    template: |
      Your prompt template here with {variable} placeholders.
    ```
"""

from metaeval.prompts.registry import (
    PromptTemplate,
    PromptRegistry,
    get_registry,
    register_prompt,
    get_prompt,
    list_prompts,
    add_prompt_path,
)

__all__ = [
    "PromptTemplate",
    "PromptRegistry",
    "get_registry",
    "register_prompt",
    "get_prompt",
    "list_prompts",
    "add_prompt_path",
]
