"""Reproduce an Alarm control panel state."""
import asyncio
import logging
from typing import Iterable
from typing import Optional

from . import DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import SERVICE_ALARM_ARM_AWAY
from homeassistant.const import SERVICE_ALARM_ARM_CUSTOM_BYPASS
from homeassistant.const import SERVICE_ALARM_ARM_HOME
from homeassistant.const import SERVICE_ALARM_ARM_NIGHT
from homeassistant.const import SERVICE_ALARM_DISARM
from homeassistant.const import SERVICE_ALARM_TRIGGER
from homeassistant.const import STATE_ALARM_ARMED_AWAY
from homeassistant.const import STATE_ALARM_ARMED_CUSTOM_BYPASS
from homeassistant.const import STATE_ALARM_ARMED_HOME
from homeassistant.const import STATE_ALARM_ARMED_NIGHT
from homeassistant.const import STATE_ALARM_DISARMED
from homeassistant.const import STATE_ALARM_TRIGGERED
from homeassistant.core import Context
from homeassistant.core import State
from homeassistant.helpers.typing import HomeAssistantType

_LOGGER = logging.getLogger(__name__)

VALID_STATES = {
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
}


async def _async_reproduce_state(hass: HomeAssistantType,
                                 state: State,
                                 context: Optional[Context] = None) -> None:
    """Reproduce a single state."""
    cur_state = hass.states.get(state.entity_id)

    if cur_state is None:
        _LOGGER.warning("Unable to find entity %s", state.entity_id)
        return

    if state.state not in VALID_STATES:
        _LOGGER.warning("Invalid state specified for %s: %s", state.entity_id,
                        state.state)
        return

    # Return if we are already at the right state.
    if cur_state.state == state.state:
        return

    service_data = {ATTR_ENTITY_ID: state.entity_id}

    if state.state == STATE_ALARM_ARMED_AWAY:
        service = SERVICE_ALARM_ARM_AWAY
    elif state.state == STATE_ALARM_ARMED_CUSTOM_BYPASS:
        service = SERVICE_ALARM_ARM_CUSTOM_BYPASS
    elif state.state == STATE_ALARM_ARMED_HOME:
        service = SERVICE_ALARM_ARM_HOME
    elif state.state == STATE_ALARM_ARMED_NIGHT:
        service = SERVICE_ALARM_ARM_NIGHT
    elif state.state == STATE_ALARM_DISARMED:
        service = SERVICE_ALARM_DISARM
    elif state.state == STATE_ALARM_TRIGGERED:
        service = SERVICE_ALARM_TRIGGER

    await hass.services.async_call(DOMAIN,
                                   service,
                                   service_data,
                                   context=context,
                                   blocking=True)


async def async_reproduce_states(hass: HomeAssistantType,
                                 states: Iterable[State],
                                 context: Optional[Context] = None) -> None:
    """Reproduce Alarm control panel states."""
    await asyncio.gather(*(_async_reproduce_state(hass, state, context)
                           for state in states))
