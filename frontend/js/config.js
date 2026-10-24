/**
 * Central API Configuration for StudentHub Frontend.
 * Automatically adapts between local development, FastAPI-hosted static mode,
 * and remote deployment.
 */

const CONFIG = {
  // If frontend is served by FastAPI on the same host, relative or window.location.origin works seamlessly.
  // For standalone frontend hosting (e.g. Netlify/Vercel/GitHub Pages), replace with your deployed backend URL.
  API_BASE_URL: (window.location.origin && window.location.origin.startsWith("http"))
    ? window.location.origin
    : "http://127.0.0.1:8000",
  
  // Default pagination limit
  DEFAULT_PAGE_SIZE: 10,
  
  // Request timeout in milliseconds
  REQUEST_TIMEOUT_MS: 15000,
};

// Export to window for global access in vanilla JS
window.APP_CONFIG = CONFIG;
