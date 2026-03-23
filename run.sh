#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Verificando Docker..."
if ! command -v docker &>/dev/null; then
    echo "ERRO: Docker não encontrado. Instale antes de continuar."
    exit 1
fi

if ! docker info &>/dev/null; then
    echo "ERRO: Docker não está em execução. Inicie o Docker e tente novamente."
    exit 1
fi

echo "==> Subindo containers (PostgreSQL + Streamlit)..."
cd "$PROJECT_DIR"
docker compose up --build
