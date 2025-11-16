#!/usr/bin/env bash
set -e
set -o pipefail

OUT="/tmp/apphost_diagnostics.txt"
echo "Running AppHost diagnostics..."
echo "Output: $OUT"

{
    echo "==================================================="
    echo "== SYSTEM INFO"
    echo "==================================================="
    date
    uname -a
    echo

    echo "==================================================="
    echo "== SYSTEMD STATUS (apphost)"
    echo "==================================================="
    systemctl status apphost --no-pager || true
    echo

    echo "==================================================="
    echo "== NGINX CONFIG TEST"
    echo "==================================================="
    nginx -t || true
    echo

    echo "==================================================="
    echo "== DOCKER CONTAINERS (apphost_*)"
    echo "==================================================="
    docker ps -a --filter "name=apphost_" || true
    echo

    echo "==================================================="
    echo "== CURL ENDPOINT TESTS"
    echo "==================================================="
    BASE="http://127.0.0.1"

    echo "---- GET /health ----"
    curl -sS -D - "$BASE/health" || true
    echo; echo

    echo "---- GET /admin/ ----"
    curl -sS -D - "$BASE/admin/" || true
    echo; echo

    echo "---- GET /apps/ ----"
    curl -sS -D - "$BASE/apps/" || true
    echo; echo

    echo "==================================================="
    echo "== DATA DIRECTORY CONTENTS"
    echo "==================================================="
    ls -R /opt/apphost || true
    echo

    echo "==================================================="
    echo "== DONE"
    echo "==================================================="
} | tee "$OUT"
