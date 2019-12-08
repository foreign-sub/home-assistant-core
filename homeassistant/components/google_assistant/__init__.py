"""Support for Actions on Google Assistant Smart Home Control."""
import logging
from typing import Any
from typing import Dict

import voluptuous as vol

from .const import CONF_ALIASES
from .const import CONF_ALLOW_UNLOCK
from .const import CONF_API_KEY
from .const import CONF_CLIENT_EMAIL
from .const import CONF_ENTITY_CONFIG
from .const import CONF_EXPOSE
from .const import CONF_EXPOSE_BY_DEFAULT
from .const import CONF_EXPOSED_DOMAINS
from .const import CONF_PRIVATE_KEY
from .const import CONF_PROJECT_ID
from .const import CONF_REPORT_STATE
from .const import CONF_ROOM_HINT
from .const import CONF_SECURE_DEVICES_PIN
from .const import CONF_SERVICE_ACCOUNT
from .const import DEFAULT_EXPOSE_BY_DEFAULT
from .const import DEFAULT_EXPOSED_DOMAINS
from .const import DOMAIN
from .const import EVENT_COMMAND_RECEIVED
from .const import EVENT_QUERY_RECEIVED  # noqa: F401
from .const import EVENT_SYNC_RECEIVED
from .const import SERVICE_REQUEST_SYNC
from .http import GoogleAssistantView
from .http import GoogleConfig
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.core import ServiceCall
from homeassistant.helpers import config_validation as cv
# Typing imports

_LOGGER = logging.getLogger(__name__)

ENTITY_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_EXPOSE): cv.boolean,
        vol.Optional(CONF_ALIASES): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_ROOM_HINT): cv.string,
    }
)

GOOGLE_SERVICE_ACCOUNT = vol.Schema(
    {
        vol.Required(CONF_PRIVATE_KEY): cv.string,
        vol.Required(CONF_CLIENT_EMAIL): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)


def _check_report_state(data):
    if data[CONF_REPORT_STATE]:
        if CONF_SERVICE_ACCOUNT not in data:
            raise vol.Invalid(
                "If report state is enabled, a service account must exist"
            )
    return data


GOOGLE_ASSISTANT_SCHEMA = vol.All(
    cv.deprecated(CONF_ALLOW_UNLOCK, invalidation_version="0.95"),
    vol.Schema(
        {
            vol.Required(CONF_PROJECT_ID): cv.string,
            vol.Optional(
                CONF_EXPOSE_BY_DEFAULT, default=DEFAULT_EXPOSE_BY_DEFAULT
            ): cv.boolean,
            vol.Optional(
                CONF_EXPOSED_DOMAINS, default=DEFAULT_EXPOSED_DOMAINS
            ): cv.ensure_list,
            vol.Optional(CONF_API_KEY): cv.string,
            vol.Optional(CONF_ENTITY_CONFIG): {cv.entity_id: ENTITY_SCHEMA},
            vol.Optional(CONF_ALLOW_UNLOCK): cv.boolean,
            # str on purpose, makes sure it is configured correctly.
            vol.Optional(CONF_SECURE_DEVICES_PIN): str,
            vol.Optional(CONF_REPORT_STATE, default=False): cv.boolean,
            vol.Optional(CONF_SERVICE_ACCOUNT): GOOGLE_SERVICE_ACCOUNT,
        },
        extra=vol.PREVENT_EXTRA,
    ),
    _check_report_state,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: GOOGLE_ASSISTANT_SCHEMA}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, yaml_config: Dict[str, Any]):
    """Activate Google Actions component."""
    config = yaml_config.get(DOMAIN, {})

    google_config = GoogleConfig(hass, config)
    await google_config.async_initialize()

    hass.http.register_view(GoogleAssistantView(google_config))

    if google_config.should_report_state:
        google_config.async_enable_report_state()

    async def request_sync_service_handler(call: ServiceCall):
        """Handle request sync service calls."""
        agent_user_id = call.data.get("agent_user_id") or call.context.user_id

        if agent_user_id is None:
            _LOGGER.warning(
                "No agent_user_id supplied for request_sync. Call as a user or pass in user id as agent_user_id."
            )
            return

        await google_config.async_sync_entities(agent_user_id)

    # Register service only if key is provided
    if CONF_API_KEY in config or CONF_SERVICE_ACCOUNT in config:
        hass.services.async_register(
            DOMAIN, SERVICE_REQUEST_SYNC, request_sync_service_handler
        )

    return True
