#!/bin/bash
# Pre-download HuggingFace datasets to shared cache
# Run on LOGIN NODE before submitting jobs (requires internet)
#
# Usage: ./cache_hf_datasets.sh [dataset1 dataset2 ...]
# Example: ./cache_hf_datasets.sh rabell/SysEngBench rabell/SysEngBench-OSQ

set -euo pipefail

# Default datasets for SysEngBench evaluation
DEFAULT_DATASETS=(
    "rabell/SysEngBench"
    "rabell/SysEngBench-OSQ"
)

# Use provided datasets or defaults
if [[ $# -gt 0 ]]; then
    DATASETS=("$@")
else
    DATASETS=("${DEFAULT_DATASETS[@]}")
fi

# Shared HuggingFace cache location
HF_CACHE="${HF_CACHE:-${PROJECT:-$HOME}/shared_models/huggingface}"

echo "=========================================="
echo "HuggingFace Dataset Cache"
echo "=========================================="
echo "[INFO] Cache location: $HF_CACHE"
echo "[INFO] Datasets to cache: ${DATASETS[*]}"
echo ""

mkdir -p "$HF_CACHE"

# Set environment
export HF_HOME="$HF_CACHE"
export HF_DATASETS_CACHE="$HF_CACHE/datasets"
export TRANSFORMERS_CACHE="$HF_CACHE/transformers"

# Python script to download datasets
python3 << PYEOF
import os
import sys

# Ensure cache dirs are set
os.environ["HF_HOME"] = "$HF_CACHE"
os.environ["HF_DATASETS_CACHE"] = "$HF_CACHE/datasets"

try:
    from datasets import load_dataset
except ImportError:
    print("[ERROR] datasets library not installed")
    print("[INFO] Install with: pip install datasets")
    sys.exit(1)

datasets = [$(printf '"%s",' "${DATASETS[@]}" | sed 's/,$//')]
success = 0
failed = 0

for ds_name in datasets:
    print(f"[CACHE] {ds_name}...")
    try:
        ds = load_dataset(ds_name, trust_remote_code=True)
        print(f"[OK] {ds_name} - {len(ds)} splits cached")
        success += 1
    except Exception as e:
        print(f"[FAIL] {ds_name}: {e}")
        failed += 1

print()
print(f"Summary: {success} cached, {failed} failed")
PYEOF

echo ""
echo "=========================================="
echo "Cache Complete"
echo "=========================================="
echo "[INFO] Cache location: $HF_CACHE"
echo ""
echo "Set these in your jobs:"
echo "  export HF_HOME=$HF_CACHE"
echo "  export HF_DATASETS_CACHE=$HF_CACHE/datasets"
echo "  export HF_DATASETS_OFFLINE=1"
