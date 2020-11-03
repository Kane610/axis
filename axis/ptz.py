"""PTZ control API.

Control the pan, tilt and zoom behavior of a PTZ unit.
The PTZ control is device-dependent. For information about supported parameters
and actual parameter values, check the specification of the Axis PTZ driver used.
"""

from typing import Optional, Union

URL = "/axis-cgi/com/ptz.cgi"

MOVE_HOME = "home"
MOVE_UP = "up"
MOVE_DOWN = "down"
MOVE_LEFT = "left"
MOVE_RIGHT = "right"
MOVE_UPLEFT = "upleft"
MOVE_UPRIGHT = "upright"
MOVE_DOWNLEFT = "downleft"
MOVE_DOWNRIGHT = "downright"
MOVE_STOP = "stop"
SUPPORTED_MOVES = (
    MOVE_HOME,
    MOVE_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UPLEFT,
    MOVE_UPRIGHT,
    MOVE_DOWNLEFT,
    MOVE_DOWNRIGHT,
    MOVE_STOP,
)

AUTO = "auto"
ON = "on"
OFF = "off"

QUERY_LIMITS = "limits"
QUERY_MODE = "mode"
QUERY_POSITION = "position"
QUERY_PRESETPOSALL = "presetposall"
QUERY_PRESETPOSCAM = "presetposcam"
QUERY_PRESETPOSCAMDATA = "presetposcamdata"
QUERY_SPEED = "speed"
SUPPORTED_QUERIES = (
    QUERY_LIMITS,
    QUERY_MODE,
    QUERY_POSITION,
    QUERY_PRESETPOSALL,
    QUERY_PRESETPOSCAM,
    QUERY_PRESETPOSCAMDATA,
    QUERY_SPEED,
)


def limit(
    num: Union[int, float], minimum: Union[int, float], maximum: Union[int, float]
) -> Union[int, float]:
    """Limits input 'num' between minimum and maximum values."""
    return max(min(num, maximum), minimum)


