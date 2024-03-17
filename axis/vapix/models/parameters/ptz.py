"""PTZ parameters from param.cgi."""

from dataclasses import dataclass
from typing import NotRequired, Self

from typing_extensions import TypedDict

from .param_cgi import ParamItem


class PtzImageSourceParamT(TypedDict):
    """PTZ image source description."""

    PTZEnabled: bool


class PtzLimitParamT(TypedDict):
    """PTZ limit data description."""

    MaxBrightness: NotRequired[int]
    MaxFieldAngle: NotRequired[int]
    MaxFocus: NotRequired[int]
    MaxIris: NotRequired[int]
    MaxPan: NotRequired[int]
    MaxTilt: NotRequired[int]
    MaxZoom: NotRequired[int]
    MinBrightness: NotRequired[int]
    MinFieldAngle: NotRequired[int]
    MinFocus: NotRequired[int]
    MinIris: NotRequired[int]
    MinPan: NotRequired[int]
    MinTilt: NotRequired[int]
    MinZoom: NotRequired[int]


class PresetPositionT(TypedDict):
    """PTZ preset position data description."""

    data: tuple[float, float, float]
    name: str | None


class PtzPresetParamT(TypedDict):
    """PTZ preset data description."""

    HomePosition: int
    ImageSource: int
    Name: str | None
    Position: dict[str, PresetPositionT]


class PtzSupportParamT(TypedDict):
    """PTZ support data description."""

    AbsoluteBrightness: bool
    AbsoluteFocus: bool
    AbsoluteIris: bool
    AbsolutePan: bool
    AbsoluteTilt: bool
    AbsoluteZoom: bool
    ActionNotification: bool
    AreaZoom: bool
    AutoFocus: bool
    AutoIrCutFilter: bool
    AutoIris: bool
    Auxiliary: bool
    BackLight: bool
    ContinuousBrightness: bool
    ContinuousFocus: bool
    ContinuousIris: bool
    ContinuousPan: bool
    ContinuousTilt: bool
    ContinuousZoom: bool
    DevicePreset: bool
    DigitalZoom: bool
    GenericHTTP: bool
    IrCutFilter: bool
    JoyStickEmulation: bool
    LensOffset: bool
    OSDMenu: bool
    ProportionalSpeed: bool
    RelativeBrightness: bool
    RelativeFocus: bool
    RelativeIris: bool
    RelativePan: bool
    RelativeTilt: bool
    RelativeZoom: bool
    ServerPreset: bool
    SpeedCtl: bool


class PtzUserAdvParamT(TypedDict):
    """PTZ user adv data description."""

    MoveSpeed: int


class PtzUserCtlQueueParamT(TypedDict):
    """PTZ user control queue data description."""

    Priority: int
    TimeoutTime: int
    TimeoutType: str
    UseCookie: str
    UserGroup: str


class PtzVariousParamT(TypedDict):
    """PTZ various configurations data description."""

    CtlQueueing: bool
    CtlQueueLimit: int
    CtlQueuePollTime: int
    HomePresetSet: bool
    Locked: NotRequired[bool]
    MaxProportionalSpeed: NotRequired[int]
    PanEnabled: NotRequired[bool]
    ProportionalSpeedEnabled: NotRequired[bool]
    ReturnToOverview: int
    SpeedCtlEnabled: NotRequired[bool]
    TiltEnabled: NotRequired[bool]
    ZoomEnabled: NotRequired[bool]


class PtzParamT(TypedDict):
    """PTZ representation."""

    BoaProtPTZOperator: str
    CameraDefault: int
    NbrOfCameras: int
    NbrOfSerPorts: int
    CamPorts: dict[str, int]
    ImageSource: dict[str, PtzImageSourceParamT]
    Limit: NotRequired[dict[str, PtzLimitParamT]]
    Preset: dict[str, PtzPresetParamT]
    PTZDriverStatuses: dict[str, int]
    Support: NotRequired[dict[str, PtzSupportParamT]]
    UserAdv: dict[str, PtzUserAdvParamT]
    UserCtlQueue: dict[str, PtzUserCtlQueueParamT]
    Various: NotRequired[dict[str, PtzVariousParamT]]


