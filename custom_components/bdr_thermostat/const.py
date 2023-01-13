"""BDR thermostat's constant """
from homeassistant.components.climate.const import HVACMode, HVACAction

# Generic

VERSION = "1.0"
DOMAIN = "climate"
PLATFORM = "bdr_thermostat"
ISSUE_URL = "https://github.com/freitdav/BDRthermostatHA"


# Keys
STORAGE_VERSION = 1
STORAGE_KEY = "bdrapi"
DATA_KEY_API = "api"
DATA_KEY_CONFIG = "config"
SERIAL_KEY = "serial"
FEATURE_OPERATING_MODE = "operating_mode"
FEATURE_ENERGY_CONSUMPTION = "energy_consumption"

# Defaults
DEFAULT_NAME = "BDR Thermostat"
DEVICE_MODEL = "TXM"
DEVICE_MANUFACTER = "BDR"
DEFAULT_VERSION = "1.0"

BDR_PRESET_MANUAL = "manual"
BDR_PRESET_SCHEDULE = "schedule"
BDR_PRESET_TEMP_OVERRIDE = "temp_override"
BDR_PRESET_MODE = "mode"


PRESET_MODE_MANUAL = "Manual"
PRESET_MODE_SCHEDULE_1 = "Schedule 1"
PRESET_MODE_SCHEDULE_2 = "Schedule 2"
PRESET_MODE_SCHEDULE_3 = "Schedule 3"
PRESET_MODE_TEMP_OVERRIDE = "Temporary Override"
PRESET_MODE_ANTIFROST = "Anti Frost"
PRESET_MODE_HOLIDAY = "Holidays"

PRESET_MODES = [
    PRESET_MODE_MANUAL,
    PRESET_MODE_SCHEDULE_1,
    PRESET_MODE_SCHEDULE_2,
    PRESET_MODE_SCHEDULE_3,
    PRESET_MODE_TEMP_OVERRIDE,
    PRESET_MODE_ANTIFROST,
    PRESET_MODE_HOLIDAY,
]

HVAC_MODES = [HVACMode.OFF, HVACMode.AUTO]

HEATER_STATUS = [
    'heating', 
    'idle', 
    'off', 
    'cooling',
    'unknown',
    'N/A'
]
