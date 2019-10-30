"""The NEW_NAME integration."""
import voluptuous as vol

from .const import DOMAIN
from homeassistant.core import HomeAssistant


CONFIG_SCHEMA = vol.Schema({vol.Optional(DOMAIN): {}}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the NEW_NAME integration."""
    return True
