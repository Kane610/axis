"""Safe application failures, independent of terminal or graphical adapters."""

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
    """Stable categories for application recovery, not raw transport exceptions."""

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
        """Preserve safe fallback behavior without logging arbitrary input."""
        LOGGER.debug("Unknown application error category.")
        return cls.UNKNOWN


class StorageError(ValueError):
    """Safe, actionable registry validation or persistence failure."""


class OperationError(Exception):
    """A device operation failed, with a message safe for presentation."""

    def __init__(
        self,
        message: str,
        *,
        kind: ErrorKind | str = ErrorKind.OPERATION,
        outcome_unknown: bool = False,
    ) -> None:
        """Expose recovery metadata without retaining a transport exception."""
        super().__init__(message)
        self.kind = ErrorKind(kind)
        self.outcome_unknown = outcome_unknown


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
