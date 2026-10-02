from app.models.base_model import BaseModel
from app.models.user import User


class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.reviews = []
        self.amenities = []

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip() or len(value) > 100:
            raise ValueError("title is required and must be at most 100 characters")
        self._title = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("description must be a string")
        self._description = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("price must be a positive number")
        self._price = float(value)

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not -90.0 <= value <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        self._latitude = float(value)

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not -180.0 <= value <= 180.0:
            raise ValueError("longitude must be between -180 and 180")
        self._longitude = float(value)

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if not isinstance(value, User):
            raise ValueError("owner must be a User instance")
        self._owner = value

    def add_review(self, review):
        self.reviews.append(review)

    def add_amenity(self, amenity):
        if amenity not in self.amenities:
            self.amenities.append(amenity)
