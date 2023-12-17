"""Image parameters from param.cgi."""

from dataclasses import dataclass
from typing import Any

from typing_extensions import Self, TypedDict

from ..api import ApiItem


class ImageParamT(TypedDict):
    """Represent an image object."""

    Enabled: str
    Name: str
    Source: str
    Appearance_ColorEnabled: str
    Appearance_Compression: str
    Appearance_MirrorEnabled: str
    Appearance_Resolution: str
    Appearance_Rotation: str
    MPEG_Complexity: str
    MPEG_ConfigHeaderInterval: str
    MPEG_FrameSkipMode: str
    MPEG_ICount: str
    MPEG_PCount: str
    MPEG_UserDataEnabled: str
    MPEG_UserDataInterval: str
    MPEG_ZChromaQPMode: str
    MPEG_ZFpsMode: str
    MPEG_ZGopMode: str
    MPEG_ZMaxGopLength: str
    MPEG_ZMinFps: str
    MPEG_ZStrength: str
    MPEG_H264_Profile: str
    MPEG_H264_PSEnabled: str
    Overlay_Enabled: str
    Overlay_XPos: str
    Overlay_YPos: str
    Overlay_MaskWindows_Color: str
    RateControl_MaxBitrate: str
    RateControl_Mode: str
    RateControl_Priority: str
    RateControl_TargetBitrate: str
    SizeControl_MaxFrameSize: str
    Stream_Duration: str
    Stream_FPS: str
    Stream_NbrOfFrames: str
    Text_BGColor: str
    Text_ClockEnabled: str
    Text_Color: str
    Text_DateEnabled: str
    Text_Position: str
    Text_String: str
    Text_TextEnabled: str
    Text_TextSize: str


@dataclass
class ImageParam(ApiItem):
    """Image parameters."""

    data: dict[int, ImageParamT]

    @classmethod
    def decode(cls, data: dict[str, Any]) -> Self:
        """Decode dictionary to class object."""
        return cls(id="image", data=data)
