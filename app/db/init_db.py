import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import User
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as database:
        existing_admin = database.scalar(
            select(User).where(User.username == settings.default_admin_username)
        )

        if existing_admin:
            return

        admin = User(
            username=settings.default_admin_username,
            email=settings.default_admin_email,
            hashed_password=get_password_hash(settings.default_admin_password),
            role="admin",
            is_active=True,
        )

        database.add(admin)
        database.commit()

        logger.info("Default admin user created.")
