const API_URL = (() => {
  const codespace = window.location.hostname.match(/^(.*)-\d+\.app\.github\.dev$/);
  if (codespace) {
    return `https://${codespace[1]}-5000.app.github.dev/api/v1`;
  }
  return 'http://127.0.0.1:5000/api/v1';
})();

/* ---------- Cookies ---------- */
function setCookie(name, value) {
  // Session cookie available on every page of the site.
  document.cookie = `${name}=${value}; path=/; SameSite=Lax`;
}

function getCookie(name) {
  // document.cookie looks like "a=1; token=xyz; b=2": split it and find our name.
  const cookies = document.cookie ? document.cookie.split('; ') : [];
  for (const cookie of cookies) {
    const separator = cookie.indexOf('=');
    if (cookie.slice(0, separator) === name) {
      return cookie.slice(separator + 1);
    }
  }
  return null;
}

/* ---------- Login ---------- */
function showLoginError(message) {
  const errorBox = document.getElementById('login-error');
  if (errorBox) {
    errorBox.textContent = message;
    errorBox.hidden = false;
  } else {
    alert(message);
  }
}

function clearLoginError() {
  const errorBox = document.getElementById('login-error');
  if (errorBox) {
    errorBox.textContent = '';
    errorBox.hidden = true;
  }
}

async function loginUser(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });

  if (response.ok) {
    const data = await response.json();
    setCookie('token', data.access_token);
    window.location.href = 'index.html';
    return;
  }

  // The API answers 401 {"error": "Invalid credentials"} for bad credentials
  // and 400 {"message": ...} when a field is missing.
  let detail = response.statusText;
  try {
    const data = await response.json();
    detail = data.error || data.message || detail;
  } catch (e) {
    // response was not JSON; keep the status text
  }
  showLoginError(`Login failed: ${detail}`);
}

/* ---------- Authentication state ---------- */
function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');

  // Login link only for visitors who are not logged in.
  if (loginLink) {
    loginLink.style.display = token ? 'none' : '';
  }

  // Place page: the add-review form is only for logged-in users.
  const addReviewSection = document.getElementById('add-review');
  if (addReviewSection) {
    addReviewSection.style.display = token ? 'block' : 'none';
  }
  return token;
}

/* ---------- Index: list of places ---------- */
async function fetchPlaces(token) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_URL}/places/`, { method: 'GET', headers });
    if (!response.ok) {
      showPlacesMessage(`Could not load places (${response.status} ${response.statusText}).`);
      return;
    }
    const places = await response.json();
    displayPlaces(places);
  } catch (error) {
    showPlacesMessage('Could not reach the server. Please try again later.');
  }
}

function showPlacesMessage(message) {
  const placesList = document.getElementById('places-list');
  placesList.innerHTML = '';
  const paragraph = document.createElement('p');
  paragraph.textContent = message;
  placesList.appendChild(paragraph);
}

function displayPlaces(places) {
  const placesList = document.getElementById('places-list');
  placesList.innerHTML = ''; // remove the static sample cards

  if (places.length === 0) {
    showPlacesMessage('No places available yet.');
    return;
  }

  places.forEach((place) => {
    const card = document.createElement('article');
    card.className = 'place-card';
    card.dataset.price = place.price; // used by the price filter

    // textContent (not innerHTML) so a title can never inject HTML.
    const title = document.createElement('h2');
    title.textContent = place.title;

    const price = document.createElement('p');
    price.className = 'price';
    price.textContent = `$${place.price} per night`;

    const link = document.createElement('a');
    link.className = 'details-button';
    link.href = `place.html?id=${encodeURIComponent(place.id)}`;
    link.textContent = 'View Details';

    card.append(title, price, link);
    placesList.appendChild(card);
  });

  // Respect whatever the dropdown currently says (e.g. after a back-navigation).
  filterPlaces(document.getElementById('price-filter').value);
}

function filterPlaces(maxPrice) {
  document.querySelectorAll('#places-list .place-card').forEach((card) => {
    const withinPrice = maxPrice === 'All' || Number(card.dataset.price) <= Number(maxPrice);
    card.style.display = withinPrice ? '' : 'none';
  });
}

/* ---------- Place details ---------- */
function getPlaceIdFromURL() {
  // "?id=abc-123" -> "abc-123" (null when the parameter is missing)
  return new URLSearchParams(window.location.search).get('id');
}

function showPlaceMessage(message) {
  const details = document.getElementById('place-details');
  details.innerHTML = '';
  const paragraph = document.createElement('p');
  paragraph.textContent = message;
  details.appendChild(paragraph);

  // Nothing to review if the place could not be loaded.
  const addReviewSection = document.getElementById('add-review');
  if (addReviewSection) {
    addReviewSection.style.display = 'none';
  }
}

async function fetchPlaceDetails(token, placeId) {
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_URL}/places/${encodeURIComponent(placeId)}`, {
      method: 'GET',
      headers
    });
    if (response.status === 404) {
      showPlaceMessage('Place not found.');
      return;
    }
    if (!response.ok) {
      showPlaceMessage(`Could not load this place (${response.status} ${response.statusText}).`);
      return;
    }
    displayPlaceDetails(await response.json());
  } catch (error) {
    showPlaceMessage('Could not reach the server. Please try again later.');
  }
}

