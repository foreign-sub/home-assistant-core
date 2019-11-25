"""Demo platform that has two fake alarm control panels."""
import datetime

from homeassistant.components.manual.alarm_control_panel import ManualAlarm
from homeassistant.const import CONF_DELAY_TIME
from homeassistant.const import CONF_PENDING_TIME
from homeassistant.const import CONF_TRIGGER_TIME
from homeassistant.const import STATE_ALARM_ARMED_AWAY
from homeassistant.const import STATE_ALARM_ARMED_CUSTOM_BYPASS
from homeassistant.const import STATE_ALARM_ARMED_HOME
from homeassistant.const import STATE_ALARM_ARMED_NIGHT
from homeassistant.const import STATE_ALARM_DISARMED
from homeassistant.const import STATE_ALARM_TRIGGERED


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Demo alarm control panel platform."""
    async_add_entities(
        [
            ManualAlarm(
                hass,
                "Alarm",
                "1234",
                None,
                True,
                False,
                {
                    STATE_ALARM_ARMED_AWAY: {
                        CONF_DELAY_TIME: datetime.timedelta(seconds=0),
                        CONF_PENDING_TIME: datetime.timedelta(seconds=5),
                        CONF_TRIGGER_TIME: datetime.timedelta(seconds=10),
                    },
                    STATE_ALARM_ARMED_HOME: {
                        CONF_DELAY_TIME: datetime.timedelta(seconds=0),
                        CONF_PENDING_TIME: datetime.timedelta(seconds=5),
                        CONF_TRIGGER_TIME: datetime.timedelta(seconds=10),
                    },
                    STATE_ALARM_ARMED_NIGHT: {
                        CONF_DELAY_TIME: datetime.timedelta(seconds=0),
                        CONF_PENDING_TIME: datetime.timedelta(seconds=5),
                        CONF_TRIGGER_TIME: datetime.timedelta(seconds=10),
                    },
                    STATE_ALARM_DISARMED: {
                        CONF_DELAY_TIME: datetime.timedelta(seconds=0),
                        CONF_TRIGGER_TIME: datetime.timedelta(seconds=10),
                    },
                    STATE_ALARM_ARMED_CUSTOM_BYPASS: {
                        CONF_DELAY_TIME: datetime.timedelta(seconds=0),
                        CONF_PENDING_TIME: datetime.timedelta(seconds=5),
                        CONF_TRIGGER_TIME: datetime.timedelta(seconds=10),
                    },
                    STATE_ALARM_TRIGGERED: {
                        CONF_PENDING_TIME: datetime.timedelta(seconds=5)
                    },
                },
            )
        ]
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo config entry."""
    await async_setup_platform(hass, {}, async_add_entities)
