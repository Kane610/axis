"""Test RTSP client.

pytest --cov-report term-missing --cov=axis.rtsp tests/test_rtsp.py
"""

import asyncio
import logging
from unittest.mock import Mock, patch

import pytest

from axis.rtsp import RTSPClient, Signal, State

from .conftest import HOST, RTSP_PORT

LOGGER = logging.getLogger(__name__)


@pytest.fixture
async def rtsp_client(axis_device) -> RTSPClient:
    """Return the RTSP client."""
    axis_device.enable_events()
    with patch("axis.rtsp.RTSP_PORT", RTSP_PORT):
        axis_device.stream.start()
    yield axis_device.stream.stream
    axis_device.stream.stop()


async def test_successful_connect(rtsp_server, rtsp_client):
    """Verify successful setup of RTSP session to server."""
    rtsp_server.register_responses(
        [
            # OPTIONS
            (
                "RTSP/1.0 200 OK\r\n"
                "CSeq: 0\r\n"
                "Public: OPTIONS, DESCRIBE, ANNOUNCE, GET_PARAMETER, PAUSE, PLAY, RECORD, SETUP, SET_PARAMETER, TEARDOWN\r\n"
                "Server: GStreamer RTSP server\r\n"
                "Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n"
            ),
            # DESCRIBE is denied since it requires authentication
            (
                "RTSP/1.0 401 Unauthorized\r\n"
                "CSeq: 1\r\n"
                'WWW-Authenticate: Digest realm="AXIS_ACCC8E012345", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", stale=FALSE\r\n'
                "Server: GStreamer RTSP server\r\n "
                "Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n"
            ),
            # DESCRIBE with digest authentication
            (
                "RTSP/1.0 200 OK\r\n"
                "CSeq: 1\r\n"
                "Content-Type: application/sdp\r\n"
                "Content-Base: rtsp://127.0.0.1/axis-media/media.amp/\r\n"
                "Server: GStreamer RTSP server\r\n"
                "Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n"
                "Content-Length: 440\r\n\r\n"
                "v=0\r\n"
                "o=- 18302136002250915122 1 IN IP4 host\r\n"
                "s=Session streamed with GStreamer\r\n"
                "i=rtsp-server\r\n"
                "t=0 0\r\n"
                "a=tool:GStreamer\r\n"
                "a=type:broadcast\r\n"
                "a=range:npt=now-\r\n"
                "a=control:rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on\r\n"
                "m=application 0 RTP/AVP 98\r\n"
                "c=IN IP4 0.0.0.0\r\n"
                "a=rtpmap:98 vnd.onvif.metadata/90000\r\n"
                "a=ts-refclk:local\r\n"
                "a=mediaclk:sender\r\n"
                "a=control:rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on\r\n"
            ),
            # SETUP requires to know the rtp and rtcp ports which are not yet known
            # "RTSP/1.0 200 OK\r\n"
            # "CSeq: 2\r\n"
            # 'Transport: RTP/AVP;unicast;client_port=45678-45679;server_port=50000-50001;ssrc=315460DA;mode="PLAY"\r\n'
            # "Server: GStreamer RTSP server\r\n"
            # "Session: ghLlkf_I9pCBP24t;timeout=60\r\n"
            # "Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n",
            # PLAY
            (
                "RTSP/1.0 200 OK\r\n"
                "CSeq: 3\r\n"
                "RTP-Info: url=rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on;seq=13114;rtptime=3803548519\r\n"
                "Range: npt=now-\r\n"
                "Server: GStreamer RTSP server\r\n"
                "Session: ghLlkf_I9pCBP24t;timeout=60\r\n"
                "Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n"
            ),
        ]
    )

    rtp_port = rtsp_client.rtp.port
    rtcp_port = rtsp_client.rtp.rtcp_port

    # Initial state of RTSP session
    await rtsp_server.next_request_received.wait()
    assert rtsp_client.time_out_handle
    assert (
        rtsp_client.session.url
        == "rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on"
    )
    assert rtsp_client.session.host == HOST
    assert rtsp_client.session.port == RTSP_PORT
    assert rtsp_client.session.username == "root"
    assert rtsp_client.session.password == "pass"
    assert rtsp_client.session.user_agent == "HASS Axis"
    assert rtsp_client.session.rtp_port == rtp_port
    assert rtsp_client.session.rtcp_port == rtcp_port
    assert rtsp_client.session.methods == [
        "OPTIONS",
        "DESCRIBE",
        "SETUP",
        "PLAY",
        "KEEP-ALIVE",
        "TEARDOWN",
    ]

    assert rtsp_client.session.sequence == 0
    assert rtsp_client.session._basic_auth is None
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

    # OPTIONS ask server to show what options it supports
    assert rtsp_server.last_request == (
        "OPTIONS "
        "rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        "CSeq: 0\r\n"
        "User-Agent: HASS Axis\r\n\r\n"
    )
    rtsp_server.step_response()
    await rtsp_server.next_request_received.wait()
    assert rtsp_client.session.sequence == 1
    assert rtsp_client.session._basic_auth is None
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
    assert rtsp_server.last_request == (
        "DESCRIBE "
        "rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        "CSeq: 1\r\n"
        "User-Agent: HASS Axis\r\n"
        "Accept: application/sdp\r\n\r\n"
    )
    rtsp_server.step_response()
    await rtsp_server.next_request_received.wait()
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
    assert rtsp_server.last_request == (
        "DESCRIBE "
        "rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        "CSeq: 1\r\n"
        'Authorization: Digest username="root", realm="AXIS_ACCC8E012345", algorithm="MD5", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", uri="rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on", response="909e6c215f6b0f350147a81ae3980018"\r\n'
        "User-Agent: HASS Axis\r\n"
        "Accept: application/sdp\r\n\r\n"
    )
    rtsp_server.step_response()
    await rtsp_server.next_request_received.wait()
    assert rtsp_client.session.sequence == 2
    assert rtsp_client.session._basic_auth is None
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
    assert rtsp_client.session.content_base == "rtsp://127.0.0.1/axis-media/media.amp/"
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
        "a=control:rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on",
        "m=application 0 RTP/AVP 98",
        "c=IN IP4 0.0.0.0",
        "a=rtpmap:98 vnd.onvif.metadata/90000",
        "a=ts-refclk:local",
        "a=mediaclk:sender",
        "a=control:rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on",
    ]
    assert (
        rtsp_client.session.control_url
        == "rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on"
    )

    # SETUP setup rtp connection to server
    assert rtsp_server.last_request == (
        "SETUP "
        "rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on RTSP/1.0\r\n"
        "CSeq: 2\r\n"
        'Authorization: Digest username="root", realm="AXIS_ACCC8E012345", algorithm="MD5", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", uri="rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on", response="3c4d88afefd4ab931f6db658326d60c2"\r\n'
        "User-Agent: HASS Axis\r\n"
        f"Transport: RTP/AVP;unicast;client_port={rtp_port}-{rtcp_port}\r\n\r\n"
    )
    rtsp_server.send_response(
        "RTSP/1.0 200 OK\r\n"
        "CSeq: 2\r\n"
        f'Transport: RTP/AVP;unicast;client_port={rtp_port}-{rtcp_port};server_port=50000-50001;ssrc=315460DA;mode="PLAY"\r\n'
        "Server: GStreamer RTSP server\r\n"
        "Session: ghLlkf_I9pCBP24t;timeout=60\r\n"
        "Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n",
    )
    await rtsp_server.next_request_received.wait()
    assert rtsp_client.session.sequence == 3
    assert rtsp_client.session._basic_auth is None
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
    assert rtsp_client.session.content_base == "rtsp://127.0.0.1/axis-media/media.amp/"
    assert rtsp_client.session.content_length == 440
    assert rtsp_client.session.session_id == "ghLlkf_I9pCBP24t"
    assert rtsp_client.session.session_timeout == 60
    assert (
        rtsp_client.session.transport_ack
        == f'RTP/AVP;unicast;client_port={rtp_port}-{rtcp_port};server_port=50000-50001;ssrc=315460DA;mode="PLAY"'
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
        "a=control:rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on",
        "m=application 0 RTP/AVP 98",
        "c=IN IP4 0.0.0.0",
        "a=rtpmap:98 vnd.onvif.metadata/90000",
        "a=ts-refclk:local",
        "a=mediaclk:sender",
        "a=control:rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on",
    ]
    assert (
        rtsp_client.session.control_url
        == "rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on"
    )

    # PLAY start stream
    assert rtsp_server.last_request == (
        "PLAY "
        "rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        "CSeq: 3\r\n"
        'Authorization: Digest username="root", realm="AXIS_ACCC8E012345", algorithm="MD5", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", uri="rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on", response="1c882325f7733b0d48d177ee8a0e6b2a"\r\n'
        "User-Agent: HASS Axis\r\n"
        "Session: ghLlkf_I9pCBP24t\r\n\r\n"
    )
    with patch.object(rtsp_client, "callback") as mock_callback:
        rtsp_server.step_response()
        # We don't expect additional requests as RTSP handshake is complete
        # but we still need to wait for rtsp client to process response before continuing
        while True:
            if len(mock_callback.call_args_list) == 0:
                await asyncio.sleep(0)
                continue
            break
        mock_callback.assert_called_with(Signal.PLAYING)
    assert rtsp_client.session.sequence == 4
    assert rtsp_client.session._basic_auth is None
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
    assert rtsp_client.session.content_base == "rtsp://127.0.0.1/axis-media/media.amp/"
    assert rtsp_client.session.content_length == 440
    assert rtsp_client.session.session_id == "ghLlkf_I9pCBP24t"
    assert rtsp_client.session.session_timeout == 60
    assert (
        rtsp_client.session.transport_ack
        == f'RTP/AVP;unicast;client_port={rtp_port}-{rtcp_port};server_port=50000-50001;ssrc=315460DA;mode="PLAY"'
    )
    assert rtsp_client.session.range == "npt=now-"
    assert (
        rtsp_client.session.rtp_info
        == "url=rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on;seq=13114;rtptime=3803548519"
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
        "a=control:rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on",
        "m=application 0 RTP/AVP 98",
        "c=IN IP4 0.0.0.0",
        "a=rtpmap:98 vnd.onvif.metadata/90000",
        "a=ts-refclk:local",
        "a=mediaclk:sender",
        "a=control:rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on",
    ]
    assert (
        rtsp_client.session.control_url
        == "rtsp://127.0.0.1/axis-media/media.amp/stream=0?video=0&audio=0&event=on"
    )

    # Connect to RTP socket
    class UDPClientProtocol:
        def __init__(self):
            self.transport = None

        def connection_made(self, transport):
            self.transport = transport

        def connection_lost(self, exc):
            LOGGER.info("Connection lost.")

        def send_message(self, message: str) -> None:
            LOGGER.info("Send: %s", message)
            self.transport.sendto(message.encode())

    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        UDPClientProtocol, remote_addr=(HOST, rtp_port)
    )
    protocol.send_message("123456789ABCDEF")
    transport.close()

    # KEEP-ALIVE send OPTIONS signal to keep session alive
    assert rtsp_client.keep_alive_handle
    assert rtsp_client.time_out_handle.cancelled()
    rtsp_client.keep_alive()
    assert not rtsp_client.time_out_handle.cancelled()
    await rtsp_server.next_request_received.wait()
    assert rtsp_server.last_request == (
        "OPTIONS "
        "rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        "CSeq: 4\r\n"
        "User-Agent: HASS Axis\r\n"
        "Session: ghLlkf_I9pCBP24t\r\n\r\n"
    )
    with patch.object(rtsp_client, "callback") as mock_callback:
        rtsp_server.send_response(
            "RTSP/1.0 200 OK\r\n"
            "CSeq: 4\r\n"
            "Public: OPTIONS, DESCRIBE, ANNOUNCE, GET_PARAMETER, PAUSE, PLAY, RECORD, SETUP, SET_PARAMETER, TEARDOWN\r\n"
            "Server: GStreamer RTSP server\r\n"
            "Session: ghLlkf_I9pCBP24t;timeout=30\r\n"
            "Date: Sat, 12 Dec 2020 10:44:25 GMT\r\n\r\n"
        )
        # We don't expect additional requests as RTSP handshake is complete
        # but we still need to wait for rtsp client to process response before continuing
        while True:
            if len(mock_callback.call_args_list) == 0:
                await asyncio.sleep(0)
                continue
            break
        mock_callback.assert_called_with(Signal.PLAYING)
    assert rtsp_client.session.session_id == "ghLlkf_I9pCBP24t"
    assert rtsp_client.session.session_timeout == 30

    rtsp_client.stop()
    assert rtsp_client.keep_alive_handle.cancelled()
    assert rtsp_client.time_out_handle.cancelled()
    await rtsp_server.next_request_received.wait()
    assert rtsp_server.last_request == (
        "TEARDOWN "
        "rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on RTSP/1.0\r\n"
        "CSeq: 5\r\n"
        'Authorization: Digest username="root", realm="AXIS_ACCC8E012345", algorithm="MD5", nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", uri="rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on", response="2417a81b93d5ae64926d226e18a5ab99"\r\n'
        "User-Agent: HASS Axis\r\n"
        "Session: ghLlkf_I9pCBP24t\r\n\r\n"
    )


