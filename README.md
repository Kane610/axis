sudo apt-get install python3-gi
sudo apt-get install gir1.2-gstreamer-1.0

ln -s /usr/lib/python3/dist-packages/gi
    /srv/homeassistant/lib/python3.4/site-packages

Run dependencies.py to test the environment