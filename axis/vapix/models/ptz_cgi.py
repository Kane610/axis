"""PTZ control API.

Control the pan, tilt and zoom behavior of a PTZ unit.
The PTZ control is device-dependent. For information about supported parameters
and actual parameter values, check the specification of the Axis PTZ driver used.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar, cast

from typing_extensions import NotRequired, Self, TypedDict

from .api import ApiItem, ApiRequest, ApiResponse
from .param_cgi import params_to_dict


class ImageSourceT(TypedDict):
    """PTZ image source description."""

    PTZEnabled: bool


class LimitT(TypedDict):
    """PTZ limit data description."""

    MaxBrightness: NotRequired[int]
    MaxFieldAngle: int
    MaxFocus: NotRequired[int]
    MaxIris: NotRequired[int]
    MaxPan: int
    MaxTilt: int
    MaxZoom: int
    MinBrightness: NotRequired[int]
    MinFieldAngle: int
    MinFocus: NotRequired[int]
    MinIris: NotRequired[int]
    MinPan: int
    MinTilt: int
    MinZoom: int


class PresetPositionT(TypedDict):
    """PTZ preset position data description."""

    data: tuple[float, float, float]
    name: str | None


class PresetT(TypedDict):
    """PTZ preset data description."""

    HomePosition: int
    ImageSource: int
    Name: str | None
    Position: dict[str, PresetPositionT]


class SupportT(TypedDict):
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


class UserAdvT(TypedDict):
    """PTZ user adv data description."""

    MoveSpeed: int


class UserCtlQueueT(TypedDict):
    """PTZ user control queue data description."""

    Priority: int
    TimeoutTime: int
    TimeoutType: str
    UseCookie: str
    UserGroup: str


class VariousT(TypedDict):
    """PTZ various configurations data description."""

    CtlQueueing: bool
    CtlQueueLimit: int
    CtlQueuePollTime: int
    HomePresetSet: bool
    Locked: NotRequired[bool]
    MaxProportionalSpeed: int
    PanEnabled: bool
    ProportionalSpeedEnabled: bool
    ReturnToOverview: int
    SpeedCtlEnabled: bool
    TiltEnabled: bool
    ZoomEnabled: bool


class PtzItemT(TypedDict):
    """PTZ representation."""

    BoaProtPTZOperator: str
    CameraDefault: int
    NbrOfCameras: int
    NbrOfSerPorts: int
    CamPorts: dict[str, int]
    ImageSource: dict[str, ImageSourceT]
    Limit: dict[str, LimitT]
    Preset: dict[str, PresetT]
    PTZDriverStatuses: dict[str, int]
    Support: dict[str, SupportT]
    UserAdv: dict[str, UserAdvT]
    UserCtlQueue: dict[str, UserCtlQueueT]
    Various: dict[str, VariousT]


class PtzMove(Enum):
    """Supported PTZ moves.

    Absolute:Moves the image 25 % of the image field width in the specified direction.
    Relative: Moves the device approx. 50-90 degrees in the specified direction.
    """

    HOME = "home"
    """Moves the image to the home position."""

    UP = "up"
    """Moves the image up."""

    DOWN = "down"
    """Moves the image down."""

    LEFT = "left"
    """Moves the image to the left."""

    RIGHT = "right"
    """Moves the image to the right."""

    UPLEFT = "upleft"
    """Moves the image up diagonal to the left."""

    UPRIGHT = "upright"
    """Moves the image up diagonal to the right."""

    DOWNLEFT = "downleft"
    """Moves the image down diagonal to the left."""

    DOWNRIGHT = "downright"
    """Moves the image down diagonal to the right."""

    STOP = "stop"
    """Stops the pan/tilt movement."""


class PtzRotation(Enum):
    """Supported PTZ rotations."""

    ROTATION_0 = "0"
    ROTATION_90 = "90"
    ROTATION_180 = "180"
    ROTATION_270 = "270"


class PtzState(Enum):
    """Supported PTZ states."""

    AUTO = "auto"
    ON = "on"
    OFF = "off"


class PtzQuery(Enum):
    """Supported PTZ queries."""

    LIMITS = "limits"
    """PTZ limits for the Axis product."""

    MODE = "mode"
    """Products with Panopsis technology: The current mode (overview or normal)."""

    POSITION = "position"
    """Values for current position."""

    PRESETPOSALL = "presetposall"
    """Current preset positions for all video channels."""

    PRESETPOSCAM = "presetposcam"
    """Current preset positions for a video channel."""

    PRESETPOSCAMDATA = "presetposcamdata"
    """Configured preset positions with position data measured in degrees."""

    SPEED = "speed"
    """Values for pan/tilt speed."""


_T = TypeVar("_T", bound=int | float)


def limit(num: _T, minimum: float, maximum: float) -> _T:
    """Limits input 'num' between minimum and maximum values."""
    return max(min(num, maximum), minimum)


@dataclass
class PtzImageSource:
    """Image source."""

    ptz_enabled: bool

    @classmethod
    def decode(cls, data: ImageSourceT) -> Self:
        """Decode dictionary to class object."""
        return cls(ptz_enabled=data["PTZEnabled"])

    @classmethod
    def from_dict(cls, data: dict[str, ImageSourceT]) -> dict[str, Self]:
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

    max_field_angle: int
    min_field_angle: int
    max_pan: int
    min_pan: int
    max_tilt: int
    min_tilt: int
    max_zoom: int
    min_zoom: int
    max_brightness: int | None
    min_brightness: int | None
    max_focus: int | None
    min_focus: int | None
    max_iris: int | None
    min_iris: int | None

    @classmethod
    def decode(cls, data: LimitT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            max_field_angle=data["MaxFieldAngle"],
            min_field_angle=data["MinFieldAngle"],
            max_pan=data["MaxPan"],
            min_pan=data["MinPan"],
            max_tilt=data["MaxTilt"],
            min_tilt=data["MinTilt"],
            max_zoom=data["MaxZoom"],
            min_zoom=data["MinZoom"],
            max_brightness=data.get("MaxBrightness"),
            min_brightness=data.get("MinBrightness"),
            max_focus=data.get("MaxFocus"),
            min_focus=data.get("MinFocus"),
            max_iris=data.get("MaxIris"),
            min_iris=data.get("MinIris"),
        )

    @classmethod
    def from_dict(cls, data: dict[str, LimitT]) -> dict[str, Self]:
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
    backLight: bool
    continuous_brightness: bool
    continuous_focus: bool
    continuous_iris: bool
    continuous_pan: bool
    continuous_tilt: bool
    continuousZoom: bool
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
    def decode(cls, data: SupportT) -> Self:
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
            backLight=data["BackLight"],
            continuous_brightness=data["ContinuousBrightness"],
            continuous_focus=data["ContinuousFocus"],
            continuous_iris=data["ContinuousIris"],
            continuous_pan=data["ContinuousPan"],
            continuous_tilt=data["ContinuousTilt"],
            continuousZoom=data["ContinuousZoom"],
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
    def from_dict(cls, data: dict[str, SupportT]) -> dict[str, Self]:
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
    home_preset_set: bool
    locked: bool
    max_proportional_speed: int
    pan_enabled: bool
    proportional_speed_enabled: bool
    return_to_overview: int
    speed_control_enabled: bool
    tilt_enabled: bool
    zoom_enabled: bool

    @classmethod
    def decode(cls, data: VariousT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            control_queueing=data["CtlQueueing"],
            control_queue_limit=data["CtlQueueLimit"],
            control_queue_poll_time=data["CtlQueuePollTime"],
            home_preset_set=data["HomePresetSet"],
            locked=data.get("Locked", False),
            max_proportional_speed=data["MaxProportionalSpeed"],
            pan_enabled=data["PanEnabled"],
            proportional_speed_enabled=data["ProportionalSpeedEnabled"],
            return_to_overview=data["ReturnToOverview"],
            speed_control_enabled=data["SpeedCtlEnabled"],
            tilt_enabled=data["TiltEnabled"],
            zoom_enabled=data["ZoomEnabled"],
        )

    @classmethod
    def from_dict(cls, data: dict[str, VariousT]) -> dict[str, Self]:
        """Create objects from dict."""
        return {k[1:]: cls.decode(v) for k, v in data.items()}


@dataclass
class PtzItem(ApiItem):
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
    def decode(cls, data: PtzItemT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            id="ptz",
            camera_default=data["CameraDefault"],
            number_of_cameras=data["NbrOfCameras"],
            number_of_serial_ports=data["NbrOfSerPorts"],
            cam_ports=data["CamPorts"],
            image_source=PtzImageSource.from_dict(data["ImageSource"]),
            limits=PtzLimit.from_dict(data["Limit"]),
            support=PtzSupport.from_dict(data["Support"]),
            various=PtzVarious.from_dict(data["Various"]),
        )


@dataclass
class GetPtzParamsRequest(ApiRequest):
    """Request object for listing PTZ parameters."""

    method = "get"
    path = "/axis-cgi/param.cgi?action=list&group=root.PTZ"
    content_type = "text/plain"


@dataclass
class GetPtzResponse(ApiResponse[dict[str, PtzItem]]):
    """Response object for listing ports."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Create response object from bytes."""
        data = bytes_data.decode()
        ptz_params: PtzItemT = (
            params_to_dict(data, "root.PTZ").get("root", {}).get("PTZ", {})
        )
        return cls({"0": PtzItem.decode(ptz_params)})

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create response object from dict."""
        return cls({"0": PtzItem.decode(cast(PtzItemT, data))})


@dataclass
class PtzControlRequest(ApiRequest):
    """Control pan, tilt and zoom behavior of a PTZ unit."""

    method = "post"
    path = "/axis-cgi/com/ptz.cgi"
    content_type = "text/plain"

    camera: int | None = None
    """Selects the video channel.

    If omitted the default value camera=1 is used.
    This argument is only valid for Axis products with
    more than one video channel. That is cameras with
    multiple view areas and video encoders with multiple video channels.
    """
    center: tuple[int, int] | None = None
    """Center the camera on positions x,y.

    x,y are pixel coordinates in the client video stream.
    """
    areazoom: tuple[int, int, int] | None = None
    """Centers on positions x,y and zooms by a factor of z/100.

    If z is more than 100 the image is zoomed in
    (for example; z=300 zooms in to 1/3 of the current field of view).
    If z is less than 100 the image is zoomed out
    (for example; z=50 zooms out to twice the current field of view).
    """
    imagewidth: int | None = None
    """Required in conjunction with center or areazoom.

    If the image width displayed is different from the default size of the image,
    which is product-specific.
    """
    imageheight: int | None = None
    """Required in conjunction with center or areazoom.

    If the image height is different from the default size of the image,
    which is product-specific.
    """
    move: PtzMove | None = None
    """Supported PTZ moves.

    Absolute:Moves the image 25 % of the image field width in the specified direction.
    Relative: Moves the device approx. 50-90 degrees in the specified direction.
    """
    pan: float | None = None
    """-180.0 ... 180.0 Pans the device to the specified absolute coordinates."""

    tilt: float | None = None
    """-180.0 ... 180.0 Tilts the device to the specified absolute coordinates."""

    zoom: int | None = None
    """1 ... 9999 Zooms the device n steps to the specified absolute position.

    A high value means zoom in, a low value means zoom out.
    """
    focus: int | None = None
    """1 ... 9999 Moves focus n steps to the specified absolute position.

    A high value means focus far, a low value means focus near.
    """
    iris: int | None = None
    """1 ... 9999 Moves iris n steps to the specified absolute position.

    A high value means open iris, a low value means close iris.
    """
    brightness: int | None = None
    """1 ... 9999 Moves brightness n steps to the specified absolute position.

    A high value means brighter image, a low value means darker image.
    """
    rpan: float | None = None
    """-360.0 ... 360.0 Pans the device n degrees relative to the current position."""
    rtilt: float | None = None
    """-360.0 ... 360.0 Tilts the device n degrees relative to the current position."""
    rzoom: int | None = None
    """-9999 ... 9999 Zooms the device n steps relative to the current position.

    Positive values mean zoom in, negative values mean zoom out.
    """
    rfocus: int | None = None
    """-9999 ... 9999 Moves focus n steps relative to the current position.

    Positive values mean focus far, negative values mean focus near.
    """
    riris: int | None = None
    """-9999 ... 9999 Moves iris n steps relative to the current position.

    Positive values mean open iris, negative values mean close iris.
    """
    rbrightness: int | None = None
    """-9999 ... 9999 Moves brightness n steps relative to the current position.

    Positive values mean brighter image, negative values mean darker image.
    """
    autofocus: bool | None = None
    """Enable/disable auto focus."""
    autoiris: bool | None = None
    """Enable/disable auto iris."""
    continuouspantiltmove: tuple[int, int] | None = None
    """-100 ... 100,-100 ... 100 Continuous pan/tilt motion.

    Positive values mean right (pan) and up (tilt),
    negative values mean left (pan) and down (tilt).
    0,0 means stop.
    Values as <pan speed>,<tilt speed>.
    """
    continuouszoommove: int | None = None
    """-100 ... 100 Continuous zoom motion.

    Positive values mean zoom in and negative values mean zoom out.
    0 means stop.
    """
    continuousfocusmove: int | None = None
    """-100 ... 100 Continuous focus motion.

    Positive values mean focus far and negative values mean focus near.
    0 means stop.
    """
    continuousirismove: int | None = None
    """-100 ... 100 Continuous iris motion.

    Positive values mean iris open and negative values mean iris close.
    0 means stop.
    """
    continuousbrightnessmove: int | None = None
    """-100 ... 100 Continuous brightness motion.

    Positive values mean brighter image and negative values mean darker image.
    0 means stop.
    """
    auxiliary: str | None = None
    """Activates/deactivates auxiliary functions of the device.

    <function name> is the name of the device specific function.
    Check in driver's documentation or in response to info=1
    for information about <function name>.
    """
    gotoserverpresetname: str | None = None
    """Move to the position associated with the <preset name>."""
    gotoserverpresetno: int | None = None
    """Move to the position associated with the specified preset position number."""
    gotodevicepreset: int | None = None
    """Bypasses the presetpos interface.

    Tells the device togo directly to the preset position number
    <preset pos> stored in the device,
    where the <preset pos> is a device-specific preset position number.
    This may also be a device-specific special function.
    """
    speed: int | None = None
    """1 ... 100 Sets the move speed of pan and tilt."""
    imagerotation: PtzRotation | None = None
    """Rotate image.

    If PTZ command refers to an image stream that is rotated differently
    than the current image setup, then the image stream rotation
    must be added to each command with this argument to
    allow the Axis product to compensate.
    """
    ircutfilter: PtzState | None = None
    """Control the IR cut filter."""
    backlight: bool | None = None
    """Control the backlight compensation."""

    @property
    def data(self) -> dict[str, str] | None:
        """Request data."""
        data = {}
        if self.camera:
            data["camera"] = str(self.camera)
        if self.center:
            x, y = self.center
            data["center"] = f"{x},{y}"
        if self.areazoom:
            x, y, z = self.areazoom
            if z < 1:
                z = 1
            data["areazoom"] = f"{x},{y},{z}"
        if self.center or self.areazoom:
            if self.imagewidth:
                data["imagewidth"] = str(self.imagewidth)
            if self.imageheight:
                data["imageheight"] = str(self.imageheight)

        for key, limit_value, minimum, maximum in (
            ("pan", self.pan, -180, 180),
            ("tilt", self.tilt, -180, 180),
            ("zoom", self.zoom, 1, 9999),
            ("focus", self.focus, 1, 9999),
            ("iris", self.iris, 1, 9999),
            ("brightness", self.brightness, 1, 9999),
            ("rpan", self.rpan, -360, 360),
            ("rtilt", self.rtilt, -360, 360),
            ("rzoom", self.rzoom, -9999, 9999),
            ("rfocus", self.rfocus, -9999, 9999),
            ("riris", self.riris, -9999, 9999),
            ("rbrightness", self.rbrightness, -9999, 9999),
            ("continuouszoommove", self.continuouszoommove, -100, 100),
            ("continuousfocusmove", self.continuousfocusmove, -100, 100),
            ("continuousirismove", self.continuousirismove, -100, 100),
            ("continuousbrightnessmove", self.continuousbrightnessmove, -100, 100),
            ("speed", self.speed, 1, 100),
        ):
            if limit_value is not None:
                data[key] = str(limit(limit_value, minimum, maximum))

        for key, command_bool in (
            ("autofocus", self.autofocus),
            ("autoiris", self.autoiris),
            ("backlight", self.backlight),
        ):
            if command_bool is not None:
                data[key] = "on" if command_bool else "off"

        for key, command_enum in (
            ("imagerotation", self.imagerotation),
            ("ircutfilter", self.ircutfilter),
            ("move", self.move),
        ):
            if command_enum is not None:
                data[key] = command_enum.value

        if self.continuouspantiltmove:
            pan_speed, tilt_speed = self.continuouspantiltmove
            pan_speed = limit(pan_speed, -100, 100)
            tilt_speed = limit(tilt_speed, -100, 100)
            data["continuouspantiltmove"] = f"{pan_speed},{tilt_speed}"
        if self.auxiliary:
            data["auxiliary"] = self.auxiliary
        if self.gotoserverpresetname:
            data["gotoserverpresetname"] = self.gotoserverpresetname
        if self.gotoserverpresetno:
            data["gotoserverpresetno"] = str(self.gotoserverpresetno)
        if self.gotodevicepreset:
            data["gotodevicepreset"] = str(self.gotodevicepreset)

        if len(data) == 0 or (len(data) == 1 and "camera" in data):
            return None
        return data


@dataclass
class PtzCommandRequest(ApiRequest):
    """Retrieve available PTZ commands."""

    method = "post"
    path = "/axis-cgi/com/ptz.cgi"
    content_type = "text/plain"

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        return {"info": "1"}


@dataclass
class DeviceDriverRequest(ApiRequest):
    """Retrieve name of the device driver."""

    method = "post"
    path = "/axis-cgi/com/ptz.cgi"
    content_type = "text/plain"

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        return {"whoami": "1"}


@dataclass
class QueryRequest(ApiRequest):
    """Retrieve current status."""

    method = "post"
    path = "/axis-cgi/com/ptz.cgi"
    content_type = "text/plain"

    query: PtzQuery

    @property
    def data(self) -> dict[str, str]:
        """Request data."""
        return {"query": self.query.value}
