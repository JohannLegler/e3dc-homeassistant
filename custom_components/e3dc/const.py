DOMAIN = "e3dc"

DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 5  # Sekunden

# ------------------------------------------------------------------
# Modbus Register – E3/DC Simple Mode
# Alle Adressen sind 1-basiert laut Doku V2.50
# pymodbus arbeitet 0-basiert → -1 beim Zugriff
# ------------------------------------------------------------------

REGISTERS = {
    # Leistungsdaten (Int32, 2 Register)
    "pv_power":        {"addr": 40068, "len": 2, "type": "int32"},
    "battery_power":   {"addr": 40070, "len": 2, "type": "int32"},
    "house_power":     {"addr": 40072, "len": 2, "type": "int32"},
    "grid_power":      {"addr": 40074, "len": 2, "type": "int32"},
    "wallbox_power":   {"addr": 40078, "len": 2, "type": "int32"},

    # Status
    "battery_soc":     {"addr": 40083, "len": 1, "type": "uint16"},
    "emergency_power": {"addr": 40084, "len": 1, "type": "uint16"},
    "ems_status":      {"addr": 40085, "len": 1, "type": "uint16"},
}

# ------------------------------------------------------------------
# DC-Strings (vollständig, auch wenn nicht alle genutzt werden)
# ------------------------------------------------------------------

DC_STRINGS = {
    # Spannung
    "dc_string_1_voltage": {"addr": 40096, "len": 1, "type": "uint16"},
    "dc_string_2_voltage": {"addr": 40097, "len": 1, "type": "uint16"},
    "dc_string_3_voltage": {"addr": 40098, "len": 1, "type": "uint16"},

    # Strom (Faktor 0,01)
    "dc_string_1_current": {"addr": 40099, "len": 1, "type": "uint16", "scale": 0.01},
    "dc_string_2_current": {"addr": 40100, "len": 1, "type": "uint16", "scale": 0.01},
    "dc_string_3_current": {"addr": 40101, "len": 1, "type": "uint16", "scale": 0.01},

    # Leistung
    "dc_string_1_power":   {"addr": 40102, "len": 1, "type": "uint16"},
    "dc_string_2_power":   {"addr": 40103, "len": 1, "type": "uint16"},
    "dc_string_3_power":   {"addr": 40104, "len": 1, "type": "uint16"},
}

# ------------------------------------------------------------------
# EMS Status Bits – Register 40085
# ------------------------------------------------------------------

EMS_BITS = {
    0: "battery_charge_locked",
    1: "battery_discharge_locked",
    2: "emergency_power_possible",
    3: "weather_based_charging",
    4: "feed_in_limited",
    5: "charge_lock_time_active",
    6: "discharge_lock_time_active",
}

# ------------------------------------------------------------------
# Leistungsmesser Typ 1 (Hausanschlusspunkt / Regelpunkt)
# Int32 – Energy-Dashboard-tauglich
# ------------------------------------------------------------------

POWER_METER_TYPE_1 = {
    "grid_l1": {"addr": 40138, "len": 2, "type": "int32"},
    "grid_l2": {"addr": 40140, "len": 2, "type": "int32"},
    "grid_l3": {"addr": 40142, "len": 2, "type": "int32"},
}

# ------------------------------------------------------------------
# Wallbox – Basis
# ------------------------------------------------------------------

WALLBOX_BASE_ADDR = 40088
MAX_WALLBOXES = 8

# ------------------------------------------------------------------
# Wallbox-Typen – schreibbare Bits (R/W)
# Nur diese Bits dürfen aktiv gesetzt werden!
# ------------------------------------------------------------------

WALLBOX_TYPES = {
    "classic": {
        "solar_mode": 1,
        "charging_blocked": 2,
        "schuko_on": 6,
        "single_phase": 12,
    },
    "easy_connect": {
        "solar_mode": 1,
        "charging_blocked": 2,
        "single_phase": 12,
    },
    "multi_connect": {
        "solar_mode": 1,
        "charging_blocked": 2,
        "single_phase": 12,
    },
    "efy": {
        "solar_mode": 1,
        "charging_blocked": 2,
        "single_phase": 12,
    },
}

# ------------------------------------------------------------------
# Wallbox Status Bits (Read-Only, generisch)
# ------------------------------------------------------------------

WALLBOX_STATUS_BITS = {
    0: "available",
    3: "car_charging",
    4: "type2_locked",
    5: "type2_plugged",
    7: "schuko_plugged",
    8: "schuko_locked",
}
