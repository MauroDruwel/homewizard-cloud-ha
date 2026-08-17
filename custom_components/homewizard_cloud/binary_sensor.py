"""Binary sensor platform for HomeWizard Cloud integration."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONFIGURATION_URL, DOMAIN, MANUFACTURER
from .coordinator import HomeWizardCloudCoordinator

if TYPE_CHECKING:
    from . import HomeWizardCloudConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HomeWizardCloudConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HomeWizard Cloud binary sensors based on a config entry."""
    coordinator = entry.runtime_data
    async_add_entities([HomeWizardConnectionSensor(coordinator, entry)])


class HomeWizardConnectionSensor(CoordinatorEntity, BinarySensorEntity):
    """WebSocket connection status for the P1 meter."""

    _attr_has_entity_name = True
    _attr_name = "WebSocket verbinding"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:connection"

    def __init__(
        self,
        coordinator: HomeWizardCloudCoordinator,
        entry: HomeWizardCloudConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_connection"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data["device_id"])},
            name="HomeWizard P1 Meter (Cloud)",
            manufacturer=MANUFACTURER,
            model="P1 Meter",
            configuration_url=CONFIGURATION_URL,
        )

    @property
    def is_on(self) -> bool:
        """Return the connection state."""
        return self.coordinator.connected