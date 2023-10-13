"""Stream profiles API.

 A stream profile contains a collection of parameters such as
video codecs, resolutions, frame rates and compressions,
and should be used to retrieve a video stream from your Axis product.
"""

from dataclasses import dataclass, field

import orjson
from typing_extensions import NotRequired, Self, TypedDict

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class StreamProfileT(TypedDict):
    """Stream profile representation."""

    name: str
    description: str
    parameters: str


class ListStreamProfilesDataT(TypedDict):
    """List of stream profiles."""

    maxProfiles: int
    streamProfile: list[StreamProfileT]


class ListStreamProfilesResponseT(TypedDict):
    """List response."""

    apiVersion: str
    context: str
    method: str
    data: ListStreamProfilesDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """ListApis response."""

    apiVersion: str
    context: str
    method: str
    data: ApiVersionsT
    error: NotRequired[ErrorDataT]


error_codes = {
    1000: "Invalid parameter value specified",
    2000: "The major version number isn't supported",
    2001: "The request was not formatted correctly, i.e. does not follow JSON schema",
    2005: "The method in the request is not supported",
    2006: "The requested profile does not exist",
}


@dataclass
class StreamProfile(ApiItem):
    """Stream profile item."""

    description: str
    parameters: str

    @property
    def name(self) -> str:
        """Stream profile name."""
        return self.id

    @classmethod
    def decode(cls, raw: StreamProfileT) -> Self:
        """Decode dict to class object."""
        return cls(
            id=raw["name"],
            description=raw["description"],
            parameters=raw["parameters"],
        )

    @classmethod
    def decode_from_list(cls, raw: list[StreamProfileT]) -> dict[str, Self]:
        """Decode list[dict] to list of class objects."""
        return {item.id: item for item in [cls.decode(item) for item in raw]}


ListStreamProfilesT = dict[str, StreamProfile]


@dataclass
class ListStreamProfilesResponse(ApiResponse[ListStreamProfilesT]):
    """Response object for list sensors response."""

    api_version: str
    context: str
    method: str
    data: ListStreamProfilesT
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: ListStreamProfilesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=StreamProfile.decode_from_list(data["data"].get("streamProfile", [])),
        )


@dataclass
class ListStreamProfilesRequest(ApiRequest):
    """Request object for listing stream profiles descriptions."""

    method = "post"
    path = "/axis-cgi/streamprofile.cgi"
    content_type = "application/json"
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    profiles: list[str] = field(default_factory=list)

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        profile_list = [{"name": profile} for profile in self.profiles]
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "list",
                "params": {"streamProfileName": profile_list},
            }
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/streamprofile.cgi"
    content_type = "application/json"
    error_codes = error_codes

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