@dataclass
class PtzImageSource:
    """Image source."""

    ptz_enabled: bool

    @classmethod
    def decode(cls, data: PtzImageSourceParamT) -> Self:
        """Decode dictionary to class object."""
        return cls(ptz_enabled=data["PTZEnabled"])

    @classmethod
    def from_dict(cls, data: dict[str, PtzImageSourceParamT]) -> dict[str, Self]:
        """Create objects from dict."""
        return {k[1:]: cls.decode(v) for k, v in data.items()}


@dataclass
class PtzLimit:
    """PTZ.Limit.L# are populated when a driver is installed on a video channel.

    Index # is the video channel number, starting on 1.
    When it is possible to obtain the current position from the driver,
    for example the current pan position, it is possible to apply limit restrictions
    to the requested operation. For instance, if an absolute pan to position 150
    is requested, but the upper limit is set to 140, the new pan position will be 140.
    This is the purpose of all but MinFieldAngle and MaxFieldAngle in this group.
    The purpose of those two parameters is to calibrate image centering.
    """

    max_brightness: int | None
    min_brightness: int | None
    max_field_angle: int | None
    min_field_angle: int | None
    max_focus: int | None
    min_focus: int | None
    max_iris: int | None
    min_iris: int | None
    max_pan: int | None
    min_pan: int | None
    max_tilt: int | None
    min_tilt: int | None
    max_zoom: int | None
    min_zoom: int | None

    @classmethod
    def decode(cls, data: PtzLimitParamT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            max_zoom=data.get("MaxZoom"),
            min_zoom=data.get("MinZoom"),
            max_brightness=data.get("MaxBrightness"),
            min_brightness=data.get("MinBrightness"),
            max_field_angle=data.get("MaxFieldAngle"),
            min_field_angle=data.get("MinFieldAngle"),
            max_focus=data.get("MaxFocus"),
            min_focus=data.get("MinFocus"),
            max_iris=data.get("MaxIris"),
            min_iris=data.get("MinIris"),
            max_pan=data.get("MaxPan"),
            min_pan=data.get("MinPan"),
            max_tilt=data.get("MaxTilt"),
            min_tilt=data.get("MinTilt"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, PtzLimitParamT]) -> dict[str, Self]:
        """Create objects from dict."""
        return {k[1:]: cls.decode(v) for k, v in data.items()}


@dataclass
class PtzSupport:
    """PTZ.Support.S# are populated when a driver is installed on a video channel.

    A parameter in the group has the value true if the corresponding capability
    is supported by the driver. The index # is the video channel number
    which starts from 1.
    An absolute operation means moving to a certain position,
    a relative operation means moving relative to the current position.
    Arguments referred to apply to PTZ control.
    """

    absolute_brightness: bool
    absolute_focus: bool
    absolute_iris: bool
    absolute_pan: bool
    absolute_tilt: bool
    absolute_zoom: bool
    action_notification: bool
    area_zoom: bool
    auto_focus: bool
    auto_ir_cut_filter: bool
    auto_iris: bool
    auxiliary: bool
    back_light: bool
    continuous_brightness: bool
    continuous_focus: bool
    continuous_iris: bool
    continuous_pan: bool
    continuous_tilt: bool
    continuous_zoom: bool
    device_preset: bool
    digital_zoom: bool
    generic_http: bool
    ir_cut_filter: bool
    joystick_emulation: bool
    lens_offset: bool
    osd_menu: bool
    proportional_speed: bool
    relative_brightness: bool
    relative_focus: bool
    relative_iris: bool
    relative_pan: bool
    relative_tilt: bool
    relative_zoom: bool
    server_preset: bool
    speed_control: bool

    @classmethod
    def decode(cls, data: PtzSupportParamT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            absolute_brightness=data["AbsoluteBrightness"],
            absolute_focus=data["AbsoluteFocus"],
            absolute_iris=data["AbsoluteIris"],
            absolute_pan=data["AbsolutePan"],
            absolute_tilt=data["AbsoluteTilt"],
            absolute_zoom=data["AbsoluteZoom"],
            action_notification=data["ActionNotification"],
            area_zoom=data["AreaZoom"],
            auto_focus=data["AutoFocus"],
            auto_ir_cut_filter=data["AutoIrCutFilter"],
            auto_iris=data["AutoIris"],
            auxiliary=data["Auxiliary"],
            back_light=data["BackLight"],
            continuous_brightness=data["ContinuousBrightness"],
            continuous_focus=data["ContinuousFocus"],
            continuous_iris=data["ContinuousIris"],
            continuous_pan=data["ContinuousPan"],
            continuous_tilt=data["ContinuousTilt"],
            continuous_zoom=data["ContinuousZoom"],
            device_preset=data["DevicePreset"],
            digital_zoom=data["DigitalZoom"],
            generic_http=data["GenericHTTP"],
            ir_cut_filter=data["IrCutFilter"],
            joystick_emulation=data["JoyStickEmulation"],
            lens_offset=data["LensOffset"],
            osd_menu=data["OSDMenu"],
            proportional_speed=data["ProportionalSpeed"],
            relative_brightness=data["RelativeBrightness"],
            relative_focus=data["RelativeFocus"],
            relative_iris=data["RelativeIris"],
            relative_pan=data["RelativePan"],
            relative_tilt=data["RelativeTilt"],
            relative_zoom=data["RelativeZoom"],
            server_preset=data["ServerPreset"],
            speed_control=data["SpeedCtl"],
        )

    @classmethod
    def from_dict(cls, data: dict[str, PtzSupportParamT]) -> dict[str, Self]:
        """Create objects from dict."""
        return {k[1:]: cls.decode(v) for k, v in data.items()}


