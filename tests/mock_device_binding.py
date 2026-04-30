"""Shared device binding helpers for test HTTP mock servers."""


def bind_device_port(device: object, port: int) -> None:
    """Bind a mock server port to supported Axis test objects.

    Supports AxisDevice, Vapix, and ApiHandler-style objects.
    """
    if hasattr(device, "vapix"):
        device.vapix.device.config.port = port
        return
    if hasattr(device, "device"):
        device.device.config.port = port
        return
    if hasattr(device, "config"):
        device.config.port = port
        return
    msg = f"Unsupported device type for mock binding: {type(device).__name__}"
    raise TypeError(msg)
