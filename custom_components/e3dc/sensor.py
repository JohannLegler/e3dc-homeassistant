from homeassistant.components.sensor import (
    RestoreSensor,
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    PERCENTAGE,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

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
    "additional_feedin_power": ("Zusatz Einspeiser", UnitOfPower.WATT, SensorDeviceClass.POWER),
    "battery_soc": ("Batterie SOC", PERCENTAGE, SensorDeviceClass.BATTERY),
    "autarky": ("Autarkie", PERCENTAGE, None),
    "self_consumption": ("Eigenverbrauch", PERCENTAGE, None),
    "wallbox_solar_power": ("Wallbox Solarleistung", UnitOfPower.WATT, SensorDeviceClass.POWER),
    "sg_ready_status": ("SG Ready Status", None, None),
}

ENERGY_SENSORS = {
    "grid_import": ("Netzbezug Energie", "grid_power", lambda v: max(v, 0)),
    "grid_export": ("Netzeinspeisung Energie", "grid_power", lambda v: max(-v, 0)),
    "battery_charge": ("Batterie Laden Energie", "battery_power", lambda v: max(v, 0)),
    "battery_discharge": ("Batterie Entladen Energie", "battery_power", lambda v: max(-v, 0)),
    "solar_production": ("PV Energie", "pv_power", lambda v: max(v, 0)),
    "wallbox_energy": ("Wallbox Energie", "wallbox_power", lambda v: max(v, 0)),
    "wallbox_solar_energy": ("Wallbox Solar Energie", "wallbox_solar_power", lambda v: max(v, 0)),
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

    # Energy dashboard sensors (derived from power)
    for key, (name, source_key, transform) in ENERGY_SENSORS.items():
        entities.append(
            E3DCEnergySensor(
                coordinator,
                entry,
                key,
                name,
                source_key,
                transform,
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
        data = self.coordinator.data
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer=data.get("manufacturer") or "HagerEnergy / E3/DC",
            model=data.get("model"),
            serial_number=data.get("serial_number"),
            sw_version=data.get("firmware_release"),
            name="E3/DC Energiespeichersystem",
        )


class E3DCEnergySensor(CoordinatorEntity, RestoreSensor):
    def __init__(self, coordinator, entry, key, name, source_key, transform):
        super().__init__(coordinator)

        self._entry = entry
        self._key = key
        self._source_key = source_key
        self._transform = transform

        self._energy = None
        self._last_update = None

        self._attr_name = f"E3DC {name}"
        self._attr_unique_id = f"{entry.entry_id}_energy_{key}"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state and state.state not in (None, "unknown", "unavailable"):
            try:
                self._energy = float(state.state)
            except ValueError:
                self._energy = None
        self._last_update = dt_util.utcnow()

    @property
    def native_value(self):
        if self._energy is None:
            return None
        return round(self._energy, 3)

    def _handle_coordinator_update(self):
        now = dt_util.utcnow()
        if self._last_update is not None:
            dt_seconds = (now - self._last_update).total_seconds()
            if dt_seconds > 0:
                power = self.coordinator.data.get(self._source_key)
                if power is not None:
                    power = self._transform(power)
                    if self._energy is None:
                        self._energy = 0.0
                    self._energy += (power / 1000.0) * (dt_seconds / 3600.0)

        self._last_update = now
        self.async_write_ha_state()

    @property
    def device_info(self):
        data = self.coordinator.data
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer=data.get("manufacturer") or "HagerEnergy / E3/DC",
            model=data.get("model"),
            serial_number=data.get("serial_number"),
            sw_version=data.get("firmware_release"),
            name="E3/DC Energiespeichersystem",
        )
