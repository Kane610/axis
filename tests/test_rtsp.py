"""Test RTSP client.

pytest --cov-report term-missing --cov=axis.rtsp tests/test_rtsp.py
"""

from unittest.mock import Mock, patch

from axis.rtsp import (
    RTSPClient,
    STATE_PLAYING,
    STATE_STARTING,
    STATE_STOPPED,
    TIME_OUT_LIMIT,
)
import pytest


@pytest.fixture
def rtsp_client(axis_device) -> RTSPClient:
    """Return the RTSP client."""
    axis_device.enable_events(event_callback=Mock())
    with patch("axis.rtsp.asyncio.get_running_loop"), patch(
        "axis.rtsp.socket"
    ) as mock_socket:
        mock_socket.socket.return_value.getsockname.return_value = ["", 45678]
        axis_device.stream.start()
    return axis_device.stream.stream


async def test_rtsp(rtsp_client):
    """Test successful setup and teardown of RTSP client."""
    rtsp_client.loop.create_connection.assert_called()
    assert len(rtsp_client.loop.call_later.call_args_list) == 0

    assert (
        rtsp_client.session.url
        == "rtsp://host/axis-media/media.amp?video=0&audio=0&event=on"
    )
    assert rtsp_client.session.host == "host"
    assert rtsp_client.session.port == 554
    assert rtsp_client.session.username == "root"
    assert rtsp_client.session.password == "pass"
    assert rtsp_client.session.user_agent == "HASS Axis"
    assert rtsp_client.session.rtp_port == 45678
    assert rtsp_client.session.rtcp_port == 45679
    assert rtsp_client.session.methods == [
        "OPTIONS",
        "DESCRIBE",
        "SETUP",
        "PLAY",
        "KEEP-ALIVE",
        "TEARDOWN",
    ]

    assert rtsp_client.session.sequence == 0
    assert rtsp_client.session.basic_auth is None
    assert rtsp_client.session.rtsp_version is None
    assert rtsp_client.session.status_code is None
    assert rtsp_client.session.status_text is None
    assert rtsp_client.session.sequence_ack is None
    assert rtsp_client.session.date is None
    assert rtsp_client.session.methods_ack is None
    assert rtsp_client.session.basic is False
    assert rtsp_client.session.digest is False
    assert rtsp_client.session.realm is None
    assert rtsp_client.session.nonce is None
    assert rtsp_client.session.stale is None
    assert rtsp_client.session.content_type is None
    assert rtsp_client.session.content_base is None
    assert rtsp_client.session.content_length is None
    assert rtsp_client.session.session_id is None
    assert rtsp_client.session.session_timeout == 0
    assert rtsp_client.session.transport_ack is None
    assert rtsp_client.session.range is None
    assert rtsp_client.session.rtp_info is None
    assert rtsp_client.session.sdp is None
    assert rtsp_client.session.control_url is None

    # Verify connection_made method
    transport = Mock()
    rtsp_client.connection_made(transport)
    assert rtsp_client.time_out_handle
    assert len(rtsp_client.loop.call_later.call_args_list) == 1
    rtsp_client.loop.call_later.assert_called_with(TIME_OUT_LIMIT, rtsp_client.time_out)

    # OPTIONS ask server to show what options it supports
    transport.write.assert_called_with(
        b"OPTIONS "
        + b"rtsp://host/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        + b"CSeq: 0\r\n"
        + b"User-Agent: HASS Axis\r\n\r\n"
    )

    # Response to OPTIONS
    rtsp_client.data_received(
        b"RTSP/1.0 200 OK\r\n"
        + b"CSeq: 0\r\n"
        + b"Public: OPTIONS, DESCRIBE, ANNOUNCE, GET_PARAMETER, PAUSE, PLAY, RECORD, SETUP, SET_PARAMETER, TEARDOWN\r\n"
        + b"Server: GStreamer RTSP server\r\n"
        + b"Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n"
    )
    assert len(rtsp_client.loop.call_later.call_args_list) == 2

    assert rtsp_client.session.sequence == 1
    assert rtsp_client.session.basic_auth is None
    assert rtsp_client.session.status_code == 200
    assert rtsp_client.session.status_text == "OK"
    assert rtsp_client.session.sequence_ack == 0
    assert rtsp_client.session.date == "Sat, 12 Dec 2020 10:44:25 GMT"
    assert rtsp_client.session.methods_ack == [
        "OPTIONS",
        "DESCRIBE",
        "ANNOUNCE",
        "GET_PARAMETER",
        "PAUSE",
        "PLAY",
        "RECORD",
        "SETUP",
        "SET_PARAMETER",
        "TEARDOWN",
    ]
    assert rtsp_client.session.basic is False
    assert rtsp_client.session.digest is False
    assert rtsp_client.session.realm is None
    assert rtsp_client.session.nonce is None
    assert rtsp_client.session.stale is None
    assert rtsp_client.session.content_type is None
    assert rtsp_client.session.content_base is None
    assert rtsp_client.session.content_length is None
    assert rtsp_client.session.session_id is None
    assert rtsp_client.session.session_timeout == 0
    assert rtsp_client.session.transport_ack is None
    assert rtsp_client.session.range is None
    assert rtsp_client.session.rtp_info is None
    assert rtsp_client.session.sdp is None
    assert rtsp_client.session.control_url is None

    # DESCRIBE ask server what it provides
    transport.write.assert_called_with(
        b"DESCRIBE "
        + b"rtsp://host/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        + b"CSeq: 1\r\n"
        + b"User-Agent: HASS Axis\r\n"
        + b"Accept: application/sdp\r\n\r\n"
    )

    # Response to unauthorized DESCRIBE
    rtsp_client.data_received(
        b"RTSP/1.0 401 Unauthorized\r\n"
        + b"CSeq: 1\r\n"
        + b'WWW-Authenticate: Digest realm="AXIS_ACCC8E012345", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", stale=FALSE\r\n'
        + b"Server: GStreamer RTSP server\r\n "
        + b"Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n"
    )
    assert len(rtsp_client.loop.call_later.call_args_list) == 3

    assert rtsp_client.session.sequence == 1
    assert rtsp_client.session.status_code == 401
    assert rtsp_client.session.status_text == "Unauthorized"
    assert rtsp_client.session.sequence_ack == 1
    assert rtsp_client.session.date == "Sat, 12 Dec 2020 10:44:25 GMT"
    assert rtsp_client.session.basic is False
    assert rtsp_client.session.digest is True
    assert rtsp_client.session.realm == "AXIS_ACCC8E012345"
    assert (
        rtsp_client.session.nonce == "0000eb57Y1462133062b37999f0cd530f02755fa37b8df1"
    )
    assert rtsp_client.session.stale is False
    assert rtsp_client.session.content_type is None
    assert rtsp_client.session.content_base is None
    assert rtsp_client.session.content_length is None
    assert rtsp_client.session.session_id is None
    assert rtsp_client.session.session_timeout == 0
    assert rtsp_client.session.transport_ack is None
    assert rtsp_client.session.range is None
    assert rtsp_client.session.rtp_info is None
    assert rtsp_client.session.sdp is None
    assert rtsp_client.session.control_url is None

    # DESCRIBE with digest authentication
    transport.write.assert_called_with(
        b"DESCRIBE "
        + b"rtsp://host/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        + b"CSeq: 1\r\n"
        + b'Authorization: Digest username="root", realm="AXIS_ACCC8E012345", algorithm="MD5", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", uri="rtsp://host/axis-media/media.amp?video=0&audio=0&event=on", response="8308595ec4e96675b99c54088ae6c2c4"\r\n'
        + b"User-Agent: HASS Axis\r\nAccept: application/sdp\r\n\r\n"
    )

    # Response to DESCRIBE
    rtsp_client.data_received(
        b"RTSP/1.0 200 OK\r\n"
        + b"CSeq: 1\r\n"
        + b"Content-Type: application/sdp\r\n"
        + b"Content-Base: rtsp://host/axis-media/media.amp/\r\n"
        + b"Server: GStreamer RTSP server\r\n"
        + b"Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n"
        + b"Content-Length: 440\r\n\r\n"
        + b"v=0\r\n"
        + b"o=- 18302136002250915122 1 IN IP4 host\r\n"
        + b"s=Session streamed with GStreamer\r\n"
        + b"i=rtsp-server\r\n"
        + b"t=0 0\r\n"
        + b"a=tool:GStreamer\r\n"
        + b"a=type:broadcast\r\n"
        + b"a=range:npt=now-\r\n"
        + b"a=control:rtsp://host/axis-media/media.amp?video=0&audio=0&event=on\r\n"
        + b"m=application 0 RTP/AVP 98\r\n"
        + b"c=IN IP4 0.0.0.0\r\n"
        + b"a=rtpmap:98 vnd.onvif.metadata/90000\r\n"
        + b"a=ts-refclk:local\r\n"
        + b"a=mediaclk:sender\r\n"
        + b"a=control:rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on\r\n"
    )
    assert len(rtsp_client.loop.call_later.call_args_list) == 4

    assert rtsp_client.session.sequence == 2
    assert rtsp_client.session.basic_auth is None
    assert rtsp_client.session.status_code == 200
    assert rtsp_client.session.status_text == "OK"
    assert rtsp_client.session.sequence_ack == 1
    assert rtsp_client.session.date == "Sat, 12 Dec 2020 10:44:25 GMT"
    assert rtsp_client.session.basic is False
    assert rtsp_client.session.digest is True
    assert rtsp_client.session.realm == "AXIS_ACCC8E012345"
    assert (
        rtsp_client.session.nonce == "0000eb57Y1462133062b37999f0cd530f02755fa37b8df1"
    )
    assert rtsp_client.session.stale is False
    assert rtsp_client.session.content_type == "application/sdp"
    assert rtsp_client.session.content_base == "rtsp://host/axis-media/media.amp/"
    assert rtsp_client.session.content_length == 440
    assert rtsp_client.session.session_id is None
    assert rtsp_client.session.session_timeout == 0
    assert rtsp_client.session.transport_ack is None
    assert rtsp_client.session.range is None
    assert rtsp_client.session.rtp_info is None
    assert rtsp_client.session.sdp == [
        "v=0",
        "o=- 18302136002250915122 1 IN IP4 host",
        "s=Session streamed with GStreamer",
        "i=rtsp-server",
        "t=0 0",
        "a=tool:GStreamer",
        "a=type:broadcast",
        "a=range:npt=now-",
        "a=control:rtsp://host/axis-media/media.amp?video=0&audio=0&event=on",
        "m=application 0 RTP/AVP 98",
        "c=IN IP4 0.0.0.0",
        "a=rtpmap:98 vnd.onvif.metadata/90000",
        "a=ts-refclk:local",
        "a=mediaclk:sender",
        "a=control:rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on",
    ]
    assert (
        rtsp_client.session.control_url
        == "rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on"
    )

    # SETUP setup rtp connection to server
    transport.write.assert_called_with(
        b"SETUP "
        + b"rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on RTSP/1.0\r\n"
        + b"CSeq: 2\r\n"
        + b'Authorization: Digest username="root", realm="AXIS_ACCC8E012345", algorithm="MD5", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", uri="rtsp://host/axis-media/media.amp?video=0&audio=0&event=on", response="1a00f47fd07f7503b6b2672e7e082d84"\r\n'
        + b"User-Agent: HASS Axis\r\n"
        + b"Transport: RTP/AVP;unicast;client_port=45678-45679\r\n\r\n"
    )

    # Response to SETUP
    rtsp_client.data_received(
        b"RTSP/1.0 200 OK\r\n"
        + b"CSeq: 2\r\n"
        + b'Transport: RTP/AVP;unicast;client_port=45678-45679;server_port=50000-50001;ssrc=315460DA;mode="PLAY"\r\n'
        + b"Server: GStreamer RTSP server\r\n"
        + b"Session: ghLlkf_I9pCBP24t;timeout=60\r\n"
        + b"Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n"
    )
    assert len(rtsp_client.loop.call_later.call_args_list) == 5

    assert rtsp_client.session.sequence == 3
    assert rtsp_client.session.basic_auth is None
    assert rtsp_client.session.status_code == 200
    assert rtsp_client.session.status_text == "OK"
    assert rtsp_client.session.sequence_ack == 2
    assert rtsp_client.session.date == "Sat, 12 Dec 2020 10:44:25 GMT"
    assert rtsp_client.session.basic is False
    assert rtsp_client.session.digest is True
    assert rtsp_client.session.realm == "AXIS_ACCC8E012345"
    assert (
        rtsp_client.session.nonce == "0000eb57Y1462133062b37999f0cd530f02755fa37b8df1"
    )
    assert rtsp_client.session.stale is False
    assert rtsp_client.session.content_type == "application/sdp"
    assert rtsp_client.session.content_base == "rtsp://host/axis-media/media.amp/"
    assert rtsp_client.session.content_length == 440
    assert rtsp_client.session.session_id == "ghLlkf_I9pCBP24t"
    assert rtsp_client.session.session_timeout == 60
    assert (
        rtsp_client.session.transport_ack
        == 'RTP/AVP;unicast;client_port=45678-45679;server_port=50000-50001;ssrc=315460DA;mode="PLAY"'
    )
    assert rtsp_client.session.range is None
    assert rtsp_client.session.rtp_info is None
    assert rtsp_client.session.sdp == [
        "v=0",
        "o=- 18302136002250915122 1 IN IP4 host",
        "s=Session streamed with GStreamer",
        "i=rtsp-server",
        "t=0 0",
        "a=tool:GStreamer",
        "a=type:broadcast",
        "a=range:npt=now-",
        "a=control:rtsp://host/axis-media/media.amp?video=0&audio=0&event=on",
        "m=application 0 RTP/AVP 98",
        "c=IN IP4 0.0.0.0",
        "a=rtpmap:98 vnd.onvif.metadata/90000",
        "a=ts-refclk:local",
        "a=mediaclk:sender",
        "a=control:rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on",
    ]
    assert (
        rtsp_client.session.control_url
        == "rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on"
    )

    # PLAY start stream
    transport.write.assert_called_with(
        b"PLAY "
        + b"rtsp://host/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        + b"CSeq: 3\r\n"
        + b'Authorization: Digest username="root", realm="AXIS_ACCC8E012345", algorithm="MD5", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", uri="rtsp://host/axis-media/media.amp?video=0&audio=0&event=on", response="6fdcc7fc66019389f50d3b4e72796bf0"\r\n'
        + b"User-Agent: HASS Axis\r\n"
        + b"Session: ghLlkf_I9pCBP24t\r\n\r\n"
    )

    # Response to PLAY
    rtsp_client.data_received(
        b"RTSP/1.0 200 OK\r\n"
        + b"CSeq: 3\r\n"
        + b"RTP-Info: url=rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on;seq=13114;rtptime=3803548519\r\n"
        + b"Range: npt=now-\r\n"
        + b"Server: GStreamer RTSP server\r\n"
        + b"Session: ghLlkf_I9pCBP24t;timeout=60\r\n"
        + b"Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n"
    )
    assert len(rtsp_client.loop.call_later.call_args_list) == 6

    assert rtsp_client.session.sequence == 4
    assert rtsp_client.session.basic_auth is None
    assert rtsp_client.session.status_code == 200
    assert rtsp_client.session.status_text == "OK"
    assert rtsp_client.session.sequence_ack == 3
    assert rtsp_client.session.date == "Sat, 12 Dec 2020 10:44:25 GMT"
    assert rtsp_client.session.basic is False
    assert rtsp_client.session.digest is True
    assert rtsp_client.session.realm == "AXIS_ACCC8E012345"
    assert (
        rtsp_client.session.nonce == "0000eb57Y1462133062b37999f0cd530f02755fa37b8df1"
    )
    assert rtsp_client.session.stale is False
    assert rtsp_client.session.content_type == "application/sdp"
    assert rtsp_client.session.content_base == "rtsp://host/axis-media/media.amp/"
    assert rtsp_client.session.content_length == 440
    assert rtsp_client.session.session_id == "ghLlkf_I9pCBP24t"
    assert rtsp_client.session.session_timeout == 60
    assert (
        rtsp_client.session.transport_ack
        == 'RTP/AVP;unicast;client_port=45678-45679;server_port=50000-50001;ssrc=315460DA;mode="PLAY"'
    )
    assert rtsp_client.session.range == "npt=now-"
    assert (
        rtsp_client.session.rtp_info
        == "url=rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on;seq=13114;rtptime=3803548519"
    )
    assert rtsp_client.session.sdp == [
        "v=0",
        "o=- 18302136002250915122 1 IN IP4 host",
        "s=Session streamed with GStreamer",
        "i=rtsp-server",
        "t=0 0",
        "a=tool:GStreamer",
        "a=type:broadcast",
        "a=range:npt=now-",
        "a=control:rtsp://host/axis-media/media.amp?video=0&audio=0&event=on",
        "m=application 0 RTP/AVP 98",
        "c=IN IP4 0.0.0.0",
        "a=rtpmap:98 vnd.onvif.metadata/90000",
        "a=ts-refclk:local",
        "a=mediaclk:sender",
        "a=control:rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on",
    ]
    assert (
        rtsp_client.session.control_url
        == "rtsp://host/axis-media/media.amp/stream=0?video=0&audio=0&event=on"
    )

    # KEEP-ALIVE
    rtsp_client.loop.call_later.assert_called_with(55, rtsp_client.keep_alive)

    rtsp_client.keep_alive()
    transport.write.assert_called_with(
        b"OPTIONS "
        + b"rtsp://host/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        + b"CSeq: 4\r\n"
        + b"User-Agent: HASS Axis\r\n"
        + b"Session: ghLlkf_I9pCBP24t\r\n\r\n"
    )
    assert len(rtsp_client.loop.call_later.call_args_list) == 7

    assert rtsp_client.session.sequence == 4

    # STOP stream
    rtsp_client.stop()
    transport.write.assert_called_with(
        b"TEARDOWN "
        + b"rtsp://host/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        + b"CSeq: 5\r\n"
        + b'Authorization: Digest username="root", realm="AXIS_ACCC8E012345", algorithm="MD5", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", uri="rtsp://host/axis-media/media.amp?video=0&audio=0&event=on", response="e403541b2a0136efd53ddc31ddf7160e"\r\n'
        + b"User-Agent: HASS Axis\r\n"
        + b"Session: ghLlkf_I9pCBP24t\r\n\r\n"
    )
    assert len(rtsp_client.loop.call_later.call_args_list) == 7

    assert rtsp_client.session.sequence == 5


