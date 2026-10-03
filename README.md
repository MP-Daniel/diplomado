# Taller 3: CI/CD, Feature Flags (ConfigCat) y Render — Modo Oscuro en Python

Este proyecto implementa la solución completa del **Taller 3** y el **Ejemplo 3: Modo oscuro (Dark Mode) en un dashboard** construido desde cero con **Python (FastAPI)**, **Trunk-Based Development (TBD)**, **ConfigCat** y despliegue continuo en **Render**.

---

## 📁 Estructura del Proyecto

```text
taller3-modo-oscuro/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Pipeline CI en GitHub Actions (Flake8 + Pytest + Docker)
├── app/
│   ├── __init__.py
│   ├── config.py                  # Configuración y variables de entorno
│   ├── feature_flags.py           # Servicio de Feature Flags (ConfigCat SDK + Fallback TBD)
│   ├── main.py                    # API FastAPI, rutas, healthcheck (/health) y templates
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css          # Ticket 1: Tokens CSS, variables de modo claro/oscuro y WCAG A11y
│   │   └── js/
│   │       └── dashboard.js       # Tickets 1, 2 y 3: Lógica cliente, WAI-ARIA switch y persistencia
│   └── templates/
│       └── index.html             # Dashboard responsivo con visualizador del Pipeline de Miro
├── tests/
│   ├── __init__.py
│   ├── test_health.py             # Verificación de salud para Render (/health)
│   ├── test_feature_flags.py      # Verificación de los 3 tickets y porcentaje de rollout
│   └── test_api.py                # Verificación de rutas de API y persistencia
├── .dockerignore
├── .gitignore
├── Dockerfile                     # Imagen de contenedor segura para Render / GHCR
├── render.yaml                    # Especificación de Infraestructura como Código (Render Blueprint)
├── requirements.txt               # Dependencias del proyecto
├── run.sh                         # Script ejecutable de arranque rápido
├── README.md                      # Documentación del proyecto
└── TALLER_3_PLAYBOOK_Y_MIRO.md    # Plantillas completas de Miro y DoD oficial
```

---

## 🎯 Implementación del Ejemplo 3: Slicing de Modo Oscuro

El taller aborda el antipatrón de historias gigantes y su correcta división en micro-tickets para Trunk-Based Development:

1. **Ticket 1: Variables CSS y HTML raíz (Flag `dark_mode_enabled` en OFF / 0%)**
   - El código de diseño y clases `.dark` se despliega a producción inactivo.
   - Nadie ve el modo oscuro ni el botón todavía.

2. **Ticket 2: Botón toggle para el 10% de usuarios (Canary Rollout)**
   - El botón se hace visible únicamente al 10% de los usuarios mediante el toggle de ConfigCat.
   - Sin persistencia todavía (en caso de recargar vuelve a su estado inicial, facilitando pruebas preliminares).

3. **Ticket 3: Persistencia en LocalStorage + Backend y Rollout al 100%**
   - Se guarda la preferencia del usuario en `localStorage` y en `/api/user/preferences`.
   - Se activa el flag al 100% para todos los usuarios.

---

## 🚀 Inicio Rápido en Local

### Opción 1: Ejecutar con el script automatizado
```bash
./run.sh
```

### Opción 2: Paso a paso manual
```bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar pruebas y linter
flake8 app tests --max-line-length=120
pytest -v

# 4. Iniciar la aplicación
uvicorn app.main:app --reload --port 8000
```

Abre en tu navegador Brave o Google Chrome:  
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Pruebas Automatizadas y CI

Para garantizar el acuerdo de calidad:  
> *"Si el CI está rojo, no se continúa con features hasta que esté verde."*

Ejecuta:
```bash
source .venv/bin/activate
pytest -v
```

Resultado de las 8 pruebas:
- `test_health_check_returns_200_ok`: Sonda requerida por Render.
- `test_ticket_1_flag_is_off`: Ticket 1 verificado.
- `test_ticket_2_ten_percent_rollout`: Ticket 2 de canary rollout verificado.
- `test_ticket_3_one_hundred_percent_rollout`: Ticket 3 de disponibilidad general verificado.
- `test_dashboard_page_loads_correctly`: Renderizado de plantilla y assets.
- `test_get_features_endpoint`: API de consulta de flags.
- `test_user_preference_persistence_flow`: API de almacenamiento de preferencias.
- `test_admin_toggle_simulation`: Simulador dinámico para demostraciones.

---

## 🌐 Despliegue en Render

1. Sube este repositorio a GitHub.
2. En [Render.com](https://render.com), crea un **Web Service**.
3. Selecciona tu repositorio y utiliza los siguientes parámetros:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
   - **Environment Variable:** `CONFIGCAT_SDK_KEY` = *(tu clave de ConfigCat)*

---

## 📋 Documentación de Miro y Definición de Terminado (DoD)

Para copiar las respuestas en tu tablero de Miro, consulta el archivo:  
📄 **[`TALLER_3_PLAYBOOK_Y_MIRO.md`](./TALLER_3_PLAYBOOK_Y_MIRO.md)**
