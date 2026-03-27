#!/bin/bash
# Build LM-Eval + Ollama container for specified CUDA version
#
# Usage:
#   ./build_container.sh [CUDA_VERSION]
#
# Examples:
#   ./build_container.sh 12.4     # CUDA 12.4 (recommended for most modern HPCs)
#   ./build_container.sh 12.1     # CUDA 12.1
#   ./build_container.sh 11.8     # CUDA 11.8 (older systems)
#   ./build_container.sh 12.8     # CUDA 12.8 (latest)
#   ./build_container.sh          # Defaults to 12.4
#
# The script will:
#   1. Generate a .def file from the template
#   2. Build the Apptainer/Singularity container
#   3. Name the output file with CUDA version for clarity

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUDA_VERSION="${1:-12.4}"

echo "=============================================="
echo "Building LM-Eval container for CUDA ${CUDA_VERSION}"
echo "=============================================="

# Map CUDA versions to base images
# Using NVIDIA's official PyTorch images for reliability
declare -A BASE_IMAGES=(
    # CUDA 11.x series (older HPC systems)
    ["11.7"]="nvcr.io/nvidia/pytorch:23.04-py3"      # CUDA 11.7
    ["11.8"]="nvcr.io/nvidia/pytorch:23.10-py3"      # CUDA 11.8

    # CUDA 12.x series (modern HPC systems)
    ["12.1"]="nvcr.io/nvidia/pytorch:24.01-py3"      # CUDA 12.1
    ["12.2"]="nvcr.io/nvidia/pytorch:24.05-py3"      # CUDA 12.2
    ["12.4"]="nvcr.io/nvidia/pytorch:24.07-py3"      # CUDA 12.4
    ["12.6"]="nvcr.io/nvidia/pytorch:24.09-py3"      # CUDA 12.6
    ["12.8"]="runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04"  # CUDA 12.8
)

# Alternative: Use plain CUDA images (smaller, no PyTorch overhead)
declare -A CUDA_IMAGES=(
    ["11.7"]="nvidia/cuda:11.7.1-cudnn8-devel-ubuntu22.04"
    ["11.8"]="nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04"
    ["12.1"]="nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04"
    ["12.2"]="nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04"
    ["12.4"]="nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04"
    ["12.6"]="nvidia/cuda:12.6.0-cudnn-devel-ubuntu22.04"
)

# Check if version is supported
if [[ -z "${BASE_IMAGES[$CUDA_VERSION]:-}" ]]; then
    echo "[ERROR] Unsupported CUDA version: $CUDA_VERSION"
    echo ""
    echo "Supported versions:"
    printf '  %s\n' "${!BASE_IMAGES[@]}" | sort
    echo ""
    echo "To add a new version, edit BASE_IMAGES in this script."
    exit 1
fi

BASE_IMAGE="${BASE_IMAGES[$CUDA_VERSION]}"

echo "[INFO] CUDA version: $CUDA_VERSION"
echo "[INFO] Base image: $BASE_IMAGE"

# Generate .def file from template
TEMPLATE_FILE="${SCRIPT_DIR}/lm_eval_ollama.def.template"
DEF_FILE="${SCRIPT_DIR}/lm_eval_ollama_cuda${CUDA_VERSION}.def"

if [[ ! -f "$TEMPLATE_FILE" ]]; then
    # Fall back to direct .def if template doesn't exist
    echo "[WARN] Template not found, using direct definition"
    DEF_FILE="${SCRIPT_DIR}/lm_eval_ollama.def"
else
    echo "[INFO] Generating definition file: $DEF_FILE"
    sed -e "s|{{BASE_IMAGE}}|${BASE_IMAGE}|g" \
        -e "s|{{CUDA_VERSION}}|${CUDA_VERSION}|g" \
        "$TEMPLATE_FILE" > "$DEF_FILE"
fi

# Output container name includes CUDA version
OUTPUT_SIF="${SCRIPT_DIR}/lm_eval_ollama_cuda${CUDA_VERSION}.sif"

# Also create a symlink to "default" container
DEFAULT_SIF="${SCRIPT_DIR}/lm_eval_ollama.sif"

# Detect container runtime
if command -v apptainer &>/dev/null; then
    BUILDER=apptainer
elif command -v singularity &>/dev/null; then
    BUILDER=singularity
else
    echo "[ERROR] Neither apptainer nor singularity found in PATH"
    echo ""
    echo "Install Apptainer: https://apptainer.org/docs/admin/main/installation.html"
    exit 1
fi

echo "[INFO] Using builder: $BUILDER"
echo "[INFO] Output file: $OUTPUT_SIF"
echo ""

# Build the container
echo "[INFO] Building container (this may take 10-20 minutes)..."
$BUILDER build --fakeroot "$OUTPUT_SIF" "$DEF_FILE"

# Create/update symlink to default
ln -sf "$(basename "$OUTPUT_SIF")" "$DEFAULT_SIF"
echo "[INFO] Updated default symlink: $DEFAULT_SIF -> $(basename "$OUTPUT_SIF")"

echo ""
echo "=============================================="
echo "Build complete!"
echo "=============================================="
echo ""
echo "Container: $OUTPUT_SIF"
echo "CUDA:      $CUDA_VERSION"
echo "Size:      $(du -h "$OUTPUT_SIF" | cut -f1)"
echo ""
echo "Test with:"
echo "  $BUILDER exec --nv $OUTPUT_SIF nvidia-smi"
echo "  $BUILDER exec --nv $OUTPUT_SIF ollama --version"
echo "  $BUILDER exec --nv $OUTPUT_SIF lm_eval --help"
