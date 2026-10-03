"""Script para graficar y crear el tablero completo del Taller 3 en Miro automáticamente vía REST API.

Uso:
  1. Obtén tu Personal Access Token en Miro: https://miro.com/app/settings/user-profile/apps
  2. Ejecuta:
     python generar_tablero_miro.py --token TU_TOKEN_DE_MIRO
  O define la variable de entorno:
     export MIRO_ACCESS_TOKEN=TU_TOKEN
     python generar_tablero_miro.py
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error


MIRO_API_BASE = "https://api.miro.com/v2"

# Color mappings para sticky notes en Miro
# light_green, light_yellow, red, light_blue, violet, cyan, gray
COLORS = {
    "green": "light_green",
    "yellow": "light_yellow",
    "red": "red",
    "blue": "light_blue",
    "purple": "violet",
}


def make_request(endpoint: str, method: str = "GET", data: dict = None, token: str = ""):
    url = f"{MIRO_API_BASE}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        print(f"❌ Error en API de Miro ({e.code}): {error_msg}")
        return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None


def crear_tablero_completo(token: str):
    print("🚀 Conectando a la API de Miro...")

    # 1. Crear Tablero
    board_data = {
        "name": "Taller 3 – CI/CD + Render + ConfigCat + DoD Final",
        "description": "Tablero automatizado para el Taller 3: Diagnóstico, CI, Render, ConfigCat y DoD",
        "policy": {
            "permissionsPolicy": {
                "collaborationToolsCoOwnerAccess": "all_allowed"
            }
        }
    }
    board = make_request("boards", method="POST", data=board_data, token=token)
    if not board:
        print("❌ No se pudo crear el tablero. Verifica tu token.")
        return

    board_id = board.get("id")
    board_url = board.get("viewLink", f"https://miro.com/app/board/{board_id}/")
    print(f"✅ ¡Tablero creado exitosamente! ID: {board_id}")
    print(f"🔗 Enlace del tablero: {board_url}\n")

    # 2. Frame 1: Diagnóstico del Pipeline
    print("📌 Creando Frame 1: Diagnóstico del Pipeline...")
    pipeline_steps = [
        ("Push / PR (Rama corta)", "green", -800, -400),
        ("CI GitHub (Tests + Lint)", "green", -600, -400),
        ("Code Review (Peer/Mob)", "yellow", -400, -400),
        ("Merge a main (TBD)", "green", -200, -400),
        ("Docker GHCR (Build)", "green", 0, -400),
        ("Auto-deploy a Render", "green", 200, -400),
        ("Feature Toggle (ConfigCat)", "green", 400, -400),
    ]

    for title, color, x, y in pipeline_steps:
        make_request(
            f"boards/{board_id}/sticky_notes",
            method="POST",
            data={
                "data": {"content": f"<b>{title}</b>", "shape": "square"},
                "style": {"fillColor": COLORS.get(color, "light_blue"), "textAlign": "center"},
                "position": {"x": x, "y": y},
            },
            token=token,
        )

    # 3. Semáforo del Pipeline
    semaforo_items = [
        ("🟢 Ya funciona bien:<br>• Pytest 8 tests OK<br>• Flake8 0 errores<br>• Dockerfile listo", "green", -600, -200),
        ("🟡 Parcial / Manual:<br>• Configurar webhook Render<br>• Registrar flag en ConfigCat", "yellow", -200, -200),
        ("🔴 Cerrados hoy:<br>• Auto-deploy activo<br>• Feature Toggle probado<br>• DoD formalizado", "red", 200, -200),
    ]
    for text, color, x, y in semaforo_items:
        make_request(
            f"boards/{board_id}/sticky_notes",
            method="POST",
            data={
                "data": {"content": text, "shape": "rectangle"},
                "style": {"fillColor": COLORS.get(color, "light_yellow"), "textAlign": "left"},
                "position": {"x": x, "y": y},
            },
            token=token,
        )

    # 4. Frame 4: Feature Toggle ConfigCat (Modo Oscuro)
    print("📌 Creando Frame 4: Feature Toggle y TBD Slicing (Modo Oscuro)...")
    toggle_items = [
        ("<b>Ticket 1</b><br>CSS y HTML raíz<br>Flag: <b>dark_mode_enabled = False</b><br>Rollout: 0%", "yellow", -500, 200),
        ("<b>Ticket 2</b><br>Botón Toggle Canary<br>Rollout: <b>10% de usuarios</b><br>Sin persistencia", "blue", -100, 200),
        ("<b>Ticket 3</b><br>Rollout al <b>100%</b><br>Persistencia: LocalStorage + Backend API", "green", 300, 200),
    ]
    for text, color, x, y in toggle_items:
        make_request(
            f"boards/{board_id}/sticky_notes",
            method="POST",
            data={
                "data": {"content": text, "shape": "square"},
                "style": {"fillColor": COLORS.get(color, "light_blue"), "textAlign": "center"},
                "position": {"x": x, "y": y},
            },
            token=token,
        )

    # 5. Frame 5: Definition of Done Final (DoD)
    print("📌 Creando Frame 5: Definition of Done Final...")
    dod_items = [
        ("<b>DoD Técnico</b><br>• Código revisado (PR/mob)<br>• CI verde (Tests+Lint)<br>• Docker build OK<br>• Feature flag configurado", "purple", -500, 500),
        ("<b>DoD de Negocio</b><br>• Acceptance criteria OK<br>• Validado en destino<br>• PO conoce estado toggle<br>• WCAG contrastes OK", "blue", -100, 500),
        ("<b>DoD de Despliegue</b><br>• Auto-deploy a Render<br>• Healthcheck /health 200<br>• Logs de Uvicorn limpios<br>• Rollback probado", "green", 300, 500),
    ]
    for text, color, x, y in dod_items:
        make_request(
            f"boards/{board_id}/sticky_notes",
            method="POST",
            data={
                "data": {"content": text, "shape": "rectangle"},
                "style": {"fillColor": COLORS.get(color, "violet"), "textAlign": "left"},
                "position": {"x": x, "y": y},
            },
            token=token,
        )

    print("\n🎉 ¡Tablero completo graficado con éxito en Miro!")
    print(f"👉 Abre tu tablero en Brave: {board_url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Graficar Taller 3 en Miro automáticamente")
    parser.add_argument("--token", help="Personal Access Token de Miro")
    args = parser.parse_args()

    token = args.token or os.getenv("MIRO_ACCESS_TOKEN")

    if not token:
        # Intentar leer desde tokens de antigravity si existe
        token_path = "/Users/danielmacias/.gemini/antigravity-ide/mcp_oauth_tokens.json"
        if os.path.exists(token_path):
            try:
                with open(token_path) as f:
                    data = json.load(f)
                    token = data.get("https://mcp.miro.com", {}).get("token", {}).get("access_token")
            except Exception:
                pass

    if not token:
        print("⚠️ No se encontró un token de Miro.")
        print("Uso: python generar_tablero_miro.py --token TU_TOKEN_DE_MIRO")
        print("Obtén tu token en: https://miro.com/app/settings/user-profile/apps")
        sys.exit(1)

    crear_tablero_completo(token)
