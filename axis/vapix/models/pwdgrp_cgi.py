"""Axis Vapix user management user class."""

from dataclasses import dataclass
import enum
import re

from typing_extensions import Self, TypedDict

from .api import ApiItem, ApiRequest, ApiResponse


class SecondaryGroup(enum.Enum):
    """Supported user secondary groups.

    Defines the user access rights for the account.
    """

    ADMIN = "viewer:operator:admin"
    ADMIN_PTZ = "viewer:operator:admin:ptz"
    OPERATOR = "viewer:operator"
    OPERATOR_PTZ = "viewer:operator:ptz"
    VIEWER = "viewer"
    VIEWER_PTZ = "viewer:ptz"


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
    def decode(cls, data: UserGroupsT) -> Self:
        """Create object from dict."""
        return cls(
            id=data["user"],
            admin=data["admin"],
            operator=data["operator"],
            viewer=data["viewer"],
            ptz=data["ptz"],
        )

    @classmethod
    def from_list(cls, data: list[UserGroupsT]) -> dict[str, Self]:
        """Create objects from list."""
        users = [cls.decode(item) for item in data]
        return {user.id: user for user in users}


@dataclass
class GetUsersRequest(ApiRequest):
    """Request object for listing users."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        return {"action": "get"}


@dataclass
class GetUsersResponse(ApiResponse[dict[str, User]]):
    """Response object for listing ports."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        if "=" not in (string_data := bytes_data.decode()):
            return cls(data={})

        data: dict[str, str] = dict(
            group.split("=", 1) for group in string_data.splitlines()
        )

        user_list = ["root"] + REGEX_STRING.findall(data["users"])

        users: list[UserGroupsT] = [
            {
                "user": user,
                "admin": user in REGEX_STRING.findall(data["admin"]),
                "operator": user in REGEX_STRING.findall(data["operator"]),
                "viewer": user in REGEX_STRING.findall(data["viewer"]),
                "ptz": user in REGEX_STRING.findall(data["ptz"]),
            }
            for user in user_list
        ]

        return cls(data=User.from_list(users))


@dataclass
class CreateUserRequest(ApiRequest):
    """Request object for creating a user."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"

    user: str
    pwd: str
    sgrp: SecondaryGroup
    comment: str | None = None

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        data = {
            "action": "add",
            "user": self.user,
            "pwd": self.pwd,
            "grp": "users",
            "sgrp": self.sgrp.value,
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

    user: str
    pwd: str | None = None
    sgrp: SecondaryGroup | None = None
    comment: str | None = None

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        data = {"action": "update", "user": self.user}

        if self.pwd is not None:
            data["pwd"] = self.pwd

        if self.sgrp:
            data["sgrp"] = self.sgrp.value

        if self.comment:
            data["comment"] = self.comment

        return data


@dataclass
class DeleteUserRequest(ApiRequest):
    """Request object for deleting a user."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"

    user: str

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        return {"action": "remove", "user": self.user}
