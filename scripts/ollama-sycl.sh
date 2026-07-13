#!/bin/bash
# Start Ollama with Intel SYCL GPU support for Arc Graphics
OLLAMA_DIR="$HOME/ollama-sycl"
export LD_LIBRARY_PATH="$OLLAMA_DIR/lib/ollama:$LD_LIBRARY_PATH"
export OLLAMA_FLASH_ATTENTION=0

exec "$OLLAMA_DIR/bin/ollama" serve
