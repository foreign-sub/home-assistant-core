"""Config flow for DialogFlow."""
from .const import DOMAIN
from homeassistant.helpers import config_entry_flow

config_entry_flow.register_webhook_flow(
    DOMAIN,
    "Dialogflow Webhook",
    {
        "dialogflow_url": "https://dialogflow.com/docs/fulfillment#webhook",
        "docs_url": "https://www.home-assistant.io/integrations/dialogflow/",
    },
)
