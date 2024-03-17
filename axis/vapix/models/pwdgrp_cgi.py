"""Axis Vapix user management user class."""

from dataclasses import dataclass
import enum
from typing import Self

from typing_extensions import TypedDict

from .api import ApiItem, ApiRequest, ApiResponse


class SecondaryGroup(enum.StrEnum):
    """Supported user secondary groups.

    Defines the user access rights for the account.
    """

    ADMIN = "viewer:operator:admin"
    ADMIN_PTZ = "viewer:operator:admin:ptz"
    OPERATOR = "viewer:operator"
    OPERATOR_PTZ = "viewer:operator:ptz"
    VIEWER = "viewer"
    VIEWER_PTZ = "viewer:ptz"

    UNKNOWN = "unknown"


class UserGroupsT(TypedDict):
    """Groups user belongs to."""

    user: str
    admin: bool
    operator: bool
    viewer: bool
    ptz: bool


@dataclass(frozen=True)
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

    @property
    def privileges(self) -> SecondaryGroup:
        """Return highest privileged role supported."""
        if self.admin:
            return SecondaryGroup.ADMIN_PTZ if self.ptz else SecondaryGroup.ADMIN
        if self.operator:
            return SecondaryGroup.OPERATOR_PTZ if self.ptz else SecondaryGroup.OPERATOR
        if self.viewer:
            return SecondaryGroup.VIEWER_PTZ if self.ptz else SecondaryGroup.VIEWER
        return SecondaryGroup.UNKNOWN

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
            group.split("=", 1) for group in string_data.replace('"', "").splitlines()
        )

        user_list = {
            user
            for group in ("admin", "operator", "viewer", "ptz")
            for user in data[group].split(",")
        }

        users: list[UserGroupsT] = [
            {
                "user": user,
                "admin": user in data["admin"].split(","),
                "operator": user in data["operator"].split(","),
                "viewer": user in data["viewer"].split(","),
                "ptz": user in data["ptz"].split(","),
            }
            for user in user_list
        ]

        return cls(data=User.decode_to_dict(users))


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

    user: str

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        return {"action": "remove", "user": self.user}
