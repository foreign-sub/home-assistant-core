"""Provide the device automations for Fan."""
from typing import Dict
from typing import List

import voluptuous as vol

from . import DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import CONF_CONDITION
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.const import CONF_DOMAIN
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.const import CONF_TYPE
from homeassistant.const import STATE_OFF
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import condition
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry
from homeassistant.helpers.config_validation import DEVICE_CONDITION_BASE_SCHEMA
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.typing import TemplateVarsType

CONDITION_TYPES = {"is_on", "is_off"}

CONDITION_SCHEMA = DEVICE_CONDITION_BASE_SCHEMA.extend({
    vol.Required(CONF_ENTITY_ID):
    cv.entity_id,
    vol.Required(CONF_TYPE):
    vol.In(CONDITION_TYPES),
})


async def async_get_conditions(hass: HomeAssistant,
                               device_id: str) -> List[Dict[str, str]]:
    """List device conditions for Fan devices."""
    registry = await entity_registry.async_get_registry(hass)
    conditions = []

    # Get all the integrations entities for this device
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain != DOMAIN:
            continue

        conditions.append({
            CONF_CONDITION: "device",
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_ENTITY_ID: entry.entity_id,
            CONF_TYPE: "is_on",
        })
        conditions.append({
            CONF_CONDITION: "device",
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_ENTITY_ID: entry.entity_id,
            CONF_TYPE: "is_off",
        })

    return conditions


def async_condition_from_config(config: ConfigType, config_validation: bool
                                ) -> condition.ConditionCheckerType:
    """Create a function to test a device condition."""
    if config_validation:
        config = CONDITION_SCHEMA(config)
    if config[CONF_TYPE] == "is_on":
        state = STATE_ON
    else:
        state = STATE_OFF

    def test_is_state(hass: HomeAssistant,
                      variables: TemplateVarsType) -> bool:
        """Test if an entity is a certain state."""
        return condition.state(hass, config[ATTR_ENTITY_ID], state)

    return test_is_state
