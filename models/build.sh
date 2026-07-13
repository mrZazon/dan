#!/bin/bash
# Build custom D.A.N. Ollama models
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Building dan-interp (intent classifier, qwen3.5:0.8b)..."
ollama create dan-interp -f "$SCRIPT_DIR/Modelfile.interp"

echo "Building dan-reason (reasoning assistant, qwen3.5:2b)..."
ollama create dan-reason -f "$SCRIPT_DIR/Modelfile.reason"

echo "Done! Models created:"
ollama list | grep dan-
