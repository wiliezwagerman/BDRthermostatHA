from homeassistant.config_entries import ConfigEntry

from .const import *
from homeassistant.components.climate.const import (
    HVACMode, HVACAction
)


from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
    CONF_TIME_ZONE
)
import datetime
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)


def preset_mode_bdr_to_ha(bdr_mode, program=None):

    if bdr_mode == "manual":
        return PRESET_MODE_MANUAL
    elif bdr_mode == "temporary-override":
        return PRESET_MODE_TEMP_OVERRIDE
    elif bdr_mode == "anti-frost":
        return PRESET_MODE_ANTIFROST
    elif bdr_mode == "schedule" and program == 1:
        return PRESET_MODE_SCHEDULE_1
    elif bdr_mode == "schedule" and program == 2:
        return PRESET_MODE_SCHEDULE_2
    elif bdr_mode == "schedule" and program == 3:
        return PRESET_MODE_SCHEDULE_3
    elif bdr_mode == "holiday":
        return PRESET_MODE_HOLIDAY


def preset_mode_ha_to_bdr(ha_mode):

    _LOGGER.info(f"{ha_mode=}")

    if ha_mode == PRESET_MODE_SCHEDULE_1:
        return BDR_PRESET_SCHEDULE, "1"
    elif ha_mode == PRESET_MODE_SCHEDULE_2:
        return BDR_PRESET_SCHEDULE, "2"
    elif ha_mode == PRESET_MODE_SCHEDULE_3:
        return BDR_PRESET_SCHEDULE, "3"
    elif ha_mode == PRESET_MODE_HOLIDAY:
        return BDR_PRESET_MODE, "holiday",
    elif ha_mode == PRESET_MODE_ANTIFROST:
        return BDR_PRESET_MODE, "anti-frost",

    return BDR_PRESET_MANUAL, "manual"

def hvac_mode_bdr_to_ha(raw_mode):
    if raw_mode == "off":
        return HVACMode.OFF
    elif raw_mode == "heating-auto":
        return HVACMode.AUTO


def hvac_mode_ha_to_bdr(ha_mode):
    if ha_mode == HVACMode.AUTO:
        return "heating-auto"
    elif ha_mode == HVACMode.OFF:
        return "off"

def hvac_action_bdr_to_ha(raw_mode):
    if raw_mode == "heating":
        return HVACAction.HEATING
    elif raw_mode == "standby":
        return HVACAction.IDLE
    else: return None
    
def hvac_unit_bdr_to_ha(raw_mode) -> UnitOfTemperature:
    if raw_mode == "°C":
        return UnitOfTemperature.CELSIUS
    elif raw_mode == "°F":
        return UnitOfTemperature.FAHRENHEIT
    else: return UnitOfTemperature.CELSIUS


def create_override_date(target_time, days_offset, create_string = False):
    now = datetime.datetime.now()
    override_date = now + timedelta(days=days_offset)
    target_hour = int(target_time.split(":")[0])
    target_minutes = int(target_time.split(":")[1])
    override_date = override_date.replace(
        hour=target_hour, minute=target_minutes, second=0, microsecond=0
    )
    if create_string:
        return override_date.isoformat("T", "minutes")
    else:
        override_date = override_date.astimezone()
        return override_date

def bdr_error_to_ha_binary(error_status):
    if error_status != "no-error":
        return True
    else:
        return False

def bdr_power_to_ha_binary(On_OffStatus):
    if On_OffStatus != "off":
        return False
    else:
        return True

def bdr_status_enum_check(heater_status):
    if heater_status in HEATER_STATUS:
        return heater_status
    else:
        _LOGGER.warning("Status ENUM does not contain %s, therefor status is unkown", heater_status)
        return 'unknown'
