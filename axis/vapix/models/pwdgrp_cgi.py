"""Axis Vapix user management user class."""

from .api import APIItem

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
