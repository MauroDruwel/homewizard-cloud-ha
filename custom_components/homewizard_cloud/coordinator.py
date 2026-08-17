"""WebSocket push coordinator for HomeWizard Cloud."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from homewizard_cloud import HomeWizardCloudClient
from homewizard_cloud.models import RealtimeMeasurement

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class HomeWizardCloudCoordinator(DataUpdateCoordinator[dict]):
    """Manages the cloud WebSocket streams and latest P1 state."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: HomeWizardCloudClient,
        device_id: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=None,
        )

        self.entry = entry
        self.client = client
        self.device_id = device_id
        self.last_update_time: datetime | None = None
        self.connected: bool = False
        self.realtime_connected: bool = False

        self.data = {"state": {}, "realtime_w": None}
        self._listen_task: asyncio.Task | None = None

    async def async_start(self) -> None:
        """Start the WebSocket streams in a background task."""
        if self._listen_task is not None and not self._listen_task.done():
            return

        self.async_set_updated_data(self.data)

        async def _on_state(_device_id: str, state: dict) -> None:
            self.async_set_updated_data({**self.data, "state": state})
            self.last_update_time = dt_util.now()

        async def _on_realtime(measurement: RealtimeMeasurement) -> None:
            self.async_set_updated_data(
                {
                    **self.data,
                    "realtime_w": measurement.wattage,
                    "realtime_wattages": measurement.wattages,
                }
            )

        async def _on_connection(connected: bool) -> None:
            self.connected = connected
            _LOGGER.info(
                "WebSocket %s for device %s",
                "connected" if connected else "disconnected",
                self.device_id,
            )
            self.async_update_listeners()

        async def _on_realtime_connection(connected: bool) -> None:
            self.realtime_connected = connected
            _LOGGER.info(
                "Realtime WebSocket %s for device %s",
                "connected" if connected else "disconnected",
                self.device_id,
            )
            self.async_update_listeners()

        self._listen_task = self.hass.async_create_task(
            self.client.listen(
                self.device_id,
                on_state=_on_state,
                on_realtime=_on_realtime,
                on_connection=_on_connection,
                on_realtime_connection=_on_realtime_connection,
            ),
            name=f"{DOMAIN}_listen_{self.device_id}",
        )

    async def async_stop(self) -> None:
        """Stop the streams."""
        self.client.close()
        if self._listen_task is not None:
            if not self._listen_task.done():
                self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None

    @property
    def state(self) -> dict:
        """Latest full P1 state."""
        return self.data.get("state", {})

    def get(self, key: str):
        """Get a value from the latest state (or realtime)."""
        if key == "realtime_w":
            return self.data.get("realtime_w")
        return self.state.get(key)
