# e3dc-homeassistant
Home Assistant Integration for E3/DC Hauskraftwerk using local Modbus/TCP communication.


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
1. Copy the `e3dc` folder to:
2. Restart Home Assistant
3. Add the integration via **Settings → Devices & Services**

## Configuration
The integration is configured via the UI (Config Flow).
You will need:
- IP address of the E3/DC system
- Modbus port (default: 502)

## Limitations
- No write/control functions yet
- Register mapping may differ between E3/DC firmware versions

## Disclaimer
This project is not affiliated with or supported by E3/DC GmbH.

Use at your own risk.

## License
MIT License © 2026 Johann Legler
