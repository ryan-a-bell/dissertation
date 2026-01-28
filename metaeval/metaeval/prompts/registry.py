"""Prompt registry for auto-discovery of prompt templates."""

from __future__ import annotations

import importlib.resources
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PromptTemplate:
    """A registered prompt template."""

    name: str
    category: str  # "judge" or "convert"
    template: str
    description: str = ""
    version: str = "1.0"
    author: str = ""
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def format(self, **kwargs: Any) -> str:
        """Format the template with provided variables."""
        return self.template.format(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "template": self.template,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "variables": self.variables,
            "metadata": self.metadata,
        }


class PromptRegistry:
    """Registry for prompt templates with auto-discovery."""

    _instance: PromptRegistry | None = None

    def __init__(self):
        """Initialize the registry."""
        self._prompts: dict[str, dict[str, PromptTemplate]] = {
            "judge": {},
            "convert": {},
        }
        self._search_paths: list[Path] = []
        self._loaded = False

    @classmethod
    def get_instance(cls) -> PromptRegistry:
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_search_path(self, path: Path | str) -> None:
        """Add a directory to search for prompt files."""
        path = Path(path)
        if path.exists() and path.is_dir():
            self._search_paths.append(path)
            self._loaded = False  # Force reload on next access
            logger.debug(f"Added prompt search path: {path}")

    def register(
        self,
        name: str,
        category: str,
        template: str,
        description: str = "",
        **kwargs: Any,
    ) -> PromptTemplate:
        """
        Register a prompt template programmatically.

        Args:
            name: Unique name for the prompt
            category: Category ("judge" or "convert")
            template: The prompt template string
            description: Description of the prompt
            **kwargs: Additional metadata

        Returns:
            The registered PromptTemplate
        """
        if category not in self._prompts:
            self._prompts[category] = {}

        prompt = PromptTemplate(
            name=name,
            category=category,
            template=template,
            description=description,
            **kwargs,
        )

        self._prompts[category][name] = prompt
        logger.debug(f"Registered prompt: {category}/{name}")
        return prompt

    def _load_from_yaml(self, path: Path) -> None:
        """Load prompts from a YAML file."""
        try:
            with open(path) as f:
                data = yaml.safe_load(f)

            if not data:
                return

            # Determine category from path or content
            category = data.get("category")
            if not category:
                if "judge" in path.parts:
                    category = "judge"
                elif "convert" in path.parts:
                    category = "convert"
                else:
                    category = "judge"  # default

            name = data.get("name", path.stem)

            prompt = PromptTemplate(
                name=name,
                category=category,
                template=data.get("template", ""),
                description=data.get("description", ""),
                version=data.get("version", "1.0"),
                author=data.get("author", ""),
                variables=data.get("variables", []),
                metadata=data.get("metadata", {}),
            )

            if category not in self._prompts:
                self._prompts[category] = {}

            self._prompts[category][name] = prompt
            logger.debug(f"Loaded prompt from {path}: {category}/{name}")

        except Exception as e:
            logger.warning(f"Failed to load prompt from {path}: {e}")

    def _discover_prompts(self) -> None:
        """Discover and load prompts from all search paths."""
        if self._loaded:
            return

        # Add default package prompts directory
        try:
            import metaeval.prompts
            pkg_path = Path(metaeval.prompts.__file__).parent
            if pkg_path not in self._search_paths:
                self._search_paths.insert(0, pkg_path)
        except (ImportError, AttributeError):
            pass

        # Load from all search paths
        for search_path in self._search_paths:
            if not search_path.exists():
                continue

            # Load YAML files directly in path
            for yaml_file in search_path.glob("*.yaml"):
                self._load_from_yaml(yaml_file)
            for yaml_file in search_path.glob("*.yml"):
                self._load_from_yaml(yaml_file)

            # Load from category subdirectories
            for category in ["judge", "convert"]:
                category_path = search_path / category
                if category_path.exists():
                    for yaml_file in category_path.glob("*.yaml"):
                        self._load_from_yaml(yaml_file)
                    for yaml_file in category_path.glob("*.yml"):
                        self._load_from_yaml(yaml_file)

        self._loaded = True
        logger.info(
            f"Discovered {sum(len(p) for p in self._prompts.values())} prompts "
            f"from {len(self._search_paths)} search paths"
        )

    def get(self, name: str, category: str = "judge") -> PromptTemplate | None:
        """
        Get a prompt template by name.

        Args:
            name: Prompt name
            category: Category ("judge" or "convert")

        Returns:
            PromptTemplate or None if not found
        """
        self._discover_prompts()
        return self._prompts.get(category, {}).get(name)

    def list(self, category: str | None = None) -> list[PromptTemplate]:
        """
        List all registered prompts.

        Args:
            category: Optional category filter

        Returns:
            List of PromptTemplates
        """
        self._discover_prompts()

        if category:
            return list(self._prompts.get(category, {}).values())

        all_prompts = []
        for cat_prompts in self._prompts.values():
            all_prompts.extend(cat_prompts.values())
        return all_prompts

    def list_names(self, category: str | None = None) -> list[str]:
        """
        List all prompt names.

        Args:
            category: Optional category filter

        Returns:
            List of prompt names
        """
        return [p.name for p in self.list(category)]

    def reload(self) -> None:
        """Force reload of all prompts."""
        self._loaded = False
        self._prompts = {"judge": {}, "convert": {}}
        self._discover_prompts()


# Global registry instance
_registry: PromptRegistry | None = None


def get_registry() -> PromptRegistry:
    """Get the global prompt registry."""
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry


def register_prompt(
    name: str,
    category: str,
    template: str,
    description: str = "",
    **kwargs: Any,
) -> PromptTemplate:
    """
    Register a prompt template.

    Args:
        name: Unique name for the prompt
        category: Category ("judge" or "convert")
        template: The prompt template string
        description: Description
        **kwargs: Additional metadata

    Returns:
        The registered PromptTemplate
    """
    return get_registry().register(name, category, template, description, **kwargs)


def get_prompt(name: str, category: str = "judge") -> PromptTemplate | None:
    """
    Get a prompt template by name.

    Args:
        name: Prompt name
        category: Category

    Returns:
        PromptTemplate or None
    """
    return get_registry().get(name, category)


def list_prompts(category: str | None = None) -> list[str]:
    """
    List all available prompt names.

    Args:
        category: Optional category filter

    Returns:
        List of prompt names
    """
    return get_registry().list_names(category)


def add_prompt_path(path: Path | str) -> None:
    """
    Add a custom directory to search for prompts.

    Args:
        path: Directory path
    """
    get_registry().add_search_path(path)
