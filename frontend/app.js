document.addEventListener('DOMContentLoaded', () => {
  const authScreen = document.querySelector('#auth-screen');
  const appShell = document.querySelector('#app-shell');
  const loginForm = document.querySelector('#login-form');
  const authFeedback = document.querySelector('#auth-feedback');
  const userAdmin = document.querySelector('#user-admin');
  const userAdminFeedback = document.querySelector('#user-admin-feedback');
  const userCreateForm = document.querySelector('#user-create-form');
  const userList = document.querySelector('#user-list');
  let accessToken = null;
  let refreshToken = null;
  let currentUser = null;
  const SESSION_KEY = 'rsl-session';

  async function request(path, options = {}, canRefresh = true) {
    const headers = new Headers(options.headers || {});
    if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
    if (options.body && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    let response = await fetch(`/api/v1${path}`, { ...options, headers });
    if (response.status === 401 && canRefresh && refreshToken && path !== '/auth/refresh') {
      const refreshed = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (refreshed.ok) {
        saveSession(await refreshed.json());
        headers.set('Authorization', `Bearer ${accessToken}`);
        response = await fetch(`/api/v1${path}`, { ...options, headers });
      } else {
        clearSession();
      }
    }
    return response;
  }

  function saveSession(session) {
    accessToken = session.access_token;
    refreshToken = session.refresh_token;
    currentUser = session.user;
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
    } catch {}
  }

  function showAuthenticatedApp() {
    authScreen.hidden = true;
    appShell.hidden = false;
    document.querySelector('#current-user-email').textContent = currentUser.email;
    document.querySelector('#current-user-role').textContent = currentUser.role;
    document.querySelector('#current-user-avatar').textContent = currentUser.email.slice(0, 2).toUpperCase();
    userAdmin.hidden = currentUser.role !== 'admin';
    if (currentUser.role === 'admin') loadUsers();
  }

  function clearSession() {
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    try {
      sessionStorage.removeItem(SESSION_KEY);
    } catch {}
    appShell.hidden = true;
    authScreen.hidden = false;
  }

  async function readError(response) {
    const body = await response.json().catch(() => ({}));
    return body.detail || 'Não foi possível concluir a solicitação.';
  }

  async function loadUsers() {
    const response = await request('/users');
    if (!response.ok) {
      userAdminFeedback.textContent = await readError(response);
      return;
    }
    const users = await response.json();
    userList.replaceChildren(...users.map((user) => {
      const row = document.createElement('tr');
      const email = document.createElement('td');
      const role = document.createElement('td');
      email.textContent = user.email;
      role.textContent = user.role;
      row.append(email, role);
      return row;
    }));
  }

  async function login(email, password) {
    authFeedback.textContent = 'Autenticando…';
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        authFeedback.textContent = await readError(response);
        return;
      }
      saveSession(await response.json());
      authFeedback.textContent = '';
      showAuthenticatedApp();
    } catch {
      authFeedback.textContent = 'API indisponível. Verifique se o servidor está em execução.';
    }
  }

  loginForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(loginForm);
    login(data.get('email'), data.get('password'));
  });

  document.querySelectorAll('.demo-account').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelector('#login-email').value = button.dataset.email;
      document.querySelector('#login-password').value = button.dataset.password;
      login(button.dataset.email, button.dataset.password);
    });
  });

  async function restoreSession() {
    let stored = null;
    try {
      stored = JSON.parse(sessionStorage.getItem(SESSION_KEY));
    } catch {}
    if (!stored) return;
    saveSession(stored);
    const response = await request('/me').catch(() => null);
    if (response && response.ok) {
      showAuthenticatedApp();
    } else {
      clearSession();
    }
  }

  restoreSession();

  userCreateForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    userAdminFeedback.textContent = 'Criando conta…';
    const data = new FormData(userCreateForm);
    const response = await request('/users', {
      method: 'POST',
      body: JSON.stringify({
        email: data.get('email'),
        password: data.get('password'),
        role: data.get('role'),
      }),
    });
    if (!response.ok) {
      userAdminFeedback.textContent = await readError(response);
      return;
    }
    userAdminFeedback.textContent = 'Conta criada.';
    userCreateForm.reset();
    await loadUsers();
  });

  document.querySelector('#logout-button').addEventListener('click', async () => {
    try {
      await request('/auth/logout', { method: 'POST' }, false);
    } finally {
      clearSession();
    }
  });

  document.querySelectorAll('.nav-item').forEach((item) => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach((navItem) => navItem.classList.remove('active'));
      item.classList.add('active');
    });
  });

  document.querySelectorAll('.filter').forEach((filter) => {
    filter.addEventListener('click', () => {
      document.querySelectorAll('.filter').forEach((item) => item.classList.remove('selected'));
      filter.classList.add('selected');
    });
  });
});