def test_rtsp_client_time_out(rtsp_client, caplog):
    """Verify RTSP client time out method."""
    with (
        patch.object(rtsp_client, "stop") as mock_rtsp_client_stop,
        patch.object(rtsp_client, "callback") as mock_rtsp_client_callback,
    ):
        rtsp_client.time_out()
        assert f"Response timed out {HOST}" in caplog.text
        mock_rtsp_client_stop.assert_called()
        mock_rtsp_client_callback.assert_called_with(Signal.FAILED)


def test_rtsp_client_connection_lost(rtsp_client, caplog):
    """Verify RTSP client connection lost method."""
    with caplog.at_level(logging.DEBUG):
        rtsp_client.connection_lost("exc")
    assert "RTSP session lost connection" in caplog.text


async def test_rtsp_client_server_sends_stop(rtsp_server, rtsp_client):
    """Verify behavior when session sequence is 5 and server sends unsupported response."""
    await rtsp_server.next_request_received.wait()
    rtsp_client.session.sequence = 5
    rtsp_server.send_response("Unsupported response")
    await rtsp_server.next_request_received.wait()
    assert rtsp_client.keep_alive_handle is None
    assert rtsp_client.time_out_handle.cancelled()


def test_rtp_client(rtsp_client, caplog):
    """Verify RTP client."""
    rtp_client = rtsp_client.rtp

    mock_transport = Mock()
    rtp_client.client.connection_made(mock_transport)
    assert rtp_client.client.transport == mock_transport

    with caplog.at_level(logging.DEBUG):
        rtp_client.client.connection_lost("exc")
    assert "Stream recepient offline" in caplog.text

    with patch.object(rtp_client.client, "callback") as mock_callback:
        rtp_client.client.datagram_received("0123456789ABCDEF", "addr")
        mock_callback.assert_called_with(Signal.DATA)
        assert rtp_client.data == "CDEF"

    rtsp_client.stop()
    mock_transport.close.assert_called()


