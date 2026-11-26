"""Tests for entry setup and unload in HomeWizard Cloud."""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import MagicMock

import pytest
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


async def test_setup_does_not_block_on_long_running_listen(
    hass: HomeAssistant, mock_homewizard_client: MagicMock, mock_config_entry
) -> None:
    """Long-running WebSocket listener must run as a background task so startup is not blocked."""
    listen_started = asyncio.Event()
    listen_cancelled = False

    async def forever_listen(*args, **kwargs) -> None:
        nonlocal listen_cancelled
        listen_started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            listen_cancelled = True
            raise

    mock_homewizard_client.listen = forever_listen
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await asyncio.wait_for(hass.async_block_till_done(), timeout=2.0)

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert listen_started.is_set()
    coordinator = mock_config_entry.runtime_data
    assert coordinator._listen_task is not None
    assert not coordinator._listen_task.done()

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await asyncio.wait_for(hass.async_block_till_done(), timeout=2.0)

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert listen_cancelled is True
    assert mock_homewizard_client.close.called


async def test_shutdown_cancels_listen_task_cleanly(
    hass: HomeAssistant,
    mock_homewizard_client: MagicMock,
    mock_config_entry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Stopping Home Assistant cancels the background listen task cleanly without delay."""
    listen_cancelled = False

    async def forever_listen(*args, **kwargs) -> None:
        nonlocal listen_cancelled
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            listen_cancelled = True
            raise

    mock_homewizard_client.listen = forever_listen
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await asyncio.wait_for(hass.async_block_till_done(), timeout=2.0)

    with caplog.at_level(logging.WARNING):
        await asyncio.wait_for(hass.async_stop(), timeout=5.0)

    assert listen_cancelled is True
    assert mock_homewizard_client.close.called
    assert "was still running after final writes shutdown stage" not in caplog.text
