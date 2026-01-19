import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_REGISTER_OFFSET,
)
from .modbus import E3DCModbusClient


WALLBOX_TYPES = {
    "classic": "Wallbox classic",
    "easy_connect": "Wallbox easy connect",
    "multi_connect": "Wallbox multi connect",
    "efy": "Wallbox efy",
}


class E3DCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                await self._validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input["host"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"E3/DC {user_input['host']}",
                    data={
                        "host": user_input["host"],
                        "port": user_input["port"],
                        "unit_id": user_input["unit_id"],
                        "register_offset": user_input["register_offset"],
                    },
                    options={
                        "scan_interval": DEFAULT_SCAN_INTERVAL,
                        "wallboxes": user_input.get("wallboxes", 1),
                        "wallbox_type": "classic",
                        "register_offset": user_input["register_offset"],
                    },
                )

        schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Optional("port", default=DEFAULT_PORT): int,
                vol.Optional("unit_id", default=DEFAULT_UNIT_ID): int,
                vol.Optional(
                    "register_offset",
                    default=DEFAULT_REGISTER_OFFSET,
                ): vol.All(int, vol.Range(min=-2, max=2)),
                vol.Optional("wallboxes", default=1): vol.All(
                    int, vol.Range(min=0, max=8)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _validate_input(self, hass: HomeAssistant, data):
        client = E3DCModbusClient(
            host=data["host"],
            port=data["port"],
            unit_id=data["unit_id"],
            register_offset=data["register_offset"],
        )

        await client.connect()
        try:
            regs = await client.read_holding_registers(40001, 1)
            if regs[0] != 0xE3DC:
                raise HomeAssistantError("Not an E3/DC device")
        finally:
            await client.close()

    @staticmethod
    def async_get_options_flow(config_entry):
        return E3DCOptionsFlow(config_entry)


class E3DCOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    "scan_interval",
                    default=self._entry.options.get(
                        "scan_interval", DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(int, vol.Range(min=2, max=60)),
                vol.Required(
                    "wallboxes",
                    default=self._entry.options.get("wallboxes", 1),
                ): vol.All(int, vol.Range(min=0, max=8)),
                vol.Required(
                    "wallbox_type",
                    default=self._entry.options.get(
                        "wallbox_type", "classic"
                    ),
                ): vol.In(WALLBOX_TYPES),
                vol.Required(
                    "register_offset",
                    default=self._entry.options.get(
                        "register_offset",
                        self._entry.data.get(
                            "register_offset", DEFAULT_REGISTER_OFFSET
                        ),
                    ),
                ): vol.All(int, vol.Range(min=-2, max=2)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
