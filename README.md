# HBnB

HBnB is a simplified Airbnb-style web application, built step by step as a
Holberton School project. It lets users browse places to stay, see their
details and amenities, log in, and leave reviews.

The repository has four parts. Each one builds on the previous one.

| Part | Folder | What it is |
|------|--------|------------|
| 1 | [`part1/`](part1/) | **Design.** Documentation and UML diagrams: package diagram, class diagram and sequence diagrams. |
| 2 | [`part2/`](part2/) | **Business logic and REST API.** Models, facade and endpoints, with data kept in memory. |
| 3 | [`part3/`](part3/) | **Authentication and database.** JWT login, admin rights, ownership rules, SQLAlchemy with SQLite. |
| 4 | [`part4/`](part4/) | **Web client.** HTML, CSS and JavaScript pages that use the Part 3 API. |

## Architecture

HBnB uses a three-layer architecture, with a **Facade** as the single entry
point between the layers:

```
 Web client (part4)  ──HTTP/JSON──▶  Presentation layer (Flask-RESTX API)
                                              │
                                              ▼
                                           Facade
                                              │
                                              ▼
                              Business logic (User, Place, Review, Amenity)
                                              │
                                              ▼
                                  Persistence (repositories → SQLite)
```

- **Presentation:** the API endpoints under `/api/v1/`.
- **Business logic:** the models and their validation rules.
- **Persistence:** repositories. In Part 2 they store data in memory; in Part 3
  they use SQLAlchemy and a SQLite database.

## Part by part

### Part 1: Design

`part1/README.md` explains the three-layer design and the Facade pattern, and
includes the Mermaid diagrams.

### Part 2: Business logic and API

Models for `User`, `Place`, `Review` and `Amenity` with validation, plus REST
endpoints for each. Data lives in memory and is lost on restart, and there is
no authentication yet. See `part2/TESTING.md` for the test plan.

### Part 3: Authentication and database

- Passwords are hashed with bcrypt and users log in through `POST /auth/login`,
  which returns a JWT.
- An administrator is created at start-up (`admin@hbnb.io` / `admin1234`).
- Permissions:
  - Only an admin can create users and amenities.
  - Creating a place or a review requires a logged-in user.
  - Only a place's owner (or an admin) can change or delete it. The same goes
    for reviews and their author.
  - You cannot review your own place, and you can review a place only once.
- Data is stored in SQLite through SQLAlchemy. The `sql/` folder has the raw
  schema, seed data and CRUD tests, and `docs/` has the ER diagram.
- 56 automated tests in `tests/` cover the models and the API.

### Part 4: Web client

Four pages: login, a list of places with a client-side price filter, a place
details page, and a form to add a review. Everything is in one `scripts.js`.
See [`part4/README.md`](part4/README.md) for details.

To support the client, two small changes were made to the Part 3 API: the places
list now includes `price`, and each review on the place-details response
includes the reviewer's name (`user_name`).

## Quick start

You need Python 3 and a recent browser.

```bash
# 1. Start the API (terminal 1)
cd part3
pip install -r requirements.txt
python run.py                     # http://127.0.0.1:5000
                                  # Swagger docs: http://127.0.0.1:5000/api/v1/

# 2. Serve the web client (terminal 2)
cd part4
python -m http.server 8000        # open http://127.0.0.1:8000/index.html
```

Then log in as the admin, or create more users in Swagger, add some places, and
browse them in the client.

### Run the tests

```bash
cd part3
python -m unittest discover -s tests -v
```

## API overview

All routes are under `/api/v1`.

