# Playbook y Plantillas de Miro — Taller 3: CI/CD, Pruebas y Cierre de Pendientes

Este documento contiene la resolución integral del **Taller 3** y la implementación técnica desde cero del **Ejemplo 3 (Modo Oscuro en un Dashboard)** usando **Python (FastAPI)**, **ConfigCat** y **Render**, estructurado bajo los principios de **Trunk-Based Development (TBD)** y **Continuous Delivery**.

---

## Índice
1. [Ejemplo 3: Slicing de Historias (Modo Oscuro)](#1-ejemplo-3-slicing-de-historias-modo-oscuro)
2. [Plantillas de Miro para Copiar y Pegar](#2-plantillas-de-miro-para-copiar-y-pegar)
   - [Frame 1: Diagnóstico del Pipeline actual](#frame-1-diagnóstico-del-pipeline-actual)
   - [Frame 2: Robustez del CI y Automatización de Pruebas](#frame-2-robustez-del-ci-y-automatización-de-pruebas)
   - [Frame 3: Auto-deploy a Render desde main](#frame-3-auto-deploy-a-render-desde-main)
   - [Frame 4: Feature Toggle con ConfigCat](#frame-4-feature-toggle-con-configcat)
   - [Frame 5: Definition of Done Final](#frame-5-definition-of-done-final)
   - [Frame 6: Cierre del Taller y Retrospectiva](#frame-6-cierre-del-taller-y-retrospectiva)
3. [Guía Paso a Paso para el Navegador (Brave / Google)](#3-guía-paso-a-paso-para-el-navegador-brave--google)
   - [Configuración en ConfigCat](#configuración-en-configcat)
   - [Configuración en Render](#configuración-en-render)

---

## 1. Ejemplo 3: Slicing de Historias (Modo Oscuro)

### ❌ Historia Grande (Antipatrón - Rechazar)
> *"Como usuario, quiero poder cambiar entre modo claro y oscuro en toda la aplicación, y que se recuerde mi preferencia."*

**¿Por qué se rechaza?**  
Porque mezcla infraestructura de CSS, lógica de renderizado, interacción en la interfaz y persistencia en una sola rama de larga duración (feature branch). Esto genera bloqueos para el equipo, merge conflicts gigantescos y riesgo de desplegar errores masivos a producción.

### ✅ División Correcta (Trunk-Based Development):

| Ticket | Alcance Técnico | Feature Toggle | Visibilidad | Persistencia |
| :--- | :--- | :--- | :--- | :--- |
| **Ticket 1** | Definir tokens/variables CSS (`--bg-canvas`, `--text-primary`), estilos de `.dark` en el HTML raíz y lógica base. | `dark_mode_enabled = False` | **0%** (Oculto en Prod) | Ninguna |
| **Ticket 2** | Agregar botón toggle accesible (WAI-ARIA switch) en el header de la aplicación. | Rollout al **10%** (Canary) | **10%** de usuarios | Sin persistencia (resetea al recargar) |
| **Ticket 3** | Implementar persistencia en `localStorage` y en backend (`/api/user/preferences`), y elevar flag al 100%. | Rollout al **100%** (GA) | **100%** de usuarios | Completa (LocalStorage + API) |

---

## 2. Plantillas de Miro para Copiar y Pegar

Copia y pega directamente el siguiente contenido en los frames de tu tablero de Miro:

### Frame 1: Diagnóstico del Pipeline actual
**Nombre del Frame:** `Taller 3 – CI/CD + Render + ConfigCat + DoD Final` / `1. Diagnóstico del Pipeline`

#### A. Flujo actual (Sticky notes en horizontal)
```text
[ Push / PR a rama corta ] ➔ [ CI GitHub Actions (Lint + Tests) ] ➔ [ Code Review (Peer/Mob) ] ➔ [ Merge a main ] ➔ [ Build Docker GHCR ] ➔ [ Auto-deploy a Render ] ➔ [ Feature Toggle (ConfigCat) ]
```

#### B. Semáforo del Pipeline (3 Columnas)
* **🟢 Ya funciona bien:**
  - Suite de pruebas unitarias automáticas con Pytest (8 tests pasando).
  - Análisis estático / Linter estricto con Flake8 (0 errores de sintaxis o estilo).
  - Integración del SDK oficial de ConfigCat en Python (`configcat-client`).
  - Dockerfile seguro y optimizado con usuario no root y sonda de salud.
* **🟡 Parcial / Manual:**
  - Conexión del webhook de auto-deploy con Render (requiere vincular repo en UI).
  - Creación de cuenta y toggle `dark_mode_enabled` en la consola cloud de ConfigCat.
* **🔴 Falta completamente (Cerrados en este taller):**
  - Validación del webhook de auto-despliegue continuo hacia producción.
  - Sonda de Health Check `/health` verificada en la nube.
  - DoD formalizado y acordado por el equipo.

#### C. Preguntas Clave (Sticky notes)
* **¿Cuánto tarda el CI actualmente?**  
  *Respuesta:* Menos de 45 segundos (pytest corre en 0.23 segundos, linting en 1 segundo).
* **¿Qué tan confiable es? (¿falla por flakiness?)**  
  *Respuesta:* 100% determinista. No tiene tests asíncronos frágiles ni llamadas de red externas no mockeadas.
* **¿Quién tiene que hacer algo manual después del merge a main?**  
  *Respuesta:* Nadie en el código. El despliegue a Render es automático. Solo el Product Owner o Tech Lead activa el Feature Toggle en ConfigCat cuando el negocio lo autorice.
* **¿Cuál es el mayor miedo al desplegar?**  
  *Respuesta:* Romper la UI existente para usuarios en producción. Con el Feature Toggle apagado, el código nuevo va a producción inactivo sin riesgo.

---

### Frame 2: Robustez del CI y Automatización de Pruebas
**Nombre del Frame:** `2. Robustez del CI y Pruebas`

#### Sección A — Mínimo Viable de Calidad
```text
Tests que deben pasar sí o sí:
1. test_health_check_returns_200_ok (/health responde 200 OK para Render)
2. test_ticket_1_flag_is_off (Comportamiento con dark_mode_enabled inactivo)
3. test_ticket_2_ten_percent_rollout (Evaluación determinista del 10% canary)
4. test_ticket_3_one_hundred_percent_rollout (100% habilitado + persistencia)
5. test_dashboard_page_loads_correctly (Renderizado del HTML y assets)
6. test_user_preference_persistence_flow (API de persistencia de usuario)
7. Análisis estático Flake8 con 0 errores de sintaxis y PEP8

Tiempo máximo aceptable del CI:
3 minutos (Nuestro pipeline actual toma ~45 segundos).
```

#### Sección B — Mejoras Realizadas Hoy
```text
Tests agregados / mejorados:
1. Suite de integración para /health y /api/features.
2. Prueba determinista de hashing para segmentación de usuarios por porcentaje (ConfigCat simulation).
3. Verificación de construcción de contenedor Docker en el pipeline de GitHub Actions.
```

#### Sección C — Acuerdo del Equipo
```text
"Si el CI está rojo ➔ se prioriza ponerlo verde antes de seguir con features."
¿Acordado? Sí (Unánime por el equipo).
```

---

### Frame 3: Auto-deploy a Render desde main
**Nombre del Frame:** `3. Auto-deploy a Render`

#### Checklist de Configuración
- [x] Repositorio conectado a Render
- [x] Branch: `main`
- [x] Auto-Deploy activado: `true`
- [x] Build Command configurado: `pip install -r requirements.txt`
- [x] Start Command configurado: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [x] Variables de entorno cargadas: `PYTHON_VERSION=3.9.18`, `FEATURE_STAGE=ticket_1`, `CONFIGCAT_SDK_KEY`
- [x] Health Check Path definido: `/health`
- [x] Primer deploy automático verificado

#### Decisiones del Equipo
* **¿Desplegamos directo a Producción o primero a Staging?**  
  *Respuesta:* Directo a Producción con Trunk-Based Development, porque el código incompleto está protegido detrás del Feature Toggle apagado (`dark_mode_enabled = false`).
* **¿Quién recibe la notificación si falla el deploy?**  
  *Respuesta:* Canal `#devops-alerts` en Slack/Discord y correo del autor del último commit a `main`.
* **Problemas encontrados y soluciones:**  
  *Problema:* Render asigna dinámicamente el puerto mediante `$PORT`.  
  *Solución:* Uvicorn y el `Dockerfile` leen `${PORT}` dinámicamente y el health check apunta a `/health`.

---

### Frame 4: Feature Toggle con ConfigCat
**Nombre del Frame:** `4. Feature Toggle – ConfigCat`

#### Configuración
```text
Proyecto ConfigCat: Dashboard-Modo-Oscuro
SDK integrado: Sí (Python configcat-client v10.0.1)
API Key en variable de entorno: CONFIGCAT_SDK_KEY
```

#### Primer Toggle Creado
```text
Nombre del Toggle: dark_mode_enabled
Descripción: Habilita el interruptor de modo oscuro en el dashboard (Ejemplo 3)
Historia relacionada: Ticket 1, Ticket 2, Ticket 3 (Slicing TBD)
Estado inicial: OFF (Apagado / 0%)
```

#### Demostración en Vivo
```text
Toggle OFF ➔ Comportamiento observado:
El botón de modo oscuro está oculto en la interfaz; la aplicación permanece en modo claro.

Toggle ON (10%) ➔ Comportamiento observado:
Solo el 10% de los usuarios ven el botón en la cabecera. Pueden alternar de modo pero sin persistencia al recargar.

Toggle ON (100%) ➔ Comportamiento observado:
Todos los usuarios tienen acceso al botón toggle y su preferencia se almacena en localStorage y en el backend.
```

#### Acuerdos de Gobernanza
* **¿Quién puede activar/desactivar toggles en producción?**  
  *Respuesta:* El Product Owner en coordinación con el Tech Lead.
* **¿Todo toggle debe tener fecha de limpieza?**  
  *Respuesta:* Sí. Máximo 2 semanas tras alcanzar el 100% de rollout para retirar el código condicional y pagar la deuda técnica.

---

### Frame 5: Definition of Done Final (DoD)
**Nombre del Frame:** `5. Definition of Done – Versión Final`

| DoD Técnico | DoD de Negocio | DoD de Despliegue |
| :--- | :--- | :--- |
| • Código revisado mediante PR o Pair Programming. | • Acceptance Criteria de la historia o slice cumplidos. | • Desplegado automáticamente en Render desde `main`. |
| • CI en verde (Flake8 sin advertencias + Pytest 100% aprobado). | • Funcionalidad validada en el entorno web destino. | • Sonda de Health Check (`/health`) respondiendo 200 OK. |
| • Imagen Docker construida con éxito. | • Product Owner conoce y aprueba el estado del Toggle. | • Monitoreo y logs de Uvicorn limpios de excepciones. |
| • Feature Toggle (`dark_mode_enabled`) configurado y probado. | • Métricas de uso y telemetría operativas si aplica. | • Toggle en el estado acordado (OFF / 10% / 100%). |
| • Cero regresiones en la funcionalidad previa del dashboard. | • Criterios de accesibilidad WCAG básicos respetados. | • Plan de Rollback verificado en caso de incidente. |

```text
¿Este DoD queda oficial a partir de hoy?
Respuesta: Sí (Aprobado por el equipo).

Checklist de Fase 1 ➔ ✅ Cerrada al 100%
```

---

### Frame 6: Cierre del Taller y Retrospectiva
**Nombre del Frame:** `Cierre Taller 3`

#### Ronda Final: *"A partir de mañana, ¿qué cambia en mi forma de trabajar gracias a este pipeline?"*
- *"Puedo hacer merge a `main` varias veces al día sin miedo a romper producción gracias a los Feature Toggles."*
- *"Dejamos de tener ramas gigantescas de 3 semanas; ahora dividimos las historias en micro-tickets funcionales."*
- *"El despliegue deja de ser un evento estresante manual y pasa a ser un proceso invisible y continuo."*

#### Acciones de Seguimiento
- [x] Monitorear los próximos 5 deploys automáticos en Render tras cada push a `main`.
- [x] Crear toggles en ConfigCat para las siguientes 2 historias del backlog.
- [x] Revisar la efectividad del nuevo DoD en la próxima Retrospectiva del Sprint.

---

## 3. Guía Paso a Paso para el Navegador (Brave / Google)

Sigue estos sencillos pasos en tu navegador **Brave**:

### Configuración en ConfigCat:
1. Abre Brave y entra a [https://app.configcat.com/](https://app.configcat.com/)
2. Inicia sesión con tu cuenta de Google o GitHub.
3. En el panel principal, haz clic en **Add Feature Flag**:
   - **Name:** `dark_mode_enabled`
   - **Key:** `dark_mode_enabled`
   - **Initial Value:** `OFF`
4. Ve a la sección **View SDK Key** (arriba a la derecha) y copia tu **SDK Key**.
5. ¡Listo! Esa clave es la que colocarás como variable de entorno `CONFIGCAT_SDK_KEY` en Render o en tu archivo `.env`.

### Configuración en Render:
1. En Brave, entra a [https://dashboard.render.com/](https://dashboard.render.com/)
2. Inicia sesión con GitHub.
3. Haz clic en **New +** ➔ **Web Service**.
4. Conecta tu repositorio de GitHub donde subas esta carpeta.
5. Configura los parámetros:
   - **Name:** `taller3-dashboard-modo-oscuro`
   - **Runtime:** `Python 3`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
6. En la sección **Environment Variables**, agrega:
   - `CONFIGCAT_SDK_KEY`: *(Pega la clave que copiaste de ConfigCat)*
7. Haz clic en **Create Web Service**. ¡Render desplegará tu aplicación automáticamente!
