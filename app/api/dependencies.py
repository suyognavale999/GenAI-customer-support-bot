from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ApplicationException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


DatabaseDependency = Annotated[Session, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    database: DatabaseDependency,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> User:
    if credentials is None:
        raise ApplicationException(
            message="Authentication is required.",
            status_code=401,
            error_code="AUTHENTICATION_REQUIRED",
        )

    payload = decode_access_token(credentials.credentials)

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ApplicationException(
            message="Invalid access token.",
            status_code=401,
            error_code="INVALID_ACCESS_TOKEN",
        ) from exc

    user = UserRepository(database).get_by_id(user_id)

    if user is None or not user.is_active:
        raise ApplicationException(
            message="User is unavailable or disabled.",
            status_code=401,
            error_code="USER_UNAVAILABLE",
        )

    return user


CurrentUserDependency = Annotated[
    User,
    Depends(get_current_user),
]


def require_admin(
    current_user: CurrentUserDependency,
) -> User:
    if current_user.role != "admin":
        raise ApplicationException(
            message="Administrator access is required.",
            status_code=403,
            error_code="ADMIN_ACCESS_REQUIRED",
        )

    return current_user


AdminUserDependency = Annotated[
    User,
    Depends(require_admin),
]