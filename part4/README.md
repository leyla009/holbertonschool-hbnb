# HBnB – Part 4: Simple Web Client

The front end of HBnB, a small vacation-rental app. It is plain HTML, CSS and
JavaScript (no framework) and talks to the REST API built in Part 3 through
`fetch`.

## Features

| Page | What it does |
|------|--------------|
| `login.html` | Logs the user in with email and password. The JWT returned by the API is stored in a `token` cookie. |
| `index.html` | Lists all places, fetched from the API. A **Max Price** dropdown (10 / 50 / 100 / All) filters the list in the browser, with no reload. The Login link is hidden when the user is logged in. |
| `place.html?id=<place id>` | Shows one place: host, price, description, amenities and reviews. The "Add a Review" form is only visible to logged-in users. |
| `add_review.html?id=<place id>` | Standalone review form. Visitors who are not logged in are redirected to `index.html`. |

## Project structure

```
part4/
├── index.html         # list of places + price filter
├── login.html         # login form
├── place.html         # place details + inline review form
├── add_review.html    # standalone review form
├── styles.css         # shared styles
├── scripts.js         # all the JavaScript, shared by every page
└── images/            # logo and icons
```

`scripts.js` is loaded on every page. Each page is recognised by the elements it
contains (`#login-form`, `#places-list`, `#place-details`, `#review-form`), so
only the code that page needs runs.

## API endpoints used

The base URL is set at the top of `scripts.js` (`http://127.0.0.1:5000/api/v1`;
in GitHub Codespaces it is worked out from the page's own address).

| Action | Request |
|--------|---------|
| Log in | `POST /auth/login` with `{ email, password }`, returns `{ access_token }` |
| List places | `GET /places/`, returns `id`, `title`, `price`, `latitude`, `longitude` |
| Place details | `GET /places/<id>`, includes owner, amenities and reviews (with `user_name`) |
| Add a review | `POST /reviews/` with `{ text, rating, place_id }`, needs `Authorization: Bearer <token>` |

### Changes made to the Part 3 API

Two small changes were needed for the front end (in `part3/app/api/v1/places.py`):

1. `GET /places/` now also returns `price`, which the price filter needs.
2. Each review in `GET /places/<id>` now includes `user_name`, so the page can
   show who wrote it.

CORS is already enabled for `/api/*` in `part3/app/__init__.py`, so the pages
can call the API from a different port.

## Running it

1. **Start the API** (from `part3/`):

   ```bash
   pip install -r requirements.txt
   python run.py            # http://127.0.0.1:5000
   ```

2. **Serve the front end** (from `part4/`), in a second terminal:

   ```bash
   python -m http.server 8000
   ```

3. Open <http://127.0.0.1:8000/index.html>.

The API creates an administrator on first start: `admin@hbnb.io` / `admin1234`.

## Testing by hand

1. In Swagger (<http://127.0.0.1:5000/api/v1/>), log in as the admin and create
   a few places with different prices, plus a second user (only the admin can
   create users).
2. **Index:** the places appear; changing *Max Price* hides the more expensive
   ones; the Login link disappears after logging in.
3. **Place details:** click *View Details*; check the host, price, description,
   amenities and reviews. The review form should only appear when logged in.
4. **Add review:** log in as a user who is *not* the owner and submit a review.
   You should see a green success message and the new review on the place page.
5. **Error cases:** reviewing the same place twice, or your own place, shows the
   API's error message. Deleting the `token` cookie and opening
   `add_review.html` redirects to `index.html`.

## Notes

- **Authentication:** the JWT lives in a session cookie named `token`. Pages
  check for it to decide what to show, and the API is what actually enforces
  access.
- **Safe rendering:** text from the API is inserted with `textContent`, never
  `innerHTML`, so titles, descriptions and reviews can't inject HTML.
- **Public data:** the places list and place details are public endpoints, so
  they load for logged-out visitors too. The token is sent only when present.
