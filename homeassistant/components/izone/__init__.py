"""
Platform for the iZone AC.

For more details about this component, please refer to the documentation
https://home-assistant.io/integrations/izone/
"""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from .const import DATA_CONFIG
from .const import IZONE
from .discovery import async_start_discovery_service
from .discovery import async_stop_discovery_service
from homeassistant import config_entries
from homeassistant.const import CONF_EXCLUDE
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import HomeAssistantType

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        IZONE:
        vol.Schema({
            vol.Optional(CONF_EXCLUDE, default=[]):
            vol.All(cv.ensure_list, [cv.string])
        })
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistantType, config: ConfigType):
    """Register the iZone component config."""
    conf = config.get(IZONE)
    if not conf:
        return True

    hass.data[DATA_CONFIG] = conf

    # Explicitly added in the config file, create a config entry.
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            IZONE, context={"source": config_entries.SOURCE_IMPORT}))

    return True


async def async_setup_entry(hass, entry):
    """Set up from a config entry."""
    await async_start_discovery_service(hass)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "climate"))
    return True


async def async_unload_entry(hass, entry):
    """Unload the config entry and stop discovery process."""
    await async_stop_discovery_service(hass)
    await hass.config_entries.async_forward_entry_unload(entry, "climate")
    return True
