"""Shared response construction helpers for test HTTP mocks."""

from aiohttp import web


def build_response(
    response_data: dict | list | str | bytes | None,
    *,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> web.Response:
    """Build an aiohttp response from common response payload shapes."""
    if isinstance(response_data, (dict, list)):
        return web.json_response(response_data, status=status, headers=headers)
    if isinstance(response_data, str):
        return web.Response(text=response_data, status=status, headers=headers)
    if isinstance(response_data, bytes):
        return web.Response(body=response_data, status=status, headers=headers)
    return web.Response(status=status, headers=headers)
