from typing import Any

from app.static import access_security, refresh_security


def create_access_token(id: int, username: str):
    subject: dict[str, Any] = {"id": id, "username": username}

    return access_security.create_access_token(subject=subject)

def create_refresh_token(id: int, username: str):
    subject: dict[str, Any] = {"id": id, "username": username}

    return refresh_security.create_refresh_token(subject=subject)
