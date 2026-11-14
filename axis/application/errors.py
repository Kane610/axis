"""Safe application failures, independent of terminal or graphical adapters."""

from typing import Never


class StorageError(ValueError):
    """Safe, actionable registry validation or persistence failure."""


class OperationError(Exception):
    """A device operation failed, with a message safe for presentation."""


def _fail(message: str) -> Never:
    raise StorageError(message) from None
