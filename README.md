

sudo apt-get install python3-gst-1.0 \
    gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0 \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly \
    gstreamer1.0-tools

sudo apt-get install python-gobject

sudo apt install python3-gi

ln -s /usr/lib/python3/dist-packages/gi
    /srv/homeassistant/lib/python3.4/site-packages

A good example of making a minimal Python package is this repo:
https://github.com/miniconfig/python-openevse-wifi/