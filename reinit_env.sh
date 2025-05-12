#!/usr/bin/env bash

# BASE_DIR="$(dirname "${0}")"
# BASE_DIR="$(realpath "${BASE_DIR}")"

###############################################################################

# shellcheck source=.base.sh
# source "${BASE_DIR}/.base.sh"

###############################################################################

export LANG=en_US.UTF-8
export LANGUAGE=en_US:en
export LC_ALL=en_US.UTF-8

###############################################################################

curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
uv self update
uv cache clean
uv sync

###############################################################################

echo ''
echo 'All have been done successfully.'
echo ''

###############################################################################
