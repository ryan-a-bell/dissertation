#!/usr/bin/env ruby
# Returns JSON with environment status for the OOD form
#
# Usage: ./check_status.rb
# Output: JSON with container status, cached models, network mode

require 'json'

base_dir = File.expand_path("~/hpc_lm_eval")
container_dir = "#{base_dir}/containers"
shared_models = ENV['SHARED_MODELS'] || "#{ENV['PROJECT'] || ENV['HOME']}/shared_models/ollama"
hf_cache = ENV['HF_CACHE'] || "#{ENV['PROJECT'] || ENV['HOME']}/shared_models/huggingface"

status = {
  container_exists: false,
  container_cuda_version: nil,
  cached_models: [],
  hf_datasets_cached: [],
  network_mode: 'unknown',
  setup_complete: false
}

# Check container
container_files = Dir.glob("#{container_dir}/lm_eval_ollama*.sif")
if container_files.any?
  status[:container_exists] = true
  # Extract CUDA version from filename
  if match = container_files.first.match(/cuda(\d+\.\d+)/)
    status[:container_cuda_version] = match[1]
  end
end

# Check cached Ollama models
manifest_file = "#{shared_models}/model_manifest.txt"
if File.exist?(manifest_file)
  status[:cached_models] = File.readlines(manifest_file)
    .drop(1)  # Skip header
    .map { |line| line.split.first }
    .compact
end

# Check cached HuggingFace datasets
hf_datasets_dir = "#{hf_cache}/datasets"
if Dir.exist?(hf_datasets_dir)
  status[:hf_datasets_cached] = Dir.glob("#{hf_datasets_dir}/*")
    .select { |f| File.directory?(f) }
    .map { |f| File.basename(f) }
end

# Detect network mode (simplified check)
status[:network_mode] = system("ping -c 1 -W 2 ollama.ai > /dev/null 2>&1") ? 'online' : 'offline'

# Setup complete if container exists and at least one model cached
status[:setup_complete] = status[:container_exists] && status[:cached_models].any?

puts JSON.pretty_generate(status)
