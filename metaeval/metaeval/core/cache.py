"""Cache management for LLM judge responses using human-readable JSONL."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """A single cache entry for a judge response."""

    key: str
    model: str
    prompt_style: str
    question_hash: str
    response_hash: str
    judgment: dict[str, Any]
    timestamp: str

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "CacheEntry":
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


def _hash_text(text: str) -> str:
    """Compute SHA256 hash of text, truncated for readability."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _compute_cache_key(
    model: str,
    prompt_style: str,
    question: str,
    response: str,
) -> str:
    """
    Compute a cache key from inputs.

    Key format: {model}_{prompt_style}_{question_hash}_{response_hash}
    """
    question_hash = _hash_text(question)
    response_hash = _hash_text(response)
    return f"{model}_{prompt_style}_{question_hash}_{response_hash}"


class JudgeCache:
    """
    Cache for LLM judge responses using human-readable JSONL format.

    The cache stores entries in a JSONL file where each line is a complete
    JSON object containing the cache key, inputs, and judgment result.
    This format is:
    - Human-readable and inspectable
    - Append-only for reliability
    - Easy to grep/search
    - Compatible with streaming tools

    Example entry:
    {"key": "llama3.1:8b_multi_dimensional_abc123_def456",
     "model": "llama3.1:8b", "prompt_style": "multi_dimensional",
     "question_hash": "abc123", "response_hash": "def456",
     "judgment": {...}, "timestamp": "2024-01-15T10:30:00"}
    """

    def __init__(
        self,
        cache_dir: Path | str | None = None,
        cache_file: str = "judge_cache.jsonl",
        enabled: bool = True,
    ):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory for cache files (default: .cache/)
            cache_file: Name of the cache file
            enabled: Whether caching is enabled
        """
        self.enabled = enabled

        if cache_dir is None:
            cache_dir = Path(".cache")
        else:
            cache_dir = Path(cache_dir)

        self.cache_dir = cache_dir
        self.cache_file = cache_dir / cache_file
        self._index: dict[str, CacheEntry] | None = None

    def _ensure_dir(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> dict[str, CacheEntry]:
        """Load cache index from file."""
        if self._index is not None:
            return self._index

        self._index = {}

        if not self.cache_file.exists():
            return self._index

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = CacheEntry.from_json(line)
                        self._index[entry.key] = entry
                    except (json.JSONDecodeError, TypeError, KeyError) as e:
                        logger.warning(f"Skipping malformed cache entry at line {line_num}: {e}")

            logger.debug(f"Loaded {len(self._index)} entries from cache")

        except OSError as e:
            logger.warning(f"Could not read cache file: {e}")

        return self._index

    def get(
        self,
        model: str,
        question: str,
        response: str,
        prompt_style: str,
    ) -> dict[str, Any] | None:
        """
        Get a cached judgment if available.

        Args:
            model: Model identifier
            question: The question text
            response: The response text
            prompt_style: The prompt style used

        Returns:
            Cached judgment dict or None if not found
        """
        if not self.enabled:
            return None

        key = _compute_cache_key(model, prompt_style, question, response)
        index = self._load_index()

        entry = index.get(key)
        if entry:
            logger.debug(f"Cache hit: {key}")
            return entry.judgment

        return None

    def put(
        self,
        model: str,
        question: str,
        response: str,
        prompt_style: str,
        judgment: dict[str, Any],
    ) -> None:
        """
        Store a judgment in the cache.

        Args:
            model: Model identifier
            question: The question text
            response: The response text
            prompt_style: The prompt style used
            judgment: The judgment result to cache
        """
        if not self.enabled:
            return

        self._ensure_dir()

        question_hash = _hash_text(question)
        response_hash = _hash_text(response)
        key = _compute_cache_key(model, prompt_style, question, response)

        entry = CacheEntry(
            key=key,
            model=model,
            prompt_style=prompt_style,
            question_hash=question_hash,
            response_hash=response_hash,
            judgment=judgment,
            timestamp=datetime.now().isoformat(),
        )

        # Append to file
        try:
            with open(self.cache_file, "a", encoding="utf-8") as f:
                f.write(entry.to_json() + "\n")

            # Update in-memory index
            if self._index is not None:
                self._index[key] = entry

            logger.debug(f"Cached judgment: {key}")

        except OSError as e:
            logger.warning(f"Could not write to cache: {e}")

    def clear(self) -> int:
        """
        Clear all cached entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._load_index())
        self._index = {}

        if self.cache_file.exists():
            self.cache_file.unlink()

        logger.info(f"Cleared {count} cache entries")
        return count

    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        index = self._load_index()

        # Count by model
        by_model: dict[str, int] = {}
        by_prompt: dict[str, int] = {}

        for entry in index.values():
            by_model[entry.model] = by_model.get(entry.model, 0) + 1
            by_prompt[entry.prompt_style] = by_prompt.get(entry.prompt_style, 0) + 1

        file_size = self.cache_file.stat().st_size if self.cache_file.exists() else 0

        return {
            "total_entries": len(index),
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "by_model": by_model,
            "by_prompt_style": by_prompt,
            "cache_file": str(self.cache_file),
        }

    def __len__(self) -> int:
        """Return number of cached entries."""
        return len(self._load_index())

    def __contains__(self, key: str) -> bool:
        """Check if a key is in the cache."""
        return key in self._load_index()


# Global cache instance
_global_cache: JudgeCache | None = None


def get_cache(cache_dir: Path | str | None = None) -> JudgeCache:
    """
    Get the global cache instance.

    Args:
        cache_dir: Optional cache directory (only used on first call)

    Returns:
        The global JudgeCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = JudgeCache(cache_dir=cache_dir)
    return _global_cache


def set_cache(cache: JudgeCache) -> None:
    """Set the global cache instance."""
    global _global_cache
    _global_cache = cache


def reset_cache() -> None:
    """Reset global cache to reload on next access."""
    global _global_cache
    _global_cache = None
