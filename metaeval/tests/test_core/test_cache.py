"""Tests for the cache module."""

import json
import tempfile
from pathlib import Path

import pytest

from metaeval.core.cache import (
    CacheEntry,
    JudgeCache,
    _compute_cache_key,
    _hash_text,
    get_cache,
    reset_cache,
    set_cache,
)


class TestHashText:
    """Tests for _hash_text function."""

    def test_returns_16_char_hex(self):
        """Test that hash is 16 character hex string."""
        result = _hash_text("test string")
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic(self):
        """Test that same input gives same hash."""
        text = "What is systems engineering?"
        hash1 = _hash_text(text)
        hash2 = _hash_text(text)
        assert hash1 == hash2

    def test_different_inputs_different_hashes(self):
        """Test that different inputs give different hashes."""
        hash1 = _hash_text("input one")
        hash2 = _hash_text("input two")
        assert hash1 != hash2

    def test_handles_unicode(self):
        """Test that unicode is handled correctly."""
        result = _hash_text("こんにちは世界 🌍")
        assert len(result) == 16


class TestComputeCacheKey:
    """Tests for _compute_cache_key function."""

    def test_key_format(self):
        """Test cache key format."""
        key = _compute_cache_key(
            model="llama3.1:8b",
            prompt_style="multi_dimensional",
            question="What is SE?",
            response="SE is a discipline...",
        )
        assert key.startswith("llama3.1:8b_multi_dimensional_")
        parts = key.split("_")
        assert len(parts) == 4

    def test_same_inputs_same_key(self):
        """Test that same inputs produce same key."""
        kwargs = {
            "model": "gpt-4o",
            "prompt_style": "binary",
            "question": "Q1",
            "response": "R1",
        }
        key1 = _compute_cache_key(**kwargs)
        key2 = _compute_cache_key(**kwargs)
        assert key1 == key2

    def test_different_model_different_key(self):
        """Test that different model produces different key."""
        base = {
            "prompt_style": "binary",
            "question": "Q1",
            "response": "R1",
        }
        key1 = _compute_cache_key(model="gpt-4o", **base)
        key2 = _compute_cache_key(model="claude-3", **base)
        assert key1 != key2

    def test_different_prompt_style_different_key(self):
        """Test that different prompt style produces different key."""
        base = {
            "model": "gpt-4o",
            "question": "Q1",
            "response": "R1",
        }
        key1 = _compute_cache_key(prompt_style="binary", **base)
        key2 = _compute_cache_key(prompt_style="rubric", **base)
        assert key1 != key2


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_create_entry(self):
        """Test creating a cache entry."""
        entry = CacheEntry(
            key="test_key",
            model="llama3.1:8b",
            prompt_style="multi_dimensional",
            question_hash="abc123",
            response_hash="def456",
            judgment={"score": 85, "justification": "Good"},
            timestamp="2024-01-15T10:30:00",
        )
        assert entry.key == "test_key"
        assert entry.model == "llama3.1:8b"
        assert entry.judgment["score"] == 85

    def test_to_json(self):
        """Test JSON serialization."""
        entry = CacheEntry(
            key="test_key",
            model="test-model",
            prompt_style="binary",
            question_hash="q123",
            response_hash="r456",
            judgment={"score": 1},
            timestamp="2024-01-01T00:00:00",
        )
        json_str = entry.to_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["key"] == "test_key"
        assert data["model"] == "test-model"
        assert data["judgment"] == {"score": 1}

    def test_from_json(self):
        """Test JSON deserialization."""
        json_str = json.dumps({
            "key": "restored_key",
            "model": "restored-model",
            "prompt_style": "rubric",
            "question_hash": "qh",
            "response_hash": "rh",
            "judgment": {"total": 90},
            "timestamp": "2024-01-01T12:00:00",
        })

        entry = CacheEntry.from_json(json_str)
        assert entry.key == "restored_key"
        assert entry.model == "restored-model"
        assert entry.judgment["total"] == 90

    def test_roundtrip(self):
        """Test JSON roundtrip."""
        original = CacheEntry(
            key="roundtrip_key",
            model="test-model",
            prompt_style="chain_of_thought",
            question_hash="qqqq",
            response_hash="rrrr",
            judgment={"a": 1, "b": [1, 2, 3]},
            timestamp="2024-06-15T08:30:00",
        )

        json_str = original.to_json()
        restored = CacheEntry.from_json(json_str)

        assert restored.key == original.key
        assert restored.model == original.model
        assert restored.judgment == original.judgment


