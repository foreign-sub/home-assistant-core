"""Class to hold all light accessories."""
import logging

from pyhap.const import CATEGORY_LIGHTBULB

from . import TYPES
from .accessories import debounce
from .accessories import HomeAccessory
from .const import CHAR_BRIGHTNESS
from .const import CHAR_COLOR_TEMPERATURE
from .const import CHAR_HUE
from .const import CHAR_ON
from .const import CHAR_SATURATION
from .const import PROP_MAX_VALUE
from .const import PROP_MIN_VALUE
from .const import SERV_LIGHTBULB
from homeassistant.components.light import ATTR_BRIGHTNESS
from homeassistant.components.light import ATTR_BRIGHTNESS_PCT
from homeassistant.components.light import ATTR_COLOR_TEMP
from homeassistant.components.light import ATTR_HS_COLOR
from homeassistant.components.light import ATTR_MAX_MIREDS
from homeassistant.components.light import ATTR_MIN_MIREDS
from homeassistant.components.light import DOMAIN
from homeassistant.components.light import SUPPORT_BRIGHTNESS
from homeassistant.components.light import SUPPORT_COLOR
from homeassistant.components.light import SUPPORT_COLOR_TEMP
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ATTR_SUPPORTED_FEATURES
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import STATE_OFF
from homeassistant.const import STATE_ON

_LOGGER = logging.getLogger(__name__)

RGB_COLOR = "rgb_color"


