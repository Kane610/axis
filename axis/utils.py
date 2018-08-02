"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import requests

_LOGGER = logging.getLogger(__name__)


def session_request(session, url, **kwargs):
    """Do HTTP/S request and return response as a string."""
    try:
        response = session(url, **kwargs)
        response.raise_for_status()
        if response.status_code != 200:
            _LOGGER.error(
                "HTTP status %d, response %s.", response.status, response.text)
            return None
    except requests.ConnectionError as err:
        _LOGGER.error("Connection error: %s", err)
        return None
    except requests.exceptions.HTTPError as err:
        _LOGGER.error("HTTP error: %s", err)
        return None
    return response.text
