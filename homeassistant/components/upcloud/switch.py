"""Support for interacting with UpCloud servers."""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from . import CONF_SERVERS
from . import DATA_UPCLOUD
from . import SIGNAL_UPDATE_UPCLOUD
from . import UpCloudServerEntity
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.components.switch import SwitchDevice
from homeassistant.const import STATE_OFF
from homeassistant.helpers.dispatcher import dispatcher_send

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_SERVERS): vol.All(cv.ensure_list, [cv.string])}
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the UpCloud server switch."""
    upcloud = hass.data[DATA_UPCLOUD]

    servers = config.get(CONF_SERVERS)

    devices = [UpCloudSwitch(upcloud, uuid) for uuid in servers]

    add_entities(devices, True)


class UpCloudSwitch(UpCloudServerEntity, SwitchDevice):
    """Representation of an UpCloud server switch."""

    def turn_on(self, **kwargs):
        """Start the server."""
        if self.state == STATE_OFF:
            self.data.start()
            dispatcher_send(self.hass, SIGNAL_UPDATE_UPCLOUD)

    def turn_off(self, **kwargs):
        """Stop the server."""
        if self.is_on:
            self.data.stop()