// <p><b>Label:</b> value</p>, built with textContent so API data can't inject HTML.
function createInfoLine(label, value) {
  const paragraph = document.createElement('p');
  const bold = document.createElement('b');
  bold.textContent = `${label}:`;
  paragraph.append(bold, ` ${value}`);
  return paragraph;
}

function displayPlaceDetails(place) {
  document.title = `${place.title} - HBnB`;

  /* --- Main details --- */
  const details = document.getElementById('place-details');
  details.innerHTML = '';

  const title = document.createElement('h1');
  title.textContent = place.title;

  const info = document.createElement('div');
  info.className = 'place-info';

  const owner = place.owner || {};
  const host = `${owner.first_name || ''} ${owner.last_name || ''}`.trim() || 'Unknown';
  info.appendChild(createInfoLine('Host', host));
  info.appendChild(createInfoLine('Price per night', `$${place.price}`));
  info.appendChild(createInfoLine('Description', place.description || 'No description provided.'));

  const amenitiesLabel = document.createElement('p');
  const amenitiesBold = document.createElement('b');
  amenitiesBold.textContent = 'Amenities:';
  amenitiesLabel.appendChild(amenitiesBold);
  info.appendChild(amenitiesLabel);

  if (place.amenities && place.amenities.length > 0) {
    const amenitiesList = document.createElement('ul');
    amenitiesList.className = 'amenities';
    place.amenities.forEach((amenity) => {
      const item = document.createElement('li');
      item.textContent = amenity.name;
      amenitiesList.appendChild(item);
    });
    info.appendChild(amenitiesList);
  } else {
    amenitiesLabel.append(' None listed');
  }

  details.append(title, info);

  /* --- Reviews --- */
  const reviewsSection = document.getElementById('reviews');
  reviewsSection.innerHTML = '';

  const reviewsTitle = document.createElement('h2');
  reviewsTitle.textContent = 'Reviews';
  reviewsSection.appendChild(reviewsTitle);

  if (!place.reviews || place.reviews.length === 0) {
    const empty = document.createElement('p');
    empty.textContent = 'No reviews yet.';
    reviewsSection.appendChild(empty);
  } else {
    place.reviews.forEach((review) => {
      const card = document.createElement('article');
      card.className = 'review-card';

      const comment = document.createElement('p');
      comment.className = 'comment';
      comment.textContent = review.text;

      const reviewer = document.createElement('p');
      reviewer.className = 'reviewer';
      const name = document.createElement('b');
      name.textContent = `${review.user_name || 'Anonymous'}:`;
      const rating = document.createElement('span');
      rating.className = 'rating';
      rating.textContent = `Rating: ${review.rating} / 5`;
      reviewer.append(name, ' ', rating);

      card.append(comment, reviewer);
      reviewsSection.appendChild(card);
    });
  }
}

/* ---------- Add review ---------- */
// Shows a success/error box just above the review form (created on first use).
function showReviewMessage(form, message, type) {
  let box = document.getElementById('review-message');
  if (!box) {
    box = document.createElement('p');
    box.id = 'review-message';
    box.setAttribute('role', 'alert');
    form.parentNode.insertBefore(box, form);
  }
  box.className = type === 'success' ? 'success-message' : 'error-message';
  box.textContent = message;
  box.hidden = false;
}

function clearReviewMessage() {
  const box = document.getElementById('review-message');
  if (box) {
    box.textContent = '';
    box.hidden = true;
  }
}

// Works for both forms: place.html (#review-text) and add_review.html (#review).
function getReviewText(form) {
  const field = form.elements['review-text'] || form.elements['review'];
  return field.value.trim();
}