class TestJudgeCache:
    """Tests for JudgeCache class."""

    def test_init_creates_instance(self):
        """Test cache initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)
            assert cache.enabled is True
            assert cache.cache_dir == Path(tmpdir)

    def test_disabled_cache_returns_none(self):
        """Test that disabled cache always returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=False)

            # Put should be silently ignored
            cache.put("model", "q", "r", "style", {"score": 100})

            # Get should return None
            result = cache.get("model", "q", "r", "style")
            assert result is None

    def test_put_and_get(self):
        """Test storing and retrieving from cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            judgment = {"score": 85, "justification": "Well done"}
            cache.put(
                model="test-model",
                question="What is SE?",
                response="SE is a discipline",
                prompt_style="binary",
                judgment=judgment,
            )

            result = cache.get(
                model="test-model",
                question="What is SE?",
                response="SE is a discipline",
                prompt_style="binary",
            )

            assert result is not None
            assert result["score"] == 85
            assert result["justification"] == "Well done"

    def test_cache_miss(self):
        """Test cache miss returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            result = cache.get(
                model="nonexistent",
                question="q",
                response="r",
                prompt_style="s",
            )
            assert result is None

    def test_different_inputs_no_collision(self):
        """Test that different inputs don't collide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            cache.put("model", "question1", "response1", "style", {"id": 1})
            cache.put("model", "question2", "response2", "style", {"id": 2})

            result1 = cache.get("model", "question1", "response1", "style")
            result2 = cache.get("model", "question2", "response2", "style")

            assert result1["id"] == 1
            assert result2["id"] == 2

    def test_clear(self):
        """Test clearing the cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            cache.put("model", "q", "r", "style", {"score": 1})
            assert len(cache) == 1

            count = cache.clear()
            assert count == 1
            assert len(cache) == 0

            # Should not find the entry anymore
            result = cache.get("model", "q", "r", "style")
            assert result is None

    def test_stats(self):
        """Test cache statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            cache.put("model-a", "q1", "r1", "binary", {"s": 1})
            cache.put("model-a", "q2", "r2", "binary", {"s": 2})
            cache.put("model-b", "q1", "r1", "rubric", {"s": 3})

            stats = cache.stats()
            assert stats["total_entries"] == 3
            assert stats["by_model"]["model-a"] == 2
            assert stats["by_model"]["model-b"] == 1
            assert stats["by_prompt_style"]["binary"] == 2
            assert stats["by_prompt_style"]["rubric"] == 1

    def test_len(self):
        """Test __len__ method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            assert len(cache) == 0
            cache.put("m", "q", "r", "s", {"x": 1})
            assert len(cache) == 1
            cache.put("m", "q2", "r2", "s", {"x": 2})
            assert len(cache) == 2

    def test_contains(self):
        """Test __contains__ method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            cache.put("model", "question", "response", "style", {"x": 1})
            key = _compute_cache_key("model", "style", "question", "response")

            assert key in cache
            assert "nonexistent_key" not in cache

    def test_persistence(self):
        """Test that cache persists to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create cache and add entry
            cache1 = JudgeCache(cache_dir=tmpdir, enabled=True)
            cache1.put("model", "q", "r", "style", {"persisted": True})

            # Create new cache instance
            cache2 = JudgeCache(cache_dir=tmpdir, enabled=True)
            result = cache2.get("model", "q", "r", "style")

            assert result is not None
            assert result["persisted"] is True

    def test_jsonl_format(self):
        """Test that cache file is valid JSONL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            cache.put("m1", "q1", "r1", "s1", {"v": 1})
            cache.put("m2", "q2", "r2", "s2", {"v": 2})

            # Read and parse the file
            with open(cache.cache_file) as f:
                lines = f.readlines()

            assert len(lines) == 2

            for line in lines:
                data = json.loads(line.strip())
                assert "key" in data
                assert "model" in data
                assert "judgment" in data

    def test_handles_malformed_entries(self):
        """Test that malformed cache entries are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "judge_cache.jsonl"

            # Write some valid and invalid entries
            with open(cache_file, "w") as f:
                f.write('{"key":"k1","model":"m","prompt_style":"s","question_hash":"q","response_hash":"r","judgment":{"x":1},"timestamp":"t"}\n')
                f.write("invalid json line\n")
                f.write('{"key":"k2","model":"m","prompt_style":"s","question_hash":"q","response_hash":"r","judgment":{"x":2},"timestamp":"t"}\n')

            cache = JudgeCache(cache_dir=tmpdir, enabled=True)

            # Should have loaded 2 entries, skipping the invalid one
            assert len(cache) == 2


class TestGlobalCache:
    """Tests for global cache functions."""

    def setup_method(self):
        """Reset global cache before each test."""
        reset_cache()

    def test_get_cache_returns_same_instance(self):
        """Test that get_cache returns singleton."""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2

    def test_set_cache(self):
        """Test setting custom cache instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_cache = JudgeCache(cache_dir=tmpdir, enabled=True)
            set_cache(custom_cache)

            assert get_cache() is custom_cache

    def test_reset_cache(self):
        """Test resetting global cache."""
        cache1 = get_cache()
        reset_cache()
        cache2 = get_cache()

        # Should be different instances after reset
        assert cache1 is not cache2