def test_methods(rtsp_client):
    """Verify method attributes."""
    method = rtsp_client.method

    assert method.sequence == "CSeq: 0\r\n"

    assert method.authentication == ""
    with patch.object(method.session, "digest", True), patch.object(
        method.session, "generate_digest", return_value="digest"
    ):
        assert method.authentication == "Authorization: digest\r\n"

    with patch.object(method.session, "basic", True), patch.object(
        method.session, "generate_basic", return_value="basic"
    ):
        assert method.authentication == "Authorization: basic\r\n"

    assert method.user_agent == "User-Agent: HASS Axis\r\n"

    assert method.session_id == ""
    with patch.object(method.session, "session_id", "1"):
        assert method.session_id == "Session: 1\r\n"

    assert method.transport == "Transport: RTP/AVP;unicast;client_port=45678-45679\r\n"


def test_session_state_method(rtsp_client):
    """Verify state method."""
    session = rtsp_client.session

    assert session.sequence == 0
    assert session.method == "OPTIONS"
    assert session.state == STATE_STARTING

    with patch.object(session, "sequence", 1):
        assert session.method == "DESCRIBE"
        assert session.state == STATE_STARTING

    with patch.object(session, "sequence", 2):
        assert session.method == "SETUP"
        assert session.state == STATE_STARTING

    with patch.object(session, "sequence", 3):
        assert session.method == "PLAY"
        assert session.state == STATE_STARTING

    with patch.object(session, "sequence", 4):
        assert session.method == "KEEP-ALIVE"
        assert session.state == STATE_PLAYING

    with patch.object(session, "sequence", 5):
        assert session.method == "TEARDOWN"
        assert session.state == STATE_STOPPED

    with patch.object(session, "sequence", 6), pytest.raises(IndexError):
        session.method
        session.state


