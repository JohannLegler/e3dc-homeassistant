from .const import DOMAIN, DEFAULT_PORT, DEFAULT_UNIT_ID, DEFAULT_REGISTER_OFFSET
from .modbus import E3DCModbusClient
from .coordinator import E3DCCoordinator

PLATFORMS = ["sensor", "binary_sensor", "switch"]


async def async_setup_entry(hass, entry):
    host = entry.data["host"]
    port = entry.data.get("port", DEFAULT_PORT)
    unit_id = entry.data.get("unit_id", DEFAULT_UNIT_ID)
    register_offset = entry.options.get(
        "register_offset",
        entry.data.get("register_offset", DEFAULT_REGISTER_OFFSET),
    )

    client = E3DCModbusClient(
        host=host,
        port=port,
        unit_id=unit_id,
        register_offset=register_offset,
    )

    coordinator = E3DCCoordinator(
        hass=hass,
        client=client,
        scan_interval=entry.options.get("scan_interval"),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        client = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("client")
        if client:
            await client.close()

        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    return unload_ok
