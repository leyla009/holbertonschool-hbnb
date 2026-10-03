import unittest
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity


class TestModels(unittest.TestCase):
    def setUp(self):
        self.user = User("Leyla", "A", "leyla@example.com")
        self.place = Place("Flat", "Nice", 80, 40.4, 49.8, self.user)

    def test_user_valid(self):
        self.assertEqual(self.user.first_name, "Leyla")
        self.assertTrue(self.user.id)

    def test_user_invalid(self):
        for args in [("", "A", "a@b.com"), ("A", "", "a@b.com"),
                     ("A", "B", "not-an-email"), ("x" * 51, "B", "a@b.com")]:
            with self.assertRaises(ValueError):
                User(*args)

    def test_amenity_invalid(self):
        for name in ("", "   ", "x" * 51, None):
            with self.assertRaises(ValueError):
                Amenity(name)

    def test_place_invalid(self):
        for args in [("", "d", 10, 0, 0), ("T", "d", 0, 0, 0), ("T", "d", -1, 0, 0),
                     ("T", "d", 10, 91, 0), ("T", "d", 10, 0, -181)]:
            with self.assertRaises(ValueError):
                Place(*args, self.user)
        with self.assertRaises(ValueError):
            Place("T", "d", 10, 0, 0, "not a user")

    def test_review_invalid(self):
        for rating in (0, 6, 4.5, "5", True):
            with self.assertRaises(ValueError):
                Review("ok", rating, self.place, self.user)
        with self.assertRaises(ValueError):
            Review("", 5, self.place, self.user)

    def test_links_are_stored_as_ids(self):
        # real relationships (ForeignKey + relationship()) arrive in Task 8
        review = Review("Nice", 5, self.place, self.user)
        self.assertEqual(self.place.owner_id, self.user.id)
        self.assertEqual(review.place_id, self.place.id)
        self.assertEqual(review.user_id, self.user.id)

    def test_review_needs_a_place_and_a_user(self):
        with self.assertRaises(ValueError):
            Review("ok", 5, "not a place", self.user)
        with self.assertRaises(ValueError):
            Review("ok", 5, self.place, "not a user")

    def test_update_changes_updated_at(self):
        before = self.user.updated_at
        self.user.update({"first_name": "New"})
        self.assertEqual(self.user.first_name, "New")
        self.assertGreater(self.user.updated_at, before)
