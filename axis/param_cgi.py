"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

action: Add, remove, update or list parameters.
usergroup: Get a certain user access level.
"""

from .api import APIItems

PROPERTY = 'Properties.API.HTTP.Version=3'

URL = '/axis-cgi/param.cgi'
URL_GET = URL + '?action=list'
GROUP = '&group={group}'

BRAND = 'root.Brand'
INPUT = 'root.Input'
IOPORT = 'root.IOPort'
OUTPUT = 'root.Output'
PROPERTIES = 'root.Properties'


class Brand:
    """Parameters describing device brand."""

    def update_brand(self) -> None:
        """Update brand group of parameters."""
        self.update(path=URL_GET + GROUP.format(group=BRAND))

    @property
    def brand(self) -> str:
        return self[BRAND + '.Brand'].raw

    @property
    def prodfullname(self) -> str:
        return self[BRAND + '.ProdFullName'].raw

    @property
    def prodnbr(self) -> str:
        return self[BRAND + '.ProdNbr'].raw

    @property
    def prodshortname(self) -> str:
        return self[BRAND + '.ProdShortName'].raw

    @property
    def prodtype(self) -> str:
        return self[BRAND + '.ProdType'].raw

    @property
    def prodvariant(self) -> str:
        return self[BRAND + '.ProdVariant'].raw

    @property
    def weburl(self) -> str:
        return self[BRAND + '.WebURL'].raw


class Ports:
    """Parameters describing device inputs and outputs."""

    def update_ports(self) -> None:
        """Update port groups of parameters."""
        self.update(path=URL_GET + GROUP.format(group=INPUT))
        self.update(path=URL_GET + GROUP.format(group=IOPORT))
        self.update(path=URL_GET + GROUP.format(group=OUTPUT))

    @property
    def nbrofinput(self) -> int:
        """Match the number of configured inputs."""
        return self[INPUT + '.NbrOfInputs'].raw

    @property
    def nbrofoutput(self) -> int:
        """Match the number of configured outputs."""
        return self[OUTPUT + '.NbrOfOutputs'].raw

    @property
    def ports(self) -> dict:
        """Create a smaller dictionary containing all ports."""
        return {
            param: self[param].raw
            for param in self
            if param.startswith(IOPORT)
        }


class Properties:
    """Parameters describing device properties."""

    def update_properties(self) -> None:
        """Update properties group of parameters."""
        self.update(path=URL_GET + GROUP.format(group=PROPERTIES))

    @property
    def api_http_version(self) -> str:
        return self[PROPERTIES + '.API.HTTP.Version'].raw

    @property
    def api_metadata(self) -> str:
        return self[PROPERTIES + '.API.Metadata.Metadata'].raw

    @property
    def api_metadata_version(self) -> str:
        return self[PROPERTIES + '.API.Metadata.Version'].raw

    @property
    def firmware_builddate(self) -> str:
        return self[PROPERTIES + '.Firmware.BuildDate'].raw

    @property
    def firmware_buildnumber(self) -> str:
        return self[PROPERTIES + '.Firmware.BuildNumber'].raw

    @property
    def firmware_version(self) -> str:
        return self[PROPERTIES + '.Firmware.Version'].raw

    @property
    def image_format(self) -> str:
        if PROPERTIES + '.Image.Format' in self:
            return self[PROPERTIES + '.Image.Format'].raw
        return None

    @property
    def image_nbrofviews(self) -> str:
        return self[PROPERTIES + '.Image.NbrOfViews'].raw

    @property
    def image_resolution(self) -> str:
        return self[PROPERTIES + '.Image.Resolution'].raw

    @property
    def image_rotation(self) -> str:
        return self[PROPERTIES + '.Image.Rotation'].raw

    @property
    def system_serialnumber(self) -> str:
        return self[PROPERTIES + '.System.SerialNumber'].raw


class Params(APIItems, Brand, Ports, Properties):
    """Represents all parameters of param.cgi."""

    def __init__(self, raw: str, request: object) -> None:
        super().__init__(raw, request, URL_GET, Param)

    def process_raw(self, raw: str) -> None:
        """Pre-process raw string.

        Prepare parameters to work with APIItems.
        """
        raw_params = dict(group.split('=', 1) for group in raw.splitlines())

        super().process_raw(raw_params)


class Param:
    """Represents a parameter group."""

    def __init__(self, id: str, raw: dict, request: str) -> None:
        self.id = id
        self.raw = raw
        self._request = request
