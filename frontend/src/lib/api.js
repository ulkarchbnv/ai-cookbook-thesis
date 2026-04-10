export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export function buildApiUrl(path) {
  if (!path) {
    return "";
  }

  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);

  if (!response.ok) {
    let errorMessage = "Request failed";

    try {
      const data = await response.json();
      errorMessage = data.detail || errorMessage;
    } catch {
      errorMessage = "Request failed";
    }

    throw new Error(errorMessage);
  }

  return response.json();
}
