from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EMS_BITS


EMS_BINARY_SENSORS = {
    "battery_charge_locked": "Batterie Laden gesperrt",
    "battery_discharge_locked": "Batterie Entladen gesperrt",
    "emergency_power_possible": "Notstrom möglich",
    "weather_based_charging": "Wetterbasiertes Laden aktiv",
    "feed_in_limited": "Einspeisung begrenzt",
    "charge_lock_time_active": "Ladesperrzeit aktiv",
    "discharge_lock_time_active": "Entladesperrzeit aktiv",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []
    for key, name in EMS_BINARY_SENSORS.items():
        entities.append(
            E3DCEMSBinarySensor(
                coordinator,
                entry,
                key,
                name,
            )
        )

    async_add_entities(entities)


class E3DCEMSBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, key, name):
        super().__init__(coordinator)

        self._entry = entry
        self._key = key

        self._attr_name = f"E3DC {name}"
        self._attr_unique_id = f"{entry.entry_id}_ems_{key}"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        return self.coordinator.data.get("ems", {}).get(self._key)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer="HagerEnergy / E3/DC",
            name="E3/DC Energiespeichersystem",
        )
