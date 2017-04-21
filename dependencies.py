import os, pkgutil, site

if pkgutil.find_loader("gi"):
    try:
        import gi
        print('Found gi:', os.path.abspath(gi.__file__))
        gi.require_version('Gst', '1.0')
        # from gi.repository import GLib, Gst
    except ValueError:
        print('Couldn\'t find Gst')
        print('Please run \'sudo apt-get install gir1.2-gstreamer-1.0\'')
    print('Environment seems to be ok.')
else:
    print('No gi installed', '\n',
          'Please run \'sudo apt-get install python3-gi\'',
          '\n',
          'A virtual environment might need extra actions like symlinking, ',
          '\n',
          'you might need to do a symlink looking similar to this:',
          '\n',
          'ln -s /usr/lib/python3/dist-packages/gi ',
          '/srv/homeassistant/lib/python3.4/site-packages',
          '\n',
          'run this script inside and outside of the virtual environment to find the paths needed')
    print(site.getsitepackages())