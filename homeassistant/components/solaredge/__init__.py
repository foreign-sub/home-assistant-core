"""The solaredge component."""
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from .const import CONF_SITE_ID
from .const import DEFAULT_NAME
from .const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_API_KEY
from homeassistant.const import CONF_NAME
from homeassistant.helpers.typing import HomeAssistantType

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN:
        vol.Schema({
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            vol.Required(CONF_API_KEY): cv.string,
            vol.Required(CONF_SITE_ID): cv.string,
        })
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Platform setup, do nothing."""
    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(DOMAIN,
                                            context={"source": SOURCE_IMPORT},
                                            data=dict(config[DOMAIN])))
    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Load the saved entities."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True
