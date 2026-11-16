"""Models for VAPIX view areas, cropped views within a camera's video image."""

from dataclasses import dataclass
from typing import NotRequired, Self, TypedDict

import orjson

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error code and message returned by the View Area API."""

    code: int
    message: str


class GeometryT(TypedDict):
    """Rectangular view-area position and size in API image coordinates."""

    horizontalOffset: int
    horizontalSize: int
    verticalOffset: int
    verticalSize: int


class SizeT(TypedDict):
    """Horizontal and vertical image dimensions reported by the API."""

    horizontal: int
    vertical: int


class ViewAreaT(TypedDict):
    """One view area's source, camera, editability, and optional geometry limits."""

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
    """View areas returned by the list method."""

    viewAreas: list[ViewAreaT]


class ListViewAreasResponseT(TypedDict):
    """JSON envelope returned by the list method."""

    apiVersion: str
    context: str
    method: str
    data: ListViewAreasDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """View Area API versions supported by the device."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """JSON envelope returned by getSupportedVersions."""

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
    """Rectangular view-area offset and dimensions."""

    horizontal_offset: int
    horizontal_size: int
    vertical_offset: int
    vertical_size: int

    @classmethod
    def from_dict(cls, data: GeometryT) -> Geometry:
        """Convert API geometry fields to normalized attribute names."""
        return Geometry(
            horizontal_offset=data["horizontalOffset"],
            horizontal_size=data["horizontalSize"],
            vertical_offset=data["verticalOffset"],
            vertical_size=data["verticalSize"],
        )


@dataclass
class Size:
    """Horizontal and vertical dimensions of a view area."""

    horizontal: int
    vertical: int

    @classmethod
    def from_dict(cls, item: SizeT) -> Size:
        """Convert API size fields into a Size model."""
        return Size(horizontal=item["horizontal"], vertical=item["vertical"])


@dataclass(frozen=True)
class ViewArea(ApiItem):
    """A cropped camera view and the geometry the device allows it to use."""

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
    def decode(cls, data: ViewAreaT) -> Self:
        """Convert one API view-area entry into a model."""

        def create_geometry(item: GeometryT | None) -> Geometry | None:
            """Convert optional rectangle data, preserving an absent geometry."""
            if item is None:
                return None
            return Geometry.from_dict(item)

        def create_size(item: SizeT | None) -> Size | None:
            """Convert optional dimensions, preserving an absent size."""
            if item is None:
                return None
            return Size.from_dict(item)

        return cls(
            id=str(data["id"]),
            camera=data["camera"],
            source=data["source"],
            configurable=data["configurable"],
            canvas_size=create_size(data.get("canvasSize")),
            rectangular_geometry=create_geometry(data.get("rectangularGeometry")),
            min_size=create_size(data.get("minSize")),
            max_size=create_size(data.get("maxSize")),
            grid=create_geometry(data.get("grid")),
        )


@dataclass
class ListViewAreasResponse(ApiResponse[dict[str, ViewArea]]):
    """Available view areas indexed by their IDs."""

    api_version: str
    context: str
    method: str
    data: dict[str, ViewArea]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the response and index decoded view areas by ID."""
        data: ListViewAreasResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=ViewArea.decode_to_dict(data.get("data", {}).get("viewAreas", [])),
        )


@dataclass
class ListViewAreasRequest(ApiRequest[ListViewAreasResponse]):
    """Request the view areas available on the device."""

    method = "post"
    path = "/axis-cgi/viewarea/info.cgi"
    content_type = "application/json"
    response_type = ListViewAreasResponse
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a list request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "list",
            }
        )


@dataclass
class SetGeometryRequest(ApiRequest[ListViewAreasResponse]):
    """Set the rectangular crop geometry for one view area."""

    method = "post"
    path = "/axis-cgi/viewarea/configure.cgi"
    content_type = "application/json"
    response_type = ListViewAreasResponse
    error_codes = general_error_codes

    id: int
    geometry: Geometry

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the target view-area ID and rectangle as a setGeometry request."""
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
class ResetGeometryRequest(ApiRequest[ListViewAreasResponse]):
    """Restore a view area to its default geometry."""

    method = "post"
    path = "/axis-cgi/viewarea/configure.cgi"
    content_type = "application/json"
    response_type = ListViewAreasResponse
    error_codes = general_error_codes

    id: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the target view-area ID as a resetGeometry request."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "resetGeometry",
                "params": {"viewArea": {"id": self.id}},
            }
        )


@dataclass
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """View Area API versions supported by the device."""

    api_version: str
    context: str
    method: str
    data: list[str]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the supported-version list from the response envelope."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest[GetSupportedVersionsResponse]):
    """Request the View Area info API versions supported by the device."""

    method = "post"
    path = "/axis-cgi/viewarea/info.cgi"
    content_type = "application/json"
    response_type = GetSupportedVersionsResponse
    error_codes = general_error_codes

    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getSupportedVersions request as JSON."""
        return orjson.dumps(
            {
                "context": self.context,
                "method": "getSupportedVersions",
            }
        )


@dataclass
class GetSupportedConfigVersionsRequest(GetSupportedVersionsRequest):
    """Request the View Area configuration API versions supported by the device."""

    path = "/axis-cgi/viewarea/configure.cgi"
