"""Axis Vapix user management user class."""

from dataclasses import dataclass

from typing_extensions import NotRequired, Self, TypedDict

from .api import APIItem, ApiItem, ApiRequest

ADMIN = "admin"
OPERATOR = "operator"
VIEWER = "viewer"
PTZ = "ptz"


class User(APIItem):
    """Represents a user."""

    @property
    def name(self) -> str:
        """User name."""
        return self.id

    @property
    def admin(self) -> bool:
        """Is user part of admin group."""
        return self.raw[ADMIN]

    @property
    def operator(self) -> bool:
        """Is user part of operator group."""
        return self.raw[OPERATOR]

    @property
    def viewer(self) -> bool:
        """Is user part of viewer group."""
        return self.raw[VIEWER]

    @property
    def ptz(self) -> bool:
        """Is user part of PTZ group."""
        return self.raw[PTZ]


# class User2(ApiItem):
#     """Represents a user."""

#     @property
#     def name(self) -> str:
#         """User name."""
#         return self.id

#     @property
#     def admin(self) -> bool:
#         """Is user part of admin group."""
#         return self.raw[ADMIN]

#     @property
#     def operator(self) -> bool:
#         """Is user part of operator group."""
#         return self.raw[OPERATOR]

#     @property
#     def viewer(self) -> bool:
#         """Is user part of viewer group."""
#         return self.raw[VIEWER]

#     @property
#     def ptz(self) -> bool:
#         """Is user part of PTZ group."""
#         return self.raw[PTZ]

#     @classmethod
#     def from_dict(cls, data: PortItemT) -> Self:
#         """Create object from dict."""
#         return cls(
#             id=data["port"],
#             configurable=data["configurable"],
#             direction=data["direction"],
#             name=data["name"],
#             normalState=data["normalState"],
#             state=data["state"],
#             usage=data["usage"],
#         )

#     @classmethod
#     def from_list(cls, data: list[PortItemT]) -> dict[str, Self]:
#         """Create objects from list."""
#         ports = [cls.from_dict(item) for item in data]
#         return {port.id: port for port in ports}


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
