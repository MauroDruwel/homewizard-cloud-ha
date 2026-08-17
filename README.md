# HomeWizard Cloud

Home Assistant integration for streaming your **HomeWizard P1 meter from the cloud**
over WebSocket — no local device access needed. Works anywhere your Home Assistant
has internet.

Based on the cloud API research by [Sven Serlier](https://github.com/smarthomesven/homey-homewizard-energy-cloud)
and the implementation in [jtebbens/com.homewizard](https://github.com/jtebbens/com.homewizard).

## Install (HACS)

1. Add this repository as a custom repository in HACS (`HomeWizard Cloud`, category: **Integration**)
2. Install and restart Home Assistant
3. Add the integration via **Settings → Devices & Services → Add Integration → HomeWizard Cloud**
4. Enter your HomeWizard account email + password and pick your P1 meter

> Requires the [`homewizard-cloud`](https://github.com/MauroDruwel/homewizard-cloud)
> Python library (installed automatically from PyPI).

## Sensors

| Sensor | Device class | Unit |
|---|---|---|
| Live vermogen (1s WebSocket stream) | power | W |
| Vermogen (cloud average) | power | W |
| Vermogen fase 1-3 | power | W |
| Spanning fase 1-3 | voltage | V |
| Stroom fase 1-3 | current | A |
| Import energie (t1, t2) | energy | kWh |
| Export energie (t1, t2) | energy | kWh |
| Actief tarief | — | — |
| Gas | gas | m³ |
| Gas laatst gelezen | — | — |
| Maandpiek | power | W |
| Stroomuitval | — | — |
| Online | — | — |
| WiFi signaal | — | % |
| **WebSocket verbinding** (binary) | connectivity | — |

The live sensor updates **every second** via the tsdb WebSocket stream; the state
sensors update when the cloud pushes deltas (1s) or full states (40s). The
*WebSocket verbinding* binary sensor shows `Connected`/`Disconnected` based on
both streams and exposes `main_stream_connected` and
`realtime_stream_connected` attributes for troubleshooting.

## Development

```bash
# run HA locally with the component symlinked into custom_components
```

## Credits

Cloud API research by Sven Serlier ([homey-homewizard-energy-cloud](https://github.com/smarthomesven/homey-homewizard-energy-cloud)).
