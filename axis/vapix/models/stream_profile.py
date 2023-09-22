"""Stream profiles API.

 A stream profile contains a collection of parameters such as
video codecs, resolutions, frame rates and compressions,
and should be used to retrieve a video stream from your Axis product.
"""

from dataclasses import dataclass, field

import orjson
from typing_extensions import NotRequired, TypedDict

from .api import CONTEXT, ApiItem, ApiRequest

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

    name: str
    description: str
    parameters: str


ListStreamProfilesT = dict[str, StreamProfile]


@dataclass
class ListStreamProfilesRequest(ApiRequest[ListStreamProfilesT]):
    """Request object for listing stream profiles descriptions."""

    method = "post"
    path = "/axis-cgi/streamprofile.cgi"
    content_type = "application/json"
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    profiles: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize request data."""
        profile_list = [{"name": profile} for profile in self.profiles]
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "list",
            "params": {"streamProfileName": profile_list},
        }

    def process_raw(self, raw: bytes) -> ListStreamProfilesT:
        """Prepare API description dictionary."""
        data: ListStreamProfilesResponseT = orjson.loads(raw)
        stream_profiles = data.get("data", {}).get("streamProfile", [])
        return {
            stream_profile["name"]: StreamProfile(
                id=stream_profile["name"],
                name=stream_profile["name"],
                description=stream_profile["description"],
                parameters=stream_profile["parameters"],
            )
            for stream_profile in stream_profiles
        }


@dataclass
class GetSupportedVersionsRequest(ApiRequest[list[str]]):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/streamprofile.cgi"
    content_type = "application/json"
    error_codes = error_codes

    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "context": self.context,
            "method": "getSupportedVersions",
        }

    def process_raw(self, raw: bytes) -> list[str]:
        """Process supported versions."""
        data: GetSupportedVersionsResponseT = orjson.loads(raw)
        return data.get("data", {}).get("apiVersions", [])