def test_methods(rtsp_client):
    """Verify method attributes."""
    method = rtsp_client.method
    rtp_port = rtsp_client.rtp.port
    rtcp_port = rtsp_client.rtp.rtcp_port

    assert method.sequence == "CSeq: 0\r\n"

    assert method.authentication == ""
    with (
        patch.object(method.session, "digest", True),
        patch.object(method.session, "generate_digest", return_value="digest"),
    ):
        assert method.authentication == "Authorization: digest\r\n"

    with (
        patch.object(method.session, "basic", True),
        patch.object(method.session, "generate_basic", return_value="basic"),
    ):
        assert method.authentication == "Authorization: basic\r\n"

    assert method.user_agent == "User-Agent: HASS Axis\r\n"

    assert method.session_id == ""
    with patch.object(method.session, "session_id", "1"):
        assert method.session_id == "Session: 1\r\n"

    assert (
        method.transport
        == f"Transport: RTP/AVP;unicast;client_port={rtp_port}-{rtcp_port}\r\n"
    )


def test_session_state_method(rtsp_client):
    """Verify state method."""
    session = rtsp_client.session

    assert session.sequence == 0
    assert session.method == "OPTIONS"
    assert session.state == State.STARTING

    with patch.object(session, "sequence", 1):
        assert session.method == "DESCRIBE"
        assert session.state == State.STARTING

    with patch.object(session, "sequence", 2):
        assert session.method == "SETUP"
        assert session.state == State.STARTING

    with patch.object(session, "sequence", 3):
        assert session.method == "PLAY"
        assert session.state == State.STARTING

    with patch.object(session, "sequence", 4):
        assert session.method == "KEEP-ALIVE"
        assert session.state == State.PLAYING

    with patch.object(session, "sequence", 5):
        assert session.method == "TEARDOWN"
        assert session.state == State.STOPPED

    with patch.object(session, "sequence", 6), pytest.raises(IndexError):
        _ = session.method

    with patch.object(session, "sequence", 6), pytest.raises(IndexError):
        _ = session.state


