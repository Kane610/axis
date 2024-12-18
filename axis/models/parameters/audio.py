"""Audio parameters from param.cgi."""

from dataclasses import dataclass
from typing import Self

from typing_extensions import TypedDict

from .param_cgi import ParamItem


class AudioT(TypedDict):
    """Represent an audio object."""

    DuplexMode: str
    MaxListeners: str
    ReceiverBuffer: str
    ReceiverTimeout: str
    NbrOfConfigs: str
    DSCP: str


@dataclass(frozen=True)
class AudioParam(ParamItem):
    """Audio parameters."""

    duplex_mode: str
    max_listeners: str
    receiver_buffer: str
    receiver_timeout: str
    num_configs: str
    dscp: str

    @classmethod
    def decode(cls, data: AudioT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            id="audio",
            duplex_mode=data["DuplexMode"],
            max_listeners=data["MaxListeners"],
            receiver_buffer=data["ReceiverBuffer"],
            receiver_timeout=data["ReceiverTimeout"],
            num_configs=data["NbrOfConfigs"],
            dscp=data["DSCP"],
        )
