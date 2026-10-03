# HBnB Part 3, Task 9: SQL scripts

| File | Purpose |
|------|---------|
| `schema.sql` | Creates `users`, `places`, `reviews`, `amenities` and `place_amenity` with primary keys, foreign keys (cascading deletes), `UNIQUE` and `CHECK` constraints |
| `initial_data.sql` | Inserts the admin user (`admin@hbnb.io` / `admin1234`, bcrypt hash, fixed id `36c9050e-ddd3-4c3b-9731-9f487208bbc1`) and the amenities WiFi, Swimming Pool, Air Conditioning |
| `crud_tests.sql` | Creates, reads, updates and deletes test rows, checks every constraint and cascade, then removes its own data |

## Run (from `part3/`)

Start from a fresh database file, because the Flask app also creates tables and its own admin when it starts:

```bash
rm -f instance/development.db
sqlite3 instance/development.db < sql/schema.sql
sqlite3 instance/development.db < sql/initial_data.sql
sqlite3 instance/development.db < sql/crud_tests.sql
```

In `crud_tests.sql`, section 4 is expected to print seven `Error: ...` lines (duplicate email, rating 6,
duplicate review, negative price, unknown owner, duplicate amenity name, latitude 120). Those errors mean the
constraints work.

Table and column names match the SQLAlchemy models in `app/models/`.
