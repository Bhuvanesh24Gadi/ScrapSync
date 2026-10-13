const BASE =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const TOKEN_KEY = "scrapsync_access_token";

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function login(email, password) {
  const response = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json().catch(() => ({
    detail: "Invalid server response",
  }));

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  localStorage.setItem(TOKEN_KEY, data.access_token);
  return data;
}

async function request(path, options = {}) {
  const token = getAccessToken();

  const response = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token
        ? { Authorization: `Bearer ${token}` }
        : {}),
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({
    detail: "Invalid server response",
  }));

  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }

  return data;
}

// Dashboard
export const getDashboard = () =>
  request("/impact/dashboard");

// Materials / Listings
export const getListings = () =>
  request("/materials");

export const createListing = (body) =>
  request("/materials", {
    method: "POST",
    body: JSON.stringify(body),
  });

// Businesses
export const getBusinesses = () =>
  request("/businesses");

// Matching
export const getMatches = (listingId) =>
  request(
    `/matches${
      listingId
        ? `?listing_id=${encodeURIComponent(listingId)}`
        : ""
    }`
  );

// Exchange requests
export const createRequest = (body) =>
  request("/requests", {
    method: "POST",
    body: JSON.stringify(body),
  });

export const getRequests = () =>
  request("/requests");

export const acceptRequest = (requestId) =>
  request(`/requests/${requestId}/accept`, {
    method: "PATCH",
  });

export const rejectRequest = (requestId) =>
  request(`/requests/${requestId}/reject`, {
    method: "PATCH",
  });

// Demo data
export const seedDemo = () =>
  request("/seed", {
    method: "POST",
  });
