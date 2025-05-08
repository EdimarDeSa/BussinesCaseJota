#! /bin/bash

echo "Iniciando o containers para desenvolvimento"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"

docker compose -f "$SCRIPT_DIR/docker-compose.yaml" up -d postgres redis rabbitmq
