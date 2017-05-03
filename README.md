Python project to set up a connection towards Axis Communications devices and to subscribe to specific events on the metadatastream.

Dependencies:

sudo apt-get install python3-gi
sudo apt-get install gir1.2-gstreamer-1.0

Depending on your environment you might need to symlink the `gi` module for python to find it. For help you can run dependencies.py to test the environment and get pointers as to what is wrong.

ln -s /usr/lib/python3/dist-packages/gi /srv/homeassistant/lib/python3.4/site-packages
