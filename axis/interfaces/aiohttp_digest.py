"""Aiohttp digest authentication handler.

Implements library-managed RFC 2617 digest authentication for aiohttp requests
to handle special characters in request parameters that break middleware-based auth.
"""

from __future__ import annotations

import hashlib
import logging
import re
import secrets
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote, urlsplit

from ..models.configuration import AuthScheme

if TYPE_CHECKING:
    from ..device import AxisDevice

LOGGER = logging.getLogger(__name__)
TIME_OUT = 15


class AiohttpDigestAuth:
    """Manages digest authentication for aiohttp requests."""

    def __init__(self, device: AxisDevice) -> None:
        """Initialize digest auth handler."""
        self.device = device
        self._nonce: str | None = None
        self._nonce_count = 0

    def should_use_library_digest(self, http_client: str, has_basic_auth: bool) -> bool:
        """Return if aiohttp requests should use library-managed digest auth.

        Args:
            http_client: Name of HTTP client ("aiohttp" or "httpx").
            has_basic_auth: Whether basic auth is configured.

        Returns:
            True if library-managed digest should be used.

        """
        return (
            http_client == "aiohttp"
            and not has_basic_auth
            and self.device.config.auth_scheme != AuthScheme.BASIC
        )

    def request_target(
        self, url: str, params: dict[str, str] | None, should_encode: bool
    ) -> tuple[str, dict[str, str] | None]:
        """Return request URL and params for aiohttp request.

        With library-managed digest auth, pre-encode params into the URL so the
        signed URI exactly matches the request-target on the wire.

        Args:
            url: Base request URL.
            params: Optional query parameters.
            should_encode: Whether to pre-encode params for digest signing.

        Returns:
            Tuple of (request_url, request_params) to use in actual request.

        """
        if params is None or not should_encode:
            return url, params

        separator = "&" if "?" in url else "?"
        encoded_parts = [
            f"{quote(k, safe='')}={quote(v, safe='')}" for k, v in params.items()
        ]
        encoded_query = "&".join(encoded_parts)
        encoded_url = f"{url}{separator}{encoded_query}"
        return encoded_url, None

    def extract_challenge(self, headers: Any) -> str | None:
        """Return digest challenge header when present.

        Args:
            headers: Response headers (dict-like or aiohttp MultiDictProxy).

        Returns:
            Digest challenge string if present, None otherwise.

        """
        candidates: list[str] = []
        if hasattr(headers, "getall"):
            candidates.extend(cast("list[str]", headers.getall("WWW-Authenticate", [])))
        else:
            for name, value in cast("dict[str, str]", headers).items():
                if name.lower() == "www-authenticate":
                    candidates.append(value)

        for value in candidates:
            if value.lower().startswith("digest "):
                return value
        return None

    def build_authorization(
        self,
        method: str,
        request_url: str,
        digest_challenge: str,
    ) -> str | None:
        """Build digest authorization header from challenge and request URI.

        Args:
            method: HTTP method (GET, POST, etc.).
            request_url: Full request URL (will extract path + query).
            digest_challenge: Digest challenge string from WWW-Authenticate header.

        Returns:
            Authorization header value or None if digest cannot be built.

        """
        challenge_values = {
            key.lower(): value.strip('"')
            for key, value in re.findall(
                r"(\w+)=((?:\"[^\"]*\")|(?:[^,]+))", digest_challenge
            )
        }

        realm = challenge_values.get("realm")
        nonce = challenge_values.get("nonce")
        if realm is None or nonce is None:
            return None

        algorithm = challenge_values.get("algorithm", "MD5").upper()
        if algorithm != "MD5":
            LOGGER.debug("Unsupported digest algorithm for aiohttp path: %s", algorithm)
            return None

        uri = self._digest_uri(request_url)
        qop = None
        if qop_header := challenge_values.get("qop"):
            qop_values = [value.strip() for value in qop_header.split(",")]
            if "auth" in qop_values:
                qop = "auth"

        username = self.device.config.username
        password = self.device.config.password
        ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
        ha2 = hashlib.md5(f"{method.upper()}:{uri}".encode()).hexdigest()

        parts = [
            f'username="{username}"',
            f'realm="{realm}"',
            f'nonce="{nonce}"',
            f'uri="{uri}"',
            'algorithm="MD5"',
        ]

        if opaque := challenge_values.get("opaque"):
            parts.append(f'opaque="{opaque}"')

        if qop == "auth":
            if nonce != self._nonce:
                self._nonce = nonce
                self._nonce_count = 0

            self._nonce_count += 1
            nc = f"{self._nonce_count:08x}"
            cnonce = secrets.token_hex(8)
            response = hashlib.md5(
                f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}".encode()
            ).hexdigest()
            parts.extend(
                [
                    f'response="{response}"',
                    f"qop={qop}",
                    f"nc={nc}",
                    f'cnonce="{cnonce}"',
                ]
            )
        else:
            response = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
            parts.append(f'response="{response}"')

        return f"Digest {', '.join(parts)}"

    def _digest_uri(self, request_url: str) -> str:
        """Return path + query request-target URI for digest signing.

        Args:
            request_url: Full request URL.

        Returns:
            Path and query string for digest signature.

        """
        split_result = urlsplit(request_url)
        if split_result.query:
            return f"{split_result.path}?{split_result.query}"
        return split_result.path

    async def perform_request(
        self,
        session: Any,
        method: str,
        url: str,
        request_data: bytes | dict[str, str] | None,
        headers: dict[str, str] | None,
        params: dict[str, str] | None,
    ) -> tuple[int, dict[str, str], bytes]:
        """Execute aiohttp request with digest auth handling.

        Args:
            session: aiohttp ClientSession.
            method: HTTP method.
            url: Request URL.
            request_data: Request body (bytes or form data).
            headers: Request headers.
            params: Query parameters.

        Returns:
            Tuple of (status_code, response_headers, response_content).

        """
        request_url, request_params = self.request_target(url, params, True)
        request_headers = dict(headers) if headers is not None else {}

        # First attempt without auth to get challenge
        async with session.request(
            method,
            request_url,
            data=request_data,
            headers=request_headers,
            params=request_params,
            auth=None,
            timeout=TIME_OUT,
        ) as response:
            response_content = await response.read()
            response_headers = dict(response.headers)
            if response.status != 401:
                return response.status, response_headers, response_content

            digest_challenge = self.extract_challenge(response.headers)
            if digest_challenge is None:
                return response.status, response_headers, response_content

        # Build digest auth and retry
        digest_authorization = self.build_authorization(
            method=method,
            request_url=request_url,
            digest_challenge=digest_challenge,
        )
        if digest_authorization is None:
            return 401, {}, b""

        retry_headers = dict(request_headers)
        retry_headers["Authorization"] = digest_authorization

        async with session.request(
            method,
            request_url,
            data=request_data,
            headers=retry_headers,
            params=request_params,
            auth=None,
            timeout=TIME_OUT,
        ) as response:
            response_content = await response.read()
            return response.status, dict(response.headers), response_content
