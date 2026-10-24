/**
 * StudentHub API Client.
 * Connects directly to the FastAPI REST backend using native fetch().
 * Handles timeouts, serialization, and structured error responses.
 */

const ApiService = {
  /**
   * Helper to perform fetch requests with error handling and timeout.
   */
  async request(endpoint, options = {}) {
    const baseUrl = window.APP_CONFIG.API_BASE_URL.replace(/\/+$/, "");
    const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
    const url = `${baseUrl}${cleanEndpoint}`;

    const headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...(options.headers || {}),
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), window.APP_CONFIG.REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Attempt to parse JSON response body
      let data = null;
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();
        data = text ? { detail: text } : {};
      }

      // Check if HTTP response is in error status
      if (!response.ok) {
        let errorMessage = "An unexpected error occurred.";

        if (data) {
          if (typeof data.detail === "string") {
            errorMessage = data.detail;
          } else if (Array.isArray(data.detail)) {
            // FastAPI Pydantic validation error array
            errorMessage = data.detail.map(e => `${e.loc?.slice(-1)[0] || 'Field'}: ${e.msg}`).join(", ");
          } else if (Array.isArray(data.errors)) {
            errorMessage = data.errors.map(e => `${e.field}: ${e.message}`).join(", ");
          } else if (data.message) {
            errorMessage = data.message;
          }
        }

        const error = new Error(errorMessage);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === "AbortError") {
        throw new Error("Request timed out. Please check your network or server status.");
      }
      if (!err.status && err.message === "Failed to fetch") {
        throw new Error("Cannot connect to server. Ensure the backend is running at " + baseUrl);
      }
      throw err;
    }
  },

  /**
   * Health check endpoint
   */
  async getHealth() {
    return this.request("/health");
  },

  /**
   * Dashboard statistics endpoint
   */
  async getStats() {
    return this.request("/stats");
  },

  /**
   * List students with query parameters
   */
  async getStudents(params = {}) {
    const query = new URLSearchParams();
    if (params.page) query.append("page", params.page);
    if (params.limit) query.append("limit", params.limit);
    if (params.search && params.search.trim()) query.append("search", params.search.trim());
    if (params.course && params.course !== "all") query.append("course", params.course);
    if (params.sort_by) query.append("sort_by", params.sort_by);
    if (params.order) query.append("order", params.order);

    const queryString = query.toString();
    const endpoint = `/students${queryString ? `?${queryString}` : ""}`;
    return this.request(endpoint);
  },

  /**
   * Get single student by ID
   */
  async getStudent(id) {
    return this.request(`/students/${id}`);
  },

  /**
   * Create a new student
   */
  async createStudent(studentData) {
    return this.request("/students", {
      method: "POST",
      body: JSON.stringify(studentData),
    });
  },

  /**
   * Update student details (PUT)
   */
  async updateStudent(id, studentData) {
    return this.request(`/students/${id}`, {
      method: "PUT",
      body: JSON.stringify(studentData),
    });
  },

  /**
   * Delete student by ID
   */
  async deleteStudent(id) {
    return this.request(`/students/${id}`, {
      method: "DELETE",
    });
  },
};

// Export to window
window.ApiService = ApiService;
