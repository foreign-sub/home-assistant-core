"""The linky component."""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from .const import DEFAULT_TIMEOUT
from .const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_PASSWORD
from homeassistant.const import CONF_TIMEOUT
from homeassistant.const import CONF_USERNAME
from homeassistant.helpers.typing import HomeAssistantType

_LOGGER = logging.getLogger(__name__)

ACCOUNT_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME):
    cv.string,
    vol.Required(CONF_PASSWORD):
    cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT):
    cv.positive_int,
})

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema(vol.All(cv.ensure_list, [ACCOUNT_SCHEMA]))},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up Linky sensors from legacy config file."""

    conf = config.get(DOMAIN)
    if conf is None:
        return True

    for linky_account_conf in conf:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=linky_account_conf.copy(),
            ))

    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Set up Linky sensors."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True


async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Unload Linky sensors."""
    return await hass.config_entries.async_forward_entry_unload(
        entry, "sensor")
