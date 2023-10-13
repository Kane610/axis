"""User group API.

Figure out what access rights an account has.
"""

from .api import APIItem
from .api_handler import ApiHandler

URL = "/axis-cgi/usergroup.cgi"

ADMIN = "admin"
OPERATOR = "operator"
VIEWER = "viewer"
PTZ = "ptz"

UNKNOWN = "unknown"


class UserGroups(ApiHandler):
    """User group access rights for Axis devices."""

    item_cls = APIItem
    path = URL

    async def _api_request(self) -> dict[str, APIItem]:
        """Get API data method defined by subsclass."""
        raw = await self.vapix.do_request("get", "/axis-cgi/usergroup.cgi")
        raw_list: list[str] = raw.decode().splitlines()

        group_list = []
        if len(raw_list) == 2:
            group_list = raw_list[1].split()

        return {
            group: APIItem(group, group in group_list, self.vapix.request)
            for group in [ADMIN, OPERATOR, VIEWER, PTZ]
        }
        # return {group: group in group_list for group in [ADMIN, OPERATOR, VIEWER, PTZ]}

    @property
    def privileges(self) -> str:
        """Return highest privileged role supported."""
        if self.admin:
            return ADMIN
        if self.operator:
            return OPERATOR
        if self.viewer:
            return VIEWER
        return UNKNOWN

    @property
    def admin(self) -> bool:
        """Is user admin."""
        return self[ADMIN].raw  # type: ignore[return-value]

    @property
    def operator(self) -> bool:
        """Is user operator."""
        return self[OPERATOR].raw  # type: ignore[return-value]

    @property
    def viewer(self) -> bool:
        """Is user viewer."""
        return self[VIEWER].raw  # type: ignore[return-value]

    @property
    def ptz(self) -> bool:
        """Is user ptz."""
        return self[PTZ].raw  # type: ignore[return-value]