def test_session_update_status_codes(rtsp_client):
    """Vertify different status codes."""
    session = rtsp_client.session

    assert session.rtsp_version is None
    assert session.status_code is None
    assert session.status_text is None
    assert session.state == State.STARTING
    assert session.sequence == 0

    session.update("RTSP/1.0 200 OK\r\n")

    assert session.rtsp_version == 1
    assert session.status_code == 200
    assert session.status_text == "OK"
    assert session.state == State.STARTING
    assert session.sequence == 1

    session.update("RTSP/1.0 421 Unauthorized\r\n")

    assert session.rtsp_version == 1
    assert session.status_code == 421
    assert session.status_text == "Unauthorized"
    assert session.state == State.STARTING
    assert session.sequence == 1

    session.update("RTSP/1.0 454 Session Not Found\r\n")

    assert session.rtsp_version == 1
    assert session.status_code == 454
    assert session.status_text == "Session"  # "Session Not Found"
    assert session.state == State.STARTING
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
        digest_auth == "Digest "
        'username="root", '
        'realm="AXIS_ACCC8E012345", '
        'algorithm="MD5", '
        'nonce="0000eb57Y1462133062b37999f0cd530f02755fa37b8df1", '
        'uri="rtsp://127.0.0.1/axis-media/media.amp?video=0&audio=0&event=on", '
        'response="359495f9e42106627750e3cd65145f6b"'
    )


def test_session_generate_basic_auth(event_loop, rtsp_client):
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
    assert basic_auth == session._basic_auth

    with patch("base64.b64encode") as mock_b64encode:
        basic_auth = session.generate_basic()
        mock_b64encode.assert_not_called()
