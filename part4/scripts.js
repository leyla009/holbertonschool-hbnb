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

document.addEventListener('DOMContentLoaded', () => {
  const token = checkAuthentication();

  // Index page: load the places and wire up the price filter.
  if (document.getElementById('places-list')) {
    fetchPlaces(token);
    document.getElementById('price-filter').addEventListener('change', (event) => {
      filterPlaces(event.target.value);
    });
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