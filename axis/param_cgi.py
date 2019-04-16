"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

action: Add, remove, update or list parameters.
usergroup: Get a certain user access level.
"""
from .api import APIItems

PROPERTY = 'Properties.API.HTTP.Version=3'

URL = '/axis-cgi/param.cgi'
URL_GET = URL + '?action=list'
URL_GET_GROUP = URL_GET + '&group={group}'

BRAND = 'root.Brand'
PROPERTIES = 'root.Properties'


class Brand:
    """Parameters describing device brand."""

    def update_brand(self):
        """Update brand group of parameters."""
        self.update(path=URL_GET_GROUP.format(group=BRAND))

    @property
    def brand(self):
        return self[BRAND + '.Brand'].raw

    @property
    def prodfullname(self):
        return self[BRAND + '.ProdFullName'].raw

    @property
    def prodnbr(self):
        return self[BRAND + '.ProdNbr'].raw

    @property
    def prodshortname(self):
        return self[BRAND + '.ProdShortName'].raw

    @property
    def prodtype(self):
        return self[BRAND + '.ProdType'].raw

    @property
    def prodvariant(self):
        return self[BRAND + '.ProdVariant'].raw

    @property
    def weburl(self):
        return self[BRAND + '.WebURL'].raw


class Properties:
    """Parameters describing device properties."""

    def update_properties(self):
        """Update properties group of parameters."""
        self.update(path=URL_GET_GROUP.format(group=PROPERTIES))

    @property
    def api_http_version(self):
        return self[PROPERTIES + '.API.HTTP.Version'].raw

    @property
    def api_metadata(self):
        return self[PROPERTIES + '.API.Metadata.Metadata'].raw

    @property
    def api_metadata_version(self):
        return self[PROPERTIES + '.API.Metadata.Version'].raw

    @property
    def firmware_builddate(self):
        return self[PROPERTIES + '.Firmware.BuildDate'].raw

    @property
    def firmware_buildnumber(self):
        return self[PROPERTIES + '.Firmware.BuildNumber'].raw

    @property
    def firmware_version(self):
        return self[PROPERTIES + '.Firmware.Version'].raw

    @property
    def image_format(self):
        return self[PROPERTIES + '.Image.Format'].raw

    @property
    def image_nbrofviews(self):
        return self[PROPERTIES + '.Image.NbrOfViews'].raw

    @property
    def image_resolution(self):
        return self[PROPERTIES + '.Image.Resolution'].raw

    @property
    def image_rotation(self):
        return self[PROPERTIES + '.Image.Rotation'].raw

    @property
    def system_serialnumber(self):
        return self[PROPERTIES + '.System.SerialNumber'].raw


class Params(APIItems, Brand, Properties):
    """Represents all parameters of param.cgi."""

    def __init__(self, raw: str, request: str):
        super().__init__(raw, request, URL_GET, Param)

    def process_raw(self, raw: str):
        """Pre-process raw string.

        Prepare parameters to work with APIItems.
        """
        raw_params = dict(group.split('=', 1) for group in raw.splitlines())
        super().process_raw(raw_params)


class Param:
    """Represents a parameter group."""

    def __init__(self, id: str, raw: dict, request: str):
        self.id = id
        self.raw = raw
        self._request = request
