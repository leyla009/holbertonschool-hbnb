import unittest
import uuid
from app import create_app
from app.services import facade
from config import Config


class APITestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.testing = True
        self.client = app.test_client()
        self.admin = self.login(Config.ADMIN_EMAIL, Config.ADMIN_PASSWORD)

    # ---- helpers (unique emails because the facade keeps data between tests) ----
    def login(self, email, password):
        r = self.client.post('/api/v1/auth/login',
                             json={"email": email, "password": password})
        return {"email": email, "token": r.get_json()['access_token']}

    def new_user(self, **overrides):
        """Create a user through the API (admin only), as the admin by default."""
        headers = overrides.pop('headers', None) or self.auth(self.admin)
        data = {"first_name": "Test", "last_name": "User",
                "email": f"{uuid.uuid4().hex[:10]}@example.com",
                "password": "secret123"}
        data.update(overrides)
        return self.client.post('/api/v1/users/', json=data, headers=headers)

    def make_user(self, **overrides):
        """Register a user, log in, and return {'id', 'email', 'token'}."""
        email = f"{uuid.uuid4().hex[:10]}@example.com"
        r = self.new_user(email=email, **overrides)
        user = self.login(email, "secret123")
        user["id"] = r.get_json()['id']
        return user

    @staticmethod
    def auth(user):
        return {'Authorization': f"Bearer {user['token']}"}

    def new_amenity(self, name="Wi-Fi"):
        return self.client.post('/api/v1/amenities/', json={"name": name},
                                headers=self.auth(self.admin))

    def new_place(self, user, **overrides):
        data = {"title": "Cozy flat", "description": "Nice", "price": 80,
                "latitude": 40.4, "longitude": 49.8}
        data.update(overrides)
        return self.client.post('/api/v1/places/', json=data, headers=self.auth(user))

    def new_review(self, user, place_id, **overrides):
        data = {"text": "Great!", "rating": 5, "place_id": place_id}
        data.update(overrides)
        return self.client.post('/api/v1/reviews/', json=data, headers=self.auth(user))


class TestUsers(APITestCase):
    def test_create_and_get(self):
        r = self.new_user()
        self.assertEqual(r.status_code, 201)
        body = r.get_json()
        self.assertNotIn('password', body)
        self.assertIn('id', body)
        g = self.client.get(f"/api/v1/users/{body['id']}")
        self.assertEqual(g.status_code, 200)
        self.assertNotIn('password', g.get_json())
        self.assertNotIn('password', self.client.get('/api/v1/users/').get_json()[0])

    def test_password_required(self):
        r = self.client.post('/api/v1/users/', json={
            "first_name": "A", "last_name": "B", "email": "nopass@example.com"},
            headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.new_user(password="").status_code, 400)

    def test_duplicate_email(self):
        email = f"{uuid.uuid4().hex[:10]}@example.com"
        self.assertEqual(self.new_user(email=email).status_code, 201)
        self.assertEqual(self.new_user(email=email).status_code, 400)

    def test_invalid_input(self):
        self.assertEqual(self.new_user(email="nope").status_code, 400)
        self.assertEqual(self.new_user(first_name="").status_code, 400)
        self.assertEqual(self.new_user(last_name="x" * 51).status_code, 400)
        r = self.client.post('/api/v1/users/', json={"first_name": "A"},
                             headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 400)

    def test_list(self):
        self.new_user()
        r = self.client.get('/api/v1/users/')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.get_json(), list)

    def test_get_not_found(self):
        self.assertEqual(self.client.get('/api/v1/users/nope').status_code, 404)

    def test_update_own_details(self):
        me = self.make_user()
        r = self.client.put(f"/api/v1/users/{me['id']}", json={"first_name": "Changed"},
                            headers=self.auth(me))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()['first_name'], "Changed")
        bad = self.client.put(f"/api/v1/users/{me['id']}", json={"first_name": ""},
                              headers=self.auth(me))
        self.assertEqual(bad.status_code, 400)

    def test_update_requires_token(self):
        me = self.make_user()
        r = self.client.put(f"/api/v1/users/{me['id']}", json={"first_name": "X"})
        self.assertEqual(r.status_code, 401)

    def test_cannot_update_someone_else(self):
        me, other = self.make_user(), self.make_user()
        r = self.client.put(f"/api/v1/users/{other['id']}", json={"first_name": "Hacked"},
                            headers=self.auth(me))
        self.assertEqual(r.status_code, 403)

    def test_cannot_change_email_or_password(self):
        me = self.make_user()
        for payload in ({"email": "new@example.com"}, {"password": "newpass123"}):
            r = self.client.put(f"/api/v1/users/{me['id']}", json=payload,
                                headers=self.auth(me))
            self.assertEqual(r.status_code, 400, payload)

    def test_cannot_make_yourself_admin(self):
        me = self.make_user()
        self.client.put(f"/api/v1/users/{me['id']}", json={"is_admin": True},
                        headers=self.auth(me))
        self.assertFalse(facade.get_user(me['id']).is_admin)


