"""View area API data model."""

from dataclasses import dataclass

import orjson
from typing_extensions import NotRequired, TypedDict

from .api import CONTEXT, APIItem, ApiItem, ApiRequest

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class GeometryT(TypedDict):
    """Represent a geometry object."""

    horizontalOffset: int
    horizontalSize: int
    verticalOffset: int
    verticalSize: int


class SizeT(TypedDict):
    """Represent a size object."""

    horizontal: int
    vertical: int


class ViewAreaT(TypedDict):
    """Pir sensor configuration representation."""

    id: int
    source: int
    camera: int
    rectangularGeometry: NotRequired[GeometryT]
    canvasSize: NotRequired[SizeT]
    minSize: NotRequired[SizeT]
    maxSize: NotRequired[SizeT]
    grid: NotRequired[GeometryT]


class ListViewAreasDataT(TypedDict):
    """List of view areas data."""

    viewAreas: list[ViewAreaT]


class ListViewAreasResponseT(TypedDict):
    """ListSensors response."""

    apiVersion: str
    context: str
    method: str
    data: ListViewAreasDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """ListSensors response."""

    apiVersion: str
    context: str
    method: str
    data: ApiVersionsT
    error: NotRequired[ErrorDataT]


general_error_codes = {
    1100: "Internal error",
    2100: "API version not supported",
    2101: "Invalid JSON",
    2102: "Method not supported",
    2103: "Required parameter missing",
    2104: "Invalid parameter value specified",
}


@dataclass
class Geometry:
    """Represent a geometry object."""

    horizontalOffset: int
    horizontalSize: int
    verticalOffset: int
    verticalSize: int

    @classmethod
    def from_dict(cls, data: GeometryT) -> "Geometry":
        """Create event instance from dict."""
        return Geometry(
            horizontalOffset=data["horizontalOffset"],
            horizontalSize=data["horizontalSize"],
            verticalOffset=data["verticalOffset"],
            verticalSize=data["verticalSize"],
        )


@dataclass
class Size:
    """Represent a size object."""

    horizontal: int
    vertical: int

    @classmethod
    def from_dict(cls, item: SizeT) -> "Size":
        """Create size object."""
        return Size(horizontal=item["horizontal"], vertical=item["vertical"])


@dataclass
class ViewArea2(ApiItem):
    """View area object."""

    camera: int
    source: int
    configurable: bool

    # These are only listed if the geometry of the view area can be configured.

    canvas_size: Size | None = None
    rectangular_geometry: Geometry | None = None
    min_size: Size | None = None
    max_size: Size | None = None
    grid: Geometry | None = None


ListViewAreasT = dict[str, ViewArea2]


@dataclass
class ListViewAreasRequest(ApiRequest[ListViewAreasT]):
    """Request object for listing view areas."""

    method = "post"
    path = "/axis-cgi/viewarea/info.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "list",
        }

    def process_raw(self, raw: str) -> ListViewAreasT:
        """Prepare view area dictionary."""
        data: ListViewAreasResponseT = orjson.loads(raw)
        items = data.get("data", {}).get("viewAreas", [])

        def create_geometry(item: GeometryT | None) -> Geometry | None:
            """Create geometry object."""
            if item is None:
                return None
            return Geometry.from_dict(item)

        def create_size(item: SizeT | None) -> Size | None:
            """Create size object."""
            if item is None:
                return None
            return Size.from_dict(item)

        return {
            str(item["id"]): ViewArea2(
                id=str(item["id"]),
                camera=item["camera"],
                source=item["source"],
                configurable=item["configurable"],
                canvas_size=create_size(item.get("canvasSize")),
                rectangular_geometry=create_geometry(item.get("rectangularGeometry")),
                min_size=create_size(item.get("minSize")),
                max_size=create_size(item.get("maxSize")),
                grid=create_geometry(item.get("grid")),
            )
            for item in items
        }


@dataclass
class SetGeometryRequest(ListViewAreasRequest):
    """Request object for setting geometry of a view area."""

    path = "/axis-cgi/viewarea/configure.cgi"
    error_codes = general_error_codes

    id: int | None = None
    geometry: Geometry | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.id is not None and self.geometry is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "setGeometry",
            "params": {
                "viewArea": {
                    "id": self.id,
                    "rectangularGeometry": {
                        "horizontalOffset": self.geometry.horizontalOffset,
                        "horizontalSize": self.geometry.horizontalSize,
                        "verticalOffset": self.geometry.verticalOffset,
                        "verticalSize": self.geometry.verticalSize,
                    },
                }
            },
        }


@dataclass
class ResetGeometryRequest(ListViewAreasRequest):
    """Request object for resetting geometry of a view area."""

    path = "/axis-cgi/viewarea/configure.cgi"
    error_codes = general_error_codes

    id: int | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "resetGeometry",
            "params": {"viewArea": {"id": self.id}},
        }


@dataclass
class GetSupportedVersionsRequest(ApiRequest[list[str]]):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/viewarea/info.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "context": self.context,
            "method": "getSupportedVersions",
        }

    def process_raw(self, raw: str) -> list[str]:
        """Process supported versions."""
        data: GetSupportedVersionsResponseT = orjson.loads(raw)
        return data.get("data", {}).get("apiVersions", [])


@dataclass
class GetSupportedConfigVersionsRequest(GetSupportedVersionsRequest):
    """Request object for listing supported API versions."""

    path = "/axis-cgi/viewarea/configure.cgi"


##########


class ViewArea(APIItem):
    """View area object."""

    @property
    def source(self) -> int:
        """Image source that created view area."""
        return self.raw["source"]

    @property
    def camera(self) -> int:
        """View area used by streaming, PTZ and other APIs."""
        return self.raw["camera"]

    @property
    def configurable(self) -> bool:
        """Define if a view can be configured.

        Some view areas can not be configured and are thus unable to be changed
        with regards to geometry, etc.
        """
        return self.raw["configurable"]

    # These are only listed if the geometry of the view area can be configured.

    @property
    def canvas_size(self) -> Size:
        """Define size of the overview image that the view area geometry is defined on."""
        return Size(**self.raw["canvasSize"])

    @property
    def rectangular_geometry(self) -> Geometry:
        """Define a geometry for the view area as a rectangle related to the canvas."""
        return Geometry(**self.raw["rectangularGeometry"])

    @property
    def min_size(self) -> Size:
        """Define the minimum size that a view area can have."""
        return Size(**self.raw["minSize"])

    @property
    def max_size(self) -> Size:
        """Define the maximum size that a view area can have."""
        return Size(**self.raw["maxSize"])

    @property
    def grid(self) -> Geometry:
        """Define the grid that a geometry is applied to on the canvas due to device limitations."""
        return Geometry(**self.raw["grid"])
