"""Tests for entity translations and English fallback in HomeWizard Cloud."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

TRANSLATIONS_DIR = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "homewizard_cloud"
    / "translations"
)


def _collect_key_paths(obj: dict, prefix: str = "") -> set[str]:
    paths: set[str] = set()
    for key, value in obj.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            paths |= _collect_key_paths(value, path)
        else:
            paths.add(path)
    return paths


def test_translation_files_match_keys() -> None:
    """Ensure en, nl, and fr translation files contain identical key paths."""
    en = json.loads((TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"))
    nl = json.loads((TRANSLATIONS_DIR / "nl.json").read_text(encoding="utf-8"))
    fr = json.loads((TRANSLATIONS_DIR / "fr.json").read_text(encoding="utf-8"))

    en_keys = _collect_key_paths(en)
    assert _collect_key_paths(nl) == en_keys
    assert _collect_key_paths(fr) == en_keys


@pytest.mark.parametrize(
    ("language", "expected_names"),
    [
        (
            "en",
            {
                "hw_test_entry_id_realtime_power": "HomeWizard P1 Meter (Cloud) Live power",
                "hw_test_entry_id_power_l1": "HomeWizard P1 Meter (Cloud) Power phase 1",
                "hw_test_entry_id_total_power_import_t1_kwh": "HomeWizard P1 Meter (Cloud) Import energy tariff 1",
                "hw_test_entry_id_connection": "HomeWizard P1 Meter (Cloud) WebSocket connection",
            },
        ),
        (
            "fr",
            {
                "hw_test_entry_id_realtime_power": "HomeWizard P1 Meter (Cloud) Puissance en direct",
                "hw_test_entry_id_power_l1": "HomeWizard P1 Meter (Cloud) Puissance phase 1",
                "hw_test_entry_id_total_power_import_t1_kwh": "HomeWizard P1 Meter (Cloud) Énergie importée tarif 1",
                "hw_test_entry_id_connection": "HomeWizard P1 Meter (Cloud) Connexion WebSocket",
            },
        ),
        (
            "nl",
            {
                "hw_test_entry_id_realtime_power": "HomeWizard P1 Meter (Cloud) Live vermogen",
                "hw_test_entry_id_power_l1": "HomeWizard P1 Meter (Cloud) Vermogen fase 1",
                "hw_test_entry_id_total_power_import_t1_kwh": "HomeWizard P1 Meter (Cloud) Import energie tarief 1",
                "hw_test_entry_id_connection": "HomeWizard P1 Meter (Cloud) WebSocket verbinding",
            },
        ),
        (
            "de",
            {
                "hw_test_entry_id_realtime_power": "HomeWizard P1 Meter (Cloud) Live power",
                "hw_test_entry_id_power_l1": "HomeWizard P1 Meter (Cloud) Power phase 1",
                "hw_test_entry_id_total_power_import_t1_kwh": "HomeWizard P1 Meter (Cloud) Import energy tariff 1",
                "hw_test_entry_id_connection": "HomeWizard P1 Meter (Cloud) WebSocket connection",
            },
        ),
    ],
)
async def test_entity_name_localization_and_fallback(
    hass: HomeAssistant,
    mock_homewizard_client: MagicMock,
    mock_config_entry,
    language: str,
    expected_names: dict[str, str],
) -> None:
    """Verify entity names localize in EN/FR/NL and fall back to EN otherwise."""
    hass.config.language = language
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)
    assert len(entries) == 24

    by_unique_id = {e.unique_id: e for e in entries}
    for unique_id, expected_friendly_name in expected_names.items():
        entry = by_unique_id[unique_id]
        state = hass.states.get(entry.entity_id)
        assert state is not None
        assert state.attributes["friendly_name"] == expected_friendly_name
