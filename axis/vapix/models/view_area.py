"""View area API data model."""

from dataclasses import dataclass

import orjson
from typing_extensions import NotRequired, Self, TypedDict

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

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
    """View area representation."""

    id: int
    source: int
    camera: int
    configurable: bool
    rectangularGeometry: NotRequired[GeometryT]
    canvasSize: NotRequired[SizeT]
    minSize: NotRequired[SizeT]
    maxSize: NotRequired[SizeT]
    grid: NotRequired[GeometryT]


class ListViewAreasDataT(TypedDict):
    """List of view areas data."""

    viewAreas: list[ViewAreaT]


class ListViewAreasResponseT(TypedDict):
    """List view areas response."""

    apiVersion: str
    context: str
    method: str
    data: ListViewAreasDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """Get supported versions response."""

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

    horizontal_offset: int
    horizontal_size: int
    vertical_offset: int
    vertical_size: int

    @classmethod
    def from_dict(cls, data: GeometryT) -> "Geometry":
        """Create geometry object from dict."""
        return Geometry(
            horizontal_offset=data["horizontalOffset"],
            horizontal_size=data["horizontalSize"],
            vertical_offset=data["verticalOffset"],
            vertical_size=data["verticalSize"],
        )


@dataclass
class Size:
    """Represent a size object."""

    horizontal: int
    vertical: int

    @classmethod
    def from_dict(cls, item: SizeT) -> "Size":
        """Create size object from dict."""
        return Size(horizontal=item["horizontal"], vertical=item["vertical"])


@dataclass
class ViewArea(ApiItem):
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

    @classmethod
    def decode(cls, raw: ViewAreaT) -> Self:
        """Decode dict to class object."""

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

        return cls(
            id=str(raw["id"]),
            camera=raw["camera"],
            source=raw["source"],
            configurable=raw["configurable"],
            canvas_size=create_size(raw.get("canvasSize")),
            rectangular_geometry=create_geometry(raw.get("rectangularGeometry")),
            min_size=create_size(raw.get("minSize")),
            max_size=create_size(raw.get("maxSize")),
            grid=create_geometry(raw.get("grid")),
        )

    @classmethod
    def decode_from_list(cls, raw: list[ViewAreaT]) -> dict[str, Self]:
        """Decode list[dict] to list of class objects."""
        return {str(item.id): item for item in [cls.decode(item) for item in raw]}


ListViewAreasT = dict[str, ViewArea]


@dataclass
class ListViewAreasResponse(ApiResponse[ListViewAreasT]):
    """Response object for list view areas response."""

    api_version: str
    context: str
    method: str
    data: ListViewAreasT
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: ListViewAreasResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=ViewArea.decode_from_list(data.get("data", {}).get("viewAreas", [])),
        )


@dataclass
class ListViewAreasRequest(ApiRequest):
    """Request object for listing view areas."""

    method = "post"
    path = "/axis-cgi/viewarea/info.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "list",
            }
        )


@dataclass
class SetGeometryRequest(ListViewAreasRequest):
    """Request object for setting geometry of a view area."""

    path = "/axis-cgi/viewarea/configure.cgi"
    error_codes = general_error_codes

    id: int | None = None
    geometry: Geometry | None = None

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        assert self.id is not None and self.geometry is not None
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setGeometry",
                "params": {
                    "viewArea": {
                        "id": self.id,
                        "rectangularGeometry": {
                            "horizontalOffset": self.geometry.horizontal_offset,
                            "horizontalSize": self.geometry.horizontal_size,
                            "verticalOffset": self.geometry.vertical_offset,
                            "verticalSize": self.geometry.vertical_size,
                        },
                    }
                },
            }
        )


@dataclass
class ResetGeometryRequest(ListViewAreasRequest):
    """Request object for resetting geometry of a view area."""

    path = "/axis-cgi/viewarea/configure.cgi"
    error_codes = general_error_codes

    id: int | None = None

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        assert self.id is not None
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "resetGeometry",
                "params": {"viewArea": {"id": self.id}},
            }
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/viewarea/info.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "context": self.context,
                "method": "getSupportedVersions",
            }
        )


@dataclass
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """Response object for supported versions."""

    api_version: str
    context: str
    method: str
    data: list[str]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )


@dataclass
class GetSupportedConfigVersionsRequest(GetSupportedVersionsRequest):
    """Request object for listing supported API versions."""

    path = "/axis-cgi/viewarea/configure.cgi"
