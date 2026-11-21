"""Mock bearer-token authentication and course ownership authorization."""
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


_TOKEN_USERS: dict[str, dict[str, str]] = {
    "user-a-token": {"id": "user-a", "role": "user"},
    "user-b-token": {"id": "user-b", "role": "user"},
    "admin-token": {"id": "admin", "role": "admin"},
}

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, str]:
    """Return the user represented by the bearer token; otherwise raise 401."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = _TOKEN_USERS.get(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The bearer token is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    
    return user.copy()


def can_access(user: dict[str, str], course: dict[str, Any]) -> bool:
    """Allow administrators or the owner of the given course."""
    return user.get("role") == "admin" or course.get("ownerId") == user.get("id")
