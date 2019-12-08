"""Provide configuration end points for scripts."""
import homeassistant.helpers.config_validation as cv
from . import EditKeyBasedConfigView
from homeassistant.components.script import DOMAIN
from homeassistant.components.script import SCRIPT_ENTRY_SCHEMA
from homeassistant.config import SCRIPT_CONFIG_PATH
from homeassistant.const import SERVICE_RELOAD


async def async_setup(hass):
    """Set up the script config API."""

    async def hook(hass):
        """post_write_hook for Config View that reloads scripts."""
        await hass.services.async_call(DOMAIN, SERVICE_RELOAD)

    hass.http.register_view(
        EditKeyBasedConfigView(
            "script",
            "config",
            SCRIPT_CONFIG_PATH,
            cv.slug,
            SCRIPT_ENTRY_SCHEMA,
            post_write_hook=hook,
        )
    )
    return True
