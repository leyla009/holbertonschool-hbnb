from app.persistence.repository import InMemoryRepository, SQLAlchemyRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

class HBnBFacade:
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(User)
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

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
        return self.user_repo.get_by_attribute('email', email)

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
        amenity = Amenity(**amenity_data)
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
        amenity.update(amenity_data)
        return amenity

    # ---------- Places ----------
    def _resolve_amenities(self, amenity_ids):
        amenities = []
        for amenity_id in amenity_ids:
            amenity = self.amenity_repo.get(amenity_id)
            if not amenity:
                raise ValueError(f"Amenity not found: {amenity_id}")
            amenities.append(amenity)
        return amenities

    def create_place(self, place_data):
        data = dict(place_data)
        owner = self.user_repo.get(data.pop('owner_id', None))
        if not owner:
            raise ValueError("Owner not found")
        amenities = self._resolve_amenities(data.pop('amenities', []))
        data.setdefault('description', None)
        place = Place(owner=owner, **data)
        for amenity in amenities:
            place.add_amenity(amenity)
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
        data = dict(place_data)
        data.pop('owner_id', None)  # the owner cannot be changed
        if 'amenities' in data:
            amenities = self._resolve_amenities(data.pop('amenities'))
            place.amenities = []
            for amenity in amenities:
                place.add_amenity(amenity)
        place.update(data)
        return place

    def delete_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            return False
        for review in list(place.reviews):
            self.review_repo.delete(review.id)
        self.place_repo.delete(place_id)
        return True

# ---------- Reviews ----------
    def create_review(self, review_data):
        data = dict(review_data)
        user = self.user_repo.get(data.pop('user_id', None))
        if not user:
            raise ValueError("User not found")
        place = self.place_repo.get(data.pop('place_id', None))
        if not place:
            raise ValueError("Place not found")
        if place.owner.id == user.id:
            raise ValueError("You cannot review your own place")
        if any(r.user.id == user.id for r in place.reviews):
            raise ValueError("You have already reviewed this place")
        review = Review(place=place, user=user, **data)
        place.add_review(review)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            return None
        return place.reviews

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if not review:
            return None
        data = dict(review_data)
        data.pop('user_id', None)   # the author cannot change
        data.pop('place_id', None)  # the place cannot change
        review.update(data)
        return review

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if not review:
            return False
        if review in review.place.reviews:
            review.place.reviews.remove(review)
        self.review_repo.delete(review_id)
        return True