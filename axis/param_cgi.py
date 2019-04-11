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

BRAND = 'root.Brand'


class Params(APIItems):
    """Represents all parameters of param.cgi."""

    def __init__(self, raw: str, request: str):
        super().__init__(raw, request, URL_GET, select_parameter_group)

    def process_raw(self, raw: str):
        """Pre-process raw string.

        Prepare parameters to work with APIItems.
        """
        raw_dict = dict(group.split('=', 1) for group in raw.splitlines())

        raw_params = {
            parentgroup: {
                group.replace(parentgroup + '.', ''): raw_dict[group]
                for group in raw_dict
                if group.startswith(parentgroup)
            }
            for parentgroup in [BRAND]
        }
        super().process_raw(raw_params)


def select_parameter_group(id: str, raw: dict, request: str):
    if id == BRAND:
        return Brand(id, raw, request)


class Param:
    """Represents a parameter group."""

    def __init__(self, id: str, raw: dict, request: str):
        self.id = id
        self.raw = raw
        self._request = request


class Brand(Param):
    """Parameters describing brand."""
    PARENTGROUP = BRAND

    @property
    def brand(self):
        return self.raw['Brand']

    @property
    def prodfullname(self):
        return self.raw['ProdFullName']

    @property
    def prodnbr(self):
        return self.raw['ProdNbr']

    @property
    def prodshortname(self):
        return self.raw['ProdShortName']

    @property
    def prodtype(self):
        return self.raw['ProdType']

    @property
    def prodvariant(self):
        return self.raw['ProdVariant']

    @property
    def weburl(self):
        return self.raw['WebURL']