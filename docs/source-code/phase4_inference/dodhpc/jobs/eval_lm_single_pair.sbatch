    #!/bin/bash
    #SBATCH --job-name=lm_eval_single
    #SBATCH --partition=gpu              # TODO: set your GPU partition
    #SBATCH --gres=gpu:1                 # 1 GPU per job
    #SBATCH --cpus-per-task=4
    #SBATCH --mem=16G
    #SBATCH --time=04:00:00
    #SBATCH --output=logs/%x-%j.out

    # Usage:
    #   sbatch eval_lm_single_pair.sbatch MODEL TASK TASKS_DIR OUTPUT_ROOT
    #
    # Example:
    #   sbatch eval_lm_single_pair.sbatch mistral:7b sysengbench-a $HOME/hpc_lm_eval/tasks $HOME/hpc_lm_eval/output

    set -euo pipefail

    MODEL="$1"
    TASK="$2"
    TASKS_DIR="$3"
    OUTPUT_ROOT="$4"

    TASKS_DIR="$(readlink -f "$TASKS_DIR")"
    OUTPUT_ROOT="$(readlink -f "$OUTPUT_ROOT")"

    CONTAINER_IMAGE="$HOME/hpc_lm_eval/containers/lm_eval_ollama.sif"

    mkdir -p logs

    SCRATCH_DIR="${SLURM_TMPDIR:-/tmp/lm_${SLURM_JOB_ID}}"
    mkdir -p "$SCRATCH_DIR"
    cd "$SCRATCH_DIR"

    echo "[INFO] Running single-pair LM-Eval: MODEL=$MODEL TASK=$TASK"
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


    export MODEL TASK TASKS_DIR OUTPUT_ROOT

    $CNT exec --nv "$CONTAINER_IMAGE" bash -lc '
      set -e

      echo "[INFO] Inside container. MODEL=${MODEL} TASK=${TASK}"

      mkdir -p tasks output

      echo "[INFO] Copying task YAML..."
      cp "${TASKS_DIR}/${TASK}.yaml" tasks/

      echo "[INFO] Starting Ollama server..."
      nohup env OLLAMA_HOST=0.0.0.0 ollama serve > ollama.log 2>&1 &
      OLLAMA_PID=$!

      sleep 15

      echo "[INFO] Pulling model: ${MODEL}"
      ollama pull "${MODEL}"

      echo "[INFO] Running lm_eval..."
      lm_eval \
        --model local-chat-completions \
        --model_args "model=${MODEL},base_url=http://localhost:11434/v1/chat/completions,num_concurrent=1" \
        --include_path ./tasks \
        --tasks "${TASK}" \
        --output "output/${TASK}" \
        --log_samples \
        --num_fewshot 0 \
        --batch_size auto \
        --gen_kwargs temperature=0.0 \
        --apply_chat_template

      echo "[INFO] lm_eval completed."

      kill $OLLAMA_PID 2>/dev/null || true
    '

    DEST_DIR="${OUTPUT_ROOT}/${MODEL//\//_}/${TASK}"
    mkdir -p "$DEST_DIR"

    if [ -d "${SCRATCH_DIR}/output/${TASK}" ]; then
      cp -r "${SCRATCH_DIR}/output/${TASK}/." "$DEST_DIR/"
      echo "[INFO] Copied results to: $DEST_DIR"
    else
      echo "[WARN] No output directory found at ${SCRATCH_DIR}/output/${TASK}"
    fi

    echo "[INFO] Done for MODEL=$MODEL TASK=$TASK"
