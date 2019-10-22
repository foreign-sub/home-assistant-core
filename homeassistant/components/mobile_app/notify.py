"""Support for mobile_app push notifications."""
import asyncio
import logging

import async_timeout

import homeassistant.util.dt as dt_util
from .const import ATTR_APP_DATA
from .const import ATTR_APP_ID
from .const import ATTR_APP_VERSION
from .const import ATTR_DEVICE_NAME
from .const import ATTR_OS_VERSION
from .const import ATTR_PUSH_RATE_LIMITS
from .const import ATTR_PUSH_RATE_LIMITS_ERRORS
from .const import ATTR_PUSH_RATE_LIMITS_MAXIMUM
from .const import ATTR_PUSH_RATE_LIMITS_RESETS_AT
from .const import ATTR_PUSH_RATE_LIMITS_SUCCESSFUL
from .const import ATTR_PUSH_TOKEN
from .const import ATTR_PUSH_URL
from .const import DATA_CONFIG_ENTRIES
from .const import DOMAIN
from homeassistant.components.notify import ATTR_DATA
from homeassistant.components.notify import ATTR_MESSAGE
from homeassistant.components.notify import ATTR_TARGET
from homeassistant.components.notify import ATTR_TITLE
from homeassistant.components.notify import ATTR_TITLE_DEFAULT
from homeassistant.components.notify import BaseNotificationService
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


def push_registrations(hass):
    """Return a dictionary of push enabled registrations."""
    targets = {}
    for webhook_id, entry in hass.data[DOMAIN][DATA_CONFIG_ENTRIES].items():
        data = entry.data
        app_data = data[ATTR_APP_DATA]
        if ATTR_PUSH_TOKEN in app_data and ATTR_PUSH_URL in app_data:
            device_name = data[ATTR_DEVICE_NAME]
            if device_name in targets:
                _LOGGER.warning("Found duplicate device name %s", device_name)
                continue
            targets[device_name] = webhook_id
    return targets


# pylint: disable=invalid-name
def log_rate_limits(hass, device_name, resp, level=logging.INFO):
    """Output rate limit log line at given level."""
    if ATTR_PUSH_RATE_LIMITS not in resp:
        return

    rate_limits = resp[ATTR_PUSH_RATE_LIMITS]
    resetsAt = rate_limits[ATTR_PUSH_RATE_LIMITS_RESETS_AT]
    resetsAtTime = dt_util.parse_datetime(resetsAt) - dt_util.utcnow()
    rate_limit_msg = (
        "mobile_app push notification rate limits for %s: "
        "%d sent, %d allowed, %d errors, "
        "resets in %s"
    )
    _LOGGER.log(
        level,
        rate_limit_msg,
        device_name,
        rate_limits[ATTR_PUSH_RATE_LIMITS_SUCCESSFUL],
        rate_limits[ATTR_PUSH_RATE_LIMITS_MAXIMUM],
        rate_limits[ATTR_PUSH_RATE_LIMITS_ERRORS],
        str(resetsAtTime).split(".")[0],
    )


async def async_get_service(hass, config, discovery_info=None):
    """Get the mobile_app notification service."""
    session = async_get_clientsession(hass)
    return MobileAppNotificationService(session)


class MobileAppNotificationService(BaseNotificationService):
    """Implement the notification service for mobile_app."""

    def __init__(self, session):
        """Initialize the service."""
        self._session = session

    @property
    def targets(self):
        """Return a dictionary of registered targets."""
        return push_registrations(self.hass)

    async def async_send_message(self, message="", **kwargs):
        """Send a message to the Lambda APNS gateway."""
        data = {ATTR_MESSAGE: message}

        if kwargs.get(ATTR_TITLE) is not None:
            # Remove default title from notifications.
            if kwargs.get(ATTR_TITLE) != ATTR_TITLE_DEFAULT:
                data[ATTR_TITLE] = kwargs.get(ATTR_TITLE)

        targets = kwargs.get(ATTR_TARGET)

        if not targets:
            targets = push_registrations(self.hass).values()

        if kwargs.get(ATTR_DATA) is not None:
            data[ATTR_DATA] = kwargs.get(ATTR_DATA)

        for target in targets:
            entry = self.hass.data[DOMAIN][DATA_CONFIG_ENTRIES][target]
            entry_data = entry.data

            app_data = entry_data[ATTR_APP_DATA]
            push_token = app_data[ATTR_PUSH_TOKEN]
            push_url = app_data[ATTR_PUSH_URL]

            data[ATTR_PUSH_TOKEN] = push_token

            reg_info = {
                ATTR_APP_ID: entry_data[ATTR_APP_ID],
                ATTR_APP_VERSION: entry_data[ATTR_APP_VERSION],
            }
            if ATTR_OS_VERSION in entry_data:
                reg_info[ATTR_OS_VERSION] = entry_data[ATTR_OS_VERSION]

            data["registration_info"] = reg_info

            try:
                with async_timeout.timeout(10):
                    response = await self._session.post(push_url, json=data)
                    result = await response.json()

                if response.status == 201:
                    log_rate_limits(self.hass, entry_data[ATTR_DEVICE_NAME], result)
                    return

                fallback_error = result.get("errorMessage", "Unknown error")
                fallback_message = (
                    "Internal server error, " "please try again later: " "{}"
                ).format(fallback_error)
                message = result.get("message", fallback_message)
                if response.status == 429:
                    _LOGGER.warning(message)
                    log_rate_limits(
                        self.hass, entry_data[ATTR_DEVICE_NAME], result, logging.WARNING
                    )
                else:
                    _LOGGER.error(message)

            except asyncio.TimeoutError:
                _LOGGER.error("Timeout sending notification to %s", push_url)
