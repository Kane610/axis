"""Setup for Axis."""

# https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
# http://peterdowns.com/posts/first-time-with-pypi.html
# pip install -e .
# Upload to PyPI Live
# python setup.py sdist bdist_wheel
# twine upload dist/axis-* --skip-existing

from setuptools import setup

setup(
  name='axis',
  packages=['axis'],
  version='23',
  description='A Python library for communicating with devices from Axis Communications',
  author='Robert Svensson',
  author_email='Kane610@users.noreply.github.com',
  license='MIT',
  url='https://github.com/Kane610/axis',
  download_url='https://github.com/Kane610/axis/archive/v23.tar.gz',
  install_requires=['requests'],
  keywords=['axis', 'vapix', 'onvif', 'event stream', 'homeassistant'],
  classifiers=[],
)
