"""Collection of helper methods.

All containing methods are legacy helpers that should not be used by new
components. Instead call the service directly.
"""
from homeassistant.components.automation import DOMAIN
from homeassistant.components.automation import SERVICE_TRIGGER
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ENTITY_MATCH_ALL
from homeassistant.const import SERVICE_RELOAD
from homeassistant.const import SERVICE_TOGGLE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.loader import bind_hass


@bind_hass
async def async_turn_on(hass, entity_id=ENTITY_MATCH_ALL):
    """Turn on specified automation or all."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    await hass.services.async_call(DOMAIN, SERVICE_TURN_ON, data)


@bind_hass
async def async_turn_off(hass, entity_id=ENTITY_MATCH_ALL):
    """Turn off specified automation or all."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    await hass.services.async_call(DOMAIN, SERVICE_TURN_OFF, data)


@bind_hass
async def async_toggle(hass, entity_id=ENTITY_MATCH_ALL):
    """Toggle specified automation or all."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    await hass.services.async_call(DOMAIN, SERVICE_TOGGLE, data)


@bind_hass
async def async_trigger(hass, entity_id=ENTITY_MATCH_ALL):
    """Trigger specified automation or all."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    await hass.services.async_call(DOMAIN, SERVICE_TRIGGER, data)


@bind_hass
async def async_reload(hass):
    """Reload the automation from config."""
    await hass.services.async_call(DOMAIN, SERVICE_RELOAD)
