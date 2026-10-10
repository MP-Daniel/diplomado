"""Feature Flag management module supporting ConfigCat SDK and local TBD Slicing simulation."""
import hashlib
import logging
from typing import Dict, Any, Optional
import configcatclient
from configcatclient.user import User

from app.config import settings

logger = logging.getLogger(__name__)

# Feature flag key matching Workshop specification
FLAG_DARK_MODE = "dark_mode_enabled"
FLAG_PAGOS_EXPRESS = "pagos-express-v1"

# Metadata for the 3 Slicing Tickets from Workshop 3
TICKETS_METADATA = {
    "ticket_1": {
        "id": "TICKET-1",
        "title": "CSS Variables y Lógica de clases en HTML raíz",
        "description": (
            "Definir variables CSS/tema oscuro y lógica de cambio de clase "
            "en el HTML raíz, detrás del flag dark_mode_enabled apagado."
        ),
        "rollout_percentage": 0,
        "is_enabled_default": False,
        "ui_toggle_visible": False,
        "persistence_enabled": False,
        "status": "In Production (Hidden behind Feature Toggle)",
    },
    "ticket_2": {
        "id": "TICKET-2",
        "title": "Botón Toggle visible para Canary Users (10%)",
        "description": (
            "Agregar el botón toggle visible solo al 10% de usuarios vía toggle, "
            "sin persistencia todavía."
        ),
        "rollout_percentage": 10,
        "is_enabled_default": False,  # Evaluated by user identifier hash
        "ui_toggle_visible": True,    # Only for the 10%
        "persistence_enabled": False,
        "status": "In Canary Testing (10% Rollout)",
    },
    "ticket_3": {
        "id": "TICKET-3",
        "title": "Persistencia de Preferencia y Rollout al 100%",
        "description": (
            "Guardar la preferencia (localStorage y backend) y subir el flag al 100%."
        ),
        "rollout_percentage": 100,
        "is_enabled_default": True,
        "ui_toggle_visible": True,
        "persistence_enabled": True,
        "status": "General Availability (100% Rollout + Persisted)",
    },
}


class FeatureFlagService:
    """Service to evaluate feature flags using ConfigCat or local simulation."""

    def __init__(self, sdk_key: Optional[str] = None):
        self.sdk_key = sdk_key or settings.CONFIGCAT_SDK_KEY
        self.client: Optional[configcatclient.ConfigCatClient] = None
        self.current_simulated_stage = settings.DEFAULT_STAGE

        if self.sdk_key:
            try:
                # Initialize real ConfigCat SDK client
                self.client = configcatclient.get(
                    sdk_key=self.sdk_key,
                    options=configcatclient.ConfigCatOptions(
                        polling_mode=configcatclient.PollingMode.auto_poll(
                            poll_interval_seconds=60)
                    )
                )
                logger.info(
                    "ConfigCat SDK initialized successfully with provided SDK Key.")
            except Exception as e:
                logger.error(
                    f"Error initializing ConfigCat client: {e}. Falling back to simulation.")
                self.client = None

    @property
    def is_cloud_mode(self) -> bool:
        """Returns True if connected to ConfigCat cloud."""
        return self.client is not None

    def evaluate_user_in_percentage(self, user_id: str, percentage: int) -> bool:
        """Deterministic percentage evaluation based on user hash (0-99)."""
        if percentage <= 0:
            return False
        if percentage >= 100:
            return True
        hash_val = int(hashlib.md5(
            user_id.encode("utf-8")).hexdigest()[:6], 16)
        bucket = hash_val % 100
        return bucket < percentage

    def is_dark_mode_enabled(self, user_id: Optional[str] = "anonymous") -> bool:
        """Evaluates whether dark_mode_enabled flag is active for the given user."""
        # 1. Real ConfigCat evaluation if connected
        if self.client:
            try:
                cc_user = User(identifier=user_id or "anonymous")
                return bool(self.client.get_value(FLAG_DARK_MODE, False, cc_user))
            except Exception as e:
                logger.error(
                    f"ConfigCat evaluation failed: {e}. Using fallback.")
                return False

        # 2. Local Simulation Mode according to Workshop 3 Tickets
        stage = self.current_simulated_stage

        if stage == "ticket_1":
            return False

        if stage == "ticket_2":
            # 10% canary rollout rule
            return self.evaluate_user_in_percentage(user_id or "anonymous", 10)

        if stage == "ticket_3":
            return True

        return False

    def is_pagos_express_enabled(self, user_id: Optional[str] = "anonymous") -> bool:
        """Evaluates whether pagos-express-v1 flag is active for the given user."""
        if self.client:
            try:
                cc_user = User(identifier=user_id or "anonymous")
                return bool(self.client.get_value(FLAG_PAGOS_EXPRESS, False, cc_user))
            except Exception as e:
                logger.error(
                    f"ConfigCat evaluation failed: {e}. Using fallback.")
                return False
        return False  # Apagado por defecto en simulacion

    def get_status_summary(self, user_id: Optional[str] = "anonymous") -> Dict[str, Any]:
        """Provides full context for the dashboard UI, testing, and Miro workshop verification."""
        user_id_clean = user_id or "anonymous"
        is_enabled = self.is_dark_mode_enabled(user_id_clean)
        is_pagos_express = self.is_pagos_express_enabled(user_id_clean)

        stage_meta = TICKETS_METADATA.get(
            self.current_simulated_stage, TICKETS_METADATA["ticket_1"])

        ui_visible = is_enabled if self.current_simulated_stage == "ticket_2" else (
            stage_meta["ui_toggle_visible"] if not self.is_cloud_mode else is_enabled
        )

        persistence = stage_meta["persistence_enabled"] if not self.is_cloud_mode else is_enabled

        return {
            "flag_key": FLAG_DARK_MODE,
            "is_enabled": is_enabled,
            "pagos_express_enabled": is_pagos_express,
            "user_id": user_id_clean,
            "provider": "ConfigCat Cloud" if self.is_cloud_mode else "Simulated TBD Slicing",
            "active_stage": self.current_simulated_stage,
            "stage_info": stage_meta,
            "ui_toggle_visible": ui_visible,
            "persistence_enabled": persistence,
            "all_stages": TICKETS_METADATA,
        }

    def set_simulation_stage(self, stage: str) -> bool:
        """Allows toggling simulation stage for demonstration and QA."""
        if stage in TICKETS_METADATA:
            self.current_simulated_stage = stage
            return True
        return False

    def close(self):
        """Cleanup ConfigCat client connections."""
        if self.client:
            configcatclient.close_all()


# Global singleton instance
feature_flag_service = FeatureFlagService()