| Resource | Endpoints | Access |
|----------|-----------|--------|
| Auth | `POST /auth/login` | public |
| Users | `POST /users/`, `GET /users/`, `GET /users/<id>`, `PUT /users/<id>` | read: public; create: admin; update: yourself (name only) or admin |
| Amenities | `POST /amenities/`, `GET /amenities/`, `GET /amenities/<id>`, `PUT /amenities/<id>` | read: public; write: admin |
| Places | `POST /places/`, `GET /places/`, `GET /places/<id>`, `PUT`, `DELETE` | read: public; write: owner or admin |
| Reviews | `POST /reviews/`, `GET /reviews/`, `GET /reviews/<id>`, `PUT`, `DELETE`, `GET /places/<id>/reviews` | read: public; write: author or admin |

Protected routes expect an `Authorization: Bearer <token>` header.

## Repository layout

```
.
├── README.md          # this file
├── part1/             # design documentation and UML diagrams
├── part2/             # in-memory API
├── part3/             # JWT + SQLAlchemy API
└── part4/             # web client
```

### `part1/`: design

```
part1/
└── README.md                 # package, class and sequence diagrams (Mermaid)
```

### `part2/`: business logic and API (in memory)

```
part2/
├── README.md
├── TESTING.md                # test plan and manual cURL tests
├── config.py                 # app configuration
├── requirements.txt
├── run.py                    # starts the API
├── app/
│   ├── __init__.py           # create_app(): builds the Flask app
│   ├── api/v1/               # presentation layer: one file per resource
│   │   ├── amenities.py
│   │   ├── places.py
│   │   ├── reviews.py
│   │   └── users.py
│   ├── models/               # business logic: entities and validation
│   │   ├── base_model.py     # id, created_at, updated_at
│   │   ├── amenity.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── user.py
│   ├── persistence/
│   │   └── repository.py     # in-memory repository
│   └── services/
│       └── facade.py         # the Facade between the layers
└── tests/
    ├── test_api.py
    └── test_models.py
```

### `part3/`: authentication and database

```
part3/
├── README.md
├── TESTING.md
├── config.py                 # development / testing configs, JWT secret, admin account
├── requirements.txt
├── run.py                    # starts the API on port 5000
├── app/
│   ├── __init__.py           # create_app(): JWT, bcrypt, CORS, namespaces, admin seed
│   ├── extensions.py         # shared SQLAlchemy instance
│   ├── api/v1/
│   │   ├── auth.py           # POST /auth/login
│   │   ├── users.py
│   │   ├── amenities.py
│   │   ├── places.py
│   │   ├── reviews.py
│   │   └── utils.py          # admin_required, current_user_is_admin
│   ├── models/               # SQLAlchemy models
│   │   ├── base_model.py
│   │   ├── user.py           # bcrypt password hashing
│   │   ├── place.py          # includes the place_amenity link table
│   │   ├── review.py
│   │   └── amenity.py
│   ├── persistence/
│   │   ├── repository.py     # SQLAlchemy repository
│   │   └── user_repository.py
│   └── services/
│       └── facade.py
├── instance/
│   └── development.db        # SQLite database
├── sql/
│   ├── README.md
│   ├── schema.sql            # tables and constraints
│   ├── initial_data.sql      # admin user and starting amenities
│   └── crud_tests.sql        # CRUD and constraint checks
├── docs/
│   ├── er_diagram.md         # ER diagram (Mermaid)
│   ├── er_diagram.mmd        # raw Mermaid source
│   └── er_diagram.png        # exported image
└── tests/
    ├── test_api.py
    └── test_models.py
```

### `part4/`: web client

```
part4/
├── README.md
├── index.html                # list of places + price filter
├── login.html                # login form
├── place.html                # place details + inline review form
├── add_review.html           # standalone review form
├── styles.css                # shared styles
├── scripts.js                # all the JavaScript, shared by every page
└── images/
    ├── logo.png
    ├── icon.png
    ├── icon_bath.png
    ├── icon_bed.png
    └── icon_wifi.png
```

## Technologies

Python, Flask, Flask-RESTX, Flask-JWT-Extended, Flask-Bcrypt, Flask-SQLAlchemy,
Flask-CORS, SQLite, HTML5, CSS3 and vanilla JavaScript (Fetch API).
