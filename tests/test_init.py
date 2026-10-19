"""Tests for entry setup and unload in HomeWizard Cloud."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant


async def test_setup_and_unload(
    hass: HomeAssistant, mock_homewizard_client: MagicMock, mock_config_entry
) -> None:
    """The entry loads, coordinator updates, and unloads cleanly."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_auth_failure(
    hass: HomeAssistant, mock_homewizard_client: MagicMock, mock_config_entry
) -> None:
    """Test setup failure due to authentication error."""
    from homewizard_cloud.exceptions import AuthenticationError

    mock_homewizard_client.authenticate.side_effect = AuthenticationError(
        "Invalid auth"
    )
    mock_config_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR


async def test_setup_connection_failure(
    hass: HomeAssistant, mock_homewizard_client: MagicMock, mock_config_entry
) -> None:
    """Test setup failure due to network/API error."""
    from homewizard_cloud.exceptions import APIError

    mock_homewizard_client.authenticate.side_effect = APIError("Network down")
    mock_config_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_coordinator_auth_failure_triggers_reauth(
    hass: HomeAssistant, mock_homewizard_client: MagicMock, mock_config_entry
) -> None:
    """When stream reports auth failure, coordinator starts reauth flow."""
    from unittest.mock import patch

    captured_callbacks = {}

    async def mock_listen(*args, **kwargs):
        captured_callbacks.update(kwargs)

    mock_homewizard_client.listen = mock_listen
    mock_config_entry.add_to_hass(hass)

    with patch.object(mock_config_entry, "async_start_reauth") as mock_start_reauth:
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert "on_auth_failed" in captured_callbacks
        await captured_callbacks["on_auth_failed"]()
        await hass.async_block_till_done()

        mock_start_reauth.assert_called_once_with(hass)
