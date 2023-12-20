"""Stream profile parameters from param.cgi."""

from dataclasses import dataclass
from typing import Any

from typing_extensions import Self, TypedDict

from ..api import ApiItem
from ..stream_profile import StreamProfile


class StreamProfileT(TypedDict):
    """Represent a property object."""

    MaxGroups: int
    API_Metadata_Metadata: str


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
                id=str(profile["Name"]),
                description=str(profile["Description"]),
                parameters=str(profile["Parameters"]),
            )
            for profile in raw_profiles.values()
        ]

        return cls(
            id="stream profiles",
            max_groups=max_groups,
            stream_profiles=profiles,
        )
