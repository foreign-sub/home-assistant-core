"""Config flow to configure demo component."""
from . import DOMAIN
from homeassistant import config_entries
# pylint: disable=unused-import


class DemoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Demo configuration flow."""

    VERSION = 1

    async def async_step_import(self, import_info):
        """Set the config entry up from yaml."""
        return self.async_create_entry(title="Demo", data={})
