export const API_BASE = 'http://34.158.61.248';
export const API_AUTH = `${API_BASE}:3000/api`;
export const API_AGENT = `${API_BASE}:8000/api`;

export async function register(username, password) {
  const res = await fetch(`${API_AUTH}/register`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return await res.json();
}

export async function login(username, password) {
  const res = await fetch(`${API_AUTH}/login`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return await res.json();
}

export async function checkSession() {
  const res = await fetch(`${API_AUTH}/check-session`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

export async function logout() {
  const res = await fetch(`${API_AUTH}/logout`, {
    method: 'POST',
    credentials: 'include'
  });
  return await res.json();
}

export async function getProvinces() {
  const res = await fetch(`${API_AUTH}/provinces`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

export async function sendAgentMessage(message) {
  const res = await fetch(`${API_AGENT}/ai/agent`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return await res.json();
}

export async function Anh() {
  const res = await fetch(`${API_AUTH}/photos`, {
    method: 'GET',
    credentials: 'include'
  })
  return await res.json();
}

export async function Vat() {
  const res = await fetch(`${API_AUTH}/artifacts`, {
    method: 'GET',
    credentials: 'include'
  })
  return await res.json();
}

export async function notifyAI(name) {
  try {
    const message = `Hãy nói cho tôi về bối cảnh lịch sử của ${name} và thông tin chi tiết về ${name}.`;

    const res = await fetch(`${API_AGENT}/ask`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    if (!res.ok) throw new Error('Request AI thất bại');

    return await res.json();
  } catch (err) {
    console.error('notify(name) lỗi:', err);
    return { error: true, message: 'Không thể truy vấn AI' };
  }
}