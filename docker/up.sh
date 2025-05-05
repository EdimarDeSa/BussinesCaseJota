#! /bin/bash

echo "Iniciando containers em modo de produção"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"

"$SCRIPT_DIR/down.sh"

docker compose -f "$SCRIPT_DIR/compose.yaml" up -d --build
