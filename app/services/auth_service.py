from sqlalchemy.orm import Session

from app.core.exceptions import ApplicationException
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, database: Session) -> None:
        self.user_repository = UserRepository(database)

    def authenticate(
        self,
        identity: str,
        password: str,
    ) -> User:
        user = self.user_repository.get_by_username_or_email(
            identity
        )

        invalid_credentials = (
            user is None
            or not verify_password(
                password,
                user.hashed_password if user else "",
            )
        )

        if invalid_credentials:
            raise ApplicationException(
                message="Invalid username or password.",
                status_code=401,
                error_code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise ApplicationException(
                message="User account is disabled.",
                status_code=403,
                error_code="USER_DISABLED",
            )

        return user

    def login(
        self,
        identity: str,
        password: str,
    ) -> str:
        user = self.authenticate(identity, password)

        return create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role,
        )