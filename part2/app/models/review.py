from app.models.base_model import BaseModel
from app.models.place import Place
from app.models.user import User


class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user

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

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, value):
        if not isinstance(value, Place):
            raise ValueError("place must be a Place instance")
        self._place = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        if not isinstance(value, User):
            raise ValueError("user must be a User instance")
        self._user = value
