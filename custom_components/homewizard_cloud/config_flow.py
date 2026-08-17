"""Config flow for HomeWizard Cloud integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)


class HomeWizardCloudConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HomeWizard Cloud."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self.email: str | None = None
        self.password: str | None = None
        self.devices: list[dict[str, str]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.email = user_input[CONF_EMAIL]
            self.password = user_input[CONF_PASSWORD]

            try:
                from homewizard_cloud import HomeWizardCloudClient

                def _test_login() -> list[dict[str, str]]:
                    client = HomeWizardCloudClient(email=self.email, password=self.password)
                    try:
                        return [
                            {"device_id": d.device_id, "name": d.name}
                            for d in client.get_p1_devices()
                        ]
                    finally:
                        client.close()

                self.devices = await self.hass.async_add_executor_job(_test_login)
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Login test failed: %s", err)
                errors["base"] = "invalid_auth"

            if not errors:
                if not self.devices:
                    errors["base"] = "no_devices"
                else:
                    return await self.async_step_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: pick a P1 device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = user_input["device"]
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"P1 Meter ({device_id})",
                data={
                    "email": self.email,
                    "password": self.password,
                    "device_id": device_id,
                },
            )

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): SelectSelector(
                        SelectSelectorConfig(
                            options=[d["device_id"] for d in self.devices],
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> ConfigFlow:
        """Return the options flow (none for now)."""
        return HomeWizardCloudOptionsFlow()


class HomeWizardCloudOptionsFlow(ConfigFlow):
    """Placeholder options flow."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """No options are configurable yet."""
        return self.async_create_entry(data=user_input or {})
