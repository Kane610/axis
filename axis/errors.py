"""Axis errors."""


class AxisError(Exception):
    """Base error for Axis."""


class RequestError(AxisError):
    """Unable to fulfill request.

    Raised when device cannot be reached.
    """


class ResponseError(AxisError):
    """Invalid response."""


class UnauthorizedError(AxisError):
    """Username is not authorized."""


class ForbiddenError(AxisError):
    """Endpoint is not accessible due to low permissions."""


class LoginRequiredError(AxisError):
    """User is logged out."""


class MethodNotAllowedError(AxisError):
    """Invalid request."""


class PathNotFoundError(AxisError):
    """Path not found."""


ERRORS = {
    401: UnauthorizedError,
    403: ForbiddenError,
    404: PathNotFoundError,
    405: MethodNotAllowedError,
}


def raise_error(error: int) -> None:
    """Raise error."""
    cls = ERRORS.get(error, AxisError)
    raise cls(error)
