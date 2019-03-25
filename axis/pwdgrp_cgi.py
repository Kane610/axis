"""Axis Vapix user management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036044
"""

from .api import APIItems

BASE_URL = '/axis-cgi/pwdgrp.cgi'
GET_URL = BASE_URL + '?action=get'
ADD_URL = BASE_URL + '?action=add&user={user}&pwd={pwd}&grp=users&sgrp{sgrp}'
COMMENT = '&comment={comment}'

SGRP_V = 'viewer'
SGRP_O = 'operator'
SGRP_A = 'admin'


class Users(APIItems):
    """Represents all users of a device."""

    def __init__(self, raw: str, request: str):
        super().__init__(raw, request, GET_URL, User)

    def add(self, user: str, pwd: str, sgrp: str, comment: str=None):
        """Create new user."""
        url = ADD_URL.format(user=user, pwd=pwd, sgrp=sgrp)
        if comment:
            url += COMMENT.format(comment=comment)
        self._request('get', url)


# http://myserver/axis-cgi/pwdgrp.cgi?action=add
# &user=joe&pwd=foo&grp=users&sgrp=viewer:operator:admin:ptz&comment=Joe



class User:
    """Represents a user."""

    def __init__(self, id: str, raw: str, request: str):
        self.id = id
        self.raw = raw
        self._request = request
