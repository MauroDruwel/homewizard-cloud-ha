"""Tests for the HomeWizard Cloud config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.homewizard_cloud.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    DOMAIN,
)


async def test_flow_user_success(hass: HomeAssistant) -> None:
    """Test successful user step followed by device selection."""
    with patch("homewizard_cloud.HomeWizardCloudClient") as mock_client_cls:
        client = MagicMock()
        client.close.return_value = None
        device = MagicMock()
        device.device_id = "hw_123"
        device.name = "My P1 Meter"
        client.get_p1_devices = AsyncMock(return_value=[device])
        mock_client_cls.return_value = client

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "user"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_EMAIL: "test@example.com",
                CONF_PASSWORD: "secret_password",
            },
        )
        assert result2["type"] is FlowResultType.FORM
        assert result2["step_id"] == "device"

        result3 = await hass.config_entries.flow.async_configure(
            result2["flow_id"],
            {"device": "hw_123"},
        )
        assert result3["type"] is FlowResultType.CREATE_ENTRY
        assert result3["title"] == "P1 Meter (hw_123)"
        assert result3["data"]["device_id"] == "hw_123"


async def test_flow_user_invalid_auth(hass: HomeAssistant) -> None:
    """Test authentication failure in config flow."""
    from homewizard_cloud.exceptions import AuthenticationError

    with patch("homewizard_cloud.HomeWizardCloudClient") as mock_client_cls:
        client = MagicMock()
        client.get_p1_devices = AsyncMock(side_effect=AuthenticationError("Auth error"))
        mock_client_cls.return_value = client

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_EMAIL: "bad@example.com",
                CONF_PASSWORD: "wrong",
            },
        )
        assert result2["type"] is FlowResultType.FORM
        assert result2["errors"]["base"] == "invalid_auth"


async def test_flow_user_cannot_connect(hass: HomeAssistant) -> None:
    """Test connection failure in config flow."""
    with patch("homewizard_cloud.HomeWizardCloudClient") as mock_client_cls:
        client = MagicMock()
        client.get_p1_devices = AsyncMock(side_effect=OSError("Network error"))
        mock_client_cls.return_value = client

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_EMAIL: "bad@example.com",
                CONF_PASSWORD: "wrong",
            },
        )
        assert result2["type"] is FlowResultType.FORM
        assert result2["errors"]["base"] == "cannot_connect"


async def test_flow_reauth_success(hass: HomeAssistant, mock_config_entry) -> None:
    """Test successful reauthentication."""
    mock_config_entry.add_to_hass(hass)

    with patch("homewizard_cloud.HomeWizardCloudClient") as mock_client_cls:
        client = MagicMock()
        client.authenticate = AsyncMock(return_value="new_token")
        client.close.return_value = None
        mock_client_cls.return_value = client

        result = await mock_config_entry.start_reauth_flow(hass)
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "reauth_confirm"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "new_secret_password"},
        )
        assert result2["type"] is FlowResultType.ABORT
        assert result2["reason"] == "reauth_successful"
        assert mock_config_entry.data[CONF_PASSWORD] == "new_secret_password"
