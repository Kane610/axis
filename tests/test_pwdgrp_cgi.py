"""Test Axis user management.

pytest --cov-report term-missing --cov=axis.pwdgrp_cgi tests/test_pwdgrp_cgi.py
"""

from unittest.mock import MagicMock, Mock, patch
import pytest

from axis.pwdgrp_cgi import SGRP_ADMIN, Users, User


def test_users():
    """Verify that you can list users."""
    mock_request = Mock()
    users = Users(fixture2, mock_request)

    assert users['userv']
    assert users['userv'].viewer
    assert not users['userv'].operator
    assert not users['userv'].admin
    assert not users['userv'].ptz

    assert users['usero']
    assert users['usero'].viewer
    assert users['usero'].operator
    assert not users['usero'].admin
    assert not users['usero'].ptz

    assert users['usera']
    assert users['usera'].viewer
    assert users['usera'].operator
    assert users['usera'].admin
    assert users['usera'].ptz


def test_create():
    """Verify that you can create users."""
    mock_request = Mock()
    users = Users(fixture2, mock_request)

    users.create('joe', pwd='abcd', sgrp=SGRP_ADMIN)
    mock_request.assert_called_with('get', '/axis-cgi/pwdgrp.cgi?action=add&grp=users&user=joe&pwd=abcd&sgrp=viewer:operator:admin')

    users.create('joe', pwd='abcd', sgrp=SGRP_ADMIN, comment='comment')
    mock_request.assert_called_with('get', '/axis-cgi/pwdgrp.cgi?action=add&grp=users&user=joe&pwd=abcd&sgrp=viewer:operator:admin&comment=comment')


def test_modify():
    """Verify that you can modify users."""
    mock_request = Mock()
    users = Users(fixture2, mock_request)

    users.modify('joe', pwd='abcd')
    mock_request.assert_called_with('get', '/axis-cgi/pwdgrp.cgi?action=update&user=joe&pwd=abcd')

    users.modify('joe', sgrp=SGRP_ADMIN)
    mock_request.assert_called_with('get', '/axis-cgi/pwdgrp.cgi?action=update&user=joe&sgrp=viewer:operator:admin')

    users.modify('joe', comment='comment')
    mock_request.assert_called_with('get', '/axis-cgi/pwdgrp.cgi?action=update&user=joe&comment=comment')

    users.modify('joe', pwd='abcd', sgrp=SGRP_ADMIN, comment='comment')
    mock_request.assert_called_with('get', '/axis-cgi/pwdgrp.cgi?action=update&user=joe&pwd=abcd&sgrp=viewer:operator:admin&comment=comment')


def test_delete():
    """Verify that you can delete users."""
    mock_request = Mock()
    users = Users(fixture2, mock_request)
    users.delete('joe')

    mock_request.assert_called_with('get', '/axis-cgi/pwdgrp.cgi?action=remove&user=joe')


fixture2 = {
    'actionengined': '""\r',
    'admin': 'usera,wwwa,wwwaop,wwwaovp,wwwao,wwwap,wwwaov,root,wwwav,wwwavp',
    'anonymous': '""\r',
    'bin': '""\r',
    'operator': '"usera,usero,sdk,wwwo,wwwaovp,wwwaop,wwwao,wwwop,wwwaov,wwwov,wwwovp,root"\r',
    'ptz': '"usera,wwwop,wwwaop,wwwaovp,wwwap,wwwp,wwwovp,root,wwwvp,wwwavp"\r',
    'root': '""\r',
    'users': '"userv,usero,usera"\r',
    'viewer': '"sdk,wwwaovp,wwwaov,wwwov,wwwovp,wwwav,root,usera,usero,userv,wwwv,wwwavp,wwwvp"\r',
    'digusers': '"root,usero,userv"\r'
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
