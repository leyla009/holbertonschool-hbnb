import uuid
from datetime import datetime
from app.extensions import db


class BaseModel(db.Model):
    """Abstract mapped base: every subclass gets id, created_at and updated_at."""
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Update updated_at whenever the object is modified."""
        self.updated_at = datetime.now()

    def update(self, data):
        """Update attributes from a dict, then refresh updated_at."""
        for key, value in data.items():
            if key not in ('id', 'created_at', 'updated_at') and hasattr(self, key):
                setattr(self, key, value)
        self.save()
