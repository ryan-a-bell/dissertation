    #!/bin/bash
    #SBATCH --job-name=lm_eval_multi_model
    #SBATCH --partition=gpu              # TODO: set your GPU partition
    #SBATCH --gres=gpu:1
    #SBATCH --cpus-per-task=4
    #SBATCH --mem=24G
    #SBATCH --time=08:00:00
    #SBATCH --output=logs/%x-%j.out

    # Usage:
    #   sbatch eval_lm_multi_model_single_task.sbatch TASK TASKS_DIR MODEL_LIST_FILE OUTPUT_ROOT

    set -euo pipefail

    TASK="$1"
    TASKS_DIR="$2"
    MODEL_LIST_FILE="$3"
    OUTPUT_ROOT="$4"

    TASKS_DIR="$(readlink -f "$TASKS_DIR")"
    MODEL_LIST_FILE="$(readlink -f "$MODEL_LIST_FILE")"
    OUTPUT_ROOT="$(readlink -f "$OUTPUT_ROOT")"

    CONTAINER_IMAGE="$HOME/hpc_lm_eval/containers/lm_eval_ollama.sif"

    mkdir -p logs

    SCRATCH_DIR="${SLURM_TMPDIR:-/tmp/lm_multi_model_${SLURM_JOB_ID}}"
    mkdir -p "$SCRATCH_DIR"
    cd "$SCRATCH_DIR"

    echo "[INFO] Running multi-model LM-Eval for TASK=$TASK"
    echo "[INFO] Model list file: $MODEL_LIST_FILE"
    echo "[INFO] Scratch dir: $SCRATCH_DIR"

    # Detect Apptainer/Singularity
if command -v apptainer &>/dev/null; then
  CNT=apptainer
elif command -v singularity &>/dev/null; then
  CNT=singularity
else
  echo "[ERROR] Neither apptainer nor singularity found in PATH." >&2
  exit 1
fi


    export TASK TASKS_DIR MODEL_LIST_FILE OUTPUT_ROOT

    $CNT exec --nv "$CONTAINER_IMAGE" bash -lc '
      set -e

      echo "[INFO] Inside container. TASK=${TASK}"
      mkdir -p tasks output

      echo "[INFO] Copying task YAML..."
      cp "${TASKS_DIR}/${TASK}.yaml" tasks/

      echo "[INFO] Starting Ollama server..."
      nohup env OLLAMA_HOST=0.0.0.0 ollama serve > ollama.log 2>&1 &
      OLLAMA_PID=$!

      sleep 15

      echo "[INFO] Beginning model loop..."
      while read -r MODEL; do
        [ -z "$MODEL" ] && continue
        echo "----"
        echo "[INFO] Pulling model: $MODEL"
        ollama pull "$MODEL"

        SAFE_MODEL="${MODEL//\//_}"
        OUTDIR="output/${SAFE_MODEL}/${TASK}"
        mkdir -p "$OUTDIR"

        echo "[INFO] Running lm_eval for MODEL=$MODEL TASK=${TASK}"
        lm_eval \
          --model local-chat-completions \
          --model_args "model=$MODEL,base_url=http://localhost:11434/v1/chat/completions,num_concurrent=1" \
          --include_path ./tasks \
          --tasks "${TASK}" \
          --output "$OUTDIR" \
          --log_samples \
          --num_fewshot 0 \
          --batch_size auto \
          --gen_kwargs temperature=0.0 \
          --apply_chat_template

      done < "${MODEL_LIST_FILE}"

      echo "[INFO] All models processed."
      kill $OLLAMA_PID 2>/dev/null || true
    '

    if [ -d "${SCRATCH_DIR}/output" ]; then
      cp -r "${SCRATCH_DIR}/output/." "$OUTPUT_ROOT/"
      echo "[INFO] Copied all model results to: $OUTPUT_ROOT"
    else
      echo "[WARN] No output directory found at ${SCRATCH_DIR}/output"
    fi

    echo "[INFO] Done for TASK=$TASK (multi-model)"
