# Taller 6: Sprint Review, Retrospective y Liberación Segura

Este documento consolida las nuevas políticas de ceremonias y estrategias de liberación continua, dando respuesta al **Taller 6**. Además, resuelve el caso de la funcionalidad *"Pagos Express"*.

---

## 1. Actualización del Playbook: Nuevas Ceremonias Ágiles

### 1.1 Formato Oficial del Nuevo Sprint Review (CD + TBD)
El Sprint Review abandona las "demos locales" y evoluciona hacia una **demostración de valor en producción**.

* **Foco:** "¿Qué valor recibieron los usuarios?" en lugar de "¿Qué construimos?".
* **Reglas de la Demo (4-5 min por incremento):**
  1. ¿Qué problema de usuario resuelve?
  2. ¿Está activo para todos o detrás de un Feature Toggle?
  3. **Demo en vivo en Render** (Mostrando el toggle ON/OFF en la URL de producción).
  4. Métrica o evidencia de valor (telemetría, feedback, analytics).
  5. **Pregunta al PO / Stakeholder:** "¿Esto genera el valor esperado?".
* **Roles:** El Developer hace la demo técnica en vivo, el PO facilita el feedback de los stakeholders, el resto del equipo anota.

### 1.2 Formato Oficial de la Nueva Sprint Retrospective
La retro ahora inspecciona el flujo de valor, la salud técnica y la disciplina del equipo.

* **Focos Obligatorios:**
  1. **Salud del Pipeline:** ¿Se rompió el CI? ¿Cuánto tardan los deploys? ¿Hubo rollbacks?
  2. **Disciplina TBD:** Frecuencia de integraciones diarias a `main`. Ninguna rama debe vivir más de 1 día. ¿Limpiamos toggles viejos?
  3. **Flujo de Valor:** Lead time (desde que se inicia hasta producción). ¿El valor llegó al usuario?
* **Dinámica (Columnas en Miro):**
  - 🟢 Lo que funcionó bien en el flujo.
  - 🟡 Lo que generó fricción.
  - 🔴 Lo que rompió el flujo o generó miedo (Ej: tests inestables).
  - 🎯 **Acciones de mejora:** Máximo 3 acciones concretas y asignables.

---

## 2. Política de Liberación Segura (Toggles + Observación)

Toda nueva funcionalidad o cambio de alto riesgo integrado en `main` debe seguir este ciclo:

1. **Estrategia Inicial:** Nace apagado (`OFF` al 0%) en producción.
2. **Activación Progresiva:**
   - Fase 1: Encendido solo para el equipo interno (QA / Devs).
   - Fase 2: Canary Release (10% - 20% de usuarios).
   - Fase 3: General Availability (100% de usuarios).
3. **Observabilidad:** Antes de encender el toggle, se debe acordar qué métrica de negocio o de sistema se observará (ej. errores HTTP 500, tasa de conversión).
4. **Criterio de Rollback:** Si el Health Check falla o la métrica de error supera el umbral tolerable, se apaga el toggle en ConfigCat instantáneamente (Rollback en milisegundos).
5. **Limpieza de Deuda:** Todo toggle al 100% debe ser eliminado del código fuente en un máximo de **2 semanas (1 sprint)** tras su liberación.

---

## 3. Resolución del Caso: "Pagos Express"

### Situación Analizada:
El equipo tiene la funcionalidad "Pagos Express" protegida tras el toggle `pagos-express-v1` (OFF para el 100%). Llevan 9 días en `main` y hay miedo de activarla.

### Diagnóstico de los "Hechos Problemáticos":
1. **Presión Comercial:** El PO quiere activar al 20%. *Riesgo alto si no hay métricas preparadas.*
2. **Inestabilidad del Deploy:** El último deploy falló el health check y hubo rollback manual. *Falta confianza en el pipeline.*
3. **Deuda Técnica Acumulada:** 3 Toggles de más de 45 días activos ensucian el código.
4. **Baja Disciplina TBD:** Solo 4 integraciones en el sprint. Las ramas son muy grandes.
5. **Flaky Tests:** Una rama duró 4 días viva porque el CI estaba rojo. *Esto rompe el principio de integración continua.*
6. **Ceguera Operativa:** No hay métricas claras de error o conversión de pagos.
7. **Desalineación de Expectativas:** Negocio cree que "ya está listo", ignorando la fase de Canary Release.

### Plan de Acción (Resolución para el Equipo):

1. **Acción 1: Establecer la métrica de observabilidad (Hoy mismo)**
   - No podemos activar el 20% a ciegas. El equipo debe agregar un log o dashboard simple que mida intentos de pago exitosos vs fallidos.
2. **Acción 2: Alinear Expectativas con el Stakeholder (Por el PO)**
   - El PO debe comunicar que "Pagos Express" entra en fase **Canary (20%)**, no está "listo al 100%", para gestionar el riesgo comercial en caso de apagar el toggle por fallas.
3. **Acción 3: Solucionar la salud del Pipeline (Prioridad Técnica)**
   - Ignorar/Remover temporalmente o arreglar urgentemente el *flaky test* que bloquea el CI.
   - Pagar la deuda técnica eliminando los 3 toggles viejos (>45 días) esta misma semana.

### Ejecución de Liberación para Pagos Express:
- **Paso 1:** Desplegar los logs/métricas de pago a `main`.
- **Paso 2:** El PO activa el toggle `pagos-express-v1` al **20%** en ConfigCat.
- **Paso 3:** Observación estricta por 24-48 horas.
- **Paso 4:** Si la conversión es positiva y los errores son nulos, subir al 100%. Si caen errores graves, apagar el toggle de inmediato.
- **Paso 5:** Eliminar el código del toggle en el próximo sprint.
