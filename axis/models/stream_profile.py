"""Models for VAPIX stream profiles, reusable video-stream settings.

A profile groups settings such as codecs, resolution, frame rate, and compression
for use when requesting a video stream.
"""

from dataclasses import dataclass, field
from typing import NotRequired, Self, TypedDict

import orjson

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error code and message returned by the stream-profile API."""

    code: int
    message: str


class StreamProfileT(TypedDict):
    """Name, description, and encoded settings for one stream profile."""

    name: str
    description: str
    parameters: str


class ListStreamProfilesDataT(TypedDict):
    """Profile limit and profile entries returned by the list method."""

    maxProfiles: int
    streamProfile: list[StreamProfileT]


class ListStreamProfilesResponseT(TypedDict):
    """JSON envelope returned by the stream-profile list method."""

    apiVersion: str
    context: str
    method: str
    data: ListStreamProfilesDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """Stream-profile API versions supported by the device."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """JSON envelope returned by getSupportedVersions."""

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


@dataclass(frozen=True)
class StreamProfile(ApiItem):
    """Reusable video-stream settings, including their name and description."""

    description: str
    parameters: str

    @property
    def name(self) -> str:
        """Stream profile name."""
        return self.id

    @classmethod
    def decode(cls, data: StreamProfileT) -> Self:
        """Convert one stream-profile entry into a model."""
        return cls(
            id=data["name"],
            description=data["description"],
            parameters=data["parameters"],
        )


@dataclass
class ListStreamProfilesResponse(ApiResponse[dict[str, StreamProfile]]):
    """Stream profiles returned by the list method, indexed by profile name."""

    api_version: str
    context: str
    method: str
    data: dict[str, StreamProfile]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the profile list and index its entries by name."""
        data: ListStreamProfilesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=StreamProfile.decode_to_dict(data["data"].get("streamProfile", [])),
        )


@dataclass
class ListStreamProfilesRequest(ApiRequest[ListStreamProfilesResponse]):
    """Request descriptions and settings for the selected stream profiles."""

    method = "post"
    path = "/axis-cgi/streamprofile.cgi"
    content_type = "application/json"
    response_type = ListStreamProfilesResponse
    error_codes = error_codes

    profiles: list[str] = field(default_factory=list)

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the selected profile names in a list request."""
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
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """Stream-profile API versions supported by the device."""

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
    """Request the stream-profile API versions supported by the device."""

    method = "post"
    path = "/axis-cgi/streamprofile.cgi"
    content_type = "application/json"
    response_type = GetSupportedVersionsResponse
    error_codes = error_codes

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