def test_session_update_status_codes(rtsp_client):
    """Vertify different status codes."""
    session = rtsp_client.session

    assert session.rtsp_version is None
    assert session.status_code is None
    assert session.status_text is None
    assert session.state == STATE_STARTING
    assert session.sequence == 0

    session.update("RTSP/1.0 200 OK\r\n")

    assert session.rtsp_version == 1
    assert session.status_code == 200
    assert session.status_text == "OK"
    assert session.state == STATE_STARTING
    assert session.sequence == 1

    session.update("RTSP/1.0 421 Unauthorized\r\n")

    assert session.rtsp_version == 1
    assert session.status_code == 421
    assert session.status_text == "Unauthorized"
    assert session.state == STATE_STARTING
    assert session.sequence == 1

    session.update("RTSP/1.0 454 Session Not Found\r\n")

    assert session.rtsp_version == 1
    assert session.status_code == 454
    assert session.status_text == "Session"  # "Session Not Found"
    assert session.state == STATE_STARTING
    assert session.sequence == 1


def test_session_generate_digest_auth(rtsp_client):
    """Verify generate digest auth method."""
    session = rtsp_client.session
    session.update(
        'WWW-Authenticate: Digest realm="AXIS_ACCC8E012345", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", stale=FALSE\r\n'
    )

    assert session.basic is False
    assert session.digest is True
    assert session.realm == "AXIS_ACCC8E012345"
    assert session.nonce == "0000eb57Y1462133062b37999f0cd530f02755fa37b8df1"
    assert session.stale is False

    digest_auth = session.generate_digest()
    assert (
        digest_auth
        == "Digest "
        + 'username="root", '
        + 'realm="AXIS_ACCC8E012345", '
        + 'algorithm="MD5", '
        + 'nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", '
        + 'uri="rtsp://host/axis-media/media.amp?video=0&audio=0&event=on", '
        + 'response="40553c9ab3be846423d1c1c0bc16bb4a"'
    )


def test_session_generate_basic_auth(rtsp_client):
    """Verify generate basic auth method."""
    session = rtsp_client.session
    session.update('WWW-Authenticate: Basic realm="AXIS_ACCC8E012345"\r\n')

    assert session.basic is True
    assert session.digest is False
    assert session.realm == "AXIS_ACCC8E012345"
    assert session.nonce is None
    assert session.stale is None

    basic_auth = session.generate_basic()

    assert basic_auth == "Basic cm9vdDpwYXNz"
    assert basic_auth == session.basic_auth  # Make session.basic_auth private

    with patch("base64.b64encode") as mock_b64encode:
        basic_auth = session.generate_basic()
        mock_b64encode.assert_not_called()