class TestAuth(APITestCase):
    def test_login_and_protected(self):
        me = self.make_user()
        ok = self.client.get('/api/v1/auth/protected', headers=self.auth(me))
        self.assertEqual(ok.status_code, 200)
        self.assertFalse(ok.get_json()['is_admin'])
        self.assertEqual(self.client.get('/api/v1/auth/protected').status_code, 401)

    def test_bad_credentials(self):
        email = f"{uuid.uuid4().hex[:10]}@example.com"
        self.new_user(email=email)
        bad = self.client.post('/api/v1/auth/login',
                               json={"email": email, "password": "wrong"})
        self.assertEqual(bad.status_code, 401)
        nobody = self.client.post('/api/v1/auth/login',
                                  json={"email": "nobody@example.com", "password": "x"})
        self.assertEqual(nobody.status_code, 401)


class TestAmenities(APITestCase):
    def test_create_get_update(self):
        r = self.new_amenity()
        self.assertEqual(r.status_code, 201)
        aid = r.get_json()['id']
        self.assertEqual(self.client.get(f'/api/v1/amenities/{aid}').status_code, 200)
        u = self.client.put(f'/api/v1/amenities/{aid}', json={"name": "Pool"},
                            headers=self.auth(self.admin))
        self.assertEqual(u.status_code, 200)
        self.assertEqual(u.get_json()['name'], "Pool")

    def test_invalid(self):
        self.assertEqual(self.new_amenity(name="").status_code, 400)
        h = self.auth(self.admin)
        self.assertEqual(self.client.post('/api/v1/amenities/', json={}, headers=h).status_code, 400)
        aid = self.new_amenity().get_json()['id']
        self.assertEqual(self.client.put(f'/api/v1/amenities/{aid}', json={"name": ""}, headers=h).status_code, 400)

    def test_not_found(self):
        self.assertEqual(self.client.get('/api/v1/amenities/nope').status_code, 404)
        r = self.client.put('/api/v1/amenities/nope', json={"name": "X"},
                            headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 404)

    def test_list(self):
        self.assertEqual(self.client.get('/api/v1/amenities/').status_code, 200)

    def test_write_requires_admin(self):
        user = self.make_user()
        aid = self.new_amenity().get_json()['id']
        for h, expected in (({}, 401), (self.auth(user), 403)):
            p = self.client.post('/api/v1/amenities/', json={"name": "Sauna"}, headers=h)
            u = self.client.put(f'/api/v1/amenities/{aid}', json={"name": "Sauna"}, headers=h)
            self.assertEqual(p.status_code, expected)
            self.assertEqual(u.status_code, expected)
        self.assertEqual(self.client.get(f'/api/v1/amenities/{aid}').get_json()['name'], "Wi-Fi")


