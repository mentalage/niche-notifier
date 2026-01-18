/**
 * API Client for Notify Niche Backend
 */

const API_BASE = "http://localhost:8000/api";

/**
 * Generic API request handler
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  const config = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// Feeds API
export const feedsApi = {
  getAll: (category = null, enabledOnly = false) => {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (enabledOnly) params.append("enabled_only", "true");
    return apiRequest(`/feeds?${params}`);
  },

  create: (feed) =>
    apiRequest("/feeds", {
      method: "POST",
      body: JSON.stringify(feed),
    }),

  update: (url, updates) =>
    apiRequest(`/feeds/${encodeURIComponent(url)}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    }),

  delete: (url) =>
    apiRequest(`/feeds/${encodeURIComponent(url)}`, {
      method: "DELETE",
    }),
};

// Categories API
export const categoriesApi = {
  getAll: () => apiRequest("/categories"),
};

// Articles API
export const articlesApi = {
  getRecent: (category = null, limit = 50) => {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    params.append("limit", limit.toString());
    return apiRequest(`/articles?${params}`);
  },

  getPreview: (category = null, limit = 5) =>
    apiRequest("/preview", {
      method: "POST",
      body: JSON.stringify({ category, limit }),
    }),
};

// Health check
export const healthApi = {
  check: () => apiRequest("/health"),
};
