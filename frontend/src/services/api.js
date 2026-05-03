// Lit l'URL depuis window.__ENV__ injecté au runtime par entrypoint.sh
// Fallback sur VITE_API_URL (dev local sans Docker) puis localhost
const getBase = () =>
  (window.__ENV__ && window.__ENV__.API_URL) ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000'

const BASE_URL = getBase()

function authHeaders(token) {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function handleResponse(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erreur inconnue' }))
    const error = new Error(err.detail || `Erreur ${res.status}`)
    error.status = res.status   // on attache le code HTTP pour le détecter dans les pages
    throw error
  }
  return res.json()
}

// ── Auth ────────────────────────────────────────────────
export async function register(id_client, nom, password) {
  const res = await fetch(`${BASE_URL}/AddClient`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_client, nom, password }),
  })
  return handleResponse(res)
}

export async function login(id_client, password) {
  const res = await fetch(`${BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_client, password }),   // id_client reste string
  })
  return handleResponse(res)
}

export async function getMe(token) {
  const res = await fetch(`${BASE_URL}/Me`, { headers: authHeaders(token) })
  return handleResponse(res)
}

// ── Prédictions ─────────────────────────────────────────
export async function makePrediction(ticket, token) {
  const res = await fetch(`${BASE_URL}/Prediction?ticket=${ticket}`, {
    method: 'POST',
    headers: authHeaders(token),
  })
  return handleResponse(res)
}

export async function getPredictionsByClient(token) {
  const res = await fetch(`${BASE_URL}/GetPredictionByIdClient`, {
    headers: authHeaders(token),
  })
  return handleResponse(res)
}

export async function getPredictionsByTicket(ticket, token) {
  const res = await fetch(`${BASE_URL}/GetPredictionByTicket?ticket=${ticket}`, {
    headers: authHeaders(token),
  })
  return handleResponse(res)
}

export async function getPredictionsByDecision(decision, token) {
  const res = await fetch(`${BASE_URL}/GetPredictionByDecision?decision=${decision}`, {
    headers: authHeaders(token),
  })
  return handleResponse(res)
}

export async function getPredictionById(id, token) {
  const res = await fetch(`${BASE_URL}/GetPredictionByIdPrediction/${id}`, {
    headers: authHeaders(token),
  })
  return handleResponse(res)
}

export async function deletePredictionsByClient(token) {
  const res = await fetch(`${BASE_URL}/DeletePredictionByIdClient`, {
    method: 'DELETE',
    headers: authHeaders(token),
  })
  return handleResponse(res)
}

export async function deletePredictionById(id, token) {
  const res = await fetch(`${BASE_URL}/DeletePredictionByIdPrediction?id_prediction=${id}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  })
  return handleResponse(res)
}

// Tickers disponibles — miroir de enumTicket côté FastAPI
export const TICKERS = [
  // US Mega-caps
  'TSLA', 'AMZN', 'GOOG', 'MSFT', 'AAPL', 'NVDA', 'META', 'NFLX',
  // US autres
  'BA', 'ZS', 'JPM', 'GLD', 'MO',
  // Françaises
  'MC.PA',      // LVMH
  'TTE',        // TotalEnergies
  'AIR.PA',     // Airbus
  // Européennes
  'ASML',       // ASML Holding (Pays-Bas, Nasdaq)
  'SAP',        // SAP SE (Allemagne, NYSE)
  // Streaming & Tech international
  'SPOT',       // Spotify (Suède, NYSE)
  '005930.KS',  // Samsung Electronics (Corée, KRX)
]