-- =============================================================================
-- HBnB - Part 3, Task 9: CRUD and constraint tests (SQLite)
-- Run after schema.sql and initial_data.sql. All test rows use ids starting
-- with 'test-' and are removed at the end, so the initial data is untouched.
--
-- Usage (from part3/):  sqlite3 instance/development.db < sql/crud_tests.sql
--
-- Sections marked "EXPECTED TO FAIL" print an "Error: ..." line in the sqlite3
-- shell: that error is the PASS result for the test.
-- =============================================================================

PRAGMA foreign_keys = ON;
.headers on
.mode column

-- ---------------------------------------------------------------------------
-- 0. Initial data is in place
-- ---------------------------------------------------------------------------
SELECT '0. initial data' AS test;
SELECT id, first_name, last_name, email, is_admin FROM users WHERE is_admin = 1;
SELECT id, name FROM amenities ORDER BY name;

-- ---------------------------------------------------------------------------
-- 1. CREATE
-- ---------------------------------------------------------------------------
SELECT '1. CREATE' AS test;

INSERT INTO users (id, first_name, last_name, email, password, is_admin)
VALUES ('test-user-1', 'John', 'Doe', 'john.doe@example.com', 'hashed-pw', 0),
       ('test-user-2', 'Jane', 'Roe', 'jane.roe@example.com', 'hashed-pw', 0);

INSERT INTO places (id, title, description, price, latitude, longitude, owner_id)
VALUES ('test-place-1', 'Cozy Flat', 'Close to the old city', 80.0, 40.4093, 49.8671, 'test-user-1');

INSERT INTO place_amenity (place_id, amenity_id)
VALUES ('test-place-1', '55f092fe-f78a-4ce9-86bc-57bc931a55fe'),
       ('test-place-1', '4ff5fcf2-7a13-4afd-bd87-ad9ccc43b92b');

INSERT INTO reviews (id, text, rating, place_id, user_id)
VALUES ('test-review-1', 'Great stay', 5, 'test-place-1', 'test-user-2');

-- ---------------------------------------------------------------------------
-- 2. READ
-- ---------------------------------------------------------------------------
SELECT '2. READ - place with owner' AS test;
SELECT p.title, p.price, u.first_name || ' ' || u.last_name AS owner
FROM places p JOIN users u ON u.id = p.owner_id
WHERE p.id = 'test-place-1';

SELECT '2. READ - place amenities' AS test;
SELECT a.name
FROM place_amenity pa JOIN amenities a ON a.id = pa.amenity_id
WHERE pa.place_id = 'test-place-1'
ORDER BY a.name;

SELECT '2. READ - place reviews' AS test;
SELECT r.rating, r.text, u.email AS reviewer
FROM reviews r JOIN users u ON u.id = r.user_id
WHERE r.place_id = 'test-place-1';

SELECT '2. READ - average rating' AS test;
SELECT AVG(rating) AS avg_rating, COUNT(*) AS review_count
FROM reviews WHERE place_id = 'test-place-1';

-- ---------------------------------------------------------------------------
-- 3. UPDATE
-- ---------------------------------------------------------------------------
SELECT '3. UPDATE' AS test;

UPDATE users SET first_name = 'Johnny', updated_at = CURRENT_TIMESTAMP WHERE id = 'test-user-1';
UPDATE places SET price = 95.5, title = 'Cozy Flat (renovated)', updated_at = CURRENT_TIMESTAMP WHERE id = 'test-place-1';
UPDATE reviews SET rating = 4, text = 'Good stay', updated_at = CURRENT_TIMESTAMP WHERE id = 'test-review-1';

SELECT u.first_name, p.title, p.price, r.rating, r.text
FROM users u, places p, reviews r
WHERE u.id = 'test-user-1' AND p.id = 'test-place-1' AND r.id = 'test-review-1';

-- ---------------------------------------------------------------------------
-- 4. CONSTRAINTS - EXPECTED TO FAIL (each statement must raise an error)
-- ---------------------------------------------------------------------------
SELECT '4. CONSTRAINTS (every statement below must fail)' AS test;

-- 4.1 duplicate email
INSERT INTO users (id, first_name, last_name, email, password)
VALUES ('test-user-x', 'Dup', 'Email', 'john.doe@example.com', 'pw');

-- 4.2 rating out of range
INSERT INTO reviews (id, text, rating, place_id, user_id)
VALUES ('test-review-x', 'Bad rating', 6, 'test-place-1', 'test-user-1');

-- 4.3 same user reviewing the same place twice
INSERT INTO reviews (id, text, rating, place_id, user_id)
VALUES ('test-review-y', 'Second review', 3, 'test-place-1', 'test-user-2');

-- 4.4 place with a negative price
INSERT INTO places (id, title, price, latitude, longitude, owner_id)
VALUES ('test-place-x', 'Free?', -10, 0, 0, 'test-user-1');

-- 4.5 place with an owner that does not exist
INSERT INTO places (id, title, price, latitude, longitude, owner_id)
VALUES ('test-place-y', 'Orphan', 50, 0, 0, 'no-such-user');

-- 4.6 duplicate amenity name
INSERT INTO amenities (id, name) VALUES ('test-amenity-x', 'WiFi');

-- 4.7 latitude out of range
INSERT INTO places (id, title, price, latitude, longitude, owner_id)
VALUES ('test-place-z', 'Nowhere', 50, 120, 0, 'test-user-1');

-- ---------------------------------------------------------------------------
-- 5. DELETE (and cascades)
-- ---------------------------------------------------------------------------
SELECT '5. DELETE - review' AS test;
DELETE FROM reviews WHERE id = 'test-review-1';
SELECT COUNT(*) AS reviews_left FROM reviews WHERE place_id = 'test-place-1';

-- put a review back so the place delete below has something to cascade to
INSERT INTO reviews (id, text, rating, place_id, user_id)
VALUES ('test-review-2', 'Nice', 5, 'test-place-1', 'test-user-2');

SELECT '5. DELETE - place cascades to its reviews and amenity links' AS test;
DELETE FROM places WHERE id = 'test-place-1';
SELECT (SELECT COUNT(*) FROM reviews       WHERE place_id = 'test-place-1') AS reviews_left,
       (SELECT COUNT(*) FROM place_amenity WHERE place_id = 'test-place-1') AS links_left,
       (SELECT COUNT(*) FROM amenities)                                      AS amenities_kept;

SELECT '5. DELETE - user cascades to their places' AS test;
INSERT INTO places (id, title, price, latitude, longitude, owner_id)
VALUES ('test-place-2', 'Temp', 10, 1, 1, 'test-user-1');
DELETE FROM users WHERE id = 'test-user-1';
SELECT COUNT(*) AS places_left FROM places WHERE id = 'test-place-2';

-- ---------------------------------------------------------------------------
-- 6. CLEAN UP
-- ---------------------------------------------------------------------------
DELETE FROM users WHERE id LIKE 'test-%';

SELECT '6. CLEAN UP - only the initial data remains' AS test;
SELECT (SELECT COUNT(*) FROM users)     AS users,
       (SELECT COUNT(*) FROM places)    AS places,
       (SELECT COUNT(*) FROM reviews)   AS reviews,
       (SELECT COUNT(*) FROM amenities) AS amenities;
