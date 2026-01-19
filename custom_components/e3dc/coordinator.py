import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    REGISTERS,
    DC_STRINGS,
    POWER_METER_TYPE_1,
    EMS_BITS,
    SYSTEM_INFO,
    SG_READY,
    WALLBOX_BASE_ADDR,
    MAX_WALLBOXES,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class E3DCCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client, scan_interval=None):
        self._client = client

        super().__init__(
            hass,
            _LOGGER,
            name="E3/DC Modbus Coordinator",
            update_interval=timedelta(
                seconds=scan_interval or DEFAULT_SCAN_INTERVAL
            ),
        )

    async def _async_update_data(self):
        try:
            data: dict = {}

            # --------------------------------------------------
            # Basisregister, DC-Strings, Leistungsmesser
            # --------------------------------------------------
            for source in (
                REGISTERS,
                DC_STRINGS,
                POWER_METER_TYPE_1,
                SYSTEM_INFO,
                SG_READY,
            ):
                for key, reg in source.items():
                    try:
                        value = await self._client.read_value(reg)
                        scale = reg.get("scale")
                        data[key] = value * scale if scale else value
                    except Exception as err:
                        _LOGGER.debug(
                            "Register %s (%s) failed: %s",
                            key,
                            reg["addr"],
                            err,
                        )
                        data[key] = None

            # --------------------------------------------------
            # Wallbox CTRL Register (40088–40095)
            # --------------------------------------------------
            for wb in range(MAX_WALLBOXES):
                addr = WALLBOX_BASE_ADDR + wb
                try:
                    regs = await self._client.read_holding_registers(addr, 1)
                    data[f"wallbox_ctrl_{wb}"] = regs[0]
                except Exception as err:
                    _LOGGER.debug(
                        "Wallbox CTRL %s (%s) failed: %s",
                        wb,
                        addr,
                        err,
                    )
                    data[f"wallbox_ctrl_{wb}"] = None

            # --------------------------------------------------
            # EMS Status Bits
            # --------------------------------------------------
            ems_raw = data.get("ems_status")
            data["ems"] = {}

            if ems_raw is not None:
                for bit, name in EMS_BITS.items():
                    data["ems"][name] = bool(ems_raw & (1 << bit))

            # --------------------------------------------------
            # Autarky / Self-consumption (2x 8-bit in 40082)
            # --------------------------------------------------
            autarky_raw = data.get("autarky_raw")
            if autarky_raw is not None:
                data["autarky"] = (autarky_raw >> 8) & 0xFF
                data["self_consumption"] = autarky_raw & 0xFF

            return data

        except Exception as err:
            raise UpdateFailed(str(err)) from err
