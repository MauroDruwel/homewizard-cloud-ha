"""HomeWizard Cloud integration for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .const import CONF_EMAIL, CONF_PASSWORD
from .coordinator import HomeWizardCloudCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]

type HomeWizardCloudConfigEntry = ConfigEntry[HomeWizardCloudCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: HomeWizardCloudConfigEntry
) -> bool:
    """Set up HomeWizard Cloud from a config entry."""
    from homewizard_cloud import HomeWizardCloudClient
    from homewizard_cloud.exceptions import APIError, AuthenticationError

    client = HomeWizardCloudClient(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
    )

    try:
        await client.authenticate()
    except AuthenticationError as err:
        client.close()
        raise ConfigEntryAuthFailed(err) from err
    except (APIError, OSError) as err:
        client.close()
        raise ConfigEntryNotReady(f"Could not reach HomeWizard Cloud: {err}") from err

    coordinator = HomeWizardCloudCoordinator(
        hass,
        entry,
        client,
        device_id=entry.data["device_id"],
    )
    await coordinator.async_start()

    entry.runtime_data = coordinator
    entry.async_on_unload(coordinator.async_stop)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: HomeWizardCloudConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
