#!/usr/bin/env bash
set -euo pipefail

WORKDIR="$(pwd)"

exec docker run \
  --rm \
  -i \
  -v "$(pwd):$WORKDIR" \
  -w "$WORKDIR" \
  --init \
  "render-bbb" \
  bash -c "python3 /app/overengineered.py $*"
