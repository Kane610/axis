"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

action: Add, remove, update or list parameters.
usergroup: Get a certain user access level.
"""
from .api import APIItems

PROPERTY = 'Properties.API.HTTP.Version=3'

URL = '/axis-cgi/param.cgi'
URL_GET = URL + '?action=list'

ADMIN = 'admin'
OPERATOR = 'operator'
VIEWER = 'viewer'
ANONYMOUS = 'anonymous'


class Params(APIItems):
    """Represents all parameters of param.cgi."""

    def __init__(self, raw: str, request: str):
        super().__init__(raw, request, URL_GET, Param)


class Param:
    """Represents a parameter group."""

    def __init__(self, id: str, raw: dict, request: str):
        self.id = id
        self.raw = raw
        self._request = request
