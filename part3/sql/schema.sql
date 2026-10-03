-- =============================================================================
-- HBnB - Part 3, Task 9: database schema (SQLite)
-- Table and column names match the SQLAlchemy models in app/models/, so the
-- application can run on a database created with this script.
--
-- Usage (from part3/):  sqlite3 instance/development.db < sql/schema.sql
-- =============================================================================

-- SQLite ignores FOREIGN KEY constraints unless this is switched on
-- (it is per-connection, so the app does the same in app/extensions.py).
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          VARCHAR(36)  PRIMARY KEY,
    first_name  VARCHAR(50)  NOT NULL,
    last_name   VARCHAR(50)  NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE,
    password    VARCHAR(128) NOT NULL,              -- bcrypt hash, never plain text
    is_admin    BOOLEAN      NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1)),
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- places  (a user owns many places)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS places (
    id          VARCHAR(36)   PRIMARY KEY,
    title       VARCHAR(100)  NOT NULL,
    description VARCHAR(1024),
    price       FLOAT         NOT NULL CHECK (price > 0),
    latitude    FLOAT         NOT NULL CHECK (latitude  BETWEEN  -90 AND  90),
    longitude   FLOAT         NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    owner_id    VARCHAR(36)   NOT NULL,
    created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------------
-- reviews  (a user writes many reviews, a place receives many reviews,
--           but a user can review a given place only once)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    id          VARCHAR(36)  PRIMARY KEY,
    text        TEXT         NOT NULL,
    rating      INTEGER      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    place_id    VARCHAR(36)  NOT NULL,
    user_id     VARCHAR(36)  NOT NULL,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (place_id) REFERENCES places (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users  (id) ON DELETE CASCADE,
    UNIQUE (user_id, place_id)
);

-- ---------------------------------------------------------------------------
-- amenities
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS amenities (
    id          VARCHAR(36) PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    created_at  DATETIME    DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME    DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------------
-- place_amenity  (many-to-many association between places and amenities)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS place_amenity (
    place_id    VARCHAR(36) NOT NULL,
    amenity_id  VARCHAR(36) NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id)   REFERENCES places    (id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES amenities (id) ON DELETE CASCADE
);
