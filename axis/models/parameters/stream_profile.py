"""Stream profile parameters from param.cgi."""

from dataclasses import dataclass
from typing import Any, NotRequired, Self, TypedDict, cast

from ..stream_profile import StreamProfile
from .param_cgi import ParamItem


class ProfileParamT(TypedDict):
    """Name, description, and settings string for one stream profile."""

    Description: str
    Name: str
    Parameters: str


class StreamProfileParamT(TypedDict):
    """Maximum profile count and numbered profiles from the StreamProfile group."""

    MaxGroups: int
    S0: NotRequired[ProfileParamT]
    S1: NotRequired[ProfileParamT]
    S2: NotRequired[ProfileParamT]
    S3: NotRequired[ProfileParamT]


@dataclass(frozen=True)
class StreamProfileParam(ParamItem):
    """Stream profile capacity and configured profiles from param.cgi."""

    max_groups: int
    """Maximum number of supported stream profiles."""

    stream_profiles: list[StreamProfile]
    """Configured profiles with their descriptions and parameter strings."""

    @classmethod
    def decode(cls, data: dict[str, Any]) -> Self:
        """Convert the StreamProfile group into profile models and a capacity limit."""
        max_groups = int(data.get("MaxGroups", 0))

        raw_profiles = dict(data)
        raw_profiles.pop("MaxGroups", None)

        stream_profiles = [
            StreamProfile(
                id=profile["Name"],
                description=profile["Description"],
                parameters=profile["Parameters"],
            )
            for profile in cast("dict[str, ProfileParamT]", raw_profiles).values()
        ]

        return cls(
            id="stream profiles",
            max_groups=max_groups,
            stream_profiles=stream_profiles,
        )
