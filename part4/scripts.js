// Base URL of the HBnB API (Part 3), which runs on port 5000.
// - On your own machine the page and the API are both on 127.0.0.1.
// - In GitHub Codespaces the browser is NOT on the same machine as the server,
//   so 127.0.0.1 would point at your computer. Each port gets its own public
//   address instead (<name>-8000.app.github.dev, <name>-5000.app.github.dev),
//   so we swap the port in the page's own address to find the API.
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

document.addEventListener('DOMContentLoaded', () => {
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