class PtzControl:
    """Configure and control the PTZ functionality."""

    def __init__(self, request: object) -> None:
        """Initialize PTZ control."""
        self._request = request

    async def control(
        self,
        camera: Optional[int] = None,
        center: Optional[tuple] = None,
        areazoom: Optional[tuple] = None,
        imagewidth: Optional[int] = None,
        imageheight: Optional[int] = None,
        move: Optional[str] = None,
        pan: Optional[float] = None,
        tilt: Optional[float] = None,
        zoom: Optional[int] = None,
        focus: Optional[int] = None,
        iris: Optional[int] = None,
        brightness: Optional[int] = None,
        rpan: Optional[float] = None,
        rtilt: Optional[float] = None,
        rzoom: Optional[int] = None,
        rfocus: Optional[int] = None,
        riris: Optional[int] = None,
        rbrightness: Optional[int] = None,
        autofocus: Optional[str] = None,
        autoiris: Optional[str] = None,
        continuouspantiltmove: Optional[tuple] = None,
        continuouszoommove: Optional[int] = None,
        continuousfocusmove: Optional[int] = None,
        continuousirismove: Optional[int] = None,
        continuousbrightnessmove: Optional[int] = None,
        auxiliary: Optional[str] = None,
        gotoserverpresetname: Optional[str] = None,
        gotoserverpresetno: Optional[int] = None,
        gotodevicepreset: Optional[int] = None,
        speed: Optional[int] = None,
        imagerotation: Optional[int] = None,
        ircutfilter: Optional[str] = None,
        backlight: Optional[str] = None,
    ) -> None:
        """Control the pan, tilt and zoom behavior of a PTZ unit.

        camera=<int> 1 (default) ... Selects the video channel. If omitted the default value camera=1 is used. This argument is only valid for Axis products with more than one video channel. That is cameras with multiple view areas and video encoders with multiple video channels.
        center=<int>,<int> <x>,<y> Center the camera on positions x,y where x,y are pixel coordinates in the client video stream.
        areazoom=<int>,<int>,<int> <x>,<y>,<z=>1> Centers on positions x,y (like the center command) and zooms by a factor of z/100. If z is more than 100 the image is zoomed in (for example; z=300 zooms in to 1/3 of the current field of view). If z is less than 100 the image is zoomed out (for example; z=50 zooms out to twice the current field of view).
        imagewidth=<int> 1, ... Required in conjunction with center or areazoom if the image width displayed is different from the default size of the image, which is product-specific.
        imageheight=<int> 1, ... Required in conjunction with center or areazoom if the image height is different from the default size of the image, which is product-specific.
        move=<string> Absolute:Moves the image 25 % of the image field width in the specified direction.
                      Relative: Moves the device approx. 50-90 degrees in the specified direction.
            home = Moves the image to the home position.
            up = Moves the image up.
            down = Moves the image down.
            left = Moves the image to the left.
            right = Moves the image to the right.
            upleft = Moves the image up diagonal to the left.
            upright = Moves the image up diagonal to the right.
            downleft = Moves the image down diagonal to the left.
            downright = Moves the image down diagonal to the right.
            stop = Stops the pan/tilt movement.
        pan=<float> -180.0 ... 180.0 Pans the device to the specified absolute coordinates.(3)
        tilt=<float> -180.0 ... 180.0 Tilts the device to the specified absolute coordinates.(3)
        zoom=<int> 1 ... 9999 Zooms the device n steps to the specified absolute position. A high value means zoom in, a low value means zoom out.(3)
        focus=<int> 1 ... 9999 Moves focus n steps to the specified absolute position. A high value means focus far, a low value means focus near.
        iris=<int> 1 ... 9999 Moves iris n steps to the specified absolute position. A high value means open iris, a low value means close iris.
        brightness=<int> 1 ... 9999 Moves brightness n steps to the specified absolute position. A high value means brighter image, a low value means darker image.
        rpan=<float> -360.0 ... 360.0 Pans the device n degrees relative to the current position.(3)
        rtilt=<float> -360.0 ... 360.0 Tilts the device n degrees relative to the current position.(3)
        rzoom=<int> -9999 ... 9999 Zooms the device n steps relative to the current position. Positive values mean zoom in, negative values mean zoom out.
        rfocus=<int> -9999 ... 9999 Moves focus n steps relative to the current position. Positive values mean focus far, negative values mean focus near.
        riris=<int> -9999 ... 9999 Moves iris n steps relative to the current position. Positive values mean open iris, negative values mean close iris.
        rbrightness=<int> -9999 ... 9999 Moves brightness n steps relative to the current position. Positive values mean brighter image, negative values mean darker image.
        autofocus=<string> on/off Enable/disable auto focus.
            on = Enables auto focus.
            off = Disables auto focus.
        autoiris=<string> on/off Enable/disable auto iris.
            on = Enable auto iris.
            off = Disable auto iris.
        continuouspantiltmove=<int>,<int> -100 ... 100,-100 ... 100 Continuous pan/tilt motion.
            Positive values mean right (pan) and up (tilt), negative values mean left (pan) and down (tilt). 0,0 means stop.(3)
            Values as <pan speed>,<tilt speed>.
        continuouszoommove=<int> -100 ... 100 Continuous zoom motion. Positive values mean zoom in and negative values mean zoom out. 0 means stop.
        continuousfocusmove=<int> -100 ... 100 Continuous focus motion. Positive values mean focus far and negative values mean focus near. 0 means stop.
        continuousirismove=<int> -100 ... 100 Continuous iris motion. Positive values mean iris open and negative values mean iris close. 0 means stop.
        continuousbrightnessmove=<int> -100 ... 100 Continuous brightness motion. Positive values mean brighter image and negative values mean darker image. 0 means stop.
        auxiliary=<string> <function name> Activates/deactivates auxiliary functions of the device where <function name> is the name of the device specific function. Check in driver's documentation or in response to info=1 for information about <function name>.
        gotoserverpresetname=<string> <preset name>(6) Move to the position associated with the <preset name>.
        gotoserverpresetno=<int> 1, ...(6) Move to the position associated with the specified preset position number.
        gotodevicepreset=<int> <preset pos>(6) Bypasses the presetpos interface and tells the device to go directly to the preset position number <preset pos> stored in the device, where the <preset pos> is a device-specific preset position number. This may also be a device-specific special function.
        speed=<int> 1 ... 100 Sets the move speed of pan and tilt.
        imagerotation=<int> 0, 90, 180, 270 If PTZ command refers to an image stream that is rotated differently than the current image setup, then the image stream rotation must be added to each command with this argument to allow the Axis product to compensate.
            0 = Rotate the image 0 degrees.
            90 = Rotate the image 90 degrees.
            180 = Rotate the image 180 degrees.
            270 = Rotate the image 270 degrees.
        ircutfilter=<string> auto on,off Control the IR cut filter.
            auto = Automatically switch between on and off depending on the lighting conditions.
            on = Apply the filter, that is block IR light.
            off = Remove the filter, that is allow IR light to reach the image sensor.
        backlight=<string> on/off Control the backlight compensation.
            on = Bright mode.
            off = Normal mode.
        """
        data = {}
        if camera:
            data["camera"] = camera
        if center:
            x, y = center
            data["center"] = f"{x},{y}"
        if areazoom:
            x, y, z = areazoom
            if z < 1:
                z = 1
            data["areazoom"] = f"{x},{y},{z}"
        if center or areazoom:
            if imagewidth:
                data["imagewidth"] = imagewidth
            if imageheight:
                data["imageheight"] = imageheight

        for key, value, minimum, maximum in (
            ("pan", pan, -180, 180),
            ("tilt", tilt, -180, 180),
            ("zoom", zoom, 1, 9999),
            ("focus", focus, 1, 9999),
            ("iris", iris, 1, 9999),
            ("brightness", brightness, 1, 9999),
            ("rpan", rpan, -360, 360),
            ("rtilt", rtilt, -360, 360),
            ("rzoom", rzoom, -9999, 9999),
            ("rfocus", rfocus, -9999, 9999),
            ("riris", riris, -9999, 9999),
            ("rbrightness", rbrightness, -9999, 9999),
            ("continuouszoommove", continuouszoommove, -100, 100),
            ("continuousfocusmove", continuousfocusmove, -100, 100),
            ("continuousirismove", continuousirismove, -100, 100),
            ("continuousbrightnessmove", continuousbrightnessmove, -100, 100),
            ("speed", speed, 1, 100),
        ):
            if value is not None:
                data[key] = limit(value, minimum, maximum)

        for key, value, supported_commands in (
            ("autofocus", autofocus, (ON, OFF)),
            ("autoiris", autoiris, (ON, OFF)),
            ("backlight", backlight, (ON, OFF)),
            ("ircutfilter", ircutfilter, (AUTO, ON, OFF)),
            ("imagerotation", imagerotation, (0, 90, 180, 270)),
            ("move", move, SUPPORTED_MOVES),
        ):
            if value in supported_commands:
                data[key] = value

        if continuouspantiltmove:
            pan_speed, tilt_speed = continuouspantiltmove
            pan_speed = limit(pan_speed, -100, 100)
            tilt_speed = limit(tilt_speed, -100, 100)
            data["continuouspantiltmove"] = f"{pan_speed},{tilt_speed}"
        if auxiliary:
            data["auxiliary"] = auxiliary
        if gotoserverpresetname:
            data["gotoserverpresetname"] = gotoserverpresetname
        if gotoserverpresetno:
            data["gotoserverpresetno"] = gotoserverpresetno
        if gotodevicepreset:
            data["gotodevicepreset"] = gotodevicepreset

        if len(data) == 0 or (len(data) == 1 and "camera" in data):
            return

        return await self._request("post", URL, data=data)

    async def query(self, query: str) -> str:
        """Returns the current status.

        limits = PTZ limits for the Axis product.
        mode = Products with Panopsis technology: The current mode (overview or normal).
        position = Values for current position.
        presetposall = Current preset positions for all video channels.
        presetposcam = Current preset positions for a video channel.
        presetposcamdata = Returns the configured preset positions with position data measured in degrees.
        speed = Values for pan/tilt speed.
        """
        if query not in SUPPORTED_QUERIES:
            return
        return await self._request("post", URL, data={"query": query})

    async def configured_device_driver(self) -> str:
        """Name of the system-configured device driver."""
        return await self._request("post", URL, data={"whoami": 1})

    async def available_ptz_commands(self) -> str:
        """Description of available PTZ commands."""
        return await self._request("post", URL, data={"info": 1})