@dataclass
class PtzVarious:
    """PTZ.Various.V# are populated when a driver is installed on a video channel.

    The index # is the video channel number which starts from 1.
    The group consists of several different types of parameters for the video channel.
    To distinguish the parameter types, the group is presented as
    three different categories below. The Enabled parameters determine
    if a specific feature can be controlled using ptz.cgi (see section PTZ control).
    """

    control_queueing: bool
    control_queue_limit: int
    control_queue_poll_time: int
    home_preset_set: bool | None
    locked: bool
    max_proportional_speed: int | None
    pan_enabled: bool | None
    proportional_speed_enabled: bool | None
    return_to_overview: int | None
    speed_control_enabled: bool | None
    tilt_enabled: bool | None
    zoom_enabled: bool | None

    @classmethod
    def decode(cls, data: PtzVariousParamT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            control_queueing=data["CtlQueueing"],
            control_queue_limit=data["CtlQueueLimit"],
            control_queue_poll_time=data["CtlQueuePollTime"],
            home_preset_set=data.get("HomePresetSet"),
            locked=data.get("Locked", False),
            max_proportional_speed=data.get("MaxProportionalSpeed"),
            pan_enabled=data.get("PanEnabled"),
            proportional_speed_enabled=data.get("ProportionalSpeedEnabled"),
            return_to_overview=data.get("ReturnToOverview"),
            speed_control_enabled=data.get("SpeedCtlEnabled"),
            tilt_enabled=data.get("TiltEnabled"),
            zoom_enabled=data.get("ZoomEnabled"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, PtzVariousParamT]) -> dict[str, Self]:
        """Create objects from dict."""
        return {k[1:]: cls.decode(v) for k, v in data.items()}


@dataclass(frozen=True)
class PtzParam(ParamItem):
    """PTZ parameters."""

    camera_default: int
    """PTZ default video channel.

    When camera parameter is omitted in HTTP requests.
    """

    number_of_cameras: int
    """Amount of video channels."""

    number_of_serial_ports: int
    """Amount of serial ports."""

    cam_ports: dict[str, int]

    image_source: dict[str, PtzImageSource]

    limits: dict[str, PtzLimit]
    """PTZ.Limit.L# are populated when a driver is installed on a video channel."""

    support: dict[str, PtzSupport]
    """PTZ.Support.S# are populated when a driver is installed on a video channel."""

    various: dict[str, PtzVarious]
    """PTZ.Various.V# are populated when a driver is installed on a video channel."""

    @classmethod
    def decode(cls, data: PtzParamT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            id="ptz",
            camera_default=data["CameraDefault"],
            number_of_cameras=data.get("NbrOfCameras", 1),
            number_of_serial_ports=data["NbrOfSerPorts"],
            cam_ports=data["CamPorts"],
            image_source=PtzImageSource.from_dict(data["ImageSource"]),
            limits=PtzLimit.from_dict(data.get("Limit", {})),
            support=PtzSupport.from_dict(data.get("Support", {})),
            various=PtzVarious.from_dict(data.get("Various", {})),
        )
