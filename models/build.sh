#!/bin/bash
# Build custom D.A.N. Ollama models
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Building dan-interp (intent classifier, qwen3.5:0.8b)..."
ollama create dan-interp -f "$SCRIPT_DIR/Modelfile.interp"

echo "Building dan-reason (tool router, qwen3.5:2b)..."
ollama create dan-reason -f "$SCRIPT_DIR/Modelfile.reason"

echo "Building dan-persona (personality layer, qwen3.5:2b)..."
ollama create dan-persona -f "$SCRIPT_DIR/Modelfile.persona"

echo "Done! Models created:"
ollama list | grep dan-
