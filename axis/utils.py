"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import httpx

from .errors import raise_error, RequestError

LOGGER = logging.getLogger(__name__)


def session_request(session, url, **kwargs):
    """Do HTTP/S request and return response as a string."""
    LOGGER.debug("%s %s", url, kwargs)
    try:
        response = session(url, **kwargs)

        response.raise_for_status()

        return response.text

    except httpx.HTTPStatusError as errh:
        LOGGER.debug("%s, %s", response, errh)
        raise_error(response.status_code)

    except httpx.TransportError as errc:
        LOGGER.debug("%s", errc)
        raise RequestError("Connection error: {}".format(errc))

    except httpx.TimeoutException as errt:
        LOGGER.debug("%s", errt)
        raise RequestError("Timeout: {}".format(errt))

    except httpx.RequestError as err:
        LOGGER.debug("%s", err)
        raise RequestError("Unknown error: {}".format(err))
