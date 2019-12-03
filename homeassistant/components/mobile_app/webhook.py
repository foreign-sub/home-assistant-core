"""Webhook handlers for mobile_app."""
import logging

import voluptuous as vol
from aiohttp.web import HTTPBadRequest
from aiohttp.web import Request
from aiohttp.web import Response

from .const import ATTR_DEVICE_ID
from .const import ATTR_DEVICE_NAME
from .const import ATTR_EVENT_DATA
from .const import ATTR_EVENT_TYPE
from .const import ATTR_MANUFACTURER
from .const import ATTR_MODEL
from .const import ATTR_OS_VERSION
from .const import ATTR_SENSOR_TYPE
from .const import ATTR_SENSOR_UNIQUE_ID
from .const import ATTR_SUPPORTS_ENCRYPTION
from .const import ATTR_TEMPLATE
from .const import ATTR_TEMPLATE_VARIABLES
from .const import ATTR_WEBHOOK_DATA
from .const import ATTR_WEBHOOK_ENCRYPTED
from .const import ATTR_WEBHOOK_ENCRYPTED_DATA
from .const import ATTR_WEBHOOK_TYPE
from .const import CONF_CLOUDHOOK_URL
from .const import CONF_REMOTE_UI_URL
from .const import CONF_SECRET
from .const import DATA_CONFIG_ENTRIES
from .const import DATA_DELETED_IDS
from .const import DATA_STORE
from .const import DOMAIN
from .const import ERR_ENCRYPTION_REQUIRED
from .const import ERR_SENSOR_DUPLICATE_UNIQUE_ID
from .const import ERR_SENSOR_NOT_REGISTERED
from .const import SIGNAL_LOCATION_UPDATE
from .const import SIGNAL_SENSOR_UPDATE
from .const import WEBHOOK_PAYLOAD_SCHEMA
from .const import WEBHOOK_SCHEMAS
from .const import WEBHOOK_TYPE_CALL_SERVICE
from .const import WEBHOOK_TYPE_FIRE_EVENT
from .const import WEBHOOK_TYPE_GET_CONFIG
from .const import WEBHOOK_TYPE_GET_ZONES
from .const import WEBHOOK_TYPE_REGISTER_SENSOR
from .const import WEBHOOK_TYPE_RENDER_TEMPLATE
from .const import WEBHOOK_TYPE_UPDATE_LOCATION
from .const import WEBHOOK_TYPE_UPDATE_REGISTRATION
from .const import WEBHOOK_TYPE_UPDATE_SENSOR_STATES
from .const import WEBHOOK_TYPES
from .helpers import _decrypt_payload
from .helpers import empty_okay_response
from .helpers import error_response
from .helpers import registration_context
from .helpers import safe_registration
from .helpers import savable_state
from .helpers import webhook_response
from homeassistant.components.frontend import MANIFEST_JSON
from homeassistant.components.zone.const import DOMAIN as ZONE_DOMAIN
from homeassistant.const import ATTR_DOMAIN
from homeassistant.const import ATTR_SERVICE
from homeassistant.const import ATTR_SERVICE_DATA
from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.const import HTTP_BAD_REQUEST
from homeassistant.const import HTTP_CREATED
from homeassistant.core import EventOrigin
from homeassistant.exceptions import HomeAssistantError
from homeassistant.exceptions import ServiceNotFound
from homeassistant.exceptions import TemplateError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.template import attach
from homeassistant.helpers.typing import HomeAssistantType

_LOGGER = logging.getLogger(__name__)


