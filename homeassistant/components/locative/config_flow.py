"""Config flow for Locative."""
from .const import DOMAIN
from homeassistant.helpers import config_entry_flow

config_entry_flow.register_webhook_flow(
    DOMAIN,
    "Locative Webhook",
    {"docs_url": "https://www.home-assistant.io/integrations/locative/"},
)
