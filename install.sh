#!/usr/bin/env bash
set -euo pipefail

DAN_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$DAN_DIR/.venv"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/dan"
LOCAL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/dan"

print_bold() { printf "\033[1m%s\033[0m\n" "$*"; }
print_green() { printf "\033[32m%s\033[0m\n" "$*"; }
print_red() { printf "\033[31m%s\033[0m\n" "$*"; }

print_bold "D.A.N. Installer"
echo

# Check Python version
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PY_VER=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)
        if [[ -n "$PY_VER" ]]; then
            IFS='.' read -r major minor <<< "$PY_VER"
            if (( major > 3 || (major == 3 && minor >= 11) )); then
                PYTHON="$cmd"
                break
            fi
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    print_red "Error: Python >= 3.11 is required."
    exit 1
fi
print_green "✓ Found $($PYTHON --version 2>&1)"

# Check for uv (preferred) or pip
INSTALL_CMD=""
if command -v uv &>/dev/null; then
    INSTALL_CMD="uv"
    print_green "✓ Found uv (uv)"
elif command -v pip3 &>/dev/null; then
    INSTALL_CMD="pip3"
    print_green "✓ Found pip3 (slower)"
else
    print_red "Error: Neither uv nor pip3 found. Install uv (https://docs.astral.sh/uv) or python3-pip."
    exit 1
fi

# Create virtual environment
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    print_bold "Creating virtual environment..."
    if [[ "$INSTALL_CMD" == "uv" ]]; then
        uv venv "$VENV_DIR"
    else
        $PYTHON -m venv "$VENV_DIR"
    fi
    print_green "✓ Virtual environment created at $VENV_DIR"
else
    print_green "✓ Virtual environment already exists"
fi

# Determine activation command for subsequent pip/uv calls
if [[ "$INSTALL_CMD" == "uv" ]]; then
    PIP_CMD="uv pip"
    SYNC_CMD="uv sync"
else
    PIP_CMD="$VENV_DIR/bin/pip3"
    SYNC_CMD=""
fi

# Install D.A.N. and core dependencies
print_bold "Installing D.A.N. and dependencies..."
if [[ -n "$SYNC_CMD" ]]; then
    # uv sync installs from uv.lock, much faster
    (cd "$DAN_DIR" && $SYNC_CMD)
else
    $PIP_CMD install -e "$DAN_DIR"
fi
print_green "✓ Core dependencies installed"

# Optional dependency groups
install_optional() {
    local label="$1" group="$2"
    local answer
    printf "Install %s? [y/N] " "$label"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        print_bold "Installing $label..."
        if [[ "$INSTALL_CMD" == "uv" ]]; then
            uv sync --group "$group"
        else
            $PIP_CMD install -e "$DAN_DIR[$group]"
        fi
        print_green "✓ $label installed"
    fi
}

install_optional "LLM support (ollama)" "llm"
install_optional "Browser automation (playwright)" "browser"
install_optional "GUI support (PyQt6)" "gui"

# Install Playwright browsers if browser support was requested
if [[ -d "$VENV_DIR/lib" ]]; then
    PW_BIN="$VENV_DIR/bin/playwright"
    if [[ -f "$PW_BIN" ]] && ! $PW_BIN install --dry-run &>/dev/null; then
        print_bold "Installing Playwright browsers..."
        $PW_BIN install chromium
        print_green "✓ Playwright browsers installed"
    fi
fi

# Create config directory and default config if not present
if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
    print_bold "Creating default configuration at $CONFIG_DIR/config.yaml..."
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_DIR/config.yaml" << CONF
core:
  threshold: 0.5
  log_level: warning

interpret:
  name: ollama
  provider: ollama
  model: llama3.2
  device: cpu

reason:
  name: ollama
  provider: ollama
  model: llama3.2
  device: cpu

persona:
  name: ollama
  provider: ollama
  model: llama3.2
  device: cpu

memory:
  short_term_limit: 10
  long_term_path: $LOCAL_DIR/memory

skills:
  store_path: $HOME/.config/dan/skills.json
  min_executions: 3
  min_confidence: 0.7
CONF
    print_green "✓ Default config created"
else
    print_green "✓ Config already exists at $CONFIG_DIR/config.yaml"
fi

# Generate desktop entry from template
DESKTOP_TEMPLATE="$DAN_DIR/assets/dan.desktop.in"
DESKTOP_OUT="$CONFIG_DIR/dan.desktop"
if [[ -f "$DESKTOP_TEMPLATE" ]]; then
    print_bold "Generating desktop entry..."
    mkdir -p "$CONFIG_DIR"
    sed \
        -e "s|@VENV_BIN@|$VENV_DIR/bin|g" \
        -e "s|@DAN_DIR@|$DAN_DIR|g" \
        "$DESKTOP_TEMPLATE" > "$DESKTOP_OUT"
    print_green "✓ Desktop entry created at $DESKTOP_OUT"
    echo "  Install system-wide with:"
    echo "    cp $DESKTOP_OUT ~/.local/share/applications/dan.desktop"
    echo "    update-desktop-database ~/.local/share/applications"
fi

echo
print_bold "Installation complete!"
echo
print_green "  Activate:  source $VENV_DIR/bin/activate"
print_green "  Run CLI:   dan <command>"
print_green "  Run GUI:   dan-gui"
echo
print_bold "Before using, make sure Ollama is running:"
echo "  ollama serve"
echo
print_bold "Optional — install Ollama models:"
echo "  ollama pull llama3.2"
echo

# Install dev dependencies if wanted
install_optional "Development tools (pytest, ruff, mypy)" "dev"
