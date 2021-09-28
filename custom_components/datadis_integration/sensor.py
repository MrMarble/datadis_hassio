import json
import logging
from datetime import timedelta
from typing import Any, Callable, Dict, Final, Mapping, Optional

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    DEVICE_CLASS_ENERGY,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

import datadis

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(days=1)

CONF_CUPS: Final = "cups"
CONF_SUPPLIES: Final = "supplies"

SUP_SCHEMA = vol.Schema(
    {vol.Required(CONF_CUPS): cv.string, vol.Optional(CONF_NAME): cv.string}
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_SUPPLIES): vol.All(cv.ensure_list, [SUP_SCHEMA]),
    }
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        DatadisSensor(config[CONF_USERNAME], config[CONF_PASSWORD], supply)
        for supply in config[CONF_SUPPLIES]
    ]
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    sensors = [
        DatadisSensor(config[CONF_USERNAME], config[CONF_PASSWORD], supply)
        for supply in config[CONF_SUPPLIES]
    ]
    async_add_entities(sensors, update_before_add=True)


class DatadisSensor(Entity):
    """Representation of a Datadis Sensor."""

    def __init__(self, username: str, password: str, supply: Dict[str, str]):
        super().__init__()
        self.username = username
        self.password = password
        self.attrs = {}
        self.cups = supply["cups"]
        if CONF_NAME in supply:
            self._name = supply[CONF_NAME]
        else:
            self._name = self.cups[:5]
        self._available = True
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.cups

    @property
    def available(self) -> bool:
        """Return True if the entity is available."""
        return self._available

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return self.attrs

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_ENERGY

    @property
    def state_class(self) -> str:
        return "measurement"

    async def async_update(self):
        try:
            _LOGGER.info("Updating Datadis")
            token = await datadis.get_token(self.username, self.password)
            _LOGGER.info(f"Received token {token}")
            supplies = await datadis.get_supplies(token)
            _LOGGER.info("Received supplies %s", json.dumps(supplies, indent=2))
            for supply in supplies:
                if supply["cups"] == self.cups:
                    self.attrs = supply
                    self._available = True
                    max = await datadis.get_max_power(
                        token,
                        self.cups,
                        supply["distributorCode"],
                        "2021/01",
                        "2021/12",
                    )
                    self._state = f"{max} kWh"
        except ConnectionError as err:
            self._available = False
            _LOGGER.exception("Error retrieving data from Datadis.", exc_info=err)
        except:
            self._available = False
            _LOGGER.exception("Error retrieving data from Datadis.")
