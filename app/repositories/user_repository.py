from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def get_by_username_or_email(
        self,
        identity: str,
    ) -> User | None:
        statement = select(User).where(
            or_(
                User.username == identity,
                User.email == identity,
            )
        )

        return self.database.scalar(statement)

    def get_by_id(self, user_id: int) -> User | None:
        return self.database.get(User, user_id)