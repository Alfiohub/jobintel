from __future__ import annotations

import argparse

from jobintel_next.cli import _cmd_auth_create_user
from jobintel_next.product.auth import authenticate_local_user


def test_auth_create_user_command_flow(tmp_path) -> None:
    db = tmp_path / "saved.db"
    rc = _cmd_auth_create_user(
        argparse.Namespace(
            saved_db=str(db),
            email="cli-user@example.com",
            password="cli-pass-123",
            user_id="cli-user",
            inactive=False,
        )
    )
    assert rc == 0
    user = authenticate_local_user(db_path=db, email="cli-user@example.com", password="cli-pass-123")
    assert user is not None
    assert user["user_id"] == "cli-user"
