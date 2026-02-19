const state = { token: localStorage.getItem('token') || '', accounts: [] };

const authSection = document.getElementById('authSection');
const dashboard = document.getElementById('dashboard');
const authMsg = document.getElementById('authMsg');

function setAuthed(isAuthed) {
  authSection.classList.toggle('hidden', isAuthed);
  dashboard.classList.toggle('hidden', !isAuthed);
}

async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const res = await fetch(path, { ...options, headers });
  if (!res.ok) throw new Error(await res.text());
  return res.status === 204 ? null : res.json();
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

async function bootstrapDashboard() {
  if (!state.token) return setAuthed(false);
  try {
    await Promise.all([refreshAccounts(), refreshTransactions()]);
    setAuthed(true);
  } catch {
    state.token = '';
    localStorage.removeItem('token');
    setAuthed(false);
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
    state.token = data.token;
    localStorage.setItem('token', data.token);
    authMsg.textContent = `Welcome ${data.fullName}`;
    await bootstrapDashboard();
  } catch (e) { authMsg.textContent = e.message; }
};

document.getElementById('loginBtn').onclick = async () => {
  try {
    const payload = {
      email: document.getElementById('email').value,
      password: document.getElementById('password').value
    };
    const data = await api('/api/auth/login', { method: 'POST', body: JSON.stringify(payload) });
    state.token = data.token;
    localStorage.setItem('token', data.token);
    authMsg.textContent = `Welcome ${data.fullName}`;
    await bootstrapDashboard();
  } catch (e) { authMsg.textContent = e.message; }
};

document.getElementById('addAccountBtn').onclick = async () => {
  await api('/api/accounts', {
    method: 'POST',
    body: JSON.stringify({
      name: document.getElementById('accountName').value,
      type: document.getElementById('accountType').value,
      openingBalance: Number(document.getElementById('openingBalance').value || 0)
    })
  });
  await refreshAccounts();
};

document.getElementById('addTxBtn').onclick = async () => {
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
};

document.getElementById('logoutBtn').onclick = () => {
  state.token = '';
  localStorage.removeItem('token');
  setAuthed(false);
};

bootstrapDashboard();
