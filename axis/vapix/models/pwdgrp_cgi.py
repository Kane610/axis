"""Axis Vapix user management user class."""

from dataclasses import dataclass
import re

from typing_extensions import NotRequired, Self, TypedDict

from .api import APIItem, ApiItem, ApiRequest, ApiResponse

ADMIN = "admin"
OPERATOR = "operator"
VIEWER = "viewer"
PTZ = "ptz"


SGRP_VIEWER = VIEWER
SGRP_OPERATOR = "{}:{}".format(VIEWER, OPERATOR)
SGRP_ADMIN = "{}:{}:{}".format(VIEWER, OPERATOR, ADMIN)

REGEX_USER = re.compile(r"^[A-Z0-9]{1,14}$", re.IGNORECASE)
REGEX_PASS = re.compile(r"^[x20-x7e]{1,64}$")
REGEX_STRING = re.compile(r"[A-Z0-9]+", re.IGNORECASE)


class UserGroupsT(TypedDict):
    """Groups user belongs to."""

    user: str
    admin: bool
    operator: bool
    viewer: bool
    ptz: bool


@dataclass
class User(ApiItem):
    """Represents a user and the groups it belongs to."""

    admin: bool
    operator: bool
    viewer: bool
    ptz: bool

    @property
    def name(self) -> str:
        """User name."""
        return self.id

    @classmethod
    def decode(cls, user: str, data: UserGroupsT) -> Self:
        """Create object from dict."""
        return cls(
            id=user,
            admin=data["admin"],
            operator=data["operator"],
            viewer=data["viewer"],
            ptz=data["ptz"],
        )

    @classmethod
    def from_dict(cls, data: dict[str, UserGroupsT]) -> dict[str, Self]:
        """Create objects from list."""
        # ports = [cls.from_dict(item) for item in data]
        return {user: cls.decode(user, groups) for user, groups in data.items()}


@dataclass
class GetUsersRequest(ApiRequest):
    """Request object for listing users."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    # params = "action=get"
    content_type = "text/plain"
    # error_codes = error_codes

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        return {"action": "get"}


@dataclass
class GetUsersResponse(ApiResponse[dict[str, User]]):
    """Response object for listing ports."""

    data: dict[str, User]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        if "=" not in (string_data := bytes_data.decode()):
            return cls(data={})

        data: dict[str, str] = dict(
            group.split("=", 1) for group in string_data.splitlines()  # type: ignore
        )

        user_list = ["root"] + REGEX_STRING.findall(data["users"])

        users = {
            user: {
                group: user in REGEX_STRING.findall(data[group])
                for group in [ADMIN, OPERATOR, VIEWER, PTZ]
            }
            for user in user_list
        }

        #
        return cls(data=User.from_dict(users))


@dataclass
class CreateUserRequest(ApiRequest):
    """Request object for creating a user."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"
    # error_codes = error_codes

    user: str
    pwd: str
    sgrp: str
    comment: str | None = None

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        data = {
            "action": "add",
            "user": self.user,
            "pwd": self.pwd,
            "grp": "users",
            "sgrp": self.sgrp,
        }

        if self.comment is not None:
            data["comment"] = self.comment

        return data


@dataclass
class ModifyUserRequest(ApiRequest):
    """Request object for modifying a user."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"
    # error_codes = error_codes

    user: str
    pwd: str | None = None
    sgrp: str | None = None
    comment: str | None = None

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        data = {"action": "update", "user": self.user}

        if self.pwd is not None:
            data["pwd"] = self.pwd

        if self.sgrp:
            data["sgrp"] = self.sgrp

        if self.comment:
            data["comment"] = self.comment

        return data


@dataclass
class DeleteUserRequest(ApiRequest):
    """Request object for deleting a user."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"
    # error_codes = error_codes

    user: str

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        return {"action": "remove", "user": self.user}
