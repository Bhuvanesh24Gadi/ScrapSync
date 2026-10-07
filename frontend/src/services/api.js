const BASE =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";


async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response
    .json()
    .catch(() => ({
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
  
// Demo data
export const seedDemo = () =>
  request("/seed", {
    method: "POST",
  });