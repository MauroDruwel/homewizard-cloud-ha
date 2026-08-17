"""Sensor platform for HomeWizard Cloud integration."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfRatio,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ACTIVE_CURRENT_L1,
    ATTR_ACTIVE_CURRENT_L2,
    ATTR_ACTIVE_CURRENT_L3,
    ATTR_ACTIVE_POWER,
    ATTR_ACTIVE_POWER_L1,
    ATTR_ACTIVE_POWER_L2,
    ATTR_ACTIVE_POWER_L3,
    ATTR_ACTIVE_VOLTAGE_L1,
    ATTR_ACTIVE_VOLTAGE_L2,
    ATTR_ACTIVE_VOLTAGE_L3,
    ATTR_ANY_POWER_FAIL,
    ATTR_AVERAGE,
    ATTR_EXPORT_T1,
    ATTR_EXPORT_T2,
    ATTR_GAS,
    ATTR_GAS_TIMESTAMP,
    ATTR_IMPORT_T1,
    ATTR_IMPORT_T2,
    ATTR_LONG_POWER_FAIL,
    ATTR_ONLINE,
    ATTR_PEAK,
    ATTR_PEAK_TIMESTAMP,
    ATTR_TARIFF,
    ATTR_WIFI_STRENGTH,
    CONFIGURATION_URL,
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import HomeWizardCloudCoordinator

if TYPE_CHECKING:
    from . import HomeWizardCloudConfigEntry


def get_device_info(entry: HomeWizardCloudConfigEntry) -> DeviceInfo:
    """Get device info for the P1 meter."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.data["device_id"])},
        name="HomeWizard P1 Meter (Cloud)",
        manufacturer=MANUFACTURER,
        model="P1 Meter",
        configuration_url=CONFIGURATION_URL,
    )


class HomeWizardCloudSensor(CoordinatorEntity, SensorEntity):
    """Base class for HomeWizard Cloud sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HomeWizardCloudCoordinator,
        entry: HomeWizardCloudConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = get_device_info(entry)

    @property
    def _state(self) -> dict:
        return self.coordinator.state


# === LIVE SENSOR ===


class HomeWizardRealtimePowerSensor(HomeWizardCloudSensor):
    """Second-by-second live power from the tsdb stream."""

    _attr_name = "Live vermogen"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:flash"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_realtime_power"

    @property
    def native_value(self) -> float | None:
        """Return the current wattage."""
        return self.coordinator.get("realtime_w")

    @property
    def extra_state_attributes(self) -> dict:
        """Return per-phase wattages when available."""
        wattages = self.coordinator.data.get("realtime_wattages")
        attrs: dict = {}
        if isinstance(wattages, list):
            for i, value in enumerate(wattages, 1):
                attrs[f"phase_{i}_w"] = value
        return attrs


# === POWER SENSORS ===


class HomeWizardPowerSensor(HomeWizardCloudSensor):
    """Total active power (cloud average)."""

    _attr_name = "Vermogen"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gauge"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power"

    @property
    def native_value(self) -> float | None:
        """Return the total active power."""
        return self._state.get(ATTR_ACTIVE_POWER)


class HomeWizardPhasePowerSensor(HomeWizardCloudSensor):
    """Active power per phase."""

    _attr_name = "Vermogen fase 1"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:flash"

    def __init__(self, coordinator, entry, phase: int, key: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._phase = phase
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_power_l{phase}"

    @property
    def native_value(self) -> float | None:
        """Return the per-phase active power."""
        return self._state.get(self._key)


class HomeWizardAveragePowerSensor(HomeWizardCloudSensor):
    """Average active power."""

    _attr_name = "Gemiddeld vermogen"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_average_power"

    @property
    def native_value(self) -> float | None:
        """Return the average active power."""
        return self._state.get(ATTR_AVERAGE)


# === VOLTAGE / CURRENT SENSORS ===


class HomeWizardVoltageSensor(HomeWizardCloudSensor):
    """Voltage per phase."""

    _attr_name = "Spanning fase 1"
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:flash-triangle"

    def __init__(self, coordinator, entry, phase: int, key: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._phase = phase
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_voltage_l{phase}"

    @property
    def native_value(self) -> float | None:
        """Return the per-phase voltage."""
        return self._state.get(self._key)


class HomeWizardCurrentSensor(HomeWizardCloudSensor):
    """Current per phase."""

    _attr_name = "Stroom fase 1"
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:current-ac"

    def __init__(self, coordinator, entry, phase: int, key: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._phase = phase
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_current_l{phase}"

    @property
    def native_value(self) -> float | None:
        """Return the per-phase current."""
        return self._state.get(self._key)


# === ENERGY SENSORS ===


class HomeWizardImportSensor(HomeWizardCloudSensor):
    """Energy imported (tariff 1+2)."""

    _attr_name = "Import energie"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:transmission-tower-import"

    def __init__(self, coordinator, entry, key: str, tariff: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._key = key
        self._tariff = tariff
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def native_value(self) -> float | None:
        """Return the imported energy for the tariff."""
        return self._state.get(self._key)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the tariff."""
        return {"tariff": self._tariff}


# === TARIFF / GAS SENSORS ===


