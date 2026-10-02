import unittest
import uuid
from app import create_app


class APITestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.testing = True
        self.client = app.test_client()

    # ---- helpers (unique emails because the facade keeps data between tests) ----
    def new_user(self, **overrides):
        data = {"first_name": "Test", "last_name": "User",
                "email": f"{uuid.uuid4().hex[:10]}@example.com"}
        data.update(overrides)
        return self.client.post('/api/v1/users/', json=data)

    def new_amenity(self, name="Wi-Fi"):
        return self.client.post('/api/v1/amenities/', json={"name": name})

    def new_place(self, owner_id, **overrides):
        data = {"title": "Cozy flat", "description": "Nice", "price": 80,
                "latitude": 40.4, "longitude": 49.8, "owner_id": owner_id}
        data.update(overrides)
        return self.client.post('/api/v1/places/', json=data)

    def new_review(self, user_id, place_id, **overrides):
        data = {"text": "Great!", "rating": 5, "user_id": user_id, "place_id": place_id}
        data.update(overrides)
        return self.client.post('/api/v1/reviews/', json=data)


class TestUsers(APITestCase):
    def test_create_and_get(self):
        r = self.new_user()
        self.assertEqual(r.status_code, 201)
        body = r.get_json()
        self.assertNotIn('password', body)
        g = self.client.get(f"/api/v1/users/{body['id']}")
        self.assertEqual(g.status_code, 200)
        self.assertEqual(g.get_json()['email'], body['email'])

    def test_duplicate_email(self):
        email = f"{uuid.uuid4().hex[:10]}@example.com"
        self.assertEqual(self.new_user(email=email).status_code, 201)
        self.assertEqual(self.new_user(email=email).status_code, 400)

    def test_invalid_input(self):
        self.assertEqual(self.new_user(email="nope").status_code, 400)
        self.assertEqual(self.new_user(first_name="").status_code, 400)
        self.assertEqual(self.new_user(last_name="x" * 51).status_code, 400)
        r = self.client.post('/api/v1/users/', json={"first_name": "A"})
        self.assertEqual(r.status_code, 400)

    def test_list(self):
        self.new_user()
        r = self.client.get('/api/v1/users/')
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.get_json(), list)

    def test_get_not_found(self):
        self.assertEqual(self.client.get('/api/v1/users/nope').status_code, 404)

    def test_update(self):
        uid = self.new_user().get_json()['id']
        r = self.client.put(f'/api/v1/users/{uid}', json={"first_name": "Changed"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()['first_name'], "Changed")
        self.assertEqual(self.client.put(f'/api/v1/users/{uid}', json={"email": "bad"}).status_code, 400)
        self.assertEqual(self.client.put('/api/v1/users/nope', json={"first_name": "X"}).status_code, 404)

    def test_update_to_taken_email(self):
        a = self.new_user().get_json()
        b = self.new_user().get_json()
        r = self.client.put(f"/api/v1/users/{b['id']}", json={"email": a['email']})
        self.assertEqual(r.status_code, 400)


class TestAmenities(APITestCase):
    def test_create_get_update(self):
        r = self.new_amenity()
        self.assertEqual(r.status_code, 201)
        aid = r.get_json()['id']
        self.assertEqual(self.client.get(f'/api/v1/amenities/{aid}').status_code, 200)
        u = self.client.put(f'/api/v1/amenities/{aid}', json={"name": "Pool"})
        self.assertEqual(u.status_code, 200)
        self.assertEqual(u.get_json()['name'], "Pool")

    def test_invalid(self):
        self.assertEqual(self.new_amenity(name="").status_code, 400)
        self.assertEqual(self.client.post('/api/v1/amenities/', json={}).status_code, 400)
        aid = self.new_amenity().get_json()['id']
        self.assertEqual(self.client.put(f'/api/v1/amenities/{aid}', json={"name": ""}).status_code, 400)

    def test_not_found(self):
        self.assertEqual(self.client.get('/api/v1/amenities/nope').status_code, 404)
        self.assertEqual(self.client.put('/api/v1/amenities/nope', json={"name": "X"}).status_code, 404)

    def test_list(self):
        self.assertEqual(self.client.get('/api/v1/amenities/').status_code, 200)


class TestPlaces(APITestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.new_user().get_json()
        self.amenity = self.new_amenity().get_json()

    def test_create_with_owner_and_amenities(self):
        r = self.new_place(self.owner['id'], amenities=[self.amenity['id']])
        self.assertEqual(r.status_code, 201)
        pid = r.get_json()['id']
        g = self.client.get(f'/api/v1/places/{pid}').get_json()
        self.assertEqual(g['owner']['first_name'], "Test")
        self.assertEqual(g['amenities'][0]['name'], "Wi-Fi")
        self.assertEqual(g['reviews'], [])

    def test_invalid_values(self):
        oid = self.owner['id']
        for bad in ({"price": -5}, {"price": 0}, {"latitude": 91}, {"latitude": -91},
                    {"longitude": 181}, {"longitude": -181}, {"title": ""}):
            self.assertEqual(self.new_place(oid, **bad).status_code, 400, bad)

    def test_unknown_relations(self):
        self.assertEqual(self.new_place("nope").status_code, 400)
        r = self.new_place(self.owner['id'], amenities=["nope"])
        self.assertEqual(r.status_code, 400)

    def test_list_and_not_found(self):
        self.new_place(self.owner['id'])
        self.assertEqual(self.client.get('/api/v1/places/').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/places/nope').status_code, 404)

    def test_update(self):
        pid = self.new_place(self.owner['id']).get_json()['id']
        r = self.client.put(f'/api/v1/places/{pid}', json={"title": "New", "price": 95})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()['message'], "Place updated successfully")
        g = self.client.get(f'/api/v1/places/{pid}').get_json()
        self.assertEqual(g['price'], 95.0)
        self.assertEqual(g['title'], "New")
        self.assertEqual(self.client.put(f'/api/v1/places/{pid}', json={"price": -1}).status_code, 400)
        self.assertEqual(self.client.put('/api/v1/places/nope', json={"title": "X"}).status_code, 404)
class TestReviews(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = self.new_user().get_json()
        self.place = self.new_place(self.user['id']).get_json()

    def test_create_and_get(self):
        r = self.new_review(self.user['id'], self.place['id'])
        self.assertEqual(r.status_code, 201)
        rid = r.get_json()['id']
        g = self.client.get(f'/api/v1/reviews/{rid}')
        self.assertEqual(g.status_code, 200)
        self.assertEqual(g.get_json()['place_id'], self.place['id'])

    def test_invalid(self):
        u, p = self.user['id'], self.place['id']
        for bad in ({"rating": 0}, {"rating": 6}, {"rating": 4.5}, {"text": ""}):
            self.assertEqual(self.new_review(u, p, **bad).status_code, 400, bad)
        self.assertEqual(self.new_review("nope", p).status_code, 400)
        self.assertEqual(self.new_review(u, "nope").status_code, 400)

    def test_update_and_delete(self):
        rid = self.new_review(self.user['id'], self.place['id']).get_json()['id']
        u = self.client.put(f'/api/v1/reviews/{rid}', json={"text": "Amazing", "rating": 4})
        self.assertEqual(u.status_code, 200)
        self.assertEqual(u.get_json()['message'], "Review updated successfully")
        self.assertEqual(self.client.put(f'/api/v1/reviews/{rid}', json={"rating": 9}).status_code, 400)
        d = self.client.delete(f'/api/v1/reviews/{rid}')
        self.assertEqual(d.status_code, 200)
        self.assertEqual(d.get_json()['message'], "Review deleted successfully")
        self.assertEqual(self.client.delete(f'/api/v1/reviews/{rid}').status_code, 404)
        self.assertEqual(self.client.get(f'/api/v1/reviews/{rid}').status_code, 404)

    def test_reviews_of_place(self):
        pid = self.place['id']
        self.new_review(self.user['id'], pid)
        r = self.client.get(f'/api/v1/places/{pid}/reviews')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.get_json()), 1)
        self.assertEqual(self.client.get('/api/v1/places/nope/reviews').status_code, 404)
        detail = self.client.get(f'/api/v1/places/{pid}').get_json()
        self.assertEqual(len(detail['reviews']), 1)

    def test_delete_removes_from_place(self):
        pid = self.place['id']
        rid = self.new_review(self.user['id'], pid).get_json()['id']
        self.client.delete(f'/api/v1/reviews/{rid}')
        self.assertEqual(self.client.get(f'/api/v1/places/{pid}/reviews').get_json(), [])


class TestAuth(APITestCase):
    def test_login_and_protected(self):
        email = f"{uuid.uuid4().hex[:10]}@example.com"
        self.new_user(email=email, password="secret123")

        r = self.client.post('/api/v1/auth/login',
                             json={"email": email, "password": "secret123"})
        self.assertEqual(r.status_code, 200)
        token = r.get_json()['access_token']

        ok = self.client.get('/api/v1/auth/protected',
                             headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(ok.status_code, 200)
        self.assertFalse(ok.get_json()['is_admin'])
        self.assertEqual(self.client.get('/api/v1/auth/protected').status_code, 401)

    def test_bad_credentials(self):
        email = f"{uuid.uuid4().hex[:10]}@example.com"
        self.new_user(email=email, password="secret123")
        bad = self.client.post('/api/v1/auth/login',
                               json={"email": email, "password": "wrong"})
        self.assertEqual(bad.status_code, 401)
        nobody = self.client.post('/api/v1/auth/login',
                                  json={"email": "nobody@example.com", "password": "x"})
        self.assertEqual(nobody.status_code, 401)

if __name__ == '__main__':
    unittest.main()
