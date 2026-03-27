#!/bin/bash
# Pre-pull Ollama models to shared cache
# Run on LOGIN NODE before submitting jobs (requires internet)
#
# Usage: ./prepull_models.sh model1 model2 model3 ...
# Example: ./prepull_models.sh gemma3:4b llama3.2:3b mistral:7b

set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 model1 [model2 ...]"
    echo ""
    echo "Examples:"
    echo "  $0 gemma3:4b llama3.2:3b mistral:7b"
    echo "  $0 gemma3:1b gemma3:4b gemma3:12b"
    echo ""
    echo "Common models:"
    echo "  gemma3:1b, gemma3:4b, gemma3:12b, gemma3:27b"
    echo "  llama3.2:3b, llama3.3:70b-instruct-q4_K_M"
    echo "  mistral:7b, mixtral:8x7b"
    echo "  phi4:14b"
    exit 1
fi

# Shared model cache location (adjust for your HPC)
SHARED_MODELS="${SHARED_MODELS:-${PROJECT:-$HOME}/shared_models/ollama}"

echo "=========================================="
echo "Ollama Model Pre-Pull"
echo "=========================================="
echo "[INFO] Model cache: $SHARED_MODELS"
echo "[INFO] Models to pull: $*"
echo ""

mkdir -p "$SHARED_MODELS"

# Point Ollama to shared cache
export OLLAMA_MODELS="$SHARED_MODELS"

# Check if Ollama is installed
if ! command -v ollama &>/dev/null; then
    echo "[ERROR] Ollama not found in PATH"
    echo "[INFO] Install with: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

# Start Ollama temporarily
echo "[INFO] Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!
sleep 10

# Trap to ensure cleanup
trap "kill $OLLAMA_PID 2>/dev/null || true" EXIT

SUCCESS=0
FAILED=0

# Pull each model
for MODEL in "$@"; do
    echo ""
    echo "[PULL] $MODEL"
    if ollama pull "$MODEL"; then
        echo "[OK] $MODEL cached successfully"
        ((SUCCESS++))
    else
        echo "[ERROR] Failed to pull $MODEL"
        ((FAILED++))
    fi
done

# Record what's cached
echo ""
echo "[INFO] Updating model manifest..."
ollama list > "$SHARED_MODELS/model_manifest.txt"

echo ""
echo "=========================================="
echo "Pre-pull Complete"
echo "=========================================="
echo "[INFO] Success: $SUCCESS, Failed: $FAILED"
echo "[INFO] Cached models:"
cat "$SHARED_MODELS/model_manifest.txt"
echo ""
echo "[INFO] Cache location: $SHARED_MODELS"
echo "[INFO] Set this in your jobs: export OLLAMA_MODELS=$SHARED_MODELS"
