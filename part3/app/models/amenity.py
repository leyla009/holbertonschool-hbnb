from app.extensions import db
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    __tablename__ = 'amenities'

    _name = db.Column('name', db.String(50), nullable=False)

    places = db.relationship('Place', secondary='place_amenity',
                             back_populates='amenities')

    def __init__(self, name):
        super().__init__()
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip() or len(value) > 50:
            raise ValueError("name is required and must be at most 50 characters")
        self._name = value
