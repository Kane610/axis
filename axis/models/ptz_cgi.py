"""PTZ control API.

Control the pan, tilt and zoom behavior of a PTZ unit.
The PTZ control is device-dependent. For information about supported parameters
and actual parameter values, check the specification of the Axis PTZ driver used.
"""

from dataclasses import dataclass
import enum

from .api import ApiRequest


class PtzMove(enum.StrEnum):
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


class PtzRotation(enum.StrEnum):
    """Supported PTZ rotations."""

    ROTATION_0 = "0"
    ROTATION_90 = "90"
    ROTATION_180 = "180"
    ROTATION_270 = "270"


class PtzState(enum.StrEnum):
    """Supported PTZ states."""

    AUTO = "auto"
    ON = "on"
    OFF = "off"


class PtzQuery(enum.StrEnum):
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
    area_zoom: tuple[int, int, int] | None = None
    """Centers on positions x,y and zooms by a factor of z/100.

    If z is more than 100 the image is zoomed in
    (for example; z=300 zooms in to 1/3 of the current field of view).
    If z is less than 100 the image is zoomed out
    (for example; z=50 zooms out to twice the current field of view).
    """
    image_width: int | None = None
    """Required in conjunction with center or areazoom.

    If the image width displayed is different from the default size of the image,
    which is product-specific.
    """
    image_height: int | None = None
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
    relative_pan: float | None = None
    """-360.0 ... 360.0 Pans the device n degrees relative to the current position."""
    relative_tilt: float | None = None
    """-360.0 ... 360.0 Tilts the device n degrees relative to the current position."""
    relative_zoom: int | None = None
    """-9999 ... 9999 Zooms the device n steps relative to the current position.

    Positive values mean zoom in, negative values mean zoom out.
    """
    relative_focus: int | None = None
    """-9999 ... 9999 Moves focus n steps relative to the current position.

    Positive values mean focus far, negative values mean focus near.
    """
    relative_iris: int | None = None
    """-9999 ... 9999 Moves iris n steps relative to the current position.

    Positive values mean open iris, negative values mean close iris.
    """
    relative_brightness: int | None = None
    """-9999 ... 9999 Moves brightness n steps relative to the current position.

    Positive values mean brighter image, negative values mean darker image.
    """
    auto_focus: bool | None = None
    """Enable/disable auto focus."""
    auto_iris: bool | None = None
    """Enable/disable auto iris."""
    continuous_pantilt_move: tuple[int, int] | None = None
    """-100 ... 100,-100 ... 100 Continuous pan/tilt motion.

    Positive values mean right (pan) and up (tilt),
    negative values mean left (pan) and down (tilt).
    0,0 means stop.
    Values as <pan speed>,<tilt speed>.
    """
    continuous_zoom_move: int | None = None
    """-100 ... 100 Continuous zoom motion.

    Positive values mean zoom in and negative values mean zoom out.
    0 means stop.
    """
    continuous_focus_move: int | None = None
    """-100 ... 100 Continuous focus motion.

    Positive values mean focus far and negative values mean focus near.
    0 means stop.
    """
    continuous_iris_move: int | None = None
    """-100 ... 100 Continuous iris motion.

    Positive values mean iris open and negative values mean iris close.
    0 means stop.
    """
    continuous_brightness_move: int | None = None
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
    go_to_server_preset_name: str | None = None
    """Move to the position associated with the <preset name>."""
    go_to_server_preset_number: int | None = None
    """Move to the position associated with the specified preset position number."""
    go_to_device_preset: int | None = None
    """Bypasses the presetpos interface.

    Tells the device togo directly to the preset position number
    <preset pos> stored in the device,
    where the <preset pos> is a device-specific preset position number.
    This may also be a device-specific special function.
    """
    speed: int | None = None
    """1 ... 100 Sets the move speed of pan and tilt."""
    image_rotation: PtzRotation | None = None
    """Rotate image.

    If PTZ command refers to an image stream that is rotated differently
    than the current image setup, then the image stream rotation
    must be added to each command with this argument to
    allow the Axis product to compensate.
    """
    ir_cut_filter: PtzState | None = None
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
        if self.area_zoom:
            x, y, z = self.area_zoom
            if z < 1:
                z = 1
            data["areazoom"] = f"{x},{y},{z}"
        if self.center or self.area_zoom:
            if self.image_width:
                data["imagewidth"] = str(self.image_width)
            if self.image_height:
                data["imageheight"] = str(self.image_height)

        for key, limit_value, minimum, maximum in (
            ("pan", self.pan, -180, 180),
            ("tilt", self.tilt, -180, 180),
            ("zoom", self.zoom, 1, 9999),
            ("focus", self.focus, 1, 9999),
            ("iris", self.iris, 1, 9999),
            ("brightness", self.brightness, 1, 9999),
            ("rpan", self.relative_pan, -360, 360),
            ("rtilt", self.relative_tilt, -360, 360),
            ("rzoom", self.relative_zoom, -9999, 9999),
            ("rfocus", self.relative_focus, -9999, 9999),
            ("riris", self.relative_iris, -9999, 9999),
            ("rbrightness", self.relative_brightness, -9999, 9999),
            ("continuouszoommove", self.continuous_zoom_move, -100, 100),
            ("continuousfocusmove", self.continuous_focus_move, -100, 100),
            ("continuousirismove", self.continuous_iris_move, -100, 100),
            ("continuousbrightnessmove", self.continuous_brightness_move, -100, 100),
            ("speed", self.speed, 1, 100),
        ):
            if limit_value is not None:
                data[key] = str(max(min(limit_value, maximum), minimum))

        for key, command_bool in (
            ("autofocus", self.auto_focus),
            ("autoiris", self.auto_iris),
            ("backlight", self.backlight),
        ):
            if command_bool is not None:
                data[key] = "on" if command_bool else "off"

        for key, command_enum in (
            ("imagerotation", self.image_rotation),
            ("ircutfilter", self.ir_cut_filter),
            ("move", self.move),
        ):
            if command_enum is not None:
                data[key] = command_enum

        if self.continuous_pantilt_move:
            pan_speed, tilt_speed = self.continuous_pantilt_move
            pan_speed = max(min(pan_speed, 100), -100)
            tilt_speed = max(min(tilt_speed, 100), -100)
            data["continuouspantiltmove"] = f"{pan_speed},{tilt_speed}"
        if self.auxiliary:
            data["auxiliary"] = self.auxiliary
        if self.go_to_server_preset_name:
            data["gotoserverpresetname"] = self.go_to_server_preset_name
        if self.go_to_server_preset_number:
            data["gotoserverpresetno"] = str(self.go_to_server_preset_number)
        if self.go_to_device_preset:
            data["gotodevicepreset"] = str(self.go_to_device_preset)

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
        return {"query": self.query}
