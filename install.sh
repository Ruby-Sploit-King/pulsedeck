#!/usr/bin/env bash
#
# PulseDeck installer
# https://github.com/Ruby-Sploit-King/pulsedeck
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Ruby-Sploit-King/pulsedeck/main/install.sh | bash
#
set -euo pipefail

REPO="Ruby-Sploit-King/pulsedeck"
SOURCE="git+https://github.com/${REPO}.git"
COMMAND="pulsedeck"

cyan() { printf '\033[1;38;2;125;207;255m%s\033[0m\n' "$*"; }
green() { printf '\033[1;38;2;158;206;106m%s\033[0m\n' "$*"; }
red() { printf '\033[1;38;2;247;118;142m%s\033[0m\n' "$*" >&2; }

cyan "Installing PulseDeck from ${REPO} ..."

if ! command -v python3 >/dev/null 2>&1; then
    red "python3 was not found. Install Python 3.11+ and run this again."
    exit 1
fi

if command -v pipx >/dev/null 2>&1; then
    pipx install --force "${SOURCE}"
elif command -v uv >/dev/null 2>&1; then
    uv tool install --force "${SOURCE}"
else
    cyan "pipx/uv not found; falling back to pip --user."
    python3 -m pip install --user --upgrade "${SOURCE}" || {
        red "Install failed. Install pipx (https://pipx.pypa.io) and try again:"
        red "  pipx install git+https://github.com/${REPO}.git"
        exit 1
    }
fi

green "✓ PulseDeck installed"
cyan  "  Run '${COMMAND}' to open the dashboard."
