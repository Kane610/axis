"""Models for listing and changing local accounts through VAPIX pwdgrp.cgi."""

from dataclasses import dataclass
import enum
from typing import Self, TypedDict

from .api import ApiItem, ApiRequest, ApiResponse, BytesResponse


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
    """Username and access-group membership flags returned by pwdgrp.cgi."""

    user: str
    admin: bool
    operator: bool
    viewer: bool
    ptz: bool


@dataclass(frozen=True)
class User(ApiItem):
    """Local account name and its admin, operator, viewer, and PTZ rights."""

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
        """Return the account's highest role, including PTZ access when present."""
        if self.admin:
            return SecondaryGroup.ADMIN_PTZ if self.ptz else SecondaryGroup.ADMIN
        if self.operator:
            return SecondaryGroup.OPERATOR_PTZ if self.ptz else SecondaryGroup.OPERATOR
        if self.viewer:
            return SecondaryGroup.VIEWER_PTZ if self.ptz else SecondaryGroup.VIEWER
        return SecondaryGroup.UNKNOWN

    @classmethod
    def decode(cls, data: UserGroupsT) -> Self:
        """Convert one username and its group flags into a user model."""
        return cls(
            id=data["user"],
            admin=data["admin"],
            operator=data["operator"],
            viewer=data["viewer"],
            ptz=data["ptz"],
        )


@dataclass
class GetUsersResponse(ApiResponse[dict[str, User]]):
    """Local users indexed by username, with their access-group membership."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse pwdgrp.cgi group assignments into one model per username."""
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
class GetUsersRequest(ApiRequest[GetUsersResponse]):
    """Request the local account names grouped by access role."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"
    response_type = GetUsersResponse

    @property
    def data(self) -> dict[str, str]:
        """Return the pwdgrp.cgi action that lists account groups."""
        return {"action": "get"}


@dataclass
class CreateUserRequest(ApiRequest[ApiResponse[bytes]]):
    """Add a local account with the selected secondary group and optional comment."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"
    response_type = BytesResponse

    user: str
    pwd: str
    sgrp: SecondaryGroup
    comment: str | None = None

    @property
    def data(self) -> dict[str, str]:
        """Return pwdgrp.cgi fields for creating this account."""
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
class ModifyUserRequest(ApiRequest[ApiResponse[bytes]]):
    """Change a local account's password, access group, or comment."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"
    response_type = BytesResponse

    user: str
    pwd: str | None = None
    sgrp: SecondaryGroup | None = None
    comment: str | None = None

    @property
    def data(self) -> dict[str, str]:
        """Return only the account fields supplied for modification."""
        data = {"action": "update", "user": self.user}

        if self.pwd is not None:
            data["pwd"] = self.pwd

        if self.sgrp:
            data["sgrp"] = self.sgrp

        if self.comment:
            data["comment"] = self.comment

        return data


@dataclass
class DeleteUserRequest(ApiRequest[ApiResponse[bytes]]):
    """Remove a local account by username."""

    method = "post"
    path = "/axis-cgi/pwdgrp.cgi"
    content_type = "text/plain"
    response_type = BytesResponse

    user: str

    @property
    def data(self) -> dict[str, str]:
        """Return the pwdgrp.cgi action and username for account removal."""
        return {"action": "remove", "user": self.user}
