"""Test Axis user management.

pytest --cov-report term-missing --cov=axis.pwdgrp_cgi tests/test_pwdgrp_cgi.py
"""

from unittest.mock import MagicMock, Mock, patch
import pytest

from axis.pwdgrp_cgi import Users, User


def test_users():
    """Verify that you can list users."""
    mock_request = Mock()
    users = Users(fixture2, mock_request)
    print(users.__dict__)
    assert False


fixture2 = {
    'actionengined': '""\r',
    'anonymous': '""\r',
    'bin': '""\r',
    'operator': '"operator,sdk,wwwo,wwwaovp,wwwaop,wwwao,wwwop,wwwaov,wwwov,wwwovp,root"\r',
    'ptz': '"wwwop,wwwaop,wwwaovp,wwwap,wwwp,wwwovp,root,wwwvp,wwwavp"\r',
    'root': '""\r',
    'users': '"viewer,operator"\r',
    'viewer': '"operator,sdk,wwwaovp,wwwaov,wwwov,wwwovp,wwwav,root,viewer,wwwv,wwwavp,wwwvp"\r',
    'digusers': '"root,operator,viewer"\r'
}




fixture = """actionengined=""
addon=""
addonexample="addonexample"
addonmanagerconf="addonmanagerconf"
adm=""
admin="wwwa,wwwaop,wwwaovp,wwwao,wwwap,wwwaov,root,wwwav,wwwavp"
ambad=""
anonymous=""
api-discovery=""
audio="streamer,sdk,audiocontrol"
audioapi=""
audiocontrol=""
axisns=""
backup=""
basic-device-info=""
bin=""
bw=""
capturemoded=""
cdrom=""
cert="sdk,streamer,actionengined,wsd"
confcached=""
confloggerd="confloggerd"
crypto="stclient,www"
daemon=""
datacollectiond=""
depd="depd"
dialout=""
dip=""
disk="axisns,motion,actionengined,tampering,ptzadm,light,streamer,imaged"
diskmanager=""
environment="environment"
event="event,triggerd,streamer,actionengined"
eventbridged="eventbridged"
eventconsumerd="eventconsumerd"
eventproducerd="eventproducerd"
fax=""
floppy=""
games=""
gnats=""
gpio="environment,actionengined,led,mediaclipcgi,iod,scheduled,ptzadm,light,streamer,imaged"
gtourd=""
httpwdd="httpwdd"
iiodevices="actionengined,ptzadm"
imaged=""
input=""
iod=""
irc=""
kmem=""
led="led"
legacymappings="imaged,ptzadm,audiocontrol,iod"
licensekey-manager="licensekey-manager"
light=""
list=""
lldpd=""
lock=""
lp=""
mail=""
man=""
messagebus=""
metadata="streamer"
motion=""
netd=""
netdev=""
news=""
nogroup=""
ntp=""
ntpconfd=""
onscreencontrols=""
operator="operator,sdk,wwwo,wwwaovp,wwwaop,wwwao,wwwop,wwwaov,wwwov,wwwovp,root"
overlay="streamer"
plugdev=""
power="power"
product-info=""
proxy=""
ptod="ptod"
ptz="wwwop,wwwaop,wwwaovp,wwwap,wwwp,wwwovp,root,wwwvp,wwwavp"
ptzadm="sdk"
pwauth="www"
rendezvous=""
root=""
ruleengined=""
sasl=""
scheduled=""
sdk="sdk"
service_registry="ptzadm,iod"
sessioncgi="sessioncgi"
shadow="www,streamer"
shutdown=""
snmpd=""
src=""
sshd=""
staff=""
statuscollectiond="statuscollectiond"
stclient=""
storage-stability-helper="storage-stability-helper"
storage="wsd,streamer,actionengined,sdk"
streamer="storage,www,mediaclipcgi,sdk"
sudo=""
sys=""
systemd-bus-proxy=""
systemd-journal=""
systemmanager=""
tampering=""
tape=""
template="environment,ptzadm"
triggerd=""
tty="imaged,scheduled,ptzadm"
upnp=""
users="viewer,operator"
utmp="streamer"
uucp=""
vdn=""
video-scene-manager=""
video-service-legacy=""
video="environment,motion,tampering,sdk,ptod,ambad,ptzadm,vision-devices,streamer,vdn,imaged"
videoapi=""
viewer="operator,sdk,wwwaovp,wwwaov,wwwov,wwwovp,wwwav,root,viewer,wwwv,wwwavp,wwwvp"
virtualinputd="virtualinputd"
vision-devices=""
voice=""
wsauth="scheduled,streamer,wsd"
wsd="wsdd,scheduled"
wsdd=""
www-data=""
www=""
digusers="root,operator,viewer"
"""
