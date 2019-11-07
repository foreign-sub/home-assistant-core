"""Provides device automations for Vacuum."""
from typing import List
from typing import Optional

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from . import DOMAIN
from . import SERVICE_RETURN_TO_BASE
from . import SERVICE_START
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.const import CONF_DOMAIN
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.const import CONF_TYPE
from homeassistant.core import Context
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry

ACTION_TYPES = {"clean", "dock"}

ACTION_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(ACTION_TYPES),
        vol.Required(CONF_ENTITY_ID): cv.entity_domain(DOMAIN),
    }
)


async def async_get_actions(hass: HomeAssistant, device_id: str) -> List[dict]:
    """List device actions for Vacuum devices."""
    registry = await entity_registry.async_get_registry(hass)
    actions = []

    # Get all the integrations entities for this device
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain != DOMAIN:
            continue

        actions.append(
            {
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "clean",
            }
        )
        actions.append(
            {
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "dock",
            }
        )

    return actions


async def async_call_action_from_config(
    hass: HomeAssistant, config: dict, variables: dict, context: Optional[Context]
) -> None:
    """Execute a device action."""
    config = ACTION_SCHEMA(config)

    service_data = {ATTR_ENTITY_ID: config[CONF_ENTITY_ID]}

    if config[CONF_TYPE] == "clean":
        service = SERVICE_START
    elif config[CONF_TYPE] == "dock":
        service = SERVICE_RETURN_TO_BASE

    await hass.services.async_call(
        DOMAIN, service, service_data, blocking=True, context=context
    )
