"""Setup for Axis."""

from setuptools import find_packages, setup

setup(
    name="axis",
    packages=find_packages(include=["axis", "axis.*"]),
    version="35",
    description="A Python library for communicating with devices from Axis Communications",
    author="Robert Svensson",
    author_email="Kane610@users.noreply.github.com",
    license="MIT",
    url="https://github.com/Kane610/axis",
    download_url="https://github.com/Kane610/axis/archive/v35.tar.gz",
    install_requires=["attrs", "requests", "xmltodict"],
    keywords=["axis", "vapix", "onvif", "event stream", "homeassistant"],
    classifiers=["Natural Language :: English", "Programming Language :: Python :: 3"],
)
