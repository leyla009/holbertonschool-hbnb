import re
from app.models.base_model import BaseModel


class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin=False, password=None):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.password = None
        # Indented correctly inside __init__ so 'password' is in scope
        if password is not None:
            self.hash_password(password)

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not isinstance(value, str) or not value.strip() or len(value) > 50:
            raise ValueError("first_name is required and must be at most 50 characters")
        self._first_name = value

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        if not isinstance(value, str) or not value.strip() or len(value) > 50:
            raise ValueError("last_name is required and must be at most 50 characters")
        self._last_name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str) or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', value):
            raise ValueError("email must be a valid email address")
        self._email = value

    @property
    def is_admin(self):
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_admin must be a boolean")
        self._is_admin = value
        
    def hash_password(self, password):
        """Hashes the password before storing it."""
        from app import bcrypt  # imported here to avoid a circular import
        if not isinstance(password, str) or not password:
            raise ValueError("password is required and must be a non-empty string")
        # Moved outside the error check block so it executes properly
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        from app import bcrypt
        if not self.password or not isinstance(password, str):
            return False
        return bcrypt.check_password_hash(self.password, password)