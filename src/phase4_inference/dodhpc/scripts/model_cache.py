#!/usr/bin/env python3
"""
Model cache manager for HPC environments.
Handles pre-pulling Ollama models and HuggingFace datasets on login nodes
for offline compute nodes.

Usage:
    python model_cache.py pull gemma3:4b llama3.2:3b
    python model_cache.py list
    python model_cache.py verify gemma3:4b
    python model_cache.py env
    python model_cache.py pull-hf rabell/SysEngBench
"""
import subprocess
import json
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ModelInfo:
    name: str
    size: str
    modified: str
    digest: str


class OllamaModelCache:
    def __init__(self, cache_dir: Optional[Path] = None):
        default_base = os.environ.get("PROJECT", str(Path.home()))
        self.cache_dir = cache_dir or Path(os.environ.get(
            "SHARED_MODELS",
            Path(default_base) / "shared_models" / "ollama"
        ))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.cache_dir / "model_manifest.json"

    def _set_env(self):
        """Set OLLAMA_MODELS to use shared cache."""
        os.environ["OLLAMA_MODELS"] = str(self.cache_dir)

    def _start_ollama(self) -> subprocess.Popen:
        """Start Ollama server temporarily."""
        self._set_env()
        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(10)  # Wait for server startup
        return proc

    def list_cached(self) -> List[ModelInfo]:
        """List models in cache."""
        self._set_env()
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True
        )
        models = []
        for line in result.stdout.strip().split("\n")[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    models.append(ModelInfo(
                        name=parts[0],
                        digest=parts[1],
                        size=parts[2],
                        modified=parts[3]
                    ))
        return models

    def pull_models(self, models: List[str], force: bool = False) -> dict:
        """
        Pull models to shared cache.
        Run this on LOGIN NODE (with internet).
        """
        proc = self._start_ollama()
        results = {"success": [], "failed": [], "skipped": []}

        try:
            cached = {m.name for m in self.list_cached()}

            for model in models:
                if model in cached and not force:
                    print(f"[SKIP] {model} already cached")
                    results["skipped"].append(model)
                    continue

                print(f"[PULL] {model}...")
                pull_result = subprocess.run(
                    ["ollama", "pull", model],
                    capture_output=True, text=True
                )
                if pull_result.returncode == 0:
                    print(f"[OK] {model}")
                    results["success"].append(model)
                else:
                    print(f"[FAIL] {model}: {pull_result.stderr}")
                    results["failed"].append(model)

            # Update manifest
            self._update_manifest()

        finally:
            proc.terminate()

        return results

    def _update_manifest(self):
        """Update manifest file with cached models."""
        models = self.list_cached()
        manifest = {
            "cache_dir": str(self.cache_dir),
            "models": [
                {"name": m.name, "size": m.size, "digest": m.digest}
                for m in models
            ]
        }
        self.manifest_file.write_text(json.dumps(manifest, indent=2))

    def verify_model(self, model: str) -> bool:
        """Check if model is available in cache."""
        cached = {m.name for m in self.list_cached()}
        # Handle tag variations (model:latest vs model)
        model_base = model.split(":")[0]
        return model in cached or f"{model_base}:latest" in cached

    def get_env_export(self) -> str:
        """Get export command for SBATCH scripts."""
        return f'export OLLAMA_MODELS="{self.cache_dir}"'


class HuggingFaceCache:
    """Manage HuggingFace dataset cache for offline compute nodes."""

    def __init__(self, cache_dir: Optional[Path] = None):
        default_base = os.environ.get("PROJECT", str(Path.home()))
        self.cache_dir = cache_dir or Path(os.environ.get(
            "HF_CACHE",
            Path(default_base) / "shared_models" / "huggingface"
        ))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _set_env(self):
        """Set HuggingFace cache environment variables."""
        os.environ["HF_HOME"] = str(self.cache_dir)
        os.environ["HF_DATASETS_CACHE"] = str(self.cache_dir / "datasets")
        os.environ["TRANSFORMERS_CACHE"] = str(self.cache_dir / "transformers")

    def pull_datasets(self, datasets: List[str]) -> dict:
        """
        Download datasets to cache.
        Run on LOGIN NODE (with internet).
        """
        self._set_env()
        results = {"success": [], "failed": []}

        try:
            from datasets import load_dataset
        except ImportError:
            print("[ERROR] datasets library not installed")
            print("[INFO] Install with: pip install datasets")
            return results

        for ds_name in datasets:
            print(f"[CACHE] {ds_name}...")
            try:
                load_dataset(ds_name, trust_remote_code=True)
                print(f"[OK] {ds_name}")
                results["success"].append(ds_name)
            except Exception as e:
                print(f"[FAIL] {ds_name}: {e}")
                results["failed"].append(ds_name)

        return results

    def list_cached(self) -> List[str]:
        """List cached datasets."""
        datasets_dir = self.cache_dir / "datasets"
        if not datasets_dir.exists():
            return []
        return [d.name for d in datasets_dir.iterdir() if d.is_dir()]

    def get_env_export(self) -> str:
        """Get export commands for SBATCH scripts."""
        return f'''export HF_HOME="{self.cache_dir}"
export HF_DATASETS_CACHE="{self.cache_dir}/datasets"
export HF_DATASETS_OFFLINE=1'''


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Manage model and dataset caches for HPC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s pull gemma3:4b llama3.2:3b     Pull Ollama models
  %(prog)s list                            List cached Ollama models
  %(prog)s verify gemma3:4b               Check if model is cached
  %(prog)s env                             Print environment exports
  %(prog)s pull-hf rabell/SysEngBench     Cache HuggingFace dataset
  %(prog)s list-hf                         List cached HF datasets
        """
    )
    parser.add_argument("command", choices=[
        "pull", "list", "verify", "env",
        "pull-hf", "list-hf", "env-hf"
    ])
    parser.add_argument("items", nargs="*", help="Models or datasets")
    parser.add_argument("--cache-dir", type=Path, help="Cache directory")
    parser.add_argument("--force", action="store_true", help="Re-pull existing")

    args = parser.parse_args()

    # Ollama commands
    if args.command in ["pull", "list", "verify", "env"]:
        cache = OllamaModelCache(args.cache_dir)

        if args.command == "pull":
            if not args.items:
                print("Error: specify models to pull")
                sys.exit(1)
            results = cache.pull_models(args.items, force=args.force)
            print(f"\nSummary: {len(results['success'])} pulled, "
                  f"{len(results['skipped'])} skipped, {len(results['failed'])} failed")

        elif args.command == "list":
            models = cache.list_cached()
            if models:
                print(f"{'NAME':<40} {'SIZE':<10} {'DIGEST':<15}")
                print("-" * 65)
                for m in models:
                    print(f"{m.name:<40} {m.size:<10} {m.digest:<15}")
            else:
                print("No models cached")

        elif args.command == "verify":
            for model in args.items:
                status = "OK" if cache.verify_model(model) else "MISSING"
                print(f"{model}: {status}")

        elif args.command == "env":
            print(cache.get_env_export())

    # HuggingFace commands
    elif args.command in ["pull-hf", "list-hf", "env-hf"]:
        cache = HuggingFaceCache(args.cache_dir)

        if args.command == "pull-hf":
            if not args.items:
                print("Error: specify datasets to pull")
                sys.exit(1)
            results = cache.pull_datasets(args.items)
            print(f"\nSummary: {len(results['success'])} cached, "
                  f"{len(results['failed'])} failed")

        elif args.command == "list-hf":
            datasets = cache.list_cached()
            if datasets:
                print("Cached datasets:")
                for ds in datasets:
                    print(f"  {ds}")
            else:
                print("No datasets cached")

        elif args.command == "env-hf":
            print(cache.get_env_export())


if __name__ == "__main__":
    main()
