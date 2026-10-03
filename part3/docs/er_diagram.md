# HBnB Part 3: Database ER Diagram

Entity-Relationship diagram of the HBnB database, written in [Mermaid.js](https://mermaid.js.org/).
It matches `sql/schema.sql` and the SQLAlchemy models in `app/models/`. GitHub and GitLab render the
diagram below automatically. The same diagram is also exported as `er_diagram.png` (image) and
`er_diagram.mmd` (raw Mermaid source, for the Mermaid Live Editor).

```mermaid
erDiagram
    users {
        string id PK "UUID4, VARCHAR(36)"
        string first_name "VARCHAR(50), NOT NULL"
        string last_name "VARCHAR(50), NOT NULL"
        string email UK "VARCHAR(120), NOT NULL"
        string password "bcrypt hash, NOT NULL"
        boolean is_admin "NOT NULL, default false"
        datetime created_at
        datetime updated_at
    }

    places {
        string id PK "UUID4, VARCHAR(36)"
        string title "VARCHAR(100), NOT NULL"
        string description "VARCHAR(1024), nullable"
        float price "NOT NULL, must be > 0"
        float latitude "NOT NULL, -90 to 90"
        float longitude "NOT NULL, -180 to 180"
        string owner_id FK "references users.id"
        datetime created_at
        datetime updated_at
    }

    reviews {
        string id PK "UUID4, VARCHAR(36)"
        string text "NOT NULL"
        int rating "NOT NULL, 1 to 5"
        string place_id FK "references places.id"
        string user_id FK "references users.id"
        datetime created_at
        datetime updated_at
    }

    amenities {
        string id PK "UUID4, VARCHAR(36)"
        string name UK "VARCHAR(50), NOT NULL"
        datetime created_at
        datetime updated_at
    }

    place_amenity {
        string place_id PK, FK "references places.id"
        string amenity_id PK, FK "references amenities.id"
    }

    users ||--o{ places : "owns"
    users ||--o{ reviews : "writes"
    places ||--o{ reviews : "receives"
    places ||--o{ place_amenity : "has"
    amenities ||--o{ place_amenity : "offered in"
```

## Relationships

| Relationship | Type | How it is implemented |
|--------------|------|-----------------------|
| `users` -> `places` | one-to-many | `places.owner_id` is a foreign key to `users.id` |
| `users` -> `reviews` | one-to-many | `reviews.user_id` is a foreign key to `users.id` |
| `places` -> `reviews` | one-to-many | `reviews.place_id` is a foreign key to `places.id` |
| `places` <-> `amenities` | many-to-many | association table `place_amenity` with the composite primary key (`place_id`, `amenity_id`) |

## Reading the notation

- `||--o{` means "exactly one on the left, zero or more on the right". For example, each place has exactly one
  owner, and a user can own zero or more places.
- A many-to-many relationship cannot be stored directly in SQL, so it is drawn as two one-to-many
  relationships that meet at the association table `place_amenity`.
- `PK` is a primary key, `FK` a foreign key and `UK` a unique key.

## Constraints that the diagram does not show

- `UNIQUE (user_id, place_id)` on `reviews`: a user can review a given place only once.
- Deleting a user, place or amenity cascades to the rows that depend on it (`ON DELETE CASCADE`).
- `CHECK` constraints on `price`, `latitude`, `longitude` and `rating` (ranges shown in the comments above).
