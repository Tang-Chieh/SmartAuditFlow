#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
# Isolate OAuth credentials and native runtime from the user's existing tools.
export HOME="$ROOT/runtime-home"
export PI_CODING_AGENT_DIR="$ROOT/auth"
unset OPENAI_API_KEY OPENAI_BASE_URL OPENAI_CODEX_OAUTH_TOKEN ANTHROPIC_API_KEY GOOGLE_API_KEY GEMINI_API_KEY
exec "$ROOT/bin/omp" "$@"
