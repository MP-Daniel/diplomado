/**
 * TALLER 3 - DASHBOARD MODO OSCURO
 * Implementación de los 3 Tickets según Trunk Based Development (TBD)
 * 
 * Ticket 1: Variables CSS y lógica de clase en HTML raíz detrás de dark_mode_enabled=OFF
 * Ticket 2: Botón toggle visible solo al 10% de usuarios, sin persistencia.
 * Ticket 3: Persistencia en localStorage + backend, flag al 100%.
 */

// State Object
const state = {
  currentUserId: localStorage.getItem('taller3_user_id') || 'user_1',
  darkModeEnabled: false,
  uiToggleVisible: false,
  persistenceEnabled: false,
  activeStage: 'ticket_1',
  isCloudMode: false,
};

// DOM Elements
const htmlRoot = document.documentElement;
const toggleBtn = document.getElementById('darkModeToggle');
const toggleWrapper = document.getElementById('toggleWrapper');
const toggleStatusText = document.getElementById('toggleStatusText');
const activeStageBadge = document.getElementById('activeStageBadge');
const rolloutPercentEl = document.getElementById('rolloutPercent');
const flagStatusEl = document.getElementById('flagStatus');
const userSelector = document.getElementById('userSelector');

/**
 * 1. Inicialización en el arranque
 */
async function initDashboard() {
  // Configurar usuario inicial
  if (userSelector) {
    userSelector.value = state.currentUserId;
    userSelector.addEventListener('change', (e) => {
      state.currentUserId = e.target.value;
      localStorage.setItem('taller3_user_id', state.currentUserId);
      fetchFeatureStatus();
    });
  }

  // Escuchar click en el botón toggle (Ticket 2 y Ticket 3)
  if (toggleBtn) {
    toggleBtn.addEventListener('click', handleToggleTheme);
  }

  // Obtener estado de Feature Flags desde el Backend
  await fetchFeatureStatus();
}

/**
 * 2. Consultar el estado de las Feature Flags desde el Backend
 */
async function fetchFeatureStatus() {
  try {
    const res = await fetch(`/api/features?user_id=${encodeURIComponent(state.currentUserId)}`);
    const data = await res.json();

    state.darkModeEnabled = data.is_enabled;
    state.uiToggleVisible = data.ui_toggle_visible;
    state.persistenceEnabled = data.persistence_enabled;
    state.activeStage = data.active_stage;
    state.isCloudMode = data.provider.includes('ConfigCat Cloud');

    updateUIState(data);
  } catch (err) {
    console.error('Error fetching feature flags:', err);
  }
}

/**
 * 3. Actualizar la interfaz según el Ticket activo
 */
function updateUIState(data) {
  // A. Control de visibilidad del Botón Toggle (Ticket 1 vs Ticket 2/3)
  if (toggleWrapper) {
    if (data.ui_toggle_visible) {
      toggleWrapper.classList.remove('hidden');
    } else {
      toggleWrapper.classList.add('hidden');
    }
  }

  // B. Badges y métricas en pantalla
  if (activeStageBadge) {
    activeStageBadge.textContent = `${data.stage_info.id}: ${data.stage_info.title}`;
  }
  if (rolloutPercentEl) {
    rolloutPercentEl.textContent = `${data.stage_info.rollout_percentage}%`;
  }
  if (flagStatusEl) {
    flagStatusEl.textContent = data.is_enabled ? 'ON (Habilitado)' : 'OFF (Apagado)';
    flagStatusEl.className = data.is_enabled ? 'badge badge-success' : 'badge badge-warning';
  }

  // C. Resaltar tarjeta del ticket activo en la guía del taller
  document.querySelectorAll('.ticket-item').forEach((card) => {
    card.classList.remove('active-stage');
  });
  const activeCard = document.getElementById(`card-${data.active_stage}`);
  if (activeCard) {
    activeCard.classList.add('active-stage');
  }

  // D. Aplicar tema según etapa y persistencia (Ticket 1, Ticket 2, Ticket 3)
  applyThemeBasedOnStage(data);
}

/**
 * 4. Lógica de Aplicación del Tema
 */
function applyThemeBasedOnStage(data) {
  if (data.active_stage === 'ticket_1') {
    // TICKET 1: Flag apagado para todos, nadie ve modo oscuro
    setTheme(false, false);
    return;
  }

  if (data.active_stage === 'ticket_2') {
    // TICKET 2: Visible solo para el 10%, SIN persistencia.
    // Si la página se recarga, vuelve al tema claro por defecto.
    const isDark = htmlRoot.classList.contains('dark');
    setTheme(isDark, false);
    return;
  }

  if (data.active_stage === 'ticket_3' || data.persistence_enabled) {
    // TICKET 3: 100% Rollout + Persistencia activada
    const savedTheme = localStorage.getItem('theme_preference');
    if (savedTheme) {
      setTheme(savedTheme === 'dark', false);
    } else {
      // Revisar preferencia del sistema si no hay guardada
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(prefersDark, false);
    }
  }
}

