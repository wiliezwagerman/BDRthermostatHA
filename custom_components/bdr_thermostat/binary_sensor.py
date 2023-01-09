import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.const import (
    CONF_NAME,
)

from .const import *
from .helper import *
from typing import Callable, Optional

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=10)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    
    config = hass.data[PLATFORM].get(DATA_KEY_CONFIG)

    _LOGGER.warning(
        "Setup entity coming from configuration.yaml named: %s. Device will not be created, only entities",
        config.get(CONF_NAME),
    )

    await async_setup_reload_service(hass, "binary_sensor", PLATFORM)
    async_add_entities(
        [
            ErrorBinarySensor(hass, config), 
        ],
        update_before_add=True,
    )

async def async_setup_entry(hass, config_entry, async_add_devices):
    await async_setup_reload_service(hass, DOMAIN, PLATFORM)
    async_add_devices(
        [
            ErrorBinarySensor(hass, config_entry.data),
        ],
        update_before_add=True,
    )     

class ErrorBinarySensor(BinarySensorEntity):

    def __init__(self, hass, config):  
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Error binary"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
        error = await self._bdr_api.get_errors()

        if error:
            self._attr_is_on = bdr_error_to_ha_binary(error)

        else: self._attr_is_on = True