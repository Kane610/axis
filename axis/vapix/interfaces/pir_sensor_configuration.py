"""PIR sensor configuration api.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""
from ..models.api_discovery import ApiId
from ..models.pir_sensor_configuration import ListSensorsRequest, PirSensorConfiguration
from .api_handler import ApiHandler


class PirSensorConfigurationHandler(ApiHandler[PirSensorConfiguration]):
    """PIR sensor configuration for Axis devices."""

    api_id = ApiId.PIR_SENSOR_CONFIGURATION
    api_request = ListSensorsRequest.create()
