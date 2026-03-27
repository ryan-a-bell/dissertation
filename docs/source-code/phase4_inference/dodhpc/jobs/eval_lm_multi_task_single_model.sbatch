    #!/bin/bash
    #SBATCH --job-name=lm_eval_multi_task
    #SBATCH --partition=gpu              # TODO: set your GPU partition
    #SBATCH --gres=gpu:1
    #SBATCH --cpus-per-task=4
    #SBATCH --mem=24G
    #SBATCH --time=08:00:00
    #SBATCH --output=logs/%x-%j.out

    # Usage:
    #   sbatch eval_lm_multi_task_single_model.sbatch MODEL TASKS_DIR TASK_LIST_FILE OUTPUT_ROOT

    set -euo pipefail

    MODEL="$1"
    TASKS_DIR="$2"
    TASK_LIST_FILE="$3"
    OUTPUT_ROOT="$4"

    TASKS_DIR="$(readlink -f "$TASKS_DIR")"
    TASK_LIST_FILE="$(readlink -f "$TASK_LIST_FILE")"
    OUTPUT_ROOT="$(readlink -f "$OUTPUT_ROOT")"

    CONTAINER_IMAGE="$HOME/hpc_lm_eval/containers/lm_eval_ollama.sif"

    mkdir -p logs

    SCRATCH_DIR="${SLURM_TMPDIR:-/tmp/lm_multi_task_${SLURM_JOB_ID}}"
    mkdir -p "$SCRATCH_DIR"
    cd "$SCRATCH_DIR"

    echo "[INFO] Running multi-task LM-Eval for MODEL=$MODEL"
    echo "[INFO] Tasks list file: $TASK_LIST_FILE"
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


    export MODEL TASKS_DIR TASK_LIST_FILE OUTPUT_ROOT

    $CNT exec --nv "$CONTAINER_IMAGE" bash -lc '
      set -e

      echo "[INFO] Inside container. MODEL=${MODEL}"
      mkdir -p tasks output

      echo "[INFO] Starting Ollama server..."
      nohup env OLLAMA_HOST=0.0.0.0 ollama serve > ollama.log 2>&1 &
      OLLAMA_PID=$!

      sleep 15

      echo "[INFO] Pulling model: ${MODEL}"
      ollama pull "${MODEL}"

      echo "[INFO] Beginning task loop..."
      while read -r TASK; do
        [ -z "$TASK" ] && continue
        echo "----"
        echo "[INFO] Running TASK=$TASK"
        cp "${TASKS_DIR}/${TASK}.yaml" tasks/

        lm_eval \
          --model local-chat-completions \
          --model_args "model=${MODEL},base_url=http://localhost:11434/v1/chat/completions,num_concurrent=1" \
          --include_path ./tasks \
          --tasks "$TASK" \
          --output "output/$TASK" \
          --log_samples \
          --num_fewshot 0 \
          --batch_size auto \
          --gen_kwargs temperature=0.0 \
          --apply_chat_template

      done < "${TASK_LIST_FILE}"

      echo "[INFO] All tasks processed."
      kill $OLLAMA_PID 2>/dev/null || true
    '

    DEST_ROOT="${OUTPUT_ROOT}/${MODEL//\//_}"
    mkdir -p "$DEST_ROOT"

    if [ -d "${SCRATCH_DIR}/output" ]; then
      cp -r "${SCRATCH_DIR}/output/." "$DEST_ROOT/"
      echo "[INFO] Copied all task results to: $DEST_ROOT"
    else
      echo "[WARN] No output directory found at ${SCRATCH_DIR}/output"
    fi

    echo "[INFO] Done for MODEL=$MODEL (multi-task)"
