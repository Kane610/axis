# ruff: noqa: D100,D101,D102

from __future__ import annotations

import getpass
from typing import Protocol


class CliIO(Protocol):
    def prompt(self, text: str) -> str: ...

    def prompt_password(self, text: str) -> str: ...

    def write(self, text: str) -> None: ...


class TerminalIO:
    def prompt(self, text: str) -> str:
        return input(text)

    def prompt_password(self, text: str) -> str:
        return getpass.getpass(text)

    def write(self, text: str) -> None:
        print(text)  # noqa: T201
