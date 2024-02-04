"""Image parameters from param.cgi."""

from dataclasses import dataclass
from typing import Self

from typing_extensions import TypedDict

from .param_cgi import ParamItem


class ImageAppearanceParamT(TypedDict):
    """Represent an appearance object."""

    ColorEnabled: str
    Compression: str
    MirrorEnabled: str
    Resolution: str
    Rotation: str


class ImageMpegH264ParamT(TypedDict):
    """Represent an MPEG H264 object."""

    Profile: str
    PSEnabled: str


class ImageMpegParamT(TypedDict):
    """Represent an MPEG object."""

    Complexity: str
    ConfigHeaderInterval: str
    FrameSkipMode: str
    ICount: str
    PCount: str
    UserDataEnabled: str
    UserDataInterval: str
    ZChromaQPMode: str
    ZFpsMode: str
    ZGopMode: str
    ZMaxGopLength: str
    ZMinFps: str
    ZStrength: str
    H264: ImageMpegH264ParamT


class ImageOverlayMaskWindowsParamT(TypedDict):
    """Represent an mask windows object."""

    Color: str


class ImageOverlayParamT(TypedDict):
    """Represent an overlay object."""

    Enabled: str
    XPos: str
    YPos: str
    MaskWindows: ImageOverlayMaskWindowsParamT


class ImageRateControlParamT(TypedDict):
    """Represent an rate control object."""

    MaxBitrate: str
    Mode: str
    Priority: str
    TargetBitrate: str


class ImageSizeControlParamT(TypedDict):
    """Represent an size control object."""

    MaxFrameSize: str


class ImageStreamParamT(TypedDict):
    """Represent a stream object."""

    Duration: str
    FPS: str
    NbrOfFrames: str


class ImageTextParamT(TypedDict):
    """Represent a text object."""

    BGColor: str
    ClockEnabled: str
    Color: str
    DateEnabled: str
    Position: str
    String: str
    TextEnabled: str
    TextSize: str


class ImageParamT(TypedDict):
    """Represent an image object."""

    Enabled: str
    Name: str
    Source: str
    Appearance: ImageAppearanceParamT
    MPEG: ImageMpegParamT
    Overlay: ImageOverlayParamT
    RateControl: ImageRateControlParamT
    SizeControl: ImageSizeControlParamT
    Stream: ImageStreamParamT
    Text: ImageTextParamT


@dataclass(frozen=True)
class ImageParam(ParamItem):
    """Image parameters."""

    data: dict[str, ImageParamT]

    @classmethod
    def decode(cls, data: dict[str, ImageParamT]) -> Self:
        """Decode dictionary to class object."""
        return cls(id="image", data=data)
