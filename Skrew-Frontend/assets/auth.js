(function () {
  'use strict';

  var TOKEN_KEY = 'skrew_token';
  var USER_KEY = 'skrew_username';

  var loginForm = document.getElementById('loginForm');
  var registerForm = document.getElementById('registerForm');
  var errorEl = document.getElementById('authError');

  function showError(message) {
    if (!errorEl) return;
    errorEl.textContent = message;
    errorEl.hidden = false;
  }

  function hideError() {
    if (!errorEl) return;
    errorEl.hidden = true;
    errorEl.textContent = '';
  }

  function parseError(body, fallback) {
    if (!body || body.detail == null) return fallback;
    if (typeof body.detail === 'string') return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map(function (d) { return d.msg || d.message; }).join(', ');
    }
    return fallback;
  }

  function saveAuth(token, username) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, username);
  }

  if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      hideError();

      var username = (document.getElementById('username').value || '').trim();
      var password = document.getElementById('password').value || '';

      if (!username || !password) {
        showError('Please enter your username and password.');
        return;
      }

      try {
        var res = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ username: username, password: password })
        });
        var body = {};
        try { body = await res.json(); } catch (_) {}
        if (!res.ok) {
          throw new Error(parseError(body, 'Could not log in'));
        }
        saveAuth(body.access_token, body.user && body.user.username ? body.user.username : username);
        window.location.href = '/dashboard.html';
      } catch (err) {
        showError(err && err.message ? err.message : 'Could not log in');
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      hideError();

      var username = (document.getElementById('username').value || '').trim();
      var password = document.getElementById('password').value || '';
      var confirmPassword = document.getElementById('confirmPassword').value || '';

      if (!username || !password || !confirmPassword) {
        showError('Please fill in all fields.');
        return;
      }
      if (username.length < 3 || username.length > 32) {
        showError('Username must be between 3 and 32 characters.');
        return;
      }
      if (!/^[A-Za-z0-9_]+$/.test(username)) {
        showError('Username can only contain letters, numbers, and underscores.');
        return;
      }
      if (password.length < 8) {
        showError('Password must be at least 8 characters.');
        return;
      }
      if (password !== confirmPassword) {
        showError('Passwords do not match.');
        return;
      }

      try {
        var res = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ username: username, password: password })
        });
        var body = {};
        try { body = await res.json(); } catch (_) {}
        if (!res.ok) {
          throw new Error(parseError(body, 'Could not register'));
        }

        var loginRes = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ username: username, password: password })
        });
        var loginBody = {};
        try { loginBody = await loginRes.json(); } catch (_) {}
        if (!loginRes.ok) {
          window.location.href = '/login.html';
          return;
        }
        saveAuth(
          loginBody.access_token,
          loginBody.user && loginBody.user.username ? loginBody.user.username : username
        );
        window.location.href = '/dashboard.html';
      } catch (err) {
        showError(err && err.message ? err.message : 'Could not register');
      }
    });
  }
})();