async def handle_webhook(
    hass: HomeAssistantType, webhook_id: str, request: Request
) -> Response:
    """Handle webhook callback."""
    if webhook_id in hass.data[DOMAIN][DATA_DELETED_IDS]:
        return Response(status=410)

    headers = {}

    config_entry = hass.data[DOMAIN][DATA_CONFIG_ENTRIES][webhook_id]

    registration = config_entry.data

    try:
        req_data = await request.json()
    except ValueError:
        _LOGGER.warning("Received invalid JSON from mobile_app")
        return empty_okay_response(status=HTTP_BAD_REQUEST)

    if (
        ATTR_WEBHOOK_ENCRYPTED not in req_data
        and registration[ATTR_SUPPORTS_ENCRYPTION]
    ):
        _LOGGER.warning(
            "Refusing to accept unencrypted webhook from %s",
            registration[ATTR_DEVICE_NAME],
        )
        return error_response(ERR_ENCRYPTION_REQUIRED, "Encryption required")

    try:
        req_data = WEBHOOK_PAYLOAD_SCHEMA(req_data)
    except vol.Invalid as ex:
        err = vol.humanize.humanize_error(req_data, ex)
        _LOGGER.error("Received invalid webhook payload: %s", err)
        return empty_okay_response()

    webhook_type = req_data[ATTR_WEBHOOK_TYPE]

    webhook_payload = req_data.get(ATTR_WEBHOOK_DATA, {})

    if req_data[ATTR_WEBHOOK_ENCRYPTED]:
        enc_data = req_data[ATTR_WEBHOOK_ENCRYPTED_DATA]
        webhook_payload = _decrypt_payload(registration[CONF_SECRET], enc_data)

    if webhook_type not in WEBHOOK_TYPES:
        _LOGGER.error("Received invalid webhook type: %s", webhook_type)
        return empty_okay_response()

    data = webhook_payload

    _LOGGER.debug("Received webhook payload for type %s: %s", webhook_type, data)

    if webhook_type in WEBHOOK_SCHEMAS:
        try:
            data = WEBHOOK_SCHEMAS[webhook_type](webhook_payload)
        except vol.Invalid as ex:
            err = vol.humanize.humanize_error(webhook_payload, ex)
            _LOGGER.error("Received invalid webhook payload: %s", err)
            return empty_okay_response(headers=headers)

    context = registration_context(registration)

    if webhook_type == WEBHOOK_TYPE_CALL_SERVICE:
        try:
            await hass.services.async_call(
                data[ATTR_DOMAIN],
                data[ATTR_SERVICE],
                data[ATTR_SERVICE_DATA],
                blocking=True,
                context=context,
            )
        except (vol.Invalid, ServiceNotFound, Exception) as ex:
            _LOGGER.error(
                "Error when calling service during mobile_app "
                "webhook (device name: %s): %s",
                registration[ATTR_DEVICE_NAME],
                ex,
            )
            raise HTTPBadRequest()

        return empty_okay_response(headers=headers)

    if webhook_type == WEBHOOK_TYPE_FIRE_EVENT:
        event_type = data[ATTR_EVENT_TYPE]
        hass.bus.async_fire(
            event_type, data[ATTR_EVENT_DATA], EventOrigin.remote, context=context
        )
        return empty_okay_response(headers=headers)

    if webhook_type == WEBHOOK_TYPE_RENDER_TEMPLATE:
        resp = {}
        for key, item in data.items():
            try:
                tpl = item[ATTR_TEMPLATE]
                attach(hass, tpl)
                resp[key] = tpl.async_render(item.get(ATTR_TEMPLATE_VARIABLES))
            except TemplateError as ex:
                resp[key] = {"error": str(ex)}

        return webhook_response(resp, registration=registration, headers=headers)

    if webhook_type == WEBHOOK_TYPE_UPDATE_LOCATION:
        hass.helpers.dispatcher.async_dispatcher_send(
            SIGNAL_LOCATION_UPDATE.format(config_entry.entry_id), data
        )
        return empty_okay_response(headers=headers)

    if webhook_type == WEBHOOK_TYPE_UPDATE_REGISTRATION:
        new_registration = {**registration, **data}

        device_registry = await dr.async_get_registry(hass)

        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={
                (ATTR_DEVICE_ID, registration[ATTR_DEVICE_ID]),
                (CONF_WEBHOOK_ID, registration[CONF_WEBHOOK_ID]),
            },
            manufacturer=new_registration[ATTR_MANUFACTURER],
            model=new_registration[ATTR_MODEL],
            name=new_registration[ATTR_DEVICE_NAME],
            sw_version=new_registration[ATTR_OS_VERSION],
        )

        hass.config_entries.async_update_entry(config_entry, data=new_registration)

        return webhook_response(
            safe_registration(new_registration),
            registration=registration,
            headers=headers,
        )

    if webhook_type == WEBHOOK_TYPE_REGISTER_SENSOR:
        entity_type = data[ATTR_SENSOR_TYPE]

        unique_id = data[ATTR_SENSOR_UNIQUE_ID]

        unique_store_key = f"{webhook_id}_{unique_id}"

        if unique_store_key in hass.data[DOMAIN][entity_type]:
            _LOGGER.error("Refusing to re-register existing sensor %s!", unique_id)
            return error_response(
                ERR_SENSOR_DUPLICATE_UNIQUE_ID,
                f"{entity_type} {unique_id} already exists!",
                status=409,
            )

        data[CONF_WEBHOOK_ID] = webhook_id

        hass.data[DOMAIN][entity_type][unique_store_key] = data

        try:
            await hass.data[DOMAIN][DATA_STORE].async_save(savable_state(hass))
        except HomeAssistantError as ex:
            _LOGGER.error("Error registering sensor: %s", ex)
            return empty_okay_response()

        register_signal = "{}_{}_register".format(DOMAIN, data[ATTR_SENSOR_TYPE])
        async_dispatcher_send(hass, register_signal, data)

        return webhook_response(
            {"success": True},
            registration=registration,
            status=HTTP_CREATED,
            headers=headers,
        )

    if webhook_type == WEBHOOK_TYPE_UPDATE_SENSOR_STATES:
        resp = {}
        for sensor in data:
            entity_type = sensor[ATTR_SENSOR_TYPE]

            unique_id = sensor[ATTR_SENSOR_UNIQUE_ID]

            unique_store_key = f"{webhook_id}_{unique_id}"

            if unique_store_key not in hass.data[DOMAIN][entity_type]:
                _LOGGER.error(
                    "Refusing to update non-registered sensor: %s", unique_store_key
                )
                err_msg = f"{entity_type} {unique_id} is not registered"
                resp[unique_id] = {
                    "success": False,
                    "error": {"code": ERR_SENSOR_NOT_REGISTERED, "message": err_msg},
                }
                continue

            entry = hass.data[DOMAIN][entity_type][unique_store_key]

            new_state = {**entry, **sensor}

            hass.data[DOMAIN][entity_type][unique_store_key] = new_state

            safe = savable_state(hass)

            try:
                await hass.data[DOMAIN][DATA_STORE].async_save(safe)
            except HomeAssistantError as ex:
                _LOGGER.error("Error updating mobile_app registration: %s", ex)
                return empty_okay_response()

            async_dispatcher_send(hass, SIGNAL_SENSOR_UPDATE, new_state)

            resp[unique_id] = {"success": True}

        return webhook_response(resp, registration=registration, headers=headers)

    if webhook_type == WEBHOOK_TYPE_GET_ZONES:
        zones = (
            hass.states.get(entity_id)
            for entity_id in sorted(hass.states.async_entity_ids(ZONE_DOMAIN))
        )
        return webhook_response(list(zones), registration=registration, headers=headers)

    if webhook_type == WEBHOOK_TYPE_GET_CONFIG:

        hass_config = hass.config.as_dict()

        resp = {
            "latitude": hass_config["latitude"],
            "longitude": hass_config["longitude"],
            "elevation": hass_config["elevation"],
            "unit_system": hass_config["unit_system"],
            "location_name": hass_config["location_name"],
            "time_zone": hass_config["time_zone"],
            "components": hass_config["components"],
            "version": hass_config["version"],
            "theme_color": MANIFEST_JSON["theme_color"],
        }

        if CONF_CLOUDHOOK_URL in registration:
            resp[CONF_CLOUDHOOK_URL] = registration[CONF_CLOUDHOOK_URL]

        if "cloud" in hass.config.components:
            try:
                resp[CONF_REMOTE_UI_URL] = hass.components.cloud.async_remote_ui_url()
            except hass.components.cloud.CloudNotAvailable:
                pass

        return webhook_response(resp, registration=registration, headers=headers)
