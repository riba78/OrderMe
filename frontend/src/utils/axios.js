/**
 * Axios HTTP Client Configuration
 * 
 * This module configures the axios HTTP client for API communication.
 * It provides a centralized, configured axios instance for all API requests.
 * 
 * Configuration:
 * - Base URL: From environment variable VUE_APP_API_URL
 * - Default headers: Content-Type: application/json
 * - Authentication: Bearer token from localStorage
 * - Error handling: Automatic logout on 401
 * 
 * Features:
 * - Automatic token injection
 * - Error response handling
 * - Authentication error management
 * - Consistent request configuration
 * 
 * Usage:
 * import axios from '@/utils/axios'
 * axios.get('/endpoint')
 */

import axios from 'axios';
import store from '@/store';
import router from '@/router';

// Create axios instance with base URL from environment variable
const instance = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
});

// Add request interceptor for authentication
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      config: error.config
    });

    if (error.response?.status === 401) {
      store.dispatch('logout');
      router.push('/signin');
    }
    return Promise.reject(error);
  }
);

export default instance; 