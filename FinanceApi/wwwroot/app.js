const state = {
  token: localStorage.getItem('token') || '',
  accounts: [],
  isAdmin: localStorage.getItem('isAdmin') === 'true'
};

const authSection = document.getElementById('authSection');
const dashboard = document.getElementById('dashboard');
const authMsg = document.getElementById('authMsg');
const adminPanel = document.getElementById('adminPanel');

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => null));
}

function setAuthed(isAuthed) {
  authSection.classList.toggle('hidden', isAuthed);
  dashboard.classList.toggle('hidden', !isAuthed);
  adminPanel.classList.toggle('hidden', !isAuthed || !state.isAdmin);
}

async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

function setSession(data) {
  state.token = data.token;
  state.isAdmin = !!data.isAdmin;
  localStorage.setItem('token', data.token);
  localStorage.setItem('isAdmin', String(state.isAdmin));
}

function clearSession() {
  state.token = '';
  state.isAdmin = false;
  localStorage.removeItem('token');
  localStorage.removeItem('isAdmin');
}

async function refreshAccounts() {
  const accounts = await api('/api/accounts');
  state.accounts = accounts;
  document.getElementById('accountsList').innerHTML = accounts
    .map(a => `<li>#${a.id} ${a.name} (${a.type}) - $${a.balance.toFixed(2)}</li>`)
    .join('') || '<li>No accounts yet</li>';

  document.getElementById('accountSelect').innerHTML = accounts
    .map(a => `<option value="${a.id}">${a.name}</option>`)
    .join('');
}

async function refreshTransactions() {
  const txs = await api('/api/transactions');
  document.getElementById('txList').innerHTML = txs
    .map(t => `<li>${t.type} $${t.amount.toFixed(2)} [${t.category}] - ${t.description}</li>`)
    .join('') || '<li>No transactions yet</li>';
}

async function refreshAdminPanel() {
  if (!state.isAdmin) return;

  const users = await api('/api/admin/users');
  document.getElementById('adminUsers').innerHTML = users.map(u => (
    `<li>#${u.id} ${u.fullName} (${u.email}) | admin=${u.isAdmin} 
      <button data-user-id="${u.id}" data-is-admin="${u.isAdmin ? 'false' : 'true'}">${u.isAdmin ? 'Revoke admin' : 'Make admin'}</button>
    </li>`
  )).join('');

  document.querySelectorAll('#adminUsers button').forEach(btn => {
    btn.onclick = async () => {
      const id = Number(btn.dataset.userId);
      const isAdmin = btn.dataset.isAdmin === 'true';
      await api(`/api/admin/users/${id}/role`, { method: 'PATCH', body: JSON.stringify({ isAdmin }) });
      await refreshAdminPanel();
    };
  });

  const accounts = await api('/api/admin/accounts');
  document.getElementById('adminAccounts').innerHTML = accounts.map(a => (
    `<li>#${a.id} owner=${a.ownerEmail} ${a.name} (${a.type}) balance=$${a.balance.toFixed(2)}
      <button data-account-id="${a.id}">Set balance</button>
    </li>`
  )).join('') || '<li>No accounts</li>';

  document.querySelectorAll('#adminAccounts button').forEach(btn => {
    btn.onclick = async () => {
      const id = Number(btn.dataset.accountId);
      const value = prompt('New balance:');
      if (value === null) return;
      await api(`/api/admin/accounts/${id}/balance`, { method: 'PATCH', body: JSON.stringify({ balance: Number(value) }) });
      await refreshAdminPanel();
      await refreshAccounts();
    };
  });

  const transactions = await api('/api/admin/transactions');
  document.getElementById('adminTransactions').innerHTML = transactions
    .map(t => `<li>${t.ownerEmail}: ${t.type} $${t.amount.toFixed(2)} [${t.category}] - ${t.description}</li>`)
    .join('') || '<li>No transactions</li>';
}

async function bootstrapDashboard() {
  if (!state.token) return setAuthed(false);
  try {
    await Promise.all([refreshAccounts(), refreshTransactions()]);
    if (state.isAdmin) await refreshAdminPanel();
    setAuthed(true);
  } catch (e) {
    clearSession();
    setAuthed(false);
    authMsg.textContent = `Session invalid: ${e.message}`;
  }
}

document.getElementById('registerBtn').onclick = async () => {
  try {
    const payload = {
      fullName: document.getElementById('fullName').value,
      email: document.getElementById('email').value,
      password: document.getElementById('password').value
    };
    const data = await api('/api/auth/register', { method: 'POST', body: JSON.stringify(payload) });
    setSession(data);
    authMsg.textContent = `Welcome ${data.fullName}`;
    await bootstrapDashboard();
  } catch (e) {
    authMsg.textContent = `Register failed: ${e.message}`;
  }
};

document.getElementById('loginBtn').onclick = async () => {
  try {
    const payload = {
      email: document.getElementById('email').value,
      password: document.getElementById('password').value
    };
    const data = await api('/api/auth/login', { method: 'POST', body: JSON.stringify(payload) });
    setSession(data);
    authMsg.textContent = `Welcome ${data.fullName}`;
    await bootstrapDashboard();
  } catch (e) {
    authMsg.textContent = `Login failed: ${e.message}`;
  }
};

document.getElementById('addAccountBtn').onclick = async () => {
  try {
    await api('/api/accounts', {
      method: 'POST',
      body: JSON.stringify({
        name: document.getElementById('accountName').value,
        type: document.getElementById('accountType').value,
        openingBalance: Number(document.getElementById('openingBalance').value || 0)
      })
    });
    await refreshAccounts();
    if (state.isAdmin) await refreshAdminPanel();
  } catch (e) {
    authMsg.textContent = `Account create failed: ${e.message}`;
  }
};

document.getElementById('addTxBtn').onclick = async () => {
  try {
    await api('/api/transactions', {
      method: 'POST',
      body: JSON.stringify({
        accountId: Number(document.getElementById('accountSelect').value),
        type: document.getElementById('txType').value,
        category: document.getElementById('txCategory').value,
        amount: Number(document.getElementById('txAmount').value),
        description: document.getElementById('txDescription').value
      })
    });
    await Promise.all([refreshAccounts(), refreshTransactions()]);
    if (state.isAdmin) await refreshAdminPanel();
  } catch (e) {
    authMsg.textContent = `Transaction create failed: ${e.message}`;
  }
};

document.getElementById('logoutBtn').onclick = () => {
  clearSession();
  setAuthed(false);
};

bootstrapDashboard();
