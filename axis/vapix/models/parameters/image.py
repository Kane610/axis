"""Image parameters from param.cgi."""

from dataclasses import dataclass
from typing import Any, NotRequired, Self, TypedDict

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


class ImageTriggerDataParamT(TypedDict):
    """Represent a trigger data object."""

    AudioEnabled: bool
    MotionDetectionEnabled: bool
    MotionLevelEnabled: bool
    TamperingEnabled: bool
    UserTriggers: str


class ImageParamT(TypedDict):
    """Represent an image object."""

    Enabled: str
    Name: str
    Source: str
    Appearance: ImageAppearanceParamT
    MPEG: NotRequired[ImageMpegParamT]
    Overlay: NotRequired[ImageOverlayParamT]
    RateControl: NotRequired[ImageRateControlParamT]
    SizeControl: NotRequired[ImageSizeControlParamT]
    Stream: ImageStreamParamT
    Text: NotRequired[ImageTextParamT]
    TriggerData: NotRequired[ImageTriggerDataParamT]


@dataclass(frozen=True)
class ImageParam(ParamItem):
    """Image parameters."""

    enabled: str
    name: str
    source: str | None
    appearance: ImageAppearanceParamT
    mpeg: ImageMpegParamT | None
    overlay: ImageOverlayParamT | None
    rate_control: ImageRateControlParamT | None
    size_control: ImageSizeControlParamT | None
    stream: ImageStreamParamT
    text: ImageTextParamT | None
    trigger_data: ImageTriggerDataParamT | None

    @classmethod
    def decode(cls, data: tuple[str, ImageParamT]) -> Self:
        """Decode dictionary to class object."""
        id, raw = data
        return cls(
            id=id,
            enabled=raw.get("Enabled", "yes"),
            name=raw["Name"],
            source=raw.get("Source"),
            appearance=raw["Appearance"],
            mpeg=raw.get("MPEG"),
            overlay=raw.get("Overlay"),
            rate_control=raw.get("RateControl"),
            size_control=raw.get("SizeControl"),
            stream=raw["Stream"],
            text=raw.get("Text"),
            trigger_data=raw.get("TriggerData"),
        )

    @classmethod
    def decode_to_dict(cls, data: list[Any]) -> dict[str, Self]:
        """Create objects from dict."""
        image_data = [  # Rename channels I0-I19 to 0-19
            (str(id), data[0][channel_id])
            for id in range(20)
            if (channel_id := f"I{id}") in data[0]
        ]
        return {v.id: v for v in cls.decode_to_list(image_data)}
