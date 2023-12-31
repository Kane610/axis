"""Stream profile parameters from param.cgi."""

from dataclasses import dataclass
from typing import Any, cast

from typing_extensions import NotRequired, Self, TypedDict

from ..api import ApiItem
from ..stream_profile import StreamProfile


class ProfileParamT(TypedDict):
    """Profile descriptions."""

    Description: str
    Name: str
    Parameters: str


class StreamProfileParamT(TypedDict):
    """Represent a property object."""

    MaxGroups: int
    S0: NotRequired[ProfileParamT]
    S1: NotRequired[ProfileParamT]
    S2: NotRequired[ProfileParamT]
    S3: NotRequired[ProfileParamT]


@dataclass
class StreamProfileParam(ApiItem):
    """Stream profile parameters."""

    max_groups: int
    """Maximum number of supported stream profiles."""

    stream_profiles: list[StreamProfile]
    """List of stream profiles."""

    @classmethod
    def decode(cls, data: dict[str, Any]) -> Self:
        """Decode dictionary to class object."""
        max_groups = int(data.get("MaxGroups", 0))

        raw_profiles = dict(data)
        raw_profiles.pop("MaxGroups", None)

        profiles = [
            StreamProfile(
                id=profile["Name"],
                description=profile["Description"],
                parameters=profile["Parameters"],
            )
            for profile in cast(dict[str, ProfileParamT], raw_profiles).values()
        ]

        return cls(
            id="stream profiles",
            max_groups=max_groups,
            stream_profiles=profiles,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> dict[str, Self]:
        """Create response object from dict."""
        return {"0": cls.decode(data)}
