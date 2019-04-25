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


class LoginRequired(AxisException):
    """User is logged out."""


class MethodNotAllowed(AxisException):
    """Invalid request."""


class NoPermission(AxisException):
    """Users permissions are not high enough."""


ERRORS = {
    401: Unauthorized,
    405: MethodNotAllowed
}


def raise_error(error):
    type = error
    cls = ERRORS.get(type, AxisException)
    raise cls("{}".format(type))
