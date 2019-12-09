"""Config flow for IFTTT."""
from .const import DOMAIN
from homeassistant.helpers import config_entry_flow

config_entry_flow.register_webhook_flow(
    DOMAIN,
    "IFTTT Webhook",
    {
        "applet_url": "https://ifttt.com/maker_webhooks",
        "docs_url": "https://www.home-assistant.io/integrations/ifttt/",
    },
)
