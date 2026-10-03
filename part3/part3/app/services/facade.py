from app.persistence.repository import SQLAlchemyRepository
from app.persistence.user_repository import UserRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

    # ---------- Users ----------
    def create_user(self, user_data):
        if self.get_user_by_email(user_data.get('email')):
            raise ValueError("Email already registered")
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None
        new_email = user_data.get('email')
        if new_email and new_email != user.email and self.get_user_by_email(new_email):
            raise ValueError("Email already registered")
        data = dict(user_data)
        password = data.pop('password', None)
        if password is not None and (not isinstance(password, str) or not password):
            raise ValueError("password must be a non-empty string")
        for protected in ('id', 'created_at', 'updated_at'):
            data.pop(protected, None)
        if password is not None:
            user.hash_password(password)
        self.user_repo.update(user_id, data)  # applies the changes and commits
        return user

    # ---------- Amenities ----------
    def create_amenity(self, amenity_data):
        try:
            amenity = Amenity(name=amenity_data.get('name'))
        except TypeError as e:
            raise ValueError(str(e))
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None
        data = {k: v for k, v in amenity_data.items() if k == 'name'}
        self.amenity_repo.update(amenity_id, data)
        return amenity

    # ---------- Places ----------
    PLACE_FIELDS = ('title', 'description', 'price', 'latitude', 'longitude')

    def _check_amenities(self, amenity_ids):
        """Make sure every amenity id exists. Linking amenities to a place is
        added with the relationships in Task 8, so nothing is stored yet."""
        for amenity_id in amenity_ids:
            if not self.amenity_repo.get(amenity_id):
                raise ValueError(f"Amenity not found: {amenity_id}")

    def create_place(self, place_data):
        owner = self.user_repo.get(place_data.get('owner_id'))
        if not owner:
            raise ValueError("Owner not found")
        self._check_amenities(place_data.get('amenities', []))
        data = {k: v for k, v in place_data.items() if k in self.PLACE_FIELDS}
        data.setdefault('description', None)
        try:
            place = Place(owner=owner, **data)
        except TypeError as e:
            raise ValueError(f"Invalid place data: {e}")
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.place_repo.get(place_id)
        if not place:
            return None
        if 'amenities' in place_data:
            self._check_amenities(place_data['amenities'])
        data = {k: v for k, v in place_data.items() if k in self.PLACE_FIELDS}
        self.place_repo.update(place_id, data)  # validates, commits or rolls back
        return place

    def delete_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            return False
        for review in self.review_repo.get_all_by_attribute('place_id', place_id):
            self.review_repo.delete(review.id)
        self.place_repo.delete(place_id)
        return True

    # ---------- Reviews ----------
    def create_review(self, review_data):
        user = self.user_repo.get(review_data.get('user_id'))
        if not user:
            raise ValueError("User not found")
        place = self.place_repo.get(review_data.get('place_id'))
        if not place:
            raise ValueError("Place not found")
        if place.owner_id == user.id:
            raise ValueError("You cannot review your own place")
        if any(r.user_id == user.id for r in self.review_repo.get_all_by_attribute('place_id', place.id)):
            raise ValueError("You have already reviewed this place")
        data = {k: v for k, v in review_data.items() if k in ('text', 'rating')}
        try:
            review = Review(place=place, user=user, **data)
        except TypeError as e:
            raise ValueError(f"Invalid review data: {e}")
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        if not self.place_repo.get(place_id):
            return None
        return self.review_repo.get_all_by_attribute('place_id', place_id)

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if not review:
            return None
        data = {k: v for k, v in review_data.items() if k in ('text', 'rating')}
        self.review_repo.update(review_id, data)
        return review

    def delete_review(self, review_id):
        if not self.review_repo.get(review_id):
            return False
        self.review_repo.delete(review_id)
        return True
