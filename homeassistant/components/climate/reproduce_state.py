"""Module that groups code required to handle state restore for component."""
import asyncio
from typing import Iterable
from typing import Optional

from .const import ATTR_AUX_HEAT
from .const import ATTR_HUMIDITY
from .const import ATTR_HVAC_MODE
from .const import ATTR_PRESET_MODE
from .const import ATTR_SWING_MODE
from .const import ATTR_TARGET_TEMP_HIGH
from .const import ATTR_TARGET_TEMP_LOW
from .const import DOMAIN
from .const import HVAC_MODES
from .const import SERVICE_SET_AUX_HEAT
from .const import SERVICE_SET_HUMIDITY
from .const import SERVICE_SET_HVAC_MODE
from .const import SERVICE_SET_PRESET_MODE
from .const import SERVICE_SET_SWING_MODE
from .const import SERVICE_SET_TEMPERATURE
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import Context
from homeassistant.core import State
from homeassistant.helpers.typing import HomeAssistantType


async def _async_reproduce_states(hass: HomeAssistantType,
                                  state: State,
                                  context: Optional[Context] = None) -> None:
    """Reproduce component states."""

    async def call_service(service: str, keys: Iterable, data=None):
        """Call service with set of attributes given."""
        data = data or {}
        data["entity_id"] = state.entity_id
        for key in keys:
            if key in state.attributes:
                data[key] = state.attributes[key]

        await hass.services.async_call(DOMAIN,
                                       service,
                                       data,
                                       blocking=True,
                                       context=context)

    if state.state in HVAC_MODES:
        await call_service(SERVICE_SET_HVAC_MODE, [],
                           {ATTR_HVAC_MODE: state.state})

    if ATTR_AUX_HEAT in state.attributes:
        await call_service(SERVICE_SET_AUX_HEAT, [ATTR_AUX_HEAT])

    if ((ATTR_TEMPERATURE in state.attributes)
            or (ATTR_TARGET_TEMP_HIGH in state.attributes)
            or (ATTR_TARGET_TEMP_LOW in state.attributes)):
        await call_service(
            SERVICE_SET_TEMPERATURE,
            [ATTR_TEMPERATURE, ATTR_TARGET_TEMP_HIGH, ATTR_TARGET_TEMP_LOW],
        )

    if ATTR_PRESET_MODE in state.attributes:
        await call_service(SERVICE_SET_PRESET_MODE, [ATTR_PRESET_MODE])

    if ATTR_SWING_MODE in state.attributes:
        await call_service(SERVICE_SET_SWING_MODE, [ATTR_SWING_MODE])

    if ATTR_HUMIDITY in state.attributes:
        await call_service(SERVICE_SET_HUMIDITY, [ATTR_HUMIDITY])


async def async_reproduce_states(hass: HomeAssistantType,
                                 states: Iterable[State],
                                 context: Optional[Context] = None) -> None:
    """Reproduce component states."""
    await asyncio.gather(*(_async_reproduce_states(hass, state, context)
                           for state in states))