class HomeWizardTariffSensor(HomeWizardCloudSensor):
    """Current active tariff."""

    _attr_name = "Actief tarief"
    _attr_icon = "mdi:counter"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_tariff"

    @property
    def native_value(self) -> str | None:
        """Return the active tariff."""
        tariff = self._state.get(ATTR_TARIFF)
        return str(tariff) if tariff is not None else None


class HomeWizardGasSensor(HomeWizardCloudSensor):
    """Total gas consumption."""

    _attr_name = "Gas"
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_device_class = SensorDeviceClass.GAS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_gas"

    @property
    def native_value(self) -> float | None:
        """Return the total gas."""
        return self._state.get(ATTR_GAS)


class HomeWizardGasTimestampSensor(HomeWizardCloudSensor):
    """Timestamp of the last gas reading."""

    _attr_name = "Gas laatst gelezen"
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_gas_timestamp"

    @property
    def native_value(self) -> str | None:
        """Return the gas timestamp."""
        return self._state.get(ATTR_GAS_TIMESTAMP)


# === PEAK / FAILURE SENSORS ===


class HomeWizardPeakSensor(HomeWizardCloudSensor):
    """Monthly power peak."""

    _attr_name = "Maandpiek"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:chart-areaspline"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_peak"

    @property
    def native_value(self) -> float | None:
        """Return the monthly peak power."""
        return self._state.get(ATTR_PEAK)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the peak timestamp."""
        return {
            "peak_timestamp": self._state.get(ATTR_PEAK_TIMESTAMP),
        }


class HomeWizardPowerFailSensor(HomeWizardCloudSensor):
    """Power fail counters."""

    _attr_name = "Stroomuitval"
    _attr_icon = "mdi:power-plug-off"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power_fail"

    @property
    def native_value(self) -> int | None:
        """Return the total number of power failures."""
        any_fail = self._state.get(ATTR_ANY_POWER_FAIL)
        long_fail = self._state.get(ATTR_LONG_POWER_FAIL)
        if any_fail is None and long_fail is None:
            return None
        return (any_fail or 0) + (long_fail or 0)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the long power fail count."""
        return {"long_power_fail_count": self._state.get(ATTR_LONG_POWER_FAIL)}


# === DIAGNOSTIC SENSORS ===


class HomeWizardOnlineSensor(HomeWizardCloudSensor):
    """Device online status."""

    _attr_name = "Online"
    _attr_icon = "mdi:cloud-check"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_online"

    @property
    def native_value(self) -> str | None:
        """Return the online status."""
        online = self._state.get(ATTR_ONLINE)
        return "Online" if online else "Offline"


class HomeWizardWifiSensor(HomeWizardCloudSensor):
    """WiFi signal strength."""

    _attr_name = "WiFi signaal"
    _attr_native_unit_of_measurement = UnitOfRatio.PERCENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:wifi"

    def __init__(self, coordinator, entry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_wifi"

    @property
    def native_value(self) -> int | None:
        """Return the WiFi strength percentage."""
        return self._state.get(ATTR_WIFI_STRENGTH)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HomeWizardCloudConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HomeWizard Cloud sensors based on a config entry."""
    coordinator = entry.runtime_data

    entities: list[SensorEntity] = [
        HomeWizardRealtimePowerSensor(coordinator, entry),
        HomeWizardPowerSensor(coordinator, entry),
        HomeWizardAveragePowerSensor(coordinator, entry),
        HomeWizardTariffSensor(coordinator, entry),
        HomeWizardImportSensor(coordinator, entry, ATTR_IMPORT_T1, "1"),
        HomeWizardImportSensor(coordinator, entry, ATTR_IMPORT_T2, "2"),
        HomeWizardImportSensor(coordinator, entry, ATTR_EXPORT_T1, "1"),
        HomeWizardImportSensor(coordinator, entry, ATTR_EXPORT_T2, "2"),
        HomeWizardGasSensor(coordinator, entry),
        HomeWizardGasTimestampSensor(coordinator, entry),
        HomeWizardPeakSensor(coordinator, entry),
        HomeWizardPowerFailSensor(coordinator, entry),
        HomeWizardOnlineSensor(coordinator, entry),
        HomeWizardWifiSensor(coordinator, entry),
    ]

    for phase, key in (
        (1, ATTR_ACTIVE_POWER_L1),
        (2, ATTR_ACTIVE_POWER_L2),
        (3, ATTR_ACTIVE_POWER_L3),
    ):
        entities.append(HomeWizardPhasePowerSensor(coordinator, entry, phase, key))

    for phase, key in (
        (1, ATTR_ACTIVE_VOLTAGE_L1),
        (2, ATTR_ACTIVE_VOLTAGE_L2),
        (3, ATTR_ACTIVE_VOLTAGE_L3),
    ):
        entities.append(HomeWizardVoltageSensor(coordinator, entry, phase, key))

    for phase, key in (
        (1, ATTR_ACTIVE_CURRENT_L1),
        (2, ATTR_ACTIVE_CURRENT_L2),
        (3, ATTR_ACTIVE_CURRENT_L3),
    ):
        entities.append(HomeWizardCurrentSensor(coordinator, entry, phase, key))

    async_add_entities(entities)
