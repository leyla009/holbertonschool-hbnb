from app.extensions import db
from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """User-specific queries on top of the generic SQLAlchemy repository."""

    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        # `email` is a validated property; the mapped column is `_email`
        return db.session.query(User).filter(User._email == email).first()
