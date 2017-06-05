import os
import pkgutil
import site
from sys import exit

if pkgutil.find_loader('gi'):
    try:
        import gi
        print("Found gi at:", os.path.abspath(gi.__file__))
        gi.require_version('Gst', '1.0')
        # from gi.repository import Gst
    except ValueError:
        print("Couldn\'t find Gst",
              '\n',
              "Please run \'sudo apt-get install gir1.2-gstreamer-1.0\'")
        exit(False)
    print("Environment seems to be ok.")
else:
    print("No gi available in this environment",
          '\n',
          "Please run \'sudo apt-get install python3-gi\'",
          '\n',
          "A virtual environment might need extra actions like symlinking,",
          '\n',
          "you might need to do a symlink looking similar to this:",
          '\n',
          "ln -s /usr/lib/python3/dist-packages/gi",
          "/srv/homeassistant/lib/python3.4/site-packages",
          '\n',
          "run this script inside and outside of the virtual environment",
          "to find the paths needed")
    print(site.getsitepackages())
