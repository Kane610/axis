"""Describe and validate account changes before sending them to an Axis device.

Prepared changes contain the account, privileges, and device to review, but no
passwords. Device writes are performed separately through application operations.
"""

from dataclasses import dataclass
import re

from axis.models.pwdgrp_cgi import SecondaryGroup

from .errors import ErrorKind, OperationError
from .records import DeviceRecord, DeviceSummary

_PRIVILEGES = {
    "admin": SecondaryGroup.ADMIN,
    "admin_ptz": SecondaryGroup.ADMIN_PTZ,
    "operator": SecondaryGroup.OPERATOR,
    "operator_ptz": SecondaryGroup.OPERATOR_PTZ,
    "viewer": SecondaryGroup.VIEWER,
    "viewer_ptz": SecondaryGroup.VIEWER_PTZ,
}


def validate_account_username(username: str) -> None:
    """Require an account name of 1-14 ASCII letters or digits."""
    if (
        not isinstance(username, str)
        or re.fullmatch(r"[A-Za-z0-9]{1,14}", username) is None
    ):
        msg = "Username must contain 1-14 ASCII letters or digits."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)


def _validate_account(action: str, username: str, privilege: str) -> None:
    if action not in {"create", "update", "delete"}:
        msg = "Unknown account action."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    validate_account_username(username)
    if privilege not in _PRIVILEGES:
        msg = "Unknown account privilege."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)


def _validate_password(action: str, password: str | None) -> None:
    if action == "create" and password is None:
        msg = "Creating an account requires a password."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    if password is not None and (
        not 1 <= len(password) <= 64
        or any(not 32 <= ord(char) <= 126 for char in password)
    ):
        msg = "Password must contain 1-64 printable ASCII characters."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)


def _validate_intent(action: str, target: object, password_change: object) -> None:
    if not isinstance(target, DeviceSummary) or type(password_change) is not bool:
        msg = "Account intentions require a device summary and boolean password intent."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    if (action == "create" and not password_change) or (
        action == "delete" and password_change
    ):
        msg = "Password intent does not match the account action."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)


@dataclass(frozen=True)
class AccountChange:
    """The account change to review, including its device but not its password."""

    action: str
    password_change: bool
    privilege: str
    target: DeviceSummary
    username: str

    def __post_init__(self) -> None:
        """Reject invalid actions, privileges, or password-change choices."""
        _validate_account(self.action, self.username, self.privilege)
        _validate_intent(self.action, self.target, self.password_change)

    def preview(self) -> dict[str, object]:
        """Describe the proposed change without contacting the device or reading a password."""
        payload: dict[str, object] = {
            "status": "preview",
            "action": self.action,
            "device": self.target.serial,
            "username": self.username,
        }
        if self.action != "delete":
            payload["privilege"] = self.privilege
            payload["password_change"] = self.password_change
        return payload


@dataclass(frozen=True)
class AccountChangeResult:
    """A change the device accepted; failed or uncertain writes do not produce this result."""

    intent: AccountChange

    def payload(self) -> dict[str, object]:
        """Return the reviewed change with its status set to applied."""
        return {**self.intent.preview(), "status": "applied"}


def prepare_account_change(
    record: DeviceRecord,
    action: str,
    username: str,
    privilege: str = "viewer",
    *,
    password_change: bool = False,
) -> AccountChange:
    """Build an account-change description without network access; new accounts need a password."""
    return AccountChange(
        action=action,
        password_change=action == "create" or password_change,
        privilege=privilege,
        target=record.summary(),
        username=username,
    )
