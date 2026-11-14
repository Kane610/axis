"""Identify device request, authentication, permission, and response failures."""


class AxisException(Exception):
    """Base exception for failures reported by the Axis device library."""


class RequestError(AxisException):
    """A device request could not be completed, for example after a connection timeout."""


class ResponseError(AxisException):
    """The device response is invalid or unexpected."""


class Unauthorized(AxisException):
    """The device rejected authentication (HTTP 401)."""


class Forbidden(AxisException):
    """The device refused access to the requested endpoint (HTTP 403)."""


class LoginRequired(AxisException):
    """The device requires the user to log in."""


class MethodNotAllowed(AxisException):
    """The endpoint does not allow the requested HTTP method (HTTP 405)."""


class PathNotFound(AxisException):
    """The requested device endpoint was not found (HTTP 404)."""


ERRORS = {
    401: Unauthorized,
    403: Forbidden,
    404: PathNotFound,
    405: MethodNotAllowed,
}


def raise_error(error: int) -> None:
    """Raise the exception mapped to an HTTP status, or AxisException for other codes."""
    cls = ERRORS.get(error, AxisException)
    raise cls(error)
