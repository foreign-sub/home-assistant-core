"""Config flow for Mobile App."""
from .const import ATTR_DEVICE_NAME
from .const import DOMAIN
from homeassistant import config_entries


@config_entries.HANDLERS.register(DOMAIN)
class MobileAppFlowHandler(config_entries.ConfigFlow):
    """Handle a Mobile App config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_PUSH

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        placeholders = {
            "apps_url":
            "https://www.home-assistant.io/components/mobile_app/#apps"
        }

        return self.async_abort(reason="install_app",
                                description_placeholders=placeholders)

    async def async_step_registration(self, user_input=None):
        """Handle a flow initialized during registration."""
        return self.async_create_entry(title=user_input[ATTR_DEVICE_NAME],
                                       data=user_input)