class TestPlaces(APITestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.make_user()
        self.other = self.make_user()
        self.amenity = self.new_amenity().get_json()

    def test_create_with_owner_and_amenities(self):
        r = self.new_place(self.owner, amenities=[self.amenity['id']])
        self.assertEqual(r.status_code, 201)
        pid = r.get_json()['id']
        g = self.client.get(f'/api/v1/places/{pid}').get_json()
        self.assertEqual(g['owner']['id'], self.owner['id'])
        self.assertEqual(g['amenities'][0]['name'], "Wi-Fi")
        self.assertEqual(g['reviews'], [])

    def test_create_requires_token(self):
        r = self.client.post('/api/v1/places/', json={
            "title": "T", "price": 10, "latitude": 1, "longitude": 1})
        self.assertEqual(r.status_code, 401)

    def test_owner_comes_from_token_not_payload(self):
        r = self.new_place(self.owner, owner_id=self.other['id'])
        self.assertEqual(r.get_json()['owner_id'], self.owner['id'])

    def test_invalid_values(self):
        for bad in ({"price": -5}, {"price": 0}, {"latitude": 91}, {"latitude": -91},
                    {"longitude": 181}, {"longitude": -181}, {"title": ""}):
            self.assertEqual(self.new_place(self.owner, **bad).status_code, 400, bad)

    def test_unknown_amenity(self):
        r = self.new_place(self.owner, amenities=["nope"])
        self.assertEqual(r.status_code, 400)

    def test_public_reads(self):
        self.new_place(self.owner)
        self.assertEqual(self.client.get('/api/v1/places/').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/places/nope').status_code, 404)

    def test_update_by_owner(self):
        pid = self.new_place(self.owner).get_json()['id']
        url = f'/api/v1/places/{pid}'
        r = self.client.put(url, json={"title": "New", "price": 95}, headers=self.auth(self.owner))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()['message'], "Place updated successfully")
        g = self.client.get(url).get_json()
        self.assertEqual(g['price'], 95.0)
        self.assertEqual(g['title'], "New")
        bad = self.client.put(url, json={"price": -1}, headers=self.auth(self.owner))
        self.assertEqual(bad.status_code, 400)
        missing = self.client.put('/api/v1/places/nope', json={"title": "X"},
                                  headers=self.auth(self.owner))
        self.assertEqual(missing.status_code, 404)

    def test_update_by_non_owner_or_anonymous(self):
        pid = self.new_place(self.owner).get_json()['id']
        url = f'/api/v1/places/{pid}'
        r = self.client.put(url, json={"title": "Hacked"}, headers=self.auth(self.other))
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.put(url, json={"title": "Hacked"}).status_code, 401)
        self.assertEqual(self.client.get(url).get_json()['title'], "Cozy flat")

    def test_delete(self):
        pid = self.new_place(self.owner).get_json()['id']
        url = f'/api/v1/places/{pid}'
        self.assertEqual(self.client.delete(url).status_code, 401)
        self.assertEqual(self.client.delete(url, headers=self.auth(self.other)).status_code, 403)
        self.assertEqual(self.client.delete(url, headers=self.auth(self.owner)).status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.delete(url, headers=self.auth(self.owner)).status_code, 404)


class TestReviews(APITestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.make_user()
        self.reviewer = self.make_user()
        self.place = self.new_place(self.owner).get_json()

    def test_create_and_get(self):
        r = self.new_review(self.reviewer, self.place['id'])
        self.assertEqual(r.status_code, 201)
        body = r.get_json()
        self.assertEqual(body['user_id'], self.reviewer['id'])
        g = self.client.get(f"/api/v1/reviews/{body['id']}")
        self.assertEqual(g.status_code, 200)
        self.assertEqual(g.get_json()['place_id'], self.place['id'])

    def test_create_requires_token(self):
        r = self.client.post('/api/v1/reviews/', json={
            "text": "x", "rating": 5, "place_id": self.place['id']})
        self.assertEqual(r.status_code, 401)

    def test_cannot_review_own_place(self):
        r = self.new_review(self.owner, self.place['id'])
        self.assertEqual(r.status_code, 400)

    def test_cannot_review_twice(self):
        self.assertEqual(self.new_review(self.reviewer, self.place['id']).status_code, 201)
        self.assertEqual(self.new_review(self.reviewer, self.place['id']).status_code, 400)

    def test_invalid(self):
        p = self.place['id']
        for bad in ({"rating": 0}, {"rating": 6}, {"rating": 4.5}, {"text": ""}):
            self.assertEqual(self.new_review(self.reviewer, p, **bad).status_code, 400, bad)
        self.assertEqual(self.new_review(self.reviewer, "nope").status_code, 400)

    def test_update_and_delete_by_author(self):
        rid = self.new_review(self.reviewer, self.place['id']).get_json()['id']
        url = f'/api/v1/reviews/{rid}'
        h = self.auth(self.reviewer)
        u = self.client.put(url, json={"text": "Amazing", "rating": 4}, headers=h)
        self.assertEqual(u.status_code, 200)
        self.assertEqual(u.get_json()['message'], "Review updated successfully")
        self.assertEqual(self.client.put(url, json={"rating": 9}, headers=h).status_code, 400)
        d = self.client.delete(url, headers=h)
        self.assertEqual(d.status_code, 200)
        self.assertEqual(d.get_json()['message'], "Review deleted successfully")
        self.assertEqual(self.client.delete(url, headers=h).status_code, 404)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_update_and_delete_by_others(self):
        rid = self.new_review(self.reviewer, self.place['id']).get_json()['id']
        url = f'/api/v1/reviews/{rid}'
        self.assertEqual(self.client.put(url, json={"text": "x"}).status_code, 401)
        self.assertEqual(self.client.delete(url).status_code, 401)
        h = self.auth(self.owner)
        self.assertEqual(self.client.put(url, json={"text": "x"}, headers=h).status_code, 403)
        self.assertEqual(self.client.delete(url, headers=h).status_code, 403)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_reviews_of_place(self):
        pid = self.place['id']
        self.new_review(self.reviewer, pid)
        r = self.client.get(f'/api/v1/places/{pid}/reviews')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.get_json()), 1)
        self.assertEqual(self.client.get('/api/v1/places/nope/reviews').status_code, 404)
        detail = self.client.get(f'/api/v1/places/{pid}').get_json()
        self.assertEqual(len(detail['reviews']), 1)

    def test_delete_removes_from_place(self):
        pid = self.place['id']
        rid = self.new_review(self.reviewer, pid).get_json()['id']
        self.client.delete(f'/api/v1/reviews/{rid}', headers=self.auth(self.reviewer))
        self.assertEqual(self.client.get(f'/api/v1/places/{pid}/reviews').get_json(), [])


