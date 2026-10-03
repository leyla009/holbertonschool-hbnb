from app.extensions import db
from app.models.base_model import BaseModel
from app.models.place import Place
from app.models.user import User


class Review(BaseModel):
    __tablename__ = 'reviews'

    _text = db.Column('text', db.Text, nullable=False)
    _rating = db.Column('rating', db.Integer, nullable=False)
    # Plain columns for now: Task 8 turns them into ForeignKeys + relationships.
    place_id = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)

    def __init__(self, text, rating, place, user):
        super().__init__()
        self.text = text
        self.rating = rating
        if not isinstance(place, Place):
            raise ValueError("place must be a Place instance")
        if not isinstance(user, User):
            raise ValueError("user must be a User instance")
        self.place_id = place.id
        self.user_id = user.id

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("text is required")
        self._text = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            raise ValueError("rating must be an integer between 1 and 5")
        self._rating = value
