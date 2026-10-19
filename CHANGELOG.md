# Changelog

All notable changes to this project are documented here.

## [1.0.5] - 2026-10-19

### Fixed
- Pass Home Assistant's default SSL context (`homeassistant.util.ssl.get_default_context()`) to `HomeWizardCloudClient` to prevent event-loop blocking certificate loading.
- Surface authentication failures via `on_auth_failed` and immediately trigger reauth (`entry.async_start_reauth(hass)`) when tokens or credentials are rejected.
- Bumped `homewizard-cloud` requirement to `>=1.0.3`.

## [1.0.4] - 2026-10-19

### Fixed
- Handled setup auth/network errors and added reauth flow.

## [1.0.2] - 2026-08-17

### Fixed
- Corrected the Home Assistant ratio unit constant to
  `UnitOfRatio.PERCENTAGE`.
- Corrected the coordinator lifecycle so entities become available through
  `async_set_updated_data`.
- Corrected the options flow base class.

### Added
- Runtime platform-import validation against Home Assistant in CI.
- Separate main and realtime WebSocket status attributes on the diagnostic
  connectivity binary sensor.

## [1.0.1] - 2026-08-17

### Fixed
- Config flow now awaits the async library client correctly.

### Added
- WebSocket connectivity diagnostic binary sensor.