/**
 * 5. Manejar click en el botón toggle
 */
async function handleToggleTheme() {
  const isCurrentlyDark = htmlRoot.classList.contains('dark');
  const targetTheme = !isCurrentlyDark;

  // Ticket 1: Este handler nunca se dispara porque el botón está oculto.
  // Ticket 2: Cambia de tema temporalmente, pero NO persiste.
  if (state.activeStage === 'ticket_2') {
    setTheme(targetTheme, false);
    showToast('Modo Oscuro activado (Ticket 2: Sin persistencia. Se reiniciará al recargar).');
    return;
  }

  // Ticket 3: Cambia de tema Y persiste en localStorage y backend
  if (state.activeStage === 'ticket_3' || state.persistenceEnabled) {
    setTheme(targetTheme, true);
    showToast('Preferencia guardada con éxito (Ticket 3: Persistencia en LocalStorage y Backend).');
  }
}

/**
 * 6. Aplicar y Persistir Tema
 */
async function setTheme(isDark, shouldPersist) {
  if (isDark) {
    htmlRoot.classList.add('dark');
    document.body.classList.add('dark');
    if (toggleBtn) toggleBtn.setAttribute('aria-checked', 'true');
    if (toggleStatusText) toggleStatusText.textContent = 'Modo Oscuro';
  } else {
    htmlRoot.classList.remove('dark');
    document.body.classList.remove('dark');
    if (toggleBtn) toggleBtn.setAttribute('aria-checked', 'false');
    if (toggleStatusText) toggleStatusText.textContent = 'Modo Claro';
  }

  if (shouldPersist) {
    const modeName = isDark ? 'dark' : 'light';
    localStorage.setItem('theme_preference', modeName);

    // Persistir en backend API
    try {
      await fetch('/api/user/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: state.currentUserId,
          theme: modeName,
        }),
      });
    } catch (e) {
      console.warn('Backend sync failed, saved locally in localStorage:', e);
    }
  }
}

/**
 * 7. Simulador de Etapas para la clase / presentación
 */
async function switchSimulationStage(stageName) {
  try {
    const res = await fetch('/api/admin/toggle-simulation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stage: stageName }),
    });
    if (res.ok) {
      document.querySelectorAll('.btn-stage').forEach((btn) => {
        btn.classList.toggle('selected', btn.dataset.stage === stageName);
      });
      await fetchFeatureStatus();
      showToast(`Cambiado a ${stageName.toUpperCase()} exitosamente.`);
    }
  } catch (err) {
    console.error('Error switching stage:', err);
  }
}

/**
 * 8. Notificaciones tipo Toast accesibles
 */
function showToast(message) {
  let toast = document.getElementById('toastNotification');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toastNotification';
    toast.style.position = 'fixed';
    toast.style.bottom = '24px';
    toast.style.right = '24px';
    toast.style.padding = '12px 20px';
    toast.style.background = 'var(--bg-surface)';
    toast.style.color = 'var(--text-primary)';
    toast.style.border = '1px solid var(--border-strong)';
    toast.style.borderRadius = '8px';
    toast.style.boxShadow = 'var(--shadow-lg)';
    toast.style.zIndex = '9999';
    toast.style.fontSize = '0.875rem';
    toast.style.fontWeight = '500';
    toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
  }, 3500);
}

// Iniciar al cargar el DOM
document.addEventListener('DOMContentLoaded', initDashboard);

// Taller 6 - Pagos Express Logic
document.addEventListener('DOMContentLoaded', () => {
    const btnPagos = document.getElementById('btnPagosExpress');
    const pagoStatus = document.getElementById('pagoStatus');
    const telemetryLog = document.getElementById('telemetryLog');

    if (btnPagos) {
        btnPagos.addEventListener('click', async () => {
            pagoStatus.textContent = 'Procesando...';
            pagoStatus.style.color = 'var(--text-primary)';
            try {
                const response = await fetch(`/api/pagos-express?user_id=${window.appUserId || 'anonymous'}`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (response.status === 403) {
                    pagoStatus.textContent = '❌ Fallback: Pago Normal (Toggle Apagado)';
                    pagoStatus.style.color = '#ffab00';
                    telemetryLog.textContent = `[INFO] Fallback executed. user_id=${window.appUserId}`;
                } else if (response.status === 500) {
                    pagoStatus.textContent = '🚨 Error en Pago Express';
                    pagoStatus.style.color = '#ff5630';
                    telemetryLog.textContent = `[ERROR] Gateway timeout. user_id=${window.appUserId} (ALERTA!)`;
                } else {
                    pagoStatus.textContent = '✅ Pago Express Exitoso!';
                    pagoStatus.style.color = '#36b37e';
                    telemetryLog.textContent = `[SUCCESS] Pago 1-click convertido. user_id=${window.appUserId}`;
                }
            } catch (error) {
                pagoStatus.textContent = 'Error de red';
                telemetryLog.textContent = `[FATAL] Network error: ${error.message}`;
            }
        });
    }
});
