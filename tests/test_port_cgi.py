"""Test Axis parameter management.

pytest --cov-report term-missing --cov=axis.port_cgi tests/test_port_cgi.py
"""

import pytest
from unittest.mock import Mock

# from axis.port_cgi import BRAND, PROPERTIES, Ports