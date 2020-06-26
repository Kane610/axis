"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Ports, Properties, Stream profiles.
"""

from .api import APIItem, APIItems
from .stream_profiles import StreamProfile

PROPERTY = "Properties.API.HTTP.Version=3"

URL = "/axis-cgi/param.cgi"
URL_GET = URL + "?action=list"
GROUP = "&group={group}"

BRAND = "root.Brand"
INPUT = "root.Input"
IOPORT = "root.IOPort"
OUTPUT = "root.Output"
PROPERTIES = "root.Properties"
STREAM_PROFILES = "root.StreamProfile"


class Params(APIItems):
    """Represents all parameters of param.cgi."""

    def __init__(self, request: object) -> None:
        super().__init__("", request, URL_GET, APIItem)

    def process_raw(self, raw: str) -> None:
        """Pre-process raw string.

        Prepare parameters to work with APIItems.
        """
        raw_params = dict(group.split("=", 1) for group in raw.splitlines())

        super().process_raw(raw_params)

    # Brand

    def update_brand(self) -> None:
        """Update brand group of parameters."""
        self.update(path=URL_GET + GROUP.format(group=BRAND))

    @property
    def brand(self) -> str:
        return self[f"{BRAND}.Brand"].raw

    @property
    def prodfullname(self) -> str:
        return self[f"{BRAND}.ProdFullName"].raw

    @property
    def prodnbr(self) -> str:
        return self[f"{BRAND}.ProdNbr"].raw

    @property
    def prodshortname(self) -> str:
        return self[f"{BRAND}.ProdShortName"].raw

    @property
    def prodtype(self) -> str:
        return self[f"{BRAND}.ProdType"].raw

    @property
    def prodvariant(self) -> str:
        return self[f"{BRAND}.ProdVariant"].raw

    @property
    def weburl(self) -> str:
        return self[f"{BRAND}.WebURL"].raw

    # Ports

    def update_ports(self) -> None:
        """Update port groups of parameters."""
        self.update(path=URL_GET + GROUP.format(group=INPUT))
        self.update(path=URL_GET + GROUP.format(group=IOPORT))
        self.update(path=URL_GET + GROUP.format(group=OUTPUT))

    @property
    def nbrofinput(self) -> int:
        """Match the number of configured inputs."""
        return self[f"{INPUT}.NbrOfInputs"].raw

    @property
    def nbrofoutput(self) -> int:
        """Match the number of configured outputs."""
        return self[f"{OUTPUT}.NbrOfOutputs"].raw

    @property
    def ports(self) -> dict:
        """Create a smaller dictionary containing all ports."""
        return {param: self[param].raw for param in self if param.startswith(IOPORT)}

    # Properties

    def update_properties(self) -> None:
        """Update properties group of parameters."""
        self.update(path=URL_GET + GROUP.format(group=PROPERTIES))

    @property
    def api_http_version(self) -> str:
        return self[f"{PROPERTIES}.API.HTTP.Version"].raw

    @property
    def api_metadata(self) -> str:
        return self[f"{PROPERTIES}.API.Metadata.Metadata"].raw

    @property
    def api_metadata_version(self) -> str:
        return self[f"{PROPERTIES}.API.Metadata.Version"].raw

    @property
    def embedded_development(self) -> str:
        """VAPIX® Application API is supported.

        Application list.cgi supported if => 1.20.
        """
        return self[f"{PROPERTIES}.EmbeddedDevelopment.Version"].raw

    @property
    def firmware_builddate(self) -> str:
        return self[f"{PROPERTIES}.Firmware.BuildDate"].raw

    @property
    def firmware_buildnumber(self) -> str:
        return self[f"{PROPERTIES}.Firmware.BuildNumber"].raw

    @property
    def firmware_version(self) -> str:
        return self[f"{PROPERTIES}.Firmware.Version"].raw

    @property
    def image_format(self) -> str:
        if f"{PROPERTIES}.Image.Format" in self:
            return self[f"{PROPERTIES}.Image.Format"].raw
        return None

    @property
    def image_nbrofviews(self) -> str:
        return self[f"{PROPERTIES}.Image.NbrOfViews"].raw

    @property
    def image_resolution(self) -> str:
        return self[f"{PROPERTIES}.Image.Resolution"].raw

    @property
    def image_rotation(self) -> str:
        return self[f"{PROPERTIES}.Image.Rotation"].raw

    @property
    def light_control(self) -> bool:
        light_control = f"{PROPERTIES}.LightControl.LightControl2"
        if light_control not in self:
            return False
        return self[light_control].raw == "yes"

    @property
    def system_serialnumber(self) -> str:
        return self[f"{PROPERTIES}.System.SerialNumber"].raw

    # Stream profiles

    def update_stream_profiles(self) -> None:
        """Update properties group of parameters."""
        self.update(path=URL_GET + GROUP.format(group=STREAM_PROFILES))

    def stream_profiles(self) -> list:
        """Return a list of stream profiles."""
        profiles = []
        length = 0
        if f"{STREAM_PROFILES}.MaxGroups" in self:
            length = int(self[f"{STREAM_PROFILES}.MaxGroups"].raw)

        try:
            for nbr in range(length):
                raw = {
                    "name": self[f"{STREAM_PROFILES}.S{nbr}.Name"].raw,
                    "description": self[f"{STREAM_PROFILES}.S{nbr}.Description"].raw,
                    "parameters": self[f"{STREAM_PROFILES}.S{nbr}.Parameters"].raw,
                }
                profiles.append(StreamProfile(raw["name"], raw, self._request))
        except KeyError:
            pass

        return profiles
