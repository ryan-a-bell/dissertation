#!/bin/bash
# Set up Python virtual environment for LM-Eval + Ollama
# Run on LOGIN NODE (requires internet)
#
# Usage: ./setup_venv.sh [VENV_DIR]
# Example: ./setup_venv.sh $HOME/hpc_lm_eval/venv

set -euo pipefail

VENV_DIR="${1:-$HOME/hpc_lm_eval/venv}"

echo "=========================================="
echo "LM-Eval Virtual Environment Setup"
echo "=========================================="
echo "[INFO] Target directory: $VENV_DIR"
echo ""

# Check if venv already exists
if [[ -d "$VENV_DIR" ]]; then
    echo "[WARN] Directory already exists: $VENV_DIR"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "[INFO] Aborted."
        exit 0
    fi
    rm -rf "$VENV_DIR"
fi

# Load required modules (adjust for your HPC)
echo "[INFO] Loading modules..."
if command -v module &>/dev/null; then
    module load python/3.11 2>/dev/null || module load python3 2>/dev/null || true
    module load cuda/12.4 2>/dev/null || module load cuda 2>/dev/null || true
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "[INFO] Python: $PYTHON_VERSION"

# Create venv
echo "[INFO] Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "[INFO] Upgrading pip..."
pip install --upgrade pip

# Install packages
echo "[INFO] Installing lm_eval and ollama..."
pip install "lm_eval[api]" ollama==0.3.3

# Install Ollama binary to user space
echo "[INFO] Installing Ollama binary..."
OLLAMA_DIR="$VENV_DIR/ollama"
mkdir -p "$OLLAMA_DIR"
curl -fsSL https://ollama.com/install.sh | OLLAMA_INSTALL_DIR="$OLLAMA_DIR" sh

# Create activation script with PATH
cat > "$VENV_DIR/activate_lm_eval" << EOF
#!/bin/bash
# Activate LM-Eval environment
source "$VENV_DIR/bin/activate"
export PATH="$OLLAMA_DIR/bin:\$PATH"
export OLLAMA_MODELS="\${OLLAMA_MODELS:-\${PROJECT:-\$HOME}/shared_models/ollama}"
export HF_HOME="\${HF_HOME:-\${PROJECT:-\$HOME}/shared_models/huggingface}"
echo "[INFO] LM-Eval environment activated"
echo "[INFO] OLLAMA_MODELS=\$OLLAMA_MODELS"
echo "[INFO] HF_HOME=\$HF_HOME"
EOF
chmod +x "$VENV_DIR/activate_lm_eval"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the environment:"
echo "  source $VENV_DIR/activate_lm_eval"
echo ""
echo "To verify installation:"
echo "  ollama --version"
echo "  lm_eval --help"
echo ""
echo "Ollama binary: $OLLAMA_DIR/bin/ollama"