async function submitReview(token, placeId, reviewText, rating) {
  const response = await fetch(`${API_URL}/reviews/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      text: reviewText,
      rating: parseInt(rating, 10), // the API wants an integer, the <select> gives a string
      place_id: placeId
    })
  });
  return response;
}

async function handleReviewResponse(response, form, token, placeId) {
  if (response.ok) {
    form.reset();
    showReviewMessage(form, 'Review submitted successfully!', 'success');
    // On the place page, reload the details so the new review shows up right away.
    if (document.getElementById('place-details')) {
      fetchPlaceDetails(token, placeId);
    }
    return;
  }

  // Expired or invalid token (401 / 422 from the JWT library).
  if (response.status === 401 || response.status === 422) {
    showReviewMessage(form, 'Your session has expired. Please log in again.', 'error');
    return;
  }

  // The API explains business-rule failures, e.g. "You have already reviewed this place".
  let detail = response.statusText;
  try {
    const data = await response.json();
    detail = data.error || data.message || data.msg || detail;
  } catch (e) {
    // response was not JSON; keep the status text
  }
  showReviewMessage(form, `Failed to submit review: ${detail}`, 'error');
}

// On add_review.html, replace the sample place name with the real one.
async function fillReviewPlaceName(token, placeId) {
  const nameTag = document.querySelector('.add-review .subtitle b');
  if (!nameTag) {
    return;
  }
  try {
    const response = await fetch(`${API_URL}/places/${encodeURIComponent(placeId)}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      nameTag.textContent = (await response.json()).title;
    } else {
      nameTag.textContent = 'Unknown place';
    }
  } catch (e) {
    // keep the sample text if the server is unreachable
  }
}

function setupReviewForm(form, token, placeId) {
  if (!placeId) {
    showReviewMessage(form, 'No place selected. Go back to the list and pick one.', 'error');
    form.querySelectorAll('input, textarea, select, button').forEach((field) => {
      field.disabled = true;
    });
    return;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearReviewMessage();

    const reviewText = getReviewText(form);
    const rating = form.elements['rating'].value;
    if (!reviewText || !rating) {
      showReviewMessage(form, 'Please write a review and choose a rating.', 'error');
      return;
    }

    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    try {
      const response = await submitReview(token, placeId, reviewText, rating);
      await handleReviewResponse(response, form, token, placeId);
    } catch (error) {
      showReviewMessage(form, 'Could not reach the server. Please try again.', 'error');
    } finally {
      submitButton.disabled = false;
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const token = checkAuthentication();

  // Index page: load the places and wire up the price filter.
  if (document.getElementById('places-list')) {
    fetchPlaces(token);
    document.getElementById('price-filter').addEventListener('change', (event) => {
      filterPlaces(event.target.value);
    });
  }

  // Place page: read ?id= from the URL, then load that place.
  if (document.getElementById('place-details')) {
    const placeId = getPlaceIdFromURL();
    if (placeId) {
      fetchPlaceDetails(token, placeId);
      // Keep the "own page" link pointing at the same place (used by the next task).
      const ownPageLink = document.querySelector('.more-link a');
      if (ownPageLink) {
        ownPageLink.href = `add_review.html?id=${encodeURIComponent(placeId)}`;
      }
    } else {
      showPlaceMessage('No place selected. Go back to the list and pick one.');
    }
  }

  // Review form (place.html and add_review.html).
  const reviewForm = document.getElementById('review-form');
  if (reviewForm) {
    const placeId = getPlaceIdFromURL();

    // The standalone add_review.html page is for logged-in users only.
    // (On place.html the form is simply hidden for visitors, see checkAuthentication.)
    const isStandalonePage = !document.getElementById('place-details');
    if (isStandalonePage && !token) {
      window.location.href = 'index.html';
      return;
    }

    if (token) {
      setupReviewForm(reviewForm, token, placeId);
      if (isStandalonePage && placeId) {
        fillReviewPlaceName(token, placeId);
      }
    }
  }

  const loginForm = document.getElementById('login-form');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      clearLoginError();

      const email = loginForm.elements['email'].value.trim();
      const password = loginForm.elements['password'].value;
      const submitButton = loginForm.querySelector('button[type="submit"]');

      submitButton.disabled = true;
      try {
        await loginUser(email, password);
      } catch (error) {
        showLoginError('Login failed: could not reach the server. Please try again.');
      } finally {
        submitButton.disabled = false;
      }
    });
  }
});