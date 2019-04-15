"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

import pytest
from unittest.mock import Mock, patch

from axis.vapix import Vapix


def test_initialize_params():
    """Verify that you can list parameters."""
    mock_config = Mock()
    mock_config.host = 'mock_host'
    mock_config.url = 'mock_url'
    mock_config.session.get = 'mock_get'

    with patch('axis.vapix.session_request', return_value='key=value') as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_params()

    mock_request.assert_called_with(
        'mock_get', 'mock_url/axis-cgi/param.cgi?action=list')
    assert vapix.params['key'].raw == 'value'


def test_initialize_params_no_data():
    """Verify that you can list parameters."""
    mock_config = Mock()
    mock_config.host = 'mock_host'

    with patch('axis.vapix.session_request', return_value='key=value') as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_params(preload_data=False)

    mock_request.assert_not_called


def test_initialize_users():
    """Verify that you can list parameters."""
    mock_config = Mock()
    mock_config.host = 'mock_host'
    mock_config.url = 'mock_url'
    mock_config.session.get = 'mock_get'

    with patch('axis.vapix.session_request', return_value="""users="userv"
viewer="userv"
operator="usera"
admin="usera"
ptz=
""") as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_users()

    mock_request.assert_called_with(
        'mock_get', 'mock_url/axis-cgi/pwdgrp.cgi?action=get')
    assert vapix.users['userv'].viewer