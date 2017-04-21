from axis.stream import MetaDataStream
import time

username = 'root'
password = 'pass'
url = '10.0.1.50'
video = 0
audio = 0
event_topics = 'onvif:VideoAnalytics/axis:MotionDetection'

rtsp = "rtsp://{0}:{1}@{2}/axis-media/media.amp?".format(username,
                                                         password,
                                                         url)
source = 'video={0}&audio={1}&even=on&eventtopic={2}'.format(video,
                                                             audio,
                                                             event_topics)
metadata_url = rtsp + source


def stream_signal():
    global metadatastream
    print(metadatastream.data)


metadatastream = MetaDataStream(metadata_url)
metadatastream.signal_parent = stream_signal

metadatastream.start()
time.sleep(10)
metadatastream.stop()
