"""Test Axis parameter management.

pytest --cov-report term-missing --cov=axis.port_cgi tests/test_port_cgi.py
"""

import pytest
from unittest.mock import Mock

# from axis.port_cgi import BRAND, PROPERTIES, Ports
from axis.port_cgi import Port

def test_port():
    mock_request = Mock()
    raw = {
            'Direction': 'output'
    }
    port = Port('0', raw, mock_request)
    port.action('/')
    mock_request.assert_called_with(
        'get', '/axis-cgi/io/port.cgi?action=1%3A%2F')


        #     await hass.async_add_executor_job(
        #         device.vapix.params.update_ports)
        # print(device.vapix.params.ports)
