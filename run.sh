#!/usr/bin/env bash
set -e

# Navegar al directorio del script
cd "$(dirname "$0")"

echo "=========================================================="
echo "  Iniciando Taller 3 - Modo Oscuro Dashboard (Python)    "
echo "=========================================================="

# Activar o crear entorno virtual
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual .venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Ejecutar pruebas rápidas
echo "Ejecutando suite de pruebas unitarias..."
pytest -q

echo "Iniciando servidor FastAPI en http://127.0.0.1:8000 ..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
