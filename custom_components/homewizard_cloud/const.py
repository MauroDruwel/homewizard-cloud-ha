"""Constants for the HomeWizard Cloud integration."""

from __future__ import annotations

DOMAIN = "homewizard_cloud"

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

MANUFACTURER = "HomeWizard"
CONFIGURATION_URL = "https://www.homewizard.com/"

DEVICE_MODEL = "P1 Meter (Cloud)"

# Sensor keys present in the P1 state payload
ATTR_ACTIVE_POWER = "active_power_w"
ATTR_ACTIVE_POWER_L1 = "active_power_l1_w"
ATTR_ACTIVE_POWER_L2 = "active_power_l2_w"
ATTR_ACTIVE_POWER_L3 = "active_power_l3_w"
ATTR_ACTIVE_VOLTAGE_L1 = "active_voltage_l1_v"
ATTR_ACTIVE_VOLTAGE_L2 = "active_voltage_l2_v"
ATTR_ACTIVE_VOLTAGE_L3 = "active_voltage_l3_v"
ATTR_ACTIVE_CURRENT = "active_current_a"
ATTR_ACTIVE_CURRENT_L1 = "active_current_l1_a"
ATTR_ACTIVE_CURRENT_L2 = "active_current_l2_a"
ATTR_ACTIVE_CURRENT_L3 = "active_current_l3_a"
ATTR_IMPORT_T1 = "total_power_import_t1_kwh"
ATTR_IMPORT_T2 = "total_power_import_t2_kwh"
ATTR_EXPORT_T1 = "total_power_export_t1_kwh"
ATTR_EXPORT_T2 = "total_power_export_t2_kwh"
ATTR_TARIFF = "current_active_tariff"
ATTR_GAS = "total_gas_m3"
ATTR_GAS_TIMESTAMP = "gas_timestamp"
ATTR_PEAK = "monthly_power_peak_w"
ATTR_PEAK_TIMESTAMP = "monthly_power_peak_timestamp"
ATTR_AVERAGE = "active_power_average_w"
ATTR_ANY_POWER_FAIL = "any_power_fail_count"
ATTR_LONG_POWER_FAIL = "long_power_fail_count"
ATTR_WIFI_STRENGTH = "wifi_strength"
ATTR_ONLINE = "online"
ATTR_IP_ADDRESS = "ip_address"
ATTR_MODEL = "model"
ATTR_FIRMWARE = "firmware"
ATTR_SMARTMETER_ID = "smartmeter_id"
