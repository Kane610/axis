"""Setup for Axis."""

from setuptools import find_packages, setup

MIN_PY_VERSION = "3.11"
PACKAGES = find_packages(exclude=["tests", "tests.*"])
VERSION = "58"

setup(
    name="axis",
    packages=PACKAGES,
    package_data={"axis": ["py.typed"]},
    version=VERSION,
    description="A Python library for communicating with devices from Axis Communications",
    author="Robert Svensson",
    author_email="Kane610@users.noreply.github.com",
    license="MIT",
    url="https://github.com/Kane610/axis",
    download_url=f"https://github.com/Kane610/axis/archive/v{VERSION}.tar.gz",
    install_requires=["async_timeout", "attrs", "httpx", "packaging", "xmltodict"],
    tests_require=["pytest", "pytest-asyncio", "respx"],
    keywords=["axis", "vapix", "onvif", "event stream", "homeassistant"],
    classifiers=["Natural Language :: English", "Programming Language :: Python :: 3"],
    python_requires=f">={MIN_PY_VERSION}",
)
