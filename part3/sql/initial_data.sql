-- =============================================================================
-- HBnB - Part 3, Task 9: initial data (SQLite)
-- Inserts the administrator user and the three starting amenities.
-- Run it after schema.sql. INSERT OR IGNORE makes it safe to run twice.
--
-- Usage (from part3/):  sqlite3 instance/development.db < sql/initial_data.sql
-- =============================================================================

PRAGMA foreign_keys = ON;

-- Administrator
--   id        : fixed UUID4 (the task requires this exact value)
--   email     : admin@hbnb.io
--   password  : admin1234, stored as a bcrypt hash ($2b$, cost 12)
--   is_admin  : true
INSERT OR IGNORE INTO users (id, first_name, last_name, email, password, is_admin)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$YgyZ6VguVCxFRb5sX66gmuX8QunDVHPCdGICTMrq7DBjsc1q4JDgC',
    1
);

-- Amenities (each id is a UUID4)
INSERT OR IGNORE INTO amenities (id, name) VALUES
    ('55f092fe-f78a-4ce9-86bc-57bc931a55fe', 'WiFi'),
    ('15b90f9e-52a2-4173-b136-83d95f6897dc', 'Swimming Pool'),
    ('4ff5fcf2-7a13-4afd-bd87-ad9ccc43b92b', 'Air Conditioning');
