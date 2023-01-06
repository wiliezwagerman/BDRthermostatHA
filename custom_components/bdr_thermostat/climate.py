import logging

import async_timeout
from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode
)
from homeassistant.const import (
    ATTR_TEMPERATURE, 
    CONF_NAME, 
    PRECISION_HALVES,
    UnitOfTemperature
)
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import (
    ConfigType, 
    DiscoveryInfoType,
    HomeAssistantType
)

from .config_schema import CLIMATE_SCHEMA, SUPPORT_FLAGS
from datetime import timedelta
from typing import Any, Callable, Dict, Optional
from .const import *
from .helper import *

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(CLIMATE_SCHEMA)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:

    config = hass.data[PLATFORM].get(DATA_KEY_CONFIG)

    """Add BdrThermostat entities from configuration.yaml."""
    _LOGGER.warning(
        "Setup entity coming from configuration.yaml named: %s. Device will not be created, only entities",
        config.get(CONF_NAME),
    )
    await async_setup_reload_service(hass, DOMAIN, PLATFORM)
    async_add_entities(
        [BdrThermostat(hass, config)],
        update_before_add=True,
    )


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add BdrThermostat entities from user config"""
    await async_setup_reload_service(hass, DOMAIN, PLATFORM)
    async_add_devices(
        [BdrThermostat(hass, config_entry.data)],
        update_before_add=True,
    )


class BdrThermostat(ClimateEntity, RestoreEntity):
    """BdrThermostat"""

    def __init__(self, hass, config):
        """Initialize the thermostat."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_name = config.get(CONF_NAME)
        self._attr_unique_id = config.get(CONF_NAME)
        self._attr_supported_features = SUPPORT_FLAGS
        self._attr_preset_modes = PRESET_MODES
        self._attr_hvac_modes = (
            HVAC_MODES
            if self._bdr_api.is_feature_enabled(FEATURE_OPERATING_MODE)
            else [HVACMode.AUTO]
        )
        self._attr_hvac_mode = HVACMode.AUTO
        self._attr_hvac_action = None
        self._attr_extra_state_attributes = {}
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get(SERIAL_KEY, "1234"),
                )
            }
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self) -> None:

        try:
            async with async_timeout.timeout(5):
                self.status = await self._bdr_api.get_status()
        except Exception as e:
            _LOGGER.info("Could not connect to API.")
            return

        if self.status:
            next_switch = self.status.get("nextSwitch", None)
            if next_switch:
                self._attr_extra_state_attributes["next_change"] = next_switch["time"]
                self._attr_extra_state_attributes["next_temp"] = next_switch[
                    "roomTemperatureSetpoint"
                ]["value"]
                self.next_switch_days = next_switch[
                    "dayOffset"
                ]  # we just need to store this
            else:
                self._attr_extra_state_attributes.pop("next_change", None)
                self._attr_extra_state_attributes.pop("next_temp", None)

        if self._bdr_api.is_feature_enabled(FEATURE_OPERATING_MODE):
            operating_mode = await self._bdr_api.get_operating_mode()

            if operating_mode:
                self._attr_hvac_mode = hvac_mode_bdr_to_ha(operating_mode["mode"])

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        await self.async_update()

        next_change = self._attr_extra_state_attributes.get("next_change", None)

        if next_change:
            # We are in scheduled mode, need to create a temporary override
            override_date = create_override_date(next_change, self.next_switch_days, True)
            await self._bdr_api.set_override_temperature(temperature, override_date)
        else:
            # Manual mode, it is fine to modify the temp
            await self._bdr_api.set_target_temperature(temperature)
        await self.async_update_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        target_bdr_mode = hvac_mode_ha_to_bdr(hvac_mode)
        await self._bdr_api.set_operating_mode(target_bdr_mode)
        await self.async_update_ha_state()

    async def async_set_preset_mode(self, preset_mode):
        _LOGGER.error(f"{preset_mode=}")
        bdr_preset_mode, program = preset_mode_ha_to_bdr(
            preset_mode
        )

        self.preset_mode = preset_mode

        # Set a schedule
        if bdr_preset_mode == BDR_PRESET_SCHEDULE:
            await self._bdr_api.set_schedule(program)
        # Set a manual temperature
        elif bdr_preset_mode == BDR_PRESET_MANUAL:
            await self._bdr_api.set_target_temperature(self.target_temperature)
        elif bdr_preset_mode == BDR_PRESET_MODE:
            await self._bdr_api.set_operating_mode(mode=program)

        await self.async_update_ha_state()

    @property
    def current_temperature(self) -> float:
        """Return current temperature."""
        return self.status["roomTemperature"]["value"]
            
    @property
    def target_temperature(self) -> float|None:
        """Return current target temperature."""
        return self.status["roomTemperatureSetpoint"]["value"]

    @property
    def hvac_action(self):
        """Return current action status."""
        return hvac_action_bdr_to_ha(self.status["zoneActivity"])

    @property
    def target_temperature_step(self) -> float:
        """Set target temperature step to halves."""
        return PRECISION_HALVES

    @property
    def temperature_unit(self):
        """return temperature units"""
        return hvac_unit_bdr_to_ha(self.status["roomTemperature"]["unit"])

    @property
    def preset_mode(self):
        """return current preset mode"""
        return preset_mode_bdr_to_ha(self.status["mode"], self.status["timeProgram"])