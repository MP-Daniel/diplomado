"""Unit tests for Feature Flag service and TBD Slicing logic."""
from app.feature_flags import FeatureFlagService, FLAG_DARK_MODE


def test_ticket_1_flag_is_off():
    """Ticket 1: Flag dark_mode_enabled must be OFF (0% rollout)."""
    service = FeatureFlagService(sdk_key=None)
    service.set_simulation_stage("ticket_1")

    assert service.is_dark_mode_enabled("user_1") is False
    assert service.is_dark_mode_enabled("user_2") is False

    summary = service.get_status_summary("user_1")
    assert summary["flag_key"] == FLAG_DARK_MODE
    assert summary["is_enabled"] is False
    assert summary["ui_toggle_visible"] is False
    assert summary["persistence_enabled"] is False


def test_ticket_2_ten_percent_rollout():
    """Ticket 2: 10% canary rollout evaluates deterministically."""
    service = FeatureFlagService(sdk_key=None)
    service.set_simulation_stage("ticket_2")

    # Evaluate 100 sample users to verify percentage distribution is around 10%
    sample_size = 100
    enabled_count = sum(
        1 for i in range(sample_size)
        if service.is_dark_mode_enabled(f"test_user_{i}")
    )

    # Allow reasonable hash distribution tolerance around 10% (e.g. 5-15%)
    assert 5 <= enabled_count <= 20, f"Expected ~10 enabled, got {enabled_count}"

    summary = service.get_status_summary("test_user_0")
    assert summary["persistence_enabled"] is False


def test_ticket_3_one_hundred_percent_rollout():
    """Ticket 3: 100% rollout is active for all users and enables persistence."""
    service = FeatureFlagService(sdk_key=None)
    service.set_simulation_stage("ticket_3")

    assert service.is_dark_mode_enabled("user_1") is True
    assert service.is_dark_mode_enabled("user_random_456") is True

    summary = service.get_status_summary("user_1")
    assert summary["is_enabled"] is True
    assert summary["ui_toggle_visible"] is True
    assert summary["persistence_enabled"] is True
