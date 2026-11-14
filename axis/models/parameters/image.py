"""Image parameters from param.cgi."""

from dataclasses import dataclass
from typing import Any, NotRequired, Self, TypedDict

from .param_cgi import ParamItem


class ImageAppearanceParamT(TypedDict):
    """Appearance settings for one image channel, including format and rotation."""

    ColorEnabled: str
    Compression: str
    MirrorEnabled: str
    Resolution: str
    Rotation: str


class ImageMpegH264ParamT(TypedDict):
    """H.264-specific encoding settings within an image channel's MPEG group."""

    Profile: str
    PSEnabled: str


class ImageMpegParamT(TypedDict):
    """Video encoding and frame-rate settings within an image channel's MPEG group."""

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
    """Mask-window color setting in an image overlay configuration."""

    Color: str


class ImageOverlayParamT(TypedDict):
    """Position, visibility, and mask-window settings for an image overlay."""

    Enabled: str
    XPos: str
    YPos: str
    MaskWindows: ImageOverlayMaskWindowsParamT


class ImageRateControlParamT(TypedDict):
    """Bitrate mode and target settings for an image channel."""

    MaxBitrate: str
    Mode: str
    Priority: str
    TargetBitrate: str


class ImageSizeControlParamT(TypedDict):
    """Maximum encoded frame size for an image channel."""

    MaxFrameSize: str


class ImageStreamParamT(TypedDict):
    """Stream duration, frame rate, and frame-count settings for an image channel."""

    Duration: str
    FPS: str
    NbrOfFrames: str


class ImageTextParamT(TypedDict):
    """Text, date, and clock overlay settings for an image channel."""

    BGColor: str
    ClockEnabled: str
    Color: str
    DateEnabled: str
    Position: str
    String: str
    TextEnabled: str
    TextSize: str


class ImageTriggerDataParamT(TypedDict):
    """Whether motion, audio, tampering, or user triggers are enabled for a channel."""

    AudioEnabled: bool
    MotionDetectionEnabled: bool
    MotionLevelEnabled: bool
    TamperingEnabled: bool
    UserTriggers: str


class ImageParamT(TypedDict):
    """Image-channel settings returned under an I<n> entry in param.cgi."""

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
    """Image-channel appearance, encoding, overlay, and stream settings."""

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
        """Convert one I<n> image-channel entry into a normalized model."""
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
        """Convert I0-I19 channel entries and index them by numeric channel ID."""
        image_data = [  # Rename channels I0-I19 to 0-19
            (str(id), data[0][channel_id])
            for id in range(20)
            if (channel_id := f"I{id}") in data[0]
        ]
        return {v.id: v for v in cls.decode_to_list(image_data)}
