export const API_BASE = 'http://localhost';
export const API_AUTH = `${API_BASE}:3000/api`;
export const API_AI = `${API_BASE}:8000/api`; // AI RAG API on port 8000
export const API_AGENT = `${API_BASE}:3000/api`; // Keep for backward compatibility

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
  try {
    const res = await fetch(`${API_AUTH}/photos`, {
      method: 'GET',
      credentials: 'include'
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    const data = await res.json();
    console.log('Anh API response:', data);
    return data;
  } catch (error) {
    console.error('Anh API error:', error);
    throw error;
  }
}

export async function Vat() {
  try {
    const res = await fetch(`${API_AUTH}/artifacts`, {
      method: 'GET',
      credentials: 'include'
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    
    const data = await res.json();
    console.log('Vat API response:', data);
    return data;
  } catch (error) {
    console.error('Vat API error:', error);
    throw error;
  }
}

export async function notifyAI(name) {
  try {
    const message = `Hãy nói cho tôi về bối cảnh lịch sử của ${name} và thông tin chi tiết về ${name}.`;

    const res = await fetch(`${API_AI}/ask`, {
      method: 'POST',
      // Don't send credentials to AI API (different port, no auth needed)
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

// ======================== TICKET API ========================
export async function getBankAccounts() {
  const res = await fetch(`${API_AUTH}/bank/accounts`, {
    method: 'GET'
  });
  return await res.json();
}

export async function purchaseTicket(bankAccount, bankPassword) {
  const res = await fetch(`${API_AUTH}/ticket/purchase`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      bank_account: bankAccount,
      bank_password: bankPassword
    })
  });
  return await res.json();
}

export async function getTicketStatus() {
  const res = await fetch(`${API_AUTH}/ticket/status`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

export async function getTicketQR() {
  const res = await fetch(`${API_AUTH}/ticket/qr`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

export async function verifyTicket(ticketCode) {
  const res = await fetch(`${API_AUTH}/ticket/verify`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticket_code: ticketCode })
  });
  return await res.json();
}

// ======================== CHECKIN API ========================
export async function generateCheckinQR(diaDiem) {
  const res = await fetch(`${API_AUTH}/checkin/generate-qr`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dia_diem: diaDiem })
  });
  return await res.json();
}

export async function scanCheckinQR(qrData) {
  const res = await fetch(`${API_AUTH}/checkin/scan-qr`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ qr_data: qrData })
  });
  return await res.json();
}

export async function submitQuiz(diaDiem, answers, correctAnswers) {
  const res = await fetch(`${API_AUTH}/checkin/submit-quiz`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dia_diem: diaDiem,
      answers,
      correct_answers: correctAnswers
    })
  });
  return await res.json();
}

export async function getCheckinList() {
  const res = await fetch(`${API_AUTH}/checkin/list`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

// ======================== TOURS API ========================
export async function getTourLocations() {
  const res = await fetch(`${API_AUTH}/tours/locations`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

export async function getLocationInfo(location) {
  const res = await fetch(`${API_AUTH}/tours/location-info`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ location })
  });
  return await res.json();
}

export async function getItemsByLocation(locations) {
  const res = await fetch(`${API_AUTH}/tours/items-by-location`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ locations })
  });
  return await res.json();
}

export async function createTour(tourName, description, items) {
  const res = await fetch(`${API_AUTH}/tours/create`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tour_name: tourName, description, items })
  });
  return await res.json();
}

export async function getMyTours() {
  const res = await fetch(`${API_AUTH}/tours/my`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

export async function getTourDetail(tourId) {
  const res = await fetch(`${API_AUTH}/tours/${tourId}`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}

// ======================== FEEDBACK API ========================
export async function submitFeedback(rating, comment, category = 'general') {
  const res = await fetch(`${API_AUTH}/feedback`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, comment, category })
  });
  return await res.json();
}

export async function getFeedbackHistory() {
  const res = await fetch(`${API_AUTH}/feedback`, {
    method: 'GET',
    credentials: 'include'
  });
  return await res.json();
}