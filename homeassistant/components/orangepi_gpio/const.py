"""Constants for Orange Pi GPIO."""
import voluptuous as vol
from nanopi import duo
from nanopi import neocore2
from orangepi import lite
from orangepi import lite2
from orangepi import one
from orangepi import oneplus
from orangepi import pc
from orangepi import pc2
from orangepi import pcplus
from orangepi import pi3
from orangepi import plus2e
from orangepi import prime
from orangepi import r1
from orangepi import winplus
from orangepi import zero
from orangepi import zeroplus
from orangepi import zeroplus2

from homeassistant.helpers import config_validation as cv

CONF_INVERT_LOGIC = "invert_logic"
CONF_PIN_MODE = "pin_mode"
CONF_PORTS = "ports"
DEFAULT_INVERT_LOGIC = False
PIN_MODES = {
    "lite": lite.BOARD,
    "lite2": lite2.BOARD,
    "one": one.BOARD,
    "oneplus": oneplus.BOARD,
    "pc": pc.BOARD,
    "pc2": pc2.BOARD,
    "pcplus": pcplus.BOARD,
    "pi3": pi3.BOARD,
    "plus2e": plus2e.BOARD,
    "prime": prime.BOARD,
    "r1": r1.BOARD,
    "winplus": winplus.BOARD,
    "zero": zero.BOARD,
    "zeroplus": zeroplus.BOARD,
    "zeroplus2": zeroplus2.BOARD,
    "duo": duo.BOARD,
    "neocore2": neocore2.BOARD,
}

_SENSORS_SCHEMA = vol.Schema({cv.positive_int: cv.string})

PORT_SCHEMA = {
    vol.Required(CONF_PORTS): _SENSORS_SCHEMA,
    vol.Required(CONF_PIN_MODE): vol.In(PIN_MODES.keys()),
    vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
}
