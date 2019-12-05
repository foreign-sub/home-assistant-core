"""Config flow for Mailgun."""
from .const import DOMAIN
from homeassistant.helpers import config_entry_flow

config_entry_flow.register_webhook_flow(
    DOMAIN,
    "Mailgun Webhook",
    {
        "mailgun_url":
        "https://documentation.mailgun.com/en/latest/user_manual.html#webhooks",
        "docs_url": "https://www.home-assistant.io/integrations/mailgun/",
    },
)
