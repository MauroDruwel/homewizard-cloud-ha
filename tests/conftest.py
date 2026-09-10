"""Fixtures for HomeWizard Cloud tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.homewizard_cloud.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Enable loading of the custom integration in every test."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="HomeWizard P1 Meter",
        data={
            CONF_EMAIL: "user@example.com",
            CONF_PASSWORD: "secret_password",
            "device_id": "hw_p1_12345",
        },
        entry_id="hw_test_entry_id",
        unique_id="hw_p1_12345",
    )


@pytest.fixture
def mock_homewizard_client() -> Generator[MagicMock]:
    """Patch HomeWizardCloudClient."""
    with patch("homewizard_cloud.HomeWizardCloudClient") as mock_cls:
        client = MagicMock()
        client.close.return_value = None
        
        device_mock = MagicMock()
        device_mock.device_id = "hw_p1_12345"
        device_mock.name = "HomeWizard P1 Meter"
        
        client.get_p1_devices = AsyncMock(return_value=[device_mock])
        client.get_p1_state = AsyncMock(return_value={
            "active_power_w": 350.0,
            "total_power_import_t1_kwh": 1250.5,
            "total_power_export_t1_kwh": 450.2,
            "online": True,
        })
        mock_cls.return_value = client
        yield client
