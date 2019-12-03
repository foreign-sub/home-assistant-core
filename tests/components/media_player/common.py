"""Collection of helper methods.

All containing methods are legacy helpers that should not be used by new
components. Instead call the service directly.
"""
from homeassistant.components.media_player.const import ATTR_INPUT_SOURCE
from homeassistant.components.media_player.const import ATTR_MEDIA_CONTENT_ID
from homeassistant.components.media_player.const import ATTR_MEDIA_CONTENT_TYPE
from homeassistant.components.media_player.const import ATTR_MEDIA_ENQUEUE
from homeassistant.components.media_player.const import ATTR_MEDIA_SEEK_POSITION
from homeassistant.components.media_player.const import ATTR_MEDIA_VOLUME_LEVEL
from homeassistant.components.media_player.const import ATTR_MEDIA_VOLUME_MUTED
from homeassistant.components.media_player.const import DOMAIN
from homeassistant.components.media_player.const import SERVICE_CLEAR_PLAYLIST
from homeassistant.components.media_player.const import SERVICE_PLAY_MEDIA
from homeassistant.components.media_player.const import SERVICE_SELECT_SOURCE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.const import ENTITY_MATCH_ALL
from homeassistant.const import SERVICE_MEDIA_NEXT_TRACK
from homeassistant.const import SERVICE_MEDIA_PAUSE
from homeassistant.const import SERVICE_MEDIA_PLAY
from homeassistant.const import SERVICE_MEDIA_PLAY_PAUSE
from homeassistant.const import SERVICE_MEDIA_PREVIOUS_TRACK
from homeassistant.const import SERVICE_MEDIA_SEEK
from homeassistant.const import SERVICE_MEDIA_STOP
from homeassistant.const import SERVICE_TOGGLE
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.const import SERVICE_VOLUME_DOWN
from homeassistant.const import SERVICE_VOLUME_MUTE
from homeassistant.const import SERVICE_VOLUME_SET
from homeassistant.const import SERVICE_VOLUME_UP
from homeassistant.loader import bind_hass


@bind_hass
def turn_on(hass, entity_id=ENTITY_MATCH_ALL):
    """Turn on specified media player or all."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_TURN_ON, data)


@bind_hass
def turn_off(hass, entity_id=ENTITY_MATCH_ALL):
    """Turn off specified media player or all."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_TURN_OFF, data)


@bind_hass
def toggle(hass, entity_id=ENTITY_MATCH_ALL):
    """Toggle specified media player or all."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_TOGGLE, data)


@bind_hass
def volume_up(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for volume up."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_VOLUME_UP, data)


@bind_hass
def volume_down(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for volume down."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_VOLUME_DOWN, data)


@bind_hass
def mute_volume(hass, mute, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for muting the volume."""
    data = {ATTR_MEDIA_VOLUME_MUTED: mute}

    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id

    hass.services.call(DOMAIN, SERVICE_VOLUME_MUTE, data)


@bind_hass
def set_volume_level(hass, volume, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for setting the volume."""
    data = {ATTR_MEDIA_VOLUME_LEVEL: volume}

    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id

    hass.services.call(DOMAIN, SERVICE_VOLUME_SET, data)


@bind_hass
def media_play_pause(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for play/pause."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_MEDIA_PLAY_PAUSE, data)


@bind_hass
def media_play(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for play/pause."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_MEDIA_PLAY, data)


@bind_hass
def media_pause(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for pause."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_MEDIA_PAUSE, data)


@bind_hass
def media_stop(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for stop."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_MEDIA_STOP, data)


@bind_hass
def media_next_track(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for next track."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_MEDIA_NEXT_TRACK, data)


@bind_hass
def media_previous_track(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for prev track."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_MEDIA_PREVIOUS_TRACK, data)


@bind_hass
def media_seek(hass, position, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command to seek in current playing media."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    data[ATTR_MEDIA_SEEK_POSITION] = position
    hass.services.call(DOMAIN, SERVICE_MEDIA_SEEK, data)


@bind_hass
def play_media(hass, media_type, media_id, entity_id=ENTITY_MATCH_ALL, enqueue=None):
    """Send the media player the command for playing media."""
    data = {ATTR_MEDIA_CONTENT_TYPE: media_type, ATTR_MEDIA_CONTENT_ID: media_id}

    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id

    if enqueue:
        data[ATTR_MEDIA_ENQUEUE] = enqueue

    hass.services.call(DOMAIN, SERVICE_PLAY_MEDIA, data)


@bind_hass
def select_source(hass, source, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command to select input source."""
    data = {ATTR_INPUT_SOURCE: source}

    if entity_id:
        data[ATTR_ENTITY_ID] = entity_id

    hass.services.call(DOMAIN, SERVICE_SELECT_SOURCE, data)


@bind_hass
def clear_playlist(hass, entity_id=ENTITY_MATCH_ALL):
    """Send the media player the command for clear playlist."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    hass.services.call(DOMAIN, SERVICE_CLEAR_PLAYLIST, data)