class TestAdmin(APITestCase):
    def test_only_admin_can_create_users(self):
        user = self.make_user()
        payload = {"first_name": "N", "last_name": "U",
                   "email": f"{uuid.uuid4().hex[:10]}@example.com", "password": "secret123"}
        self.assertEqual(self.client.post('/api/v1/users/', json=payload).status_code, 401)
        r = self.client.post('/api/v1/users/', json=payload, headers=self.auth(user))
        self.assertEqual(r.status_code, 403)
        r = self.client.post('/api/v1/users/', json=payload, headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 201)

    def test_admin_can_create_another_admin(self):
        email = f"{uuid.uuid4().hex[:10]}@example.com"
        r = self.new_user(email=email, is_admin=True)
        self.assertEqual(r.status_code, 201)
        token = self.login(email, "secret123")
        r = self.client.get('/api/v1/auth/protected', headers=self.auth(token))
        self.assertTrue(r.get_json()['is_admin'])

    def test_admin_modifies_any_user_including_email_and_password(self):
        user = self.make_user()
        url = f"/api/v1/users/{user['id']}"
        new_email = f"{uuid.uuid4().hex[:10]}@example.com"
        r = self.client.put(url, json={"first_name": "Changed", "email": new_email,
                                       "password": "brandnew123"},
                            headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()['email'], new_email)
        stored = facade.get_user(user['id'])
        self.assertNotEqual(stored.password, "brandnew123")
        self.assertTrue(stored.verify_password("brandnew123"))
        self.assertFalse(stored.verify_password("secret123"))

    def test_admin_cannot_take_an_existing_email(self):
        a, b = self.make_user(), self.make_user()
        r = self.client.put(f"/api/v1/users/{b['id']}", json={"email": a['email']},
                            headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 400)

    def test_admin_update_errors(self):
        r = self.client.put('/api/v1/users/nope', json={"first_name": "X"},
                            headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 404)
        user = self.make_user()
        r = self.client.put(f"/api/v1/users/{user['id']}", json={"email": "not-an-email"},
                            headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 400)
        r = self.client.put(f"/api/v1/users/{user['id']}", json={"password": ""},
                            headers=self.auth(self.admin))
        self.assertEqual(r.status_code, 400)

    def test_admin_bypasses_place_ownership(self):
        owner = self.make_user()
        pid = self.new_place(owner).get_json()['id']
        url = f'/api/v1/places/{pid}'
        h = self.auth(self.admin)
        r = self.client.put(url, json={"title": "By admin"}, headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get(url).get_json()['title'], "By admin")
        self.assertEqual(self.client.delete(url, headers=h).status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_admin_bypasses_review_ownership(self):
        owner, reviewer = self.make_user(), self.make_user()
        pid = self.new_place(owner).get_json()['id']
        h = self.auth(self.admin)
        rid = self.new_review(reviewer, pid).get_json()['id']
        url = f'/api/v1/reviews/{rid}'
        self.assertEqual(self.client.put(url, json={"text": "Edited"}, headers=h).status_code, 200)
        self.assertEqual(self.client.get(url).get_json()['text'], "Edited")
        self.assertEqual(self.client.delete(url, headers=h).status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_regular_user_still_restricted(self):
        owner, other = self.make_user(), self.make_user()
        pid = self.new_place(owner).get_json()['id']
        r = self.client.put(f'/api/v1/places/{pid}', json={"title": "x"}, headers=self.auth(other))
        self.assertEqual(r.status_code, 403)


if __name__ == '__main__':
    unittest.main()