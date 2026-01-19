# E3/DC Home Assistant Integration
Custom Home Assistant integration for E3/DC Hauskraftwerk systems using local Modbus/TCP.

## Features
- Local polling (no cloud)
- Read-only sensors (initially)
- PV production
- Battery SOC
- Grid import/export
- House consumption

## Requirements
- Home Assistant 2023.9+
- E3/DC system with Modbus/TCP enabled
- Network access to the E3/DC device

## Installation

### Manual
1. Copy `custom_components/e3dc` to your Home Assistant config directory.
2. Restart Home Assistant.
3. Add the integration via **Settings > Devices & Services**.

## Configuration
The integration is configured via the UI (Config Flow).
You will need:
- IP address of the E3/DC system
- Modbus port (default: 502)
- Optional: register offset (auto-detected via magic byte)

## Available Registers (Simple Mode)
- System information: manufacturer, model, serial number, firmware release
- Power values: PV, battery, house, grid, additional feed-in, wallbox power
- Status: SOC, EMS status bits, autarky, self-consumption
- DC strings: voltage, current (factor 0.01), power
- SG-Ready status

## Addressing and Magic Byte
- Simple Mode magic byte is `0xE3DC` at register `40001`.
- Some clients use different base addresses; the integration probes offsets
  around `40001` and applies the detected offset to all registers.
- SunSpec mode is not supported; its magic is `0x53756e53` (`SunS`).

## Troubleshooting
- If setup fails, verify Modbus/TCP is enabled and reachable on port 502.
- If values look unreasonable, ensure Simple Mode is enabled and that the
  register offset was detected correctly.

## Limitations
- No write/control functions yet
- Register mapping may differ between E3/DC firmware versions

## Disclaimer
This project is not affiliated with or supported by E3/DC GmbH.

Use at your own risk.

## License
MIT License - 2026 Johann Legler