@TYPES.register("Light")
class Light(HomeAccessory):
    """Generate a Light accessory for a light entity.

    Currently supports: state, brightness, color temperature, rgb_color.
    """

    def __init__(self, *args):
        """Initialize a new Light accessory object."""
        super().__init__(*args, category=CATEGORY_LIGHTBULB)
        self._flag = {
            CHAR_ON: False,
            CHAR_BRIGHTNESS: False,
            CHAR_HUE: False,
            CHAR_SATURATION: False,
            CHAR_COLOR_TEMPERATURE: False,
            RGB_COLOR: False,
        }
        self._state = 0

        self.chars = []
        self._features = self.hass.states.get(
            self.entity_id).attributes.get(ATTR_SUPPORTED_FEATURES)
        if self._features & SUPPORT_BRIGHTNESS:
            self.chars.append(CHAR_BRIGHTNESS)
        if self._features & SUPPORT_COLOR_TEMP:
            self.chars.append(CHAR_COLOR_TEMPERATURE)
        if self._features & SUPPORT_COLOR:
            self.chars.append(CHAR_HUE)
            self.chars.append(CHAR_SATURATION)
            self._hue = None
            self._saturation = None

        serv_light = self.add_preload_service(SERV_LIGHTBULB, self.chars)
        self.char_on = serv_light.configure_char(
            CHAR_ON, value=self._state, setter_callback=self.set_state)

        if CHAR_BRIGHTNESS in self.chars:
            # Initial value is set to 100 because 0 is a special value (off). 100 is
            # an arbitrary non-zero value. It is updated immediately by update_state
            # to set to the correct initial value.
            self.char_brightness = serv_light.configure_char(
                CHAR_BRIGHTNESS,
                value=100,
                setter_callback=self.set_brightness)
        if CHAR_COLOR_TEMPERATURE in self.chars:
            min_mireds = self.hass.states.get(self.entity_id).attributes.get(
                ATTR_MIN_MIREDS, 153)
            max_mireds = self.hass.states.get(self.entity_id).attributes.get(
                ATTR_MAX_MIREDS, 500)
            self.char_color_temperature = serv_light.configure_char(
                CHAR_COLOR_TEMPERATURE,
                value=min_mireds,
                properties={
                    PROP_MIN_VALUE: min_mireds,
                    PROP_MAX_VALUE: max_mireds
                },
                setter_callback=self.set_color_temperature,
            )
        if CHAR_HUE in self.chars:
            self.char_hue = serv_light.configure_char(
                CHAR_HUE, value=0, setter_callback=self.set_hue)
        if CHAR_SATURATION in self.chars:
            self.char_saturation = serv_light.configure_char(
                CHAR_SATURATION, value=75, setter_callback=self.set_saturation)

    def set_state(self, value):
        """Set state if call came from HomeKit."""
        if self._state == value:
            return

        _LOGGER.debug("%s: Set state to %d", self.entity_id, value)
        self._flag[CHAR_ON] = True
        params = {ATTR_ENTITY_ID: self.entity_id}
        service = SERVICE_TURN_ON if value == 1 else SERVICE_TURN_OFF
        self.call_service(DOMAIN, service, params)

    @debounce
    def set_brightness(self, value):
        """Set brightness if call came from HomeKit."""
        _LOGGER.debug("%s: Set brightness to %d", self.entity_id, value)
        self._flag[CHAR_BRIGHTNESS] = True
        if value == 0:
            self.set_state(0)  # Turn off light
            return
        params = {ATTR_ENTITY_ID: self.entity_id, ATTR_BRIGHTNESS_PCT: value}
        self.call_service(DOMAIN, SERVICE_TURN_ON, params,
                          f"brightness at {value}%")

    def set_color_temperature(self, value):
        """Set color temperature if call came from HomeKit."""
        _LOGGER.debug("%s: Set color temp to %s", self.entity_id, value)
        self._flag[CHAR_COLOR_TEMPERATURE] = True
        params = {ATTR_ENTITY_ID: self.entity_id, ATTR_COLOR_TEMP: value}
        self.call_service(DOMAIN, SERVICE_TURN_ON, params,
                          f"color temperature at {value}")

    def set_saturation(self, value):
        """Set saturation if call came from HomeKit."""
        _LOGGER.debug("%s: Set saturation to %d", self.entity_id, value)
        self._flag[CHAR_SATURATION] = True
        self._saturation = value
        self.set_color()

    def set_hue(self, value):
        """Set hue if call came from HomeKit."""
        _LOGGER.debug("%s: Set hue to %d", self.entity_id, value)
        self._flag[CHAR_HUE] = True
        self._hue = value
        self.set_color()

    def set_color(self):
        """Set color if call came from HomeKit."""
        if (self._features & SUPPORT_COLOR and self._flag[CHAR_HUE]
                and self._flag[CHAR_SATURATION]):
            color = (self._hue, self._saturation)
            _LOGGER.debug("%s: Set hs_color to %s", self.entity_id, color)
            self._flag.update({
                CHAR_HUE: False,
                CHAR_SATURATION: False,
                RGB_COLOR: True
            })
            params = {ATTR_ENTITY_ID: self.entity_id, ATTR_HS_COLOR: color}
            self.call_service(DOMAIN, SERVICE_TURN_ON, params,
                              f"set color at {color}")

    def update_state(self, new_state):
        """Update light after state change."""
        # Handle State
        state = new_state.state
        if state in (STATE_ON, STATE_OFF):
            self._state = 1 if state == STATE_ON else 0
            if not self._flag[CHAR_ON] and self.char_on.value != self._state:
                self.char_on.set_value(self._state)
            self._flag[CHAR_ON] = False

        # Handle Brightness
        if CHAR_BRIGHTNESS in self.chars:
            brightness = new_state.attributes.get(ATTR_BRIGHTNESS)
            if not self._flag[CHAR_BRIGHTNESS] and isinstance(brightness, int):
                brightness = round(brightness / 255 * 100, 0)
                if self.char_brightness.value != brightness:
                    # The homeassistant component might report its brightness as 0 but is
                    # not off. But 0 is a special value in homekit. When you turn on a
                    # homekit accessory it will try to restore the last brightness state
                    # which will be the last value saved by char_brightness.set_value.
                    # But if it is set to 0, HomeKit will update the brightness to 100 as
                    # it thinks 0 is off.
                    #
                    # Therefore, if the the brighness is 0 and the device is still on,
                    # the brightness is mapped to 1 otherwise the update is ignored in
                    # order to avoid this incorrect behavior.
                    if brightness == 0:
                        if state == STATE_ON:
                            self.char_brightness.set_value(1)
                    else:
                        self.char_brightness.set_value(brightness)
            self._flag[CHAR_BRIGHTNESS] = False

        # Handle color temperature
        if CHAR_COLOR_TEMPERATURE in self.chars:
            color_temperature = new_state.attributes.get(ATTR_COLOR_TEMP)
            if (not self._flag[CHAR_COLOR_TEMPERATURE]
                    and isinstance(color_temperature, int) and
                    self.char_color_temperature.value != color_temperature):
                self.char_color_temperature.set_value(color_temperature)
            self._flag[CHAR_COLOR_TEMPERATURE] = False

        # Handle Color
        if CHAR_SATURATION in self.chars and CHAR_HUE in self.chars:
            hue, saturation = new_state.attributes.get(ATTR_HS_COLOR,
                                                       (None, None))
            if (not self._flag[RGB_COLOR]
                    and (hue != self._hue or saturation != self._saturation)
                    and isinstance(hue, (int, float))
                    and isinstance(saturation, (int, float))):
                self.char_hue.set_value(hue)
                self.char_saturation.set_value(saturation)
                self._hue, self._saturation = (hue, saturation)
            self._flag[RGB_COLOR] = False
