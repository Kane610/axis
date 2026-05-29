# ruff: noqa: D100,D103,TC001

from __future__ import annotations

import asyncio
import getpass
import re
from typing import TYPE_CHECKING

from axis.cli.packs.devices import DeviceEntry, run_on_selected_device
from axis.device import AxisDevice
from axis.errors import Forbidden, PathNotFound
from axis.models.pwdgrp_cgi import SecondaryGroup

if TYPE_CHECKING:
    from collections.abc import Mapping

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9]{1,14}$")


def register(registry: object, router: object) -> None:
    """Register account-pack commands and menu nodes (explicit composition placeholder)."""


def _validate_username(username: str) -> str | None:
    if not _USERNAME_RE.match(username):
        return "Username must be 1-14 alphanumeric characters (a-z, A-Z, 0-9)."
    return None


def _select_privilege() -> SecondaryGroup | None:
    options: list[tuple[str, SecondaryGroup]] = [
        ("Viewer", SecondaryGroup.VIEWER),
        ("Viewer + PTZ", SecondaryGroup.VIEWER_PTZ),
        ("Operator", SecondaryGroup.OPERATOR),
        ("Operator + PTZ", SecondaryGroup.OPERATOR_PTZ),
        ("Admin", SecondaryGroup.ADMIN),
        ("Admin + PTZ", SecondaryGroup.ADMIN_PTZ),
    ]
    print("\nPrivilege levels:")  # noqa: T201
    for idx, (label, _) in enumerate(options, 1):
        print(f"  {idx}. {label}")  # noqa: T201
    print("  b. Back")  # noqa: T201
    print("  e. Exit")  # noqa: T201
    sel = input("Select privilege [b/e]: ").strip().lower()
    if sel == "e":
        print("Exiting.")  # noqa: T201
        raise SystemExit(0)
    if sel == "b":
        return None
    try:
        idx = int(sel)
    except ValueError:
        print("Invalid selection.")  # noqa: T201
        return None
    if idx < 1 or idx > len(options):
        print("Invalid selection.")  # noqa: T201
        return None
    return options[idx - 1][1]


def _account_init_confirm(
    target_user: str,
    sgrp: SecondaryGroup,
    exists: bool,
) -> bool:
    if exists:
        answer = (
            input(
                f"User '{target_user}' already exists. "
                "Update password and privilege? (y/n): "
            )
            .strip()
            .lower()
        )
        if answer != "y":
            print("Account update aborted.")  # noqa: T201
            return False
    else:
        answer = (
            input(
                f"Create user '{target_user}' with "
                f"{sgrp.name.lower()} privileges? (y/n): "
            )
            .strip()
            .lower()
        )
        if answer != "y":
            print("Account creation aborted.")  # noqa: T201
            return False
    return True


async def _account_init_operation(
    device: AxisDevice,
    target_user: str,
    target_pwd: str,
    sgrp: SecondaryGroup,
    existing_users: Mapping[str, object],
) -> None:
    exists = target_user in existing_users
    if not _account_init_confirm(target_user, sgrp, exists):
        return
    if exists:
        await device.vapix.users.modify(target_user, pwd=target_pwd, sgrp=sgrp)
        print(f"User '{target_user}' updated.")  # noqa: T201
    else:
        await device.vapix.users.create(
            target_user,
            pwd=target_pwd,
            sgrp=sgrp,
            comment="Created via Axis CLI",
        )
        print(f"User '{target_user}' created.")  # noqa: T201


def _list_users_flow(device_entry: DeviceEntry) -> None:
    async def _op(device: AxisDevice) -> dict[str, object]:
        return dict(await device.vapix.users.list())

    users = asyncio.run(run_on_selected_device(device_entry, _op))
    if not users:
        print("No users found (or insufficient privileges).")  # noqa: T201
        return
    print("\nUsers:")  # noqa: T201
    for name, user in users.items():
        privs = str(getattr(user, "privileges", "unknown"))
        print(f"  - {name} ({privs})")  # noqa: T201


def _create_or_update_user_flow(device_entry: DeviceEntry) -> None:
    target_user = input("Username: ").strip()
    err = _validate_username(target_user)
    if err:
        print(f"Invalid username: {err}")  # noqa: T201
        return

    target_pwd = getpass.getpass("Password: ")
    if not (1 <= len(target_pwd) <= 64):
        print("Password must be 1-64 characters.")  # noqa: T201
        return

    sgrp = _select_privilege()
    if sgrp is None:
        return

    async def _op(device: AxisDevice) -> None:
        existing = await device.vapix.users.list()
        await _account_init_operation(device, target_user, target_pwd, sgrp, existing)

    try:
        asyncio.run(run_on_selected_device(device_entry, _op))
    except (Forbidden, PathNotFound) as exc:
        print(f"Access denied or unsupported on this device: {exc}")  # noqa: T201


def _delete_user_flow(device_entry: DeviceEntry) -> None:
    _list_users_flow(device_entry)
    target_user = input("\nUsername to delete: ").strip()
    if not target_user:
        print("No username provided.")  # noqa: T201
        return

    confirm = input(f"Permanently delete user '{target_user}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Deletion aborted.")  # noqa: T201
        return

    async def _op(device: AxisDevice) -> None:
        await device.vapix.users.delete(target_user)
        print(f"User '{target_user}' deleted.")  # noqa: T201

    try:
        asyncio.run(run_on_selected_device(device_entry, _op))
    except (Forbidden, PathNotFound) as exc:
        print(f"Access denied or unsupported on this device: {exc}")  # noqa: T201


def account_management_flow(serial: str, device_entry: DeviceEntry) -> None:
    while True:
        print(f"\nAccount management for {serial}:")  # noqa: T201
        print("  1. List users")  # noqa: T201
        print("  2. Create or update user")  # noqa: T201
        print("  3. Delete user")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        choice = input("Select option [1/2/3/b/e]: ").strip().lower()

        if choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if choice == "b":
            return

        if choice == "1":
            _list_users_flow(device_entry)
            continue

        if choice == "2":
            _create_or_update_user_flow(device_entry)
            continue

        if choice == "3":
            _delete_user_flow(device_entry)
            continue

        print("Invalid option. Please enter 1, 2, 3, b, or e.")  # noqa: T201
