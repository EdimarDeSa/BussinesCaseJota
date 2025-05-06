#! /bin/bash

echo "Parando os containers"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"

docker compose -f $SCRIPT_DIR/docker-compose.yaml down --remove-orphans -v
