"""Report device and configuration problems without exposing login details."""

from enum import StrEnum
import logging
from ssl import SSLError
from typing import Never

from aiohttp import ClientConnectionError, ClientPayloadError

from axis.errors import (
    Forbidden,
    LoginRequired,
    MethodNotAllowed,
    PathNotFound,
    RequestError,
    ResponseError,
    Unauthorized,
)

LOGGER = logging.getLogger(__name__)


class ErrorKind(StrEnum):
    """Identify a failure so applications can offer an appropriate next step."""

    AUTHENTICATION = "authentication"
    CERTIFICATE = "certificate"
    CONFLICT = "conflict"
    CONNECTION = "connection"
    OPERATION = "operation"
    PERMISSION = "permission"
    RESPONSE = "response"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"
    VALIDATION = "validation"

    @classmethod
    def _missing_(cls, value: object) -> ErrorKind:
        """Treat unrecognized categories as unknown without logging their contents."""
        LOGGER.debug("Unknown application error category.")
        return cls.UNKNOWN


class StorageError(ValueError):
    """Saved device configuration is invalid or cannot be read or updated."""


class OperationError(Exception):
    """A device operation failed, with a safe message and information about recovery."""

    def __init__(
        self,
        message: str,
        *,
        kind: ErrorKind | str = ErrorKind.OPERATION,
        outcome_unknown: bool = False,
        device_code: int | None = None,
    ) -> None:
        """Store the failure category and whether a device write may have completed."""
        super().__init__(message)
        self.kind = ErrorKind(kind)
        self.outcome_unknown = outcome_unknown
        self.device_code = device_code


def _fail(message: str) -> Never:
    raise StorageError(message) from None


def _failure(
    exc: Exception,
    *,
    outcome_unknown: bool = False,
    message: str = "Device operation failed.",
) -> OperationError:
    if isinstance(exc, (Unauthorized, LoginRequired)):
        kind = ErrorKind.AUTHENTICATION
    elif isinstance(exc, Forbidden):
        kind = ErrorKind.PERMISSION
    elif isinstance(exc, SSLError):
        kind = ErrorKind.CERTIFICATE
    elif isinstance(exc, TimeoutError):
        kind = ErrorKind.TIMEOUT
    elif isinstance(exc, (RequestError, ClientConnectionError)):
        kind = ErrorKind.CONNECTION
    elif isinstance(exc, (PathNotFound, MethodNotAllowed)):
        kind = ErrorKind.UNSUPPORTED
    elif isinstance(exc, (ResponseError, ClientPayloadError)):
        kind = ErrorKind.RESPONSE
    elif isinstance(exc, ValueError):
        kind = ErrorKind.VALIDATION
    else:
        kind = ErrorKind.OPERATION
    uncertain = outcome_unknown and kind in {
        ErrorKind.CONNECTION,
        ErrorKind.OPERATION,
        ErrorKind.RESPONSE,
        ErrorKind.TIMEOUT,
    }
    msg = (
        "Device operation failed; the account change outcome is unknown. "
        "Read accounts before retrying."
        if uncertain
        else message
    )
    return OperationError(msg, kind=kind, outcome_unknown=uncertain)
