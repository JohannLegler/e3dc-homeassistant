from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfPower, UnitOfElectricPotential, UnitOfElectricCurrent, PERCENTAGE
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REGISTERS,
    DC_STRINGS,
    POWER_METER_TYPE_1,
)


BASE_SENSORS = {
    "pv_power": ("PV Leistung", UnitOfPower.WATT, SensorDeviceClass.POWER),
    "battery_power": ("Batterie Leistung", UnitOfPower.WATT, SensorDeviceClass.POWER),
    "house_power": ("Hausverbrauch", UnitOfPower.WATT, SensorDeviceClass.POWER),
    "grid_power": ("Netzleistung", UnitOfPower.WATT, SensorDeviceClass.POWER),
    "battery_soc": ("Batterie SOC", PERCENTAGE, SensorDeviceClass.BATTERY),
}

GRID_PHASE_SENSORS = {
    "grid_l1": "Netz L1 Leistung",
    "grid_l2": "Netz L2 Leistung",
    "grid_l3": "Netz L3 Leistung",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []

    for key, (name, unit, device_class) in BASE_SENSORS.items():
        entities.append(
            E3DCSensor(
                coordinator,
                entry,
                key,
                name,
                unit,
                device_class,
            )
        )

    for key, name in GRID_PHASE_SENSORS.items():
        entities.append(
            E3DCSensor(
                coordinator,
                entry,
                key,
                name,
                UnitOfPower.WATT,
                SensorDeviceClass.POWER,
            )
        )

    # DC-Strings
    for key in DC_STRINGS.keys():
        unit = None
        device_class = None
        if key.endswith("_voltage"):
            unit = UnitOfElectricPotential.VOLT
        elif key.endswith("_current"):
            unit = UnitOfElectricCurrent.AMPERE
        elif key.endswith("_power"):
            unit = UnitOfPower.WATT
            device_class = SensorDeviceClass.POWER
        entities.append(
            E3DCSensor(
                coordinator,
                entry,
                key,
                key.replace("_", " ").title(),
                unit,
                device_class,
            )
        )

    async_add_entities(entities)


class E3DCSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, key, name, unit, device_class):
        super().__init__(coordinator)

        self._entry = entry
        self._key = key

        self._attr_name = f"E3DC {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer="HagerEnergy / E3/DC",
            name="E3/DC Energiespeichersystem",
        )
