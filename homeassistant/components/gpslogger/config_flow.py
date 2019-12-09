"""Config flow for GPSLogger."""
from .const import DOMAIN
from homeassistant.helpers import config_entry_flow

config_entry_flow.register_webhook_flow(
    DOMAIN,
    "GPSLogger Webhook",
    {"docs_url": "https://www.home-assistant.io/integrations/gpslogger/"},
)
