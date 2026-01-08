import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    WALLBOX_BASE_ADDR,
    WALLBOX_TYPES,
    MAX_WALLBOXES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    wallboxes = entry.options.get(
        "wallboxes",
        entry.data.get("wallboxes", 1),
    )

    wallbox_type = entry.options.get("wallbox_type", "classic")
    writable_bits = WALLBOX_TYPES.get(wallbox_type, {})

    entities = []

    for wb in range(min(wallboxes, MAX_WALLBOXES)):
        for key, bit in writable_bits.items():
            entities.append(
                E3DCWallboxSwitch(
                    coordinator=coordinator,
                    client=client,
                    entry=entry,
                    wallbox_index=wb,
                    key=key,
                    bit=bit,
                )
            )

    async_add_entities(entities)


class E3DCWallboxSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, client, entry, wallbox_index, key, bit):
        super().__init__(coordinator)

        self._client = client
        self._entry = entry
        self._wallbox = wallbox_index
        self._key = key
        self._bit = bit

        self._addr = WALLBOX_BASE_ADDR + wallbox_index

        self._attr_name = (
            f"E3DC Wallbox {wallbox_index} {key.replace('_', ' ').title()}"
        )
        self._attr_unique_id = (
            f"{entry.entry_id}_wallbox_{wallbox_index}_{key}"
        )

    # --------------------------------------------------
    # State
    # --------------------------------------------------

    @property
    def is_on(self):
        # Status immer live aus dem Register lesen
        try:
            value = self.coordinator.data.get(
                f"wallbox_ctrl_{self._wallbox}"
            )
            if value is None:
                return None
            return bool(value & (1 << self._bit))
        except Exception:
            return None

    # --------------------------------------------------
    # Control
    # --------------------------------------------------

    async def async_turn_on(self):
        await self._async_set_state(True)

    async def async_turn_off(self):
        await self._async_set_state(False)

    async def _async_set_state(self, state: bool):
        try:
            # aktuellen Registerwert lesen
            regs = await self._client.read_holding_registers(
                self._addr,
                1,
            )
            current = regs[0]

            new_value = (
                current | (1 << self._bit)
                if state
                else current & ~(1 << self._bit)
            )

            if new_value != current:
                await self._client.write_register(
                    self._addr,
                    new_value,
                )

            await self.coordinator.async_request_refresh()

        except Exception as err:
            _LOGGER.error(
                "Wallbox %s (%s) write failed: %s",
                self._wallbox,
                self._key,
                err,
            )
            raise

    # --------------------------------------------------
    # Device
    # --------------------------------------------------

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer="HagerEnergy / E3/DC",
            name="E3/DC Energiespeichersystem",
        )
