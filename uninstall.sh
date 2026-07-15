#!/usr/bin/env bash
set -euo pipefail

DAN_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$DAN_DIR/.venv"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/dan"
LOCAL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/dan"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/dan"

print_bold() { printf "\033[1m%s\033[0m\n" "$*"; }
print_green() { printf "\033[32m%s\033[0m\n" "$*"; }
print_red() { printf "\033[31m%s\033[0m\n" "$*"; }
print_warn() { printf "\033[33m%s\033[0m\n" "$*"; }

print_bold "D.A.N. Uninstaller"
echo

# Confirm
print_warn "This will remove D.A.N. and all its data."
echo "  • Virtual environment: $VENV_DIR"
echo "  • Config files:        $CONFIG_DIR"
echo "  • User data:           $LOCAL_DIR"
echo "  • Cache:               $CACHE_DIR"
echo "  • Runtime logs/tmp:    $DAN_DIR/runtime/"
echo "  • Desktop entries:     ~/.local/share/applications/dan*.desktop"
echo "  • Build artifacts:     $DAN_DIR/dist/ $DAN_DIR/build/ $DAN_DIR/*.egg-info/"
echo
printf "Uninstall D.A.N.? [y/N] "
read -r answer
if [[ ! "$answer" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi
echo

# Kill any running dan processes
if command -v pkill &>/dev/null; then
    if pkill -f "dan serve" 2>/dev/null || pkill -f "dan-gui" 2>/dev/null; then
        print_green "✓ Stopped running D.A.N. processes"
        sleep 1
    fi
fi

# Remove virtual environment
if [[ -d "$VENV_DIR" ]]; then
    print_bold "Removing virtual environment..."
    rm -rf "$VENV_DIR"
    print_green "✓ Removed $VENV_DIR"
fi

# Remove desktop entries from system-wide locations
for desktop in "$HOME/.local/share/applications/dan.desktop" \
               "$HOME/.local/share/applications/dan-gui.desktop" \
               "/usr/local/share/applications/dan.desktop" \
               "/usr/share/applications/dan.desktop"; do
    if [[ -f "$desktop" ]]; then
        rm -f "$desktop"
        print_green "✓ Removed desktop entry: $desktop"
    fi
done
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

# Remove config
if [[ -d "$CONFIG_DIR" ]]; then
    print_bold "Removing configuration..."
    rm -rf "$CONFIG_DIR"
    print_green "✓ Removed $CONFIG_DIR"
fi

# Remove user data
if [[ -d "$LOCAL_DIR" ]]; then
    print_bold "Removing user data..."
    rm -rf "$LOCAL_DIR"
    print_green "✓ Removed $LOCAL_DIR"
fi

# Remove cache
if [[ -d "$CACHE_DIR" ]]; then
    print_bold "Removing cache..."
    rm -rf "$CACHE_DIR"
    print_green "✓ Removed $CACHE_DIR"
fi

# Remove runtime artifacts (keep dirs, remove contents)
if [[ -d "$DAN_DIR/runtime" ]]; then
    print_bold "Cleaning runtime artifacts..."
    rm -rf "$DAN_DIR/runtime/cache/"* \
           "$DAN_DIR/runtime/logs/"* \
           "$DAN_DIR/runtime/models/"* \
           "$DAN_DIR/runtime/sessions/"* \
           "$DAN_DIR/runtime/tmp/"* 2>/dev/null || true
    print_green "✓ Cleaned runtime/"
fi

# Remove build artifacts
rm -rf "$DAN_DIR/dist" "$DAN_DIR/build" "$DAN_DIR/"*.egg-info 2>/dev/null || true

# Remove pytest/mypy/ruff caches
rm -rf "$DAN_DIR/.pytest_cache" "$DAN_DIR/.mypy_cache" "$DAN_DIR/.ruff_cache" 2>/dev/null || true

# Remove persistent skill/memory files in project dir
rm -f "$DAN_DIR/dan_skills.json" "$DAN_DIR/dan_memory.json" 2>/dev/null || true

echo
print_bold "Uninstall complete."
echo
print_green "  To also remove Ollama models used by D.A.N., run:"
echo "    ollama rm dan-interp dan-reason dan-persona"
echo
print_green "  To remove Playwright browsers (if installed):"
echo "    playwright uninstall chromium"
echo "    pip3 uninstall playwright"
echo
print_green "  Source directory kept at: $DAN_DIR"
echo "  Remove it manually if desired: rm -rf $DAN_DIR"
