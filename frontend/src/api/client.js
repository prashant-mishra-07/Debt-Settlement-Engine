const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

async function handleResponse(response) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload?.detail || payload?.message || response.statusText;
    throw new Error(message || "API request failed");
  }
  return payload;
}

export async function createGroup(name) {
  const groupId = typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : `group-${Date.now()}`;

  const payload = {
    group_id: groupId,
    name,
    raw_transactions: [],
    optimized_transactions: [],
    is_optimized: false,
    created_at: new Date().toISOString(),
  };

  const response = await fetch(`${BASE_URL}/groups`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function getGroup(groupId) {
  const response = await fetch(`${BASE_URL}/groups/${encodeURIComponent(groupId)}`);
  return handleResponse(response);
}

export async function addTransaction(groupId, transactionData) {
  const response = await fetch(`${BASE_URL}/groups/${encodeURIComponent(groupId)}/transactions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(transactionData),
  });
  return handleResponse(response);
}

export async function optimizeGroup(groupId) {
  const response = await fetch(`${BASE_URL}/optimize/${encodeURIComponent(groupId)}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}
