"""Axis errors."""


class AxisException(Exception):
    """Base error for Axis."""


class RequestError(AxisException):
    """Unable to fulfill request.

    Raised when device cannot be reached.
    """


class ResponseError(AxisException):
    """Invalid response."""


class Unauthorized(AxisException):
    """Username is not authorized."""


class Forbidden(AxisException):
    """Endpoint is not accessible due to low permissions."""


class LoginRequired(AxisException):
    """User is logged out."""


class MethodNotAllowed(AxisException):
    """Invalid request."""


class PathNotFound(AxisException):
    """Path not found."""


ERRORS = {
    401: Unauthorized,
    403: Forbidden,
    404: PathNotFound,
    405: MethodNotAllowed,
}


def raise_error(error: int) -> None:
    """Raise error."""
    cls = ERRORS.get(error, AxisException)
    raise cls(error)
