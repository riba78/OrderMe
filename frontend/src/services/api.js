import axios from 'axios';

/**
 * @typedef {Object} ApiError
 * @property {number} status - HTTP status code
 * @property {string} message - Error message
 * @property {any} detail - Detailed error information
 */

/**
 * Custom error class for API errors
 */
class ApiError extends Error {
  constructor(status, message, detail) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for API calls
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    
    // Debug logging for requests
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
      headers: config.headers,
      data: config.data
    });
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    console.error('[API Request Error]', error);
    return Promise.reject(new ApiError(
      error.response?.status,
      'Request configuration error',
      error.message
    ));
  }
);

// Response interceptor for API calls
api.interceptors.response.use(
  response => {
    // Debug logging for successful responses
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      data: response.data
    });
    return response;
  },
  error => {
    // Enhanced error handling with specific error types
    const status = error.response?.status;
    const detail = error.response?.data?.detail || error.message;
    
    console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
      status,
      detail,
      error: error.response?.data
    });

    switch (status) {
      case 401:
        // Handle authentication errors
        console.warn('[API] Authentication error - redirecting to login');
        localStorage.removeItem('token');
        window.location.href = '/signin';
        break;
      
      case 403:
        // Handle authorization errors
        console.warn('[API] Authorization error - insufficient permissions');
        break;
      
      case 405:
        // Handle method not allowed errors
        console.error('[API] Method Not Allowed - Check API endpoint configuration', {
          method: error.config?.method,
          url: error.config?.url
        });
        break;
      
      case 422:
        // Handle validation errors
        console.error('[API] Validation Error', error.response?.data);
        break;
    }

    return Promise.reject(new ApiError(
      status,
      'API request failed',
      detail
    ));
  }
);

export { ApiError };
export default api; 